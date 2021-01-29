import mmap
import struct
import os
import time
import sys
import numpy as np
from pathlib import Path

# maximum number of channels (8 or 16?)
CHANNEL_NUM = 8

class RpDOG:

    def __init__(self, bitfile="", fclk_Hz=125e6, maxevents=64, invertvals=False):
		self.MAX_EVENTS = maxevents
		self.FCLK_HZ = fclk_Hz
		# future proofing in case we need a line driver
		self.INVERT_VALS = invertvals

		self.bitfile = bitfile
		if self.bitfile.exists():
			os.system("cat {} > /dev/xdevcfg".format(self.bitfile))
		else:
			print("Couldn't load bitfile, exiting...", e)
			sys.exit()
		
        # ADDRESSES IN THE MEMORY MAPPED ADDRESS SPACE
		self.RP_BASEADDRESS = 0x40000000
		self.RP_FPGARAMSIZE = 0x00800000

		self.LEDADDRESS = 0x40000030    #address in FPGA memory map to control RP LEDS

        # INSERT MORE ADDRESSES HERE ONCE BIT FILE IS DEFINED 

        fd = os.open('/dev/mem', os.O_RDWR)
		self.m = mmap.mmap(fileno=fd, length=self.RP_FPGARAMSIZE, offset=self.RP_BASEADDRESS)

    @staticmethod
	def convert_2c(val, bits): 
        """ Takes an int 'val' and returns its 'bits'-bit two's complement representation. """
		if (val>=0):
			return val
		return ((1 << bits)+val)

	@staticmethod
	def twoc32(val):
        """ Convert 'val' to 32-bit two's complement representation. """
		numbits=32
		return RpDOG.convert_2c(val,numbits)

	@staticmethod
	def replacebit(value, newval, position):
		""" Replaces the bit at 'position' in 'value' with 'newval' """
		temp = value & ~(1 << position)  # zero out the bit at position in value
		return temp | (newval << position)

    def write(self, addr, val):
        """ Write an int 'val to memory address 'addr'. """
		aa = addr - self.RP_BASEADDRESS  # do we have to subtract RP_BASEADDRESS?!
		self.m[aa:aa+4] = struct.pack('<I', val)  # format val as an unsigned, little-endian int

    def write_long(self, addr, val): 
        """ Write long 'val' to memory address 'addr'. """
		val2c = RpDDS.convert_2c(val,64)
		val2cH = val2c >> 32
		val2cL = val & (0xffffffff)
		self.write(addr, val2cL)
		self.write(addr + 4, val2cH)

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
		

	def data_for_plot(seq):
		""" Takes a sequence and prepares it for plot. """
		
		# Convert to a list of [timestamp, sample] pairs, where both are ints
		rpseq = self.parse_data(seq)  

		# Un-invert the values if need be:
			if self.INVERT_VALS:
				rpseq = [[e[0], ~e[1]] for e in rpseq]

		# Convert int timestamps to float time lists
		timeList = np.array([float(e[0] / self.FCLK_HZ) for e in rpseq])

		# Convert int samples to array of binary values
		chanData = np.zeros((len(rpseq), CHANNEL_NUM)
		for ii in range(len(rpseq)):
			chanData[ii] = [1 if d=='1' else 0 for d in format(rpseq[ii][1], '0'+CHANNEL_NUM+'b')]
		
		# Do I need to transpose chanData?
		return timeList, chanData
		

	def run_server(server, seq, autostart=1):
		""" Configures and runs a sequence once received. """
		
		TIME_START = time.time()
		seq_duration = float(seq.TIME_STOP) # microseconds
		timeout = 10.0 # (seconds) will this be relevant?
		samps_per_channel = int(math.ceil(seq_duration * self.FCLK_HZ) + 1)
		
		seq_data = self.parse_data(seq, samps_per_channel)
		
		# THIS IS WHERE THE SEQUENCE WRITING AND RUNNING WILL GO
		
		TIME_STOP = time.time()

		return TIME_STOP - TIME_START


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