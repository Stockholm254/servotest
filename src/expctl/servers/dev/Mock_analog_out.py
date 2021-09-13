#!/usr/bin/python
import sys
import math
import time
import numpy as np
from ..ServerClass import Server, logger
from ...utilities.util import formatTimeUnits
import ctypes
import zmq

# This server implements a global "trigger" via Zeromq pub/sub to receive a trigger from digital out
trigger_port = 70111

uInt8   = ctypes.c_ubyte
int16   = ctypes.c_short
uInt16  = ctypes.c_ushort
int32   = ctypes.c_long
uInt32  = ctypes.c_ulong
uInt64  = ctypes.c_ulonglong
float64 = ctypes.c_double
task_handle_type = uInt32

''' For the PCI6723, sample rate depends on the number of channels: It should not exceed 800 kS/s
		 per channel for one channel, or 45 kS/s per channel for 32 channels '''
sample_rate = 4.0/100  # number of samples per microsecond (clock speed in MHz) # use 40kS/s to avoid timing offset (DO NOT USE 45kS/s!!!)

def ParseData(seq, samps_per_channel):
	logger.debug("Converting "+ formatTimeUnits(seq.TIME_STOP) +" sequence to NI-readable data.")
	seq_data = np.zeros((seq.max_channels*samps_per_channel,), dtype=float64)
	
	for chan in seq.allChannels:
		if chan == None:
			continue
		offset = chan.chanid * (samps_per_channel)
		stop = 0
		lastVal = float64(chan.GetHardwareSSV())
		chanValues = chan.GetHardwareValues()
		for interval in chanValues:
			# Regular time interval. Format (start_time, start_value, stop_time, stop_value)
			if len(interval) == 4:
				start = int(interval[0] * sample_rate) # New start time of the interval
				seq_data[offset+stop:offset+start] = lastVal # Define the time between the last stop time and the new start time with the last value
				stop = int(interval[2] * sample_rate) # New stop time of the interval
				if start == stop: # For zero length interval, the value will be set to the end value of the zero interval
					seq_data[offset + start] = interval.end_V()
				else: # For non-zero interval, create a ramp between the start and stop value
					seq_data[offset+start:offset+stop] = np.linspace(interval.start_V(), interval.end_V(), num=stop-start)
				lastVal = float64(interval[3]) # Remember the last previous value.
			# Repeat stamps. Format: (start_time, start_value, stop_time, stop_value, stamp, stamp_length, modulation_number)
			elif len(interval) == 7:
				stamps = interval[4]
				stamp_length = interval[5]
				mod_num = int(interval[6])
				for ii in range(mod_num):
					for stamp in stamps:
						start = int((interval[0]+stamp[0]+stamp_length*ii) * sample_rate)
						seq_data[offset+stop:offset+start] = lastVal
						stop = int((interval[0]+stamp[2]+stamp_length*ii) * sample_rate)
						if start == stop:
							seq_data[offset+start] = stamp[3]
						else:
							seq_data[offset+start:offset+stop] = np.linspace(stamp[1], stamp[3], num=stop-start)
						lastVal = float64(stamp[3])
		seq_data[offset+samps_per_channel-1] = chan.GetHardwareSSV() # set steady state val
		
	return seq_data
	
def DataForPlot(seq):
	# IMPORTANT: EVERY TIME THE DATA PARSING PROCESS IS MODIFIED (NEW CARD OR DRIVER INSTALLED), THIS MODULE 
	#            MUST BE REVISITED IN ORDER TO ENSURE THE PLOTTING IS CORRECT.
	# This module get the machine readable data from the ParseDate function, and then partition it into 32*sample_per_channel
	# array. Due to the plot memory limit, this only return the value only when any channel is updated. 
	
	seq_duration = float(seq.TIME_STOP) # microseconds
	samps_per_channel = int(math.ceil(sample_rate * seq_duration) + 1) # MHz * us (+ 1 for the steady_state_value)

	parsedDatas = ParseData(seq, samps_per_channel) # Get the machine readable data
	parsedDatas = parsedDatas.reshape(16, samps_per_channel) # Partition the data according to channel
	
	ind_diff = np.nonzero(np.diff(parsedDatas, axis=1))[1] # Detect the update point
	ind_diff = np.unique(ind_diff) # We only need to know the time indices when things are updated, this get rid of the redundant ind in the list
	chanData = [parsedDatas[:, 0]] # Add the first value to the list
	timeList = [0] # Add the first time point to the list
	for ind in ind_diff:
		chanData.append(parsedDatas[:, ind+1])
		timeList.append((ind+1)/sample_rate)
	chanData.append(parsedDatas[:, -1]) # Add the final value
	timeList.append((samps_per_channel-1)/sample_rate)
	
	chanData = np.array(chanData)
	chanData = np.transpose(chanData) # Conter the array to [channel, values] form
	
	return timeList, chanData

def RunServer(seq, autostart = 1):
	TIME_START = time.time()
	localMHz = 1e6  
	seq_duration = float(seq.TIME_STOP) # microseconds
	timeout = 10.0 # (seconds)
	''' For the PCI6723, sample rate depends on the number of channels: It should not exceed 800 kS/s
		 per channel for one channel, or 45 kS/s per channel for 32 channels '''
	sample_rate = 4.0/100  # number of samples per microsecond (clock speed in MHz) # use 40kS/s to avoid timing offset (DO NOT USE 45kS/s!!!)
	samps_per_channel = int(math.ceil(sample_rate * seq_duration) + 1) # MHz * us (+ 1 for the steady_state_value)
	logger.debug("samps rate: {}".format(sample_rate*localMHz))
	buffer_size = samps_per_channel # number of samples
	logger.debug("samples per channel: {}".format(samps_per_channel))
	seq_data = ParseData(seq, samps_per_channel)
	#server.task_id += 1
	TIME_STOP = time.time()
	return TIME_STOP-TIME_START

class AnalogServer(Server):

	def cmd_queue(self):
		if self.seq is None:
			logger.error('QUEUE failed. Sequence has not been imported!')
			self.send_msg(self.ReplyHeader() + 'QUEUE failed. Sequence has not been imported!')
		else:
			RunServer(self.seq, autostart=0)
			logger.debug("Sequence has been queued... Trigger it whenever!")
			self.send_msg(self.ReplyHeader() + 'Sequence has been queued... Trigger it whenever!')
			try:
				string = socket.recv()
			except:
				logger.exception("Waiting for trigger timed out!")
			else:
				logger.info("Received tigger: {}".format(string.decode()))
				time.sleep(0.03)
				logger.info("Sequence ran successfully")

	def run(self):
		return RunServer(self.seq)

	def plotdata(self):
		return DataForPlot(self.seq)

if __name__ == '__main__':
	message = """===========================================
	==       Dummy Analog Output Server     ==
	==              for PCI 6723            ==
	=========================================== 
	"""
	# Socket to talk to server
	context = zmq.Context()
	socket = context.socket(zmq.SUB)
	socket.setsockopt(zmq.LINGER,      0 )
	socket.setsockopt(zmq.RCVTIMEO, 10000)

	socket.connect("tcp://localhost:{:d}".format(trigger_port))
	socket.subscribe("") # Subscribe to all topics
	logger.info("Connected to trigger")

	server = AnalogServer("AOut1", 60616, message=message)
	server.main_loop()