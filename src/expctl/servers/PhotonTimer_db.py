from .util import ok # OpalKelly library for (Python) wrappings (checking clk rate on, resetting, and grabbing data)
from math import ceil #, floor
import sys
import os
import math
import time
import numpy as np
from .ServerClass import Server, logger
from ..utilities.util import formatTimeUnits
import datetime
from pathlib import Path

import expdatabase.conf as conf
from expdatabase.db import insertTimer
from expdatabase.types import ShotTimer
from pymongo import MongoClient
from bson import ObjectId

#DIR_DATA = "E:/Data/"
from ..config.config import DIR_DATA
DIR_BITFILE = Path(__file__).parent/"FPGA_bit_file/"

fullpath = "" #os.path.abspath(inspect.getfile(inspect.currentframe()))

# Variables for configuring Verilog to FPGA
dev = ok.okCFrontPanel()
pll = ok.okCPLL22150()

code = DIR_BITFILE/"PhotonTimers.bit"
FPGAsn = '1452000AQ7'

# Settings Used on the FPGA
N_blocks = 32 # number of RAM blocks instantiated
FPGAchan = 8 # number of bits assigned for each set of channels
L_t = 17 # number of bits assigned for each time value

# Set up bytearrays for piping out from blocks of RAM
data_byt = [bytearray(2048) for x in range(N_blocks)]

# Two Functions needed to convert RAM block data into readable data:
# Convert RAM block of byte arrays to bit string
def byt_to_bi(byt):
	bi = bin(byt)[2:].zfill(8)
	return bi
# Convert binary data back to channels and times
def bi_to_dat(array, T):
	dat = []
	for section in range(len(array)/32):
		ramO_din = array[section*32:(section+1)*32]
		if ramO_din == '0'*32:
			pass
		else:
			time_val = 0
			for digit in range(L_t):
				if ramO_din[31-digit] == '1':
					time_val += 2**digit
			time_val *= T
			channels = ''
			for ch in range(FPGAchan):
				if ramO_din[FPGAchan-1-ch] == '1':
					channels += str(ch)
			dat.append(channels+' '+str(time_val))
	return dat

## All the subroutines for the Main Function
# Subroutine 1: Configure the FPGA for Timr Program
def Config_FPGA():
	#Instantiate okC structure
	if dev.OpenBySerial(FPGAsn) == -1:
		print("I can't connect...")
		exit()
	dev.GetEepromPLL22150Configuration(pll)
	dev.SetPLL22150Configuration(pll)
	
	f = str(float(pll.GetOutputFrequency(0)) * (10 ** 6))
	T = 1 / float(f)
	print("Timing Resolution =", T*1e9, "ns")
	dev.ConfigureFPGA(str(code)) # Configure FPGA with bit code
	
	return T
	
# Subroutine 2: Start the FPGA state machine and let it wait for the trigger
def RunServer(seq, autostart=0):
	TIME_START = time.time()
	chan = seq.getChannelByName("Photon Timer")
	thehardwarevalues = chan.GetHardwareValues()
	save_switch_chan = seq.getChannelByName("Photon Timer Save")
	save_switch = save_switch_chan.GetHardwareValues()[0][1] # Getting the save switch from the sequence
	
	if autostart == 0:
		# Start FPGA state machine
		dev.SetWireInValue(0x00, 1)
		dev.UpdateWireIns()
		dev.SetWireInValue(0x00, 0)
		dev.UpdateWireIns()
		
		newval = 0
		oldval = 0
		NumOfTrace = 0
		for interval in thehardwarevalues:
			if interval[1] == 1 and interval[3] == 1:
				newval = 1
				if newval != oldval:
					NumOfTrace += 1
			oldval = newval
		
		if NumOfTrace > 0:
			return 1, save_switch
		else:
			return 0, 0
			
	elif autostart == 1:
		TIME_STOP = time.time()
		return TIME_STOP-TIME_START
	
