import sys
import math
import time
import numpy as np
from ..ServerClass import Server, logger
from pathlib import Path
from ..util.SequenceProcessor import *
from .rpdog import *
import time


def parse_data(self, seq):
	"""Parses data from the standard sequence format into the format it needs to 
	have when it's written to the red pitaya's RAM, i.e. a list of 
	[sample_number, sample] pairs, where sample is a binary representation of 
	the values on the different channels."""

	allStartTimes = [] # will contain tuples (startTime, chanid, value, endTime)
	steady_state = 0 # should this be 2^CHANNEL_NUM - 1?

	# Load all the events from all the channels into a single list
	for chan in seq.allChannels:
		if chan == None:
			continue
		# Go through all the values from a single channel and put them in the list
		chanValues = chan.GetHardwareValues()
		for interval in chanValues:
			if len(interval) == 4: # Regular interval
				newval == int(interval[1] and interval[3])
				allStartTimes.append((interval[0], chan.chanid, newval, interval[2]))
			elif len(interval) == 7: # Modulation stamps
				stamps = interval[4]
				stamp_length = interval[5]
				mod_num = int(interval[6])
				for ii in range(mod_num):
					for stamp in stamps:
						newval = int(stamp[1] and stamp[3])
						allStartTimes.append((
							interval[0] + stamp[0] + ii*stamp_length, 
							chan.chanid, 
							newval,
							interval[0] + stamp[2] + ii*stamp_length))
		# Record the steady state value for that channel
		steady_state = RpDOG.replacebit(steady_state, chan.GetHardwareSSV(), chan.chanid)

	# Make sure elements are in order
	allStartTimes = sorted(allStartTimes, key=lambda x: (x[0], x[3]))

	# Convert to RP-readable format. We need a list of (sample_num, sample) pairs
	rpseq = [[0, steady_state]]  # the list we will populate
	curr = steady_state  # dummy variable to track the current output state
	for evt in allStartTimes:
		curr = RpDOG.replacebit(curr, evt[2], evt[1])
		rpseq.append([int(evt[0] * self.FCLK_HZ), curr])
	rpseq.append([int(seq.TIME_STOP * self.FCLK_HZ), steady_state])  # add the final state

	# This is where we would invert the values for the line driver if necessary:
	if self.INVERT_VALS:
		rpseq = [[e[0], ~e[1]] for e in rpseq]

	# What data types will the RPDOG bit file take? We will have to cast both the start times and 
	# the values to the appropriate data type, and I might also possibly need to fix the multiplier
	# on the time values, depending on how it gets passed in.

	return rpseq

class RPDigitalServer(Server):

	def __init__(self, name, port, message):
		super().__init__(name, port, message)
		self.task_id = 0
		self.rp = RpDOG(bitfile="", fclk_Hz=125e6, maxevents=64, invertvals=False)

	def queue(self):
		return self.rp.run_server(self.seq, autostart=0)

	def run(self):
		return self.rp.run_server(self.seq, autostart=1)

	def plotdata(self):
		return self.rp.data_for_plot(self.seq)

		

if __name__ == '__main__':
	message = """
	===============================================
	==      Digital Output Generator Server      ==
	==                 for Red Pitaya            ==
	===============================================
	"""

	server = RPDigitalServer("DOut1", 50001, message=message)
	server.main_loop()