import mmap
import struct
import os
import time
import sys
import numpy as np
from pathlib import Path

# maximum number of channels (8 or 16?)
CHANNEL_NUM = 16

class RpDOG:
	"""The RpDOG class offers a simple and general API for interfacing with the Simonlab 
	Red-Pitaya-based DAC system. The key methods are queue_sequence() and trigger(),
	which do what their names suggest. This script is for Python 3, and runs directly on the 
	Red Pitaya. It is designed to act as an intermediary between a server running on the Red 
	Pitaya and the FPGA itself. 
	"""

	def __init__(self, bitfile="", fclk_Hz=125e6, max_events=64, invert_vals=False):
		
		# Save arguments, define constants
		self.MAX_EVENTS = max_events
		self.FCLK_HZ = fclk_Hz
		self.bitfile = bitfile
		# future proofing in case we need a line driver
		self.INVERT_VALS = invert_vals
		
		# Load the bitfile
		if self.bitfile.exists():
			os.system("cat {} > /dev/xdevcfg".format(self.bitfile))
		else:
			print("Couldn't load bitfile, exiting...", e)
			sys.exit()

		# ADDRESSES IN THE MEMORY MAPPED ADDRESS SPACE
		self.RP_BASEADDRESS = 0x40000000
		self.RP_FPGARAMSIZE = 0x00800000

		self.LEDADDRESS = 0x40000030    #address in FPGA memory map to control RP LEDS

		self.N_SAMPLES_OFFSET          = 1076887552+4*2          #number of samples
		self.AWAIT_TRIGGER_OFFSET      = 1076887552+4*24         #offset in WORDS (4 bytes) to address where we write ANYTHING to tell system to reset and await trigger
		self.SOFTWARE_TRIGGER_OFFSET   = 1076887552+4*25         #offset in WORDS (4 bytes) to address where we write ANYTHING to give the system a software trigger!
		self.SAMPLES_OFFSET            = 1076887552+4*30         #offset in WORDS (4 bytes) to the zeroeth sample

		# Open the memory-mapped space where the CPU interfaces with the FPGA
		fd = os.open('/dev/mem', os.O_RDWR)
		self.m = mmap.mmap(fileno=fd, length=self.RP_FPGARAMSIZE, offset=self.RP_BASEADDRESS)


	def write(self, addr, val):
		"""Write a 4 byte unsigned int to address addr"""
		aa = addr - self.RP_BASEADDRESS 
		dd = bytes(struct.pack('<I',val))
		self.m[aa:aa+4] = dd[0:4]

	
	def trigger(self):
		"""Trigger the DOG"""
		self.write(self.SOFTWARE_TRIGGER_OFFSET, 0)  # value sent doesn't matter
		print("Software triggered!")


	def queue_sequence(self, seq):
		"""Main method for writing sequences to the FPGA. Takes a seq with format
			[samp0, samp1,...,sampN]
		Each sample should be an integer, where the i-th bit of the j-th sample 
		corresponds to the value of the i-th channel on the j-th clock cycle.
		"""

		# tell the FPGA how many samples are in the sequence
		self.write(self.N_SAMPLES_OFFSET, len(seq))

		# write each sample into memory
		for i in range(len(seq)):
			self.write(self.SAMPLES_OFFSET + i*4, seq[i])

		# prepare it for triggering and running
		self.write(self.AWAIT_TRIGGER_OFFSET, 0)  # value sent doesn't matter


if __name__ == '__main__':

	# Main method is just a test of the hardware. It outputs a clock on each channel with different frequencies.
	minsamps = 4
	seq = [int(i/minsamps) for i in range(int(2**16))]

	bitfile = Path("/root/red_pitaya_dog.bit")
	rp = RpDOG(bitfile=bitfile)
	rp.queue_sequence(seq)
	rp.trigger()
