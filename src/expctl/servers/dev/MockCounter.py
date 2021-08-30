#from .util import ok # OpalKelly library for (Python) wrappings (checking clk rate on, resetting, and grabbing data)
from math import ceil #, floor
import sys
import os
import math
import time
import numpy as np
from numpy.lib.npyio import save
from ..ServerClass import Server, logger
#from ...utilities.util import formatTimeUnits
import datetime
from pathlib import Path
from ...config.config import DIR_DATA
import zmq
import expdatabase.conf as conf
from expdatabase.db import insertCounter
from expdatabase.types import ShotCounter
from pymongo import MongoClient
from bson import ObjectId

# This server implements a global "trigger" via Zeromq pub/sub to receive a trigger from digital out
trigger_port = 70111

from .datagenerator import DataGenerator, Lorentzian

def samplefunc(x, vrs=10., x0=0.):
	return Lorentzian(x-x0,-vrs, 1.3) + Lorentzian(x-x0,vrs-2, 1.7) + Lorentzian(x-x0,0, 0.2)

dg = DataGenerator(samplefunc, df=20., nbins=1000)

# Subroutine 1: Start the FPGA's state machine
def Config_FPGA():
	logger.debug("FPGA configured.")
		
# Subroutine 2: Get data from FPGA, one run of laser pulsing on and off
def SetBinSize(binsize, maxrate=20): 
	# In: binsize in microseconds
	# Out: Data array (converted from the bytearray piped out from FPGA
	
	# Prepare to configure the bin of time for counts on FPGA
	f = 100.0
	print("FPGA Clk rate =", f, "MHz")
	T_bins_cycs = int(ceil(binsize * f)) - 1 # How high must t count in Verilog code to reach t_bins
	T_bins_rounded = (T_bins_cycs + 1) / f
	print("I've rounded your desired time bin size to ", T_bins_rounded, " microseconds.")
	return 1

def Acquire():
	# Wait for the FPGA to finish collecting counts for one laser cycle
	try:
		string = socket.recv()
	except:
		logger.exception("Waiting for trigger timed out!")
		return -1
	else:
		logger.info("Received tigger: {}".format(string.decode()))
				
		# Once the FPGA says a laser cycle finished, grab the data and then convert/graph it
		addr_max = 1000
		print("This laser pulse has counts parsed into", addr_max, "bins.")
		
		clockcount = 10327971744482
		_, data = dg.hist(np.random.poisson(200)) #200 is roughly the number of counts we get per shot now
		print("Clock cycles:", clockcount)
		print("Total counts:", np.sum(data), '\n')
		if len(data) == 0:
			return -1
		return data, clockcount

def SaveData(FolderName, SeqRunName, data):
	if FolderName.strip() == "":
		FolderName = 'SPCM'
	
	run_time = datetime.datetime.now()
	trace_dir = run_time.strftime("%Y/%m/%d/")
	trace_full_dir = DIR_DATA/trace_dir/FolderName
	trace_name = ""
	
	if not os.path.exists(trace_full_dir):
			os.makedirs(trace_full_dir)
	
	trace_name = trace_full_dir/(SeqRunName+".txt")
	
	with open(trace_name, 'w') as f:
			for item in data:
					f.write("{}\n".format(item))
	f.close()

def SaveDataWithCLK(FolderName, SeqRunName, DataCLK):
	data, clk = DataCLK

	if FolderName.strip() == "":
		FolderName = 'SPCM'
	
	run_time = datetime.datetime.now()
	trace_dir = run_time.strftime("%Y/%m/%d/")
	trace_full_dir = DIR_DATA/trace_dir/FolderName
	trace_name = ""
	
	if not os.path.exists(trace_full_dir):
			os.makedirs(trace_full_dir)
	
	trace_name = trace_full_dir/("PC"+SeqRunName+"_CLK"+str(clk)+".txt")
	
	with open(trace_name, 'w') as f:
			for item in data:
					f.write("{}\n".format(item))
	f.close()

def SaveDataDB(client, run_id, counter, DataCLK, save):
	data, clk = DataCLK
	data = np.asarray(data)
	clk = int(clk)
	j = int(counter)
	run_id_bson = ObjectId(run_id)
	run_time = datetime.datetime.now()
	shot = ShotCounter(run_time, j, clk, data)
	insertCounter(client=client, run_id=run_id_bson, shot=shot, save=save)
	
		