# Subroutine 3: Acquire Data from the FPGA
def Acquire(T, SeqFolderName='', SeqRunName='michael', save=0):
	# Get data from FPGA
	print('Waiting for trigger!')
	status = 'wait'
	while status == 'wait':
		dev.UpdateTriggerOuts()
		if dev.IsTriggered(0x60, 0x01) == True:
			status = 'grab data'
			print("FPGA finished recording, ready to pipe out data!")
	if status == 'grab data':
		for block in range(N_blocks):
			dev.ReadFromPipeOut(0xA0 + block, data_byt[block])
	dev.SetWireInValue(0x06, 1)
	dev.UpdateWireIns()
	dev.SetWireInValue(0x06, 0)
	dev.UpdateWireIns()
	
	# Convert the data from the PipeOut to string data
	# if save == 1:
	# 	print(SeqFolderName)
	# 	if SeqFolderName.strip() == '':
	# 		SeqFolderName = "PhotonCounter"
	# 	date_dir = datetime.datetime.now().strftime("%Y/%m/%d/")
	# 	#full_dir = DATA_DIR+date_dir+SeqFolderName+"/"
	# 	full_dir = DIR_DATA/date_dir/SeqFolderName

	# 	if not os.path.exists(full_dir):
	# 		os.makedirs(full_dir)
		
	# 	data_byt_np = np.array(data_byt)
	# 	data_byt_np = np.reshape(data_byt_np, (2048*32))
		
	# 	f = open(full_dir/("PT"+SeqRunName+'.bin'), 'wb')
	# 	for ii in range(N_blocks):
	# 		f.write(data_byt[ii])
	# 	f.close()
		
	# 	print('Finish saving the data!')
	data_byt_flat = bytearray(b''.join(data_byt))

	return data_byt_flat


def SaveDataDB(client, run_id, counter, data, save):
	if client is not None:
		j = int(counter)
		run_id_bson = ObjectId(run_id)
		run_time = datetime.datetime.now()
		shot = ShotTimer(run_time, j, 1, data)
		insertTimer(client=client, run_id=run_id_bson, shot=shot, save=save)
		logger.info("Saved shot to DB")

class TimerServer(Server):

	def __init__(self, name, port, message, client):
		super().__init__(name, port, message)
		self.client = client

	def cmd_queue(self):
		if self.seq is None:
			logger.error('QUEUE failed. Sequence has not been imported!')
			#self.send_msg(self.ReplyHeader() + 'QUEUE failed. Sequence has not been imported!')
		else:
			try:
				acquire_data, save_data = RunServer(self.seq, autostart=0)
				logger.debug('Sequence has been queued... Trigger it whenever!')
				self.send_msg(self.ReplyHeader() + 'Sequence has been queued... Trigger it whenever!')
				logger.debug(f'Acquire: {acquire_data}, Save: {save_data}')
				# Get the save switch from the sequence
				save_switch = self.seq.saveswitch
				logger.info(f"Saving according to save_switch {save_switch}")
				
				if acquire_data == 1:
					data = Acquire(CLK_freq, self.seq.foldername, self.seq.runname, save_data)
					#logger.debug(f"Acquired data")
					if save_switch > 0:
							#SaveDataWithCLK(self.seq.foldername, self.seq.runname, data)
							save = True if save_switch==2 else False
							SaveDataDB(client=self.client, run_id=self.seq.run_id, counter=self.seq.counter, data=data, save=save)
			
			except:
				logger.exception("Failed to acquire and save data!")

	def run(self):
		return RunServer(self.seq, 1)

	def plotdata(self):
		return [0,], [0,]

if __name__ == '__main__':
	message = """===========================================
	==       Photon Timer Server 1           ==
	===========================================
	Number of RAM blocks used: 32
	"""
	CLK_freq = Config_FPGA()
	#Initialize experiment database connection
	try:
		client = MongoClient(host=conf.DB_HOST, port=conf.DB_PORT, username=conf.USER_RAW_WRITER , password=conf.PASSWORD_RAW_WRITER, authSource=conf.DB_AUTH)
	except:
		logger.exception("Database connection could not be established!")
		client = None
	else:
		logger.info("Database connected.")

	server = TimerServer("PTIn1", 60623, message=message, client=client)
	server.main_loop()