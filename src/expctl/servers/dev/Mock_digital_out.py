#!/usr/bin/python
import sys
import math
import time
import numpy as np
from ..ServerClass import Server, logger
from ...utilities.util import formatTimeUnits
import ctypes
import zmq

# This server implements a global "trigger" via Zeromq pub/sub to trigger other mock servers
trigger_port = 70111

uInt8   = ctypes.c_ubyte
int16   = ctypes.c_short
uInt16  = ctypes.c_ushort
int32   = ctypes.c_long
uInt32  = ctypes.c_ulong
uInt64  = ctypes.c_ulonglong
float64 = ctypes.c_double
task_handle_type = uInt32

localMHz = 1e6
# seq_duration = float(seq.TIME_STOP) # microseconds
timeout = 10.0 # (seconds)
sample_rate = 10.0  # number of samples per microsecond (clock speed in MHz)
# samps_per_channel = int(math.ceil(sample_rate * seq_duration) + 1) # MHz * us (+1 for steady_state_value)
# buffer_size = samps_per_channel # number of samples
channel_num = 32
		
def ParseData(seq, samps_per_channel):
	#invert logical values because of line driver
	NI_OFF = 1
	NI_ON = 0
	
	allStartTimes = [] # will contain tuples (startTime, chanid, value)
	final_state = 0 # should probably be 2^32-1
	
	for chan in seq.allChannels:
		if chan == None:
			continue
		chanValues = chan.GetHardwareValues()
		for interval in chanValues:
			# Note: had to invert logical values because of the line driver
			if len(interval) == 4: # Regular interval
				if interval[1] == 0 and interval[3] == 0:
					newval = NI_OFF
				else:
					newval = NI_ON
				allStartTimes.append((interval[0], chan.chanid, newval, interval[2]))
			elif len(interval) == 7: # Modulation stamps
				stamps = interval[4]
				stamp_length = interval[5]
				mod_num = int(interval[6])
				for ii in range(mod_num):
					for stamp in stamps:
						if stamp[1] == 0 and stamp[3] == 0:
							newval = NI_OFF
						else:
							newval = NI_ON
						allStartTimes.append((interval[0]+stamp[0]+stamp_length*ii, chan.chanid, newval,interval[0]+stamp[2]+stamp_length*ii))
		# Note: had to invert logical values because of the line driver
		if chan.GetHardwareSSV() == 0:
			final_state = final_state | (1 << chan.chanid)
		else:
			final_state = final_state & ~(1 << chan.chanid)

	allStartTimes = sorted(allStartTimes, key=lambda x: (x[0],x[3])) # make sure they're in order, in case the for loop ran in a weird order
 
	# Convert the data to NI-readable data
	logger.debug("Converting "+ formatTimeUnits(seq.TIME_STOP) +" sequence to NI-readable data.")
	seq_data = np.zeros((samps_per_channel,), dtype=uInt32)
	stop = 0 #this gets overriden immediately
	#the default initial state is being set by the server to be OFF. Perhaps this is bad!?
	state = 2**32 -1 # state = 0 if there's no inverting line drivers
	for ii in range(0, len(allStartTimes)-1):#loop over the intervals, i.e. the "commands" given to all the channels; they are in time order
		if allStartTimes[ii][2] == 1:#value of this interval is 1 (note that the line driver is irrelevant at this point)
			state = state | (1 << allStartTimes[ii][1]) #set state value for the channel to 1
		else:
			state = state & ~(1 << allStartTimes[ii][1]) #set state value for the channel to 0
		if allStartTimes[ii][0] != allStartTimes[ii+1][0]:#non-equal start times, ortherwise nothing would happen anyway
			start = int(allStartTimes[ii][0] * sample_rate) #index of the sample corresponding to the start time, rounded to an integer
			stop = int(allStartTimes[ii+1][0] * sample_rate) #ignore the declared end time because it means nothing. The real end time is the start of the next interval
			seq_data[start:stop] = state #set the binary state during these samples
	#Treat the final state specially.
	#First do the normal stuff as in the above loop,
	#but now you can't look at the next interval to get the stop index, because there is no next interval.
	if allStartTimes[-1][2] == 1:#last value set was 1
		state = state | (1 << allStartTimes[-1][1]) #
	else:
		state = state & ~(1 << allStartTimes[-1][1])#
	seq_data[stop:-1] = state # carry values to end
	#Then set the final state using the steady state values
	#Remember this last sample was added as an extra
	seq_data[-1] = final_state # at end, chan values to steady state values
		
	return seq_data

# Convert the machine readable data to plot data
# !!!!!!!THIS NEED TO BE UPDATED EVERYTIME ParseData FUNCTION IS MODIFIED!!!!!!!
def DataForPlot(seq):
	# This module get the machine readable data from the ParseDate function, and then transform it into integer
	# value for 32 channels. The values are inverted due to the line driver. Only update points are returned 
	# because the plot memory limit. 
	
	seq_duration = float(seq.TIME_STOP) # microseconds
	samps_per_channel = int(math.ceil(sample_rate * seq_duration) + 1) # MHz * us (+1 for steady_state_value)
	
	parsedDatas = ParseData(seq, samps_per_channel) # Get the machine readable data
	parsedDatas = np.invert(parsedDatas) # Bitwise invert to correct the line driver inversion
	
	firstVal = format(parsedDatas[0], '#034b')[2:] # Add first value to the list
	chanData = [np.array(list(firstVal), dtype='int')]
	timeList = [0] # Add first time point to the time list
	ind_update = np.nonzero(np.diff(parsedDatas))[0] # Find the sample where the value is updated. Cannot plot all the data due to the memory limit
	for ind in ind_update:
		binData = format(parsedDatas[ind+1], '#034b')[2:] # Convert state integer to binary form
		chanData.append(np.array(list(binData), dtype='int'))
		timeList.append((ind+1)/sample_rate)
	finalVal = format(parsedDatas[-1], '#034b')[2:] # Add final value to the value list
	chanData.append(np.array(list(finalVal), dtype='int'))
	timeList.append((samps_per_channel-1)/sample_rate) # Add final time point to the time list
	
	timeList = np.array(timeList)
	chanData = np.array(chanData)
	chanData = np.transpose(np.fliplr(chanData)) # Transpose the matrix so that match the sequence format and channel indicies.
	return timeList, chanData
	
def RunServer(seq, autostart = 1):
	TIME_START = time.time()
	seq_data = ParseData(seq, 1000)
	if autostart:
		logger.info("Sent Pub/Sub trigger")
		socket.send("TRIG".encode())
	time.sleep(0.03)
	TIME_STOP = time.time()
	return TIME_STOP-TIME_START

class DigitalServer(Server):

	def queue(self):
		return RunServer(self.seq, autostart=0)

	def run(self):
		return RunServer(self.seq)

	def plotdata(self):
		return DataForPlot(self.seq)

if __name__ == '__main__':
	message = """===========================================
	==       Dummy Digital Output Server     ==
	==              for PCIe 6537            ==
	=========================================== 
	"""

	context = zmq.Context()
	socket = context.socket(zmq.PUB)
	socket.bind("tcp://*:{:d}".format(trigger_port))

	server = DigitalServer("DOut1", 50001, message=message)
	server.main_loop()