def RunServer(seq, autostart = 1):
	TIME_START = time.time()
	
	chan = seq.getChannelByName("Photon Counter")
	sample_num_chan = seq.getChannelByName("Counter Bin Num")
	save_switch_chan = seq.getChannelByName("Counter Save")
	max_rate = seq.getChannelByName("Counter Max Rate")
	
	# Get sample number and save switch
	sample_num_values = sample_num_chan.GetHardwareValues()
	save_switch_values = save_switch_chan.GetHardwareValues()
	max_rate_values = max_rate.GetHardwareValues()
	sample_num = sample_num_values[0][1]
	save_switch = save_switch_values[0][1]
	max_count_rate = max_rate_values[0][1]
	# Get trigger channel
	thehardwarevalues = chan.GetHardwareValues()
	run_name = seq.runname
	run_id = seq.run_id
	logger.info("Sequence has run_id: {}".format(run_id))
	logger.info("Sequence has j: {}".format(seq.counter))
	newval = 0
	oldval = 0
	NumOfTrace = 0
	TraceStart = 0
	TraceEnd = 0
	TraceLength = []
	
	BinSize = 0
	MaxTraceLength = 0
	MaxSampleNum = sample_num
	
	e = 1
	if autostart == 0: # Load sequence data and calculate bin size
		for interval in thehardwarevalues:
			if interval[1] == 0 and interval[3] == 0:
				newval = 0
				if newval != oldval:
					TraceEnd = interval[0]
					TraceLength.append((TraceEnd-TraceStart))
					NumOfTrace += 1
			else:
				newval = 1
				if newval != oldval:
					TraceStart = interval[0]
			oldval = newval
				
		if NumOfTrace > 0:
			MaxTraceLength = max(TraceLength)
			BinSize = MaxTraceLength / MaxSampleNum
			print("Bin size:", BinSize, "us")
			e = SetBinSize(BinSize, max_count_rate)
			
			if e == 1:
				if save_switch == 1:
					return 1, 1 # First argument is acquring switch, and the second one is saving switch
				else:
					return 1, 0
		else:
			return 0, 0
	
	elif autostart == 1:
		TIME_STOP = time.time()
		return TIME_STOP - TIME_START
			

class MockCounterServer(Server):

	def __init__(self, name, port, message, client):
		super().__init__(name, port, message)
		self.client = client

	def cmd_queue(self):
		if self.seq is None:
			logger.error('QUEUE failed. Sequence has not been imported!')
			self.send_msg(self.ReplyHeader() + 'QUEUE failed. Sequence has not been imported!')
		else:
			try:
				#Config_FPGA()
				acquire_data, save_data = RunServer(self.seq, 0)
				logger.debug('Sequence has been queued... Trigger it whenever!')
				self.send_msg(self.ReplyHeader() + 'Sequence has been queued... Trigger it whenever!')
				logger.debug(f'Acquire: {acquire_data}, Save: {save_data}')
				# Get the save switch from the sequence
				save_switch = self.seq.saveswitch
				if acquire_data == 1:
					data = Acquire()
					if data == -1:
						logger.error("FPGA returned nothing")
					if save_switch > 0:
						#SaveData(server.seq.foldername, server.seq.runname, data[0])
						#SaveDataWithCLK(self.seq.foldername, self.seq.runname, data)
						save = True if save_switch==2 else False
						SaveDataDB(client=self.client, run_id=self.seq.run_id, counter=self.seq.counter, DataCLK=data, save=save)
			except:
				logger.exception("Failed to acquire data from FPGA.")

	def run(self):
		return RunServer(self.seq, 1)

	def plotdata(self):
		return 1

if __name__ == '__main__':
	message = """===========================================
	==       Photon Counter Server 1         ==
	===========================================
	Maximum Number of Data Points: 1024
	"""
	# Socket to talk to server
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.setsockopt(zmq.LINGER,      0 )
	socket.setsockopt(zmq.RCVTIMEO, 10000)

	socket.connect("tcp://localhost:{:d}".format(trigger_port))
	socket.subscribe("") # Subscribe to all topics
	logger.info("Connected to trigger")

	#Initialize experiment database connection
	try:
		client = MongoClient(host=conf.DB_HOST, port=conf.DB_PORT, username=conf.USER_RAW_WRITER , password=conf.PASSWORD_RAW_WRITER, authSource=conf.DB_AUTH)
	except:
		logger.exception("Database connection could not be established!")
	else:
		logger.info("Database connected.")

	Config_FPGA()
	server = MockCounterServer("SOut1", 60621, message=message, client=client)
	server.main_loop()