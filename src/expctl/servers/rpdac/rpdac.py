import mmap
import struct
import os
import time
import sys
from math import sin, pi, exp, cos
from pathlib import Path


class RpDAC:
	"""The RpDAC class offers a simple and general API for interfacing with the Simonlab 
	Red-Pitaya-based DAC system. The key methods are queue_sequence() and trigger(),
	which do what their names suggest. This script is for Python 3, and runs directly on the 
	Red Pitaya. It is designed to act as an intermediary between a server running on the Red 
	Pitaya and the FPGA itself. 
	"""

	def __init__(self, bitfile="", num_channels=16, fclk_Hz=125e6, max_events=64*16, vmin_volts=-10., vmax_volts=10.):
		
		# Save arguments, define constants
		self.bitfile = bitfile
		self.MAX_EVENTS = max_events
		self.FCLK_HZ = fclk_Hz
		self.NUM_CHANNELS = num_channels

		# These constants are used to convert voltages into hardware values
		vmin_mmap = 0 
		vmax_mmap = 2.0**32 - 1
		vmin_volts = -10.
		vmax_volts = 10.
		self.VSCALE = (vmax_mmap - vmin_mmap) / (vmax_volts - vmin_volts)
		self.VOFFSET = vmin_mmap - self.VSCALE * vmin_volts

		# Load the bitfile
		if self.bitfile.exists():
			os.system("cat {} > /dev/xdevcfg".format(self.bitfile))
		else:
			print("Couldn't load bitfile, exiting...", e)
			sys.exit()

		# Addresses in the memory-mapped space
		self.RP_BASEADDRESS = 0x40000000
		self.RP_FPGARAMSIZE = 0x00800000

		self.LED_OFFSET = 0x40000030    # address in FPGA memory map to control RP LEDS

		self.CHANNEL_OFFSET          = 1076887552+4*0    # offset in WORDS (4 bytes) to the channel that we are currently writing to!
		self.AWAIT_TRIGGER_OFFSET    = 1076887552+4*24   # offset in WORDS (4 bytes) to address where we write ANYTHING to tell system to reset and await trigger
		self.SOFTWARE_TRIGGER_OFFSET = 1076887552+4*25   # offset in WORDS (4 bytes) to address where we write ANYTHING to give the system a software trigger!
		self.V_IF_OFFSET             = 1076887552+4*1    # offset in WORDS (4 bytes) to the initial/final FTW for the current channel
		self.legacy_IF_OFFSET        = 1076887552+4*3    # offset in WORDS (4 bytes) to the initial/final amp for the current channel
		self.SAMPLES_OFFSET          = 1076887552+4*2    # offset in WORDS (4 bytes) to # of samples for the current channel

		self.VOLTS_OFFSET            = 1076887552+4*40   # offset in WORDS to the first element of the current freq list
		self.CYCLES_OFFSET           = self.VOLTS_OFFSET  + 4*self.MAX_EVENTS*2  # offset in WORDS to the first element of the current cyc. list
		self.legacy_OFFSET           = self.CYCLES_OFFSET + 4*self.MAX_EVENTS*1  # offset in WORDS to the first element of the current cyc. list

		# Open the memory-mapped space where the CPU interfaces with the FPGA
		fd = os.open('/dev/mem', os.O_RDWR)
		self.m = mmap.mmap(fileno=fd, length=self.RP_FPGARAMSIZE, offset=self.RP_BASEADDRESS)


	def convert_2c(self, val, bits): 
		"""Take a signed integer and return it in 2c form"""
		val = int(val)
		if (val>=0):
			return val
		return ((1 << bits)+val)


	def write(self, addr, val):
		"""Write a 4 byte unsigned int to address addr"""
		aa = addr - self.RP_BASEADDRESS 
		dd = bytes(struct.pack('<I',val))
		self.m[aa:aa+4] = dd[0:4]


	def write_2cLong(self, addr, val): 
		"""Write a float that needs to be send in 2c form"""
		val2c = self.convert_2c(int(val), 64)
		val2cH = val2c >> 32
		val2cL = val & (0xffffffff)
		self.write(addr, val2cL)
		self.write(addr+4, val2cH)


	def VtoInt(self, v_volts): 
		"""Take a voltage in volts and convert it to an RP appropriate int."""
		return self.VSCALE * v_volts + self.VOFFSET


	def SecToCycles(self, t_sec): 
		"""Take a time in seconds and convert it to RP timesteps in cycles, without rounding, so we can do it later when we compute deltas!"""
		return t_sec * self.FCLK_HZ


	def trigger(self):
		"""Trigger the DAC"""
		self.write(self.SOFTWARE_TRIGGER_OFFSET, 0)  # value sent doesn't matter
		print("Software triggered!")


	def queue_sequence(self, seq):
		"""Main method for writing sequences to the FPGA. Takes a seq with format
			[[chan, vIF, [t0, t1,...], [v0, v1,...]],...]
		Times should be in seconds and voltages should be in volts. vIF is the 
		stead-state (initial and final state) voltage, also in volts.
		"""

		self.write(self.LED_OFFSET, 0)  # for some reason the DAC works better with LED turned off!

		# Must write SOMETHING to all channels even if unused, which necessitates iterating like this
		for chan in range(self.NUM_CHANNELS):
			# Find the right channel data
			dat = None
			for c in seq:
				if c[0] == chan:
					dat = c
			# If no data for chan, use filler
			if dat is None:
				dat = [chan, 0.0, [0.0001], [0.0]]

			# Convert the voltages
			vIF = self.VtoInt(dat[1])
			vs = list(map(self.VtoInt, dat[3]))  # vs in RP memory scale

			# Compute the change in voltage between given values
			dvs = [(vs[i+1] - vs[i]) for i in range(len(vs)-1)]
			dvs.insert(0, vs[0] - vIF)

			# Convert times to cycles
			ts = list(map(self.SecToCycles, dat[2]))  # ts in units of cycles

			# We use two cycles min, as the RAM might not be fast enough otherwise :(
			dts = [max(2, int(round(ts[i+1] - ts[i]))) for i in range(len(vs) - 1)] 
			dts.insert(0, max(2, int(round(ts[0]))))

			# Compute the change in voltage per cycle 
			dvdts = [int(round((2.0**32) * dvs[i] / dts[i])) for i in range(len(dts))]

			# Start programming the FPGA for this run.
			# The data MUST be written in this order and with this exact data format!

			# Tell the FPGA which channel we are programming and how many samples it gets
			self.write(self.CHANNEL_OFFSET, int(chan))
			self.write(self.SAMPLES_OFFSET, int(len(ts)))

			# Program this channel
			for i in range(len(dts)):
				
				self.write_2cLong(
					self.VOLTS_OFFSET + 8*i, dvdts[i])
				self.write_2cLong(self.legacy_OFFSET + 8*i, 0)  # this is leftover from an earlier version of the system
				self.write(self.CYCLES_OFFSET + 4*i, dts[i])

			# Send the I/F values of the channel
			self.write(self.V_IF_OFFSET, int(vIF))
			self.write(self.legacy_IF_OFFSET, 0)  # another leftover
		
		# After preparing all the channels, await a trigger
		self.write(self.AWAIT_TRIGGER_OFFSET, 0)  # value sent doesn't matter


if __name__ == "__main__":

	# Main method is just a test of the system. It outputs Gaussian-enveloped sinusoids on each channel, with 
	# different frequencies on each channel.

	vrng=5 

	npts=30
	ncyc=3
	Tmax=0.01
	dt=Tmax/npts
	w=Tmax

	seq = [
		[
			k, 
			0,
			[jj*dt for jj in range(ncyc*npts)],
			[vrng * exp(-(jj-npts*ncyc/2)**2*dt**2/w**2) * sin(3.0*(k+1)*pi*jj/npts) for jj in range(ncyc*npts)]
		] 
		for k in range(16)]

	bitfile = Path("/root/red_pitaya_top.bit")
	rp = RpDAC(bitfile=bitfile)
	rp.queue_sequence(seq)
	rp.trigger()
