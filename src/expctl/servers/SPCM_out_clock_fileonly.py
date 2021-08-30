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

#DIR_DATA = "E:/Data/"
from ..config.config import DIR_DATA
DIR_BITFILE = Path(__file__).parent/"FPGA_bit_file/"

fullpath = "" #os.path.abspath(inspect.getfile(inspect.currentframe()))

# Variables for configuring Verilog to FPGA
dev = ok.okCFrontPanel()
pll = ok.okCPLL22150()
# code = r"C:\Users\Simonlab\Programming\dev\photons_counter\photon_count_DAC_comp_v_clock\counters.bit"
# code = r"C:\Users\Simonlab\Programming\Control Suite\servers\FPGA_bit_file\counters_TwoSPCM.bit"
code = DIR_BITFILE/"counters.bit" #"C:\ExperimentSoftwares\Control_Suite_X\servers\FPGA_bit_file\counters.bit"
fpga_clk = 100 # desired FPGA clk speed (in MHz)[must be in {200/n: n is a positive integer}]
FPGAsn = '14290008XL'

## Functions to help Configure the FPGA
# Function to turn time bin from any type (convertible to int) into bytearray
def dec_to_bytearray(no):
	hex_no = hex(int(no))[2:]
	hex_no = hex_no.zfill(4)
	array = [] # Decoding hex encoding of number into bytearray
	for i in range(len(hex_no)):
		if not i%2: # even indeces --> new bytearray digit;
			array.append(hex_no[i])
		else: # otherwise add onto newest existing digit
			array[i//2] += hex_no[i] #PY3 fix
	byte_array = [int(array[i], 16) for i in range(len(array)-1,-1,-1)]
	return byte_array

# Two Functions needed to convert RAM block data into readable data:
# 1) Convert 2 bytes back to 16 bits
def byte_to_bi(byte):
	bi = bin(byte)[2: ]
	if len(bi) < 8:
		bi = str(0) * (8 - len(bi)) + bi
	bi = [bi[j] for j in range(len(bi))]
	return bi

# 2) Convert 16 bits into base-10 count of photons from pipe
def bi_to_data(array):
	count = 0
	n = len(array)
	for digit in range(n):
		if array[n - 1 - digit] == '1':
			count += 2 ** digit
	return count


## All the subroutines for the Main Function
# Assuming binsize inputted as a float or int; Hardcoding (maxF_lsr = 5 MHz) for now

# Subroutine 1: Start the FPGA's state machine
def Config_FPGA():
	# In: 
	# Out: FPGA configured and started state machine (beginning to count and output to DAC)
	
	# Instantiate okC structure / Check whether FPGA can be configured
	if dev.OpenBySerial(FPGAsn) == -1:
		print("I currently can't configure the FPGA. You may need to turn off Opal Kelly FrontPanel or still plug in the FPGA microUSB.")
		exit()
	else:
		print("Connected to the FPGA " + FPGAsn)
	dev.GetEepromPLL22150Configuration(pll)
	dev.SetPLL22150Configuration(pll)
	
	# Configure (clk rate and setup of) FPGA, reset it and start waiting for 'laser' to go on
	print(dev.ConfigureFPGA(str(code)), " ~ Connected to FPGA!")
	pll.SetDiv1(pll.GetDiv1Source(), int(ceil(200 / fpga_clk))) # Set FPGA clk rate 200/n MHz; here n = 2
	

# Subroutine 2: Get data from FPGA, one run of laser pulsing on and off
def SetBinSize(binsize, maxrate=20): 
	# In: binsize in microseconds
	# Out: Data array (converted from the bytearray piped out from FPGA
	
	# Prepare to configure the bin of time for counts on FPGA
	f = float(pll.GetOutputFrequency(0))
	print("FPGA Clk rate =", f, "MHz")
	T_bins_cycs = int(ceil(binsize * f)) - 1 # How high must t count in Verilog code to reach t_bins
	T_bins_rounded = (T_bins_cycs + 1) / f
	print("I've rounded your desired time bin size to ", T_bins_rounded, " microseconds.")
	T_bins_array = dec_to_bytearray(T_bins_cycs)
	
	# Prepare to configure DAC scaling factor; max laser freq ~ max counts per time bin
	maxF_lsr_usr    = 1.0*maxrate # Max count rate (MHz)
	count_scale_dec = 65535/(maxF_lsr_usr*binsize) if binsize!=0 else 1. # Avoid zero probe time
	# count_scale_dec = 6e4
	# fractional scaling of total counts per bin such that we can see it from DACout
	count_scale = dec_to_bytearray(count_scale_dec)
	
	# Start FPGA's state machine, Configure binsize, scalefact
	dev.SetWireInValue(0x00, 1) # WireIn: FPGA start running Verilog
	dev.UpdateWireIns()
	dev.WriteToPipeIn(0x80, bytearray(T_bins_array)) # WireIn how to bin time for counts of detections
	dev.WriteToPipeIn(0x81, bytearray(count_scale)) # WireIn how many photons to expect per time bin
	print("Wrote to pipes!")
	dev.SetWireInValue(0x00, 0) # stop telling FPGA to start
	dev.UpdateWireIns()
	print("Bin size set!")
	#dev.UpdateTriggerOuts() #Hack to fix the triggering problem
	return 1
	
def Acquire():
	# Wait for the FPGA to finish collecting counts for one laser cycle
	status = 'wait' 
	while status == 'wait':
		dev.UpdateTriggerOuts()
		if dev.IsTriggered(0x60, 0x01) == True:
			status = 'grab data'
			print("Device is triggered!")
			
	# Once the FPGA says a laser cycle finished, grab the data and then convert/graph it
	if status == 'grab data': 
		dev.UpdateWireOuts() # Check with FPGA to see how big the byte array should be (2x highest bin's address)
		addr_max = dev.GetWireOutValue(0x30)
		print("This laser pulse has counts parsed into", addr_max, "bins.")
		
		dev.UpdateWireOuts() 
		clockcount1 = dev.GetWireOutValue(0x20)
		clockcount2 = dev.GetWireOutValue(0x21)
		clockcount3 = dev.GetWireOutValue(0x22)
		clockcount4 = dev.GetWireOutValue(0x23)
		clockcount = (clockcount4<<48) + (clockcount3<<32) + (clockcount2<<16) + clockcount1
		# clockcount = [clockcount1, clockcount2, clockcount3, clockcount4]
		print("Clock cycles:", clockcount)
		
		data_byte = bytearray(2*addr_max)
		dev.ReadFromPipeOut(0xA0, data_byte)
		print("Read from pipe!")
		dev.SetWireInValue(0x06, 1) # Communicate to FPGA that Comp graphed most recent set of counts
		dev.UpdateWireIns()
		dev.SetWireInValue(0x06, 0)
		dev.UpdateWireIns()
		N = len(data_byte) // 2 #FIX py3
		data_bi, data = [], []
		for j in range(N):
			data_bi.append(byte_to_bi(data_byte[2*j+1]) + byte_to_bi(data_byte[2*j]))
			data.append(bi_to_data(data_bi[j]))
	
	print("Total counts:", np.sum(data), '\n')
	if len(data) == 0:
		return -1
	
	return data, clockcount

# Subroutine 3: Graph data array (counts vs time) for one period of laser being turned on
# def Plot(binsize, data): 
#   # In: Converted data from the FPGA in the form of counts per time bin, size of time bins
#   # Out: Graph of the data array; counts per time bin vs. time (relative to start) of the time bin's finish
	
#   times = [binsize * (j + 1) for j in range(len(data))]
#   #plt.close()
#   plt.plot(times, data, 'D')
#   plt.xlabel('Time (in milliseconds)')
#   plt.ylabel('Number of single-photon detections')
#   #plt.ion()
#   plt.show()
#   #time.sleep(1)

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
			

class FPGAServer(Server):

	def cmd_queue(self):
		if self.seq is None:
			logger.error('QUEUE failed. Sequence has not been imported!')
			#self.send_msg(self.ReplyHeader() + 'QUEUE failed. Sequence has not been imported!')
		else:
			try:
				#Config_FPGA()
				acquire_data, save_data = RunServer(self.seq, 0)
				logger.debug('Sequence has been queued... Trigger it whenever!')
				self.send_msg(self.ReplyHeader() + 'Sequence has been queued... Trigger it whenever!')
				logger.debug(f'Acquire: {acquire_data}, Save: {save_data}')
				if acquire_data == 1:
					data = Acquire()
					if data == -1:
						#server.sock.close() # If the FPGA returns nothing, then kill the server
						logger.error("FPGA returned nothing")
					if save_data == 1:
						#SaveData(server.seq.foldername, server.seq.runname, data[0])
						SaveDataWithCLK(self.seq.foldername, self.seq.runname, data)
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
	Config_FPGA()
	server = FPGAServer("SOut1", 60621, message=message)
	server.main_loop()