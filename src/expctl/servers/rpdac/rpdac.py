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
	which do what their names suggest. 
	"""

	### Should we be accepting maxevents as argument??
	def __init__(self, bitfile="", fclk_Hz=125e6, maxevents=64*16):
		
		# Save arguments
		self.bitfile = bitfile
		self.maxevents = maxevents
		self.fclk_Hz = fclk_Hz

		# Load the bitfile
		if self.bitfile.exists():
			os.system("cat {} > /dev/xdevcfg".format(self.bitfile))
		else:
			print("Couldn't load bitfile, exiting...", e)
			sys.exit()

		# Constants
		self.NUM_CHANNELS = 16
		self.VMIN_MMAP = 0
		self.VMAX_MMAP = (2**11)*(2**16-4500)  #as Jon says, not clear why this is the right value
		self.VMIN_VOLTS = -15
		self.VMAX_VOLTS = 15

		# Addresses in the memory-mapped space
		### Names have not been adapted from the DDS context yet

		self.RP_BASEADDRESS = 0x40000000
		self.RP_FPGARAMSIZE = 0x00800000

		self.LEDADDRESS = 0x40000030    #address in FPGA memory map to control RP LEDS

		self.DDS_CHANNEL_OFFSET          = 1076887552+4*0                  #offset in WORDS (4 bytes) to the channel that we are currently writing to!
		self.DDSawaittrigger_OFFSET      = 1076887552+4*24                 #offset in WORDS (4 bytes) to address where we write ANYTHING to tell system to reset and await trigger
		self.DDSsoftwaretrigger_OFFSET   = 1076887552+4*25                 #offset in WORDS (4 bytes) to address where we write ANYTHING to give the system a software trigger!
		self.DDSftw_IF_OFFSET            = 1076887552+4*1                  #offset in WORDS (4 bytes) to the initial/final FTW for the current channel
		self.DDSamp_IF_OFFSET            = 1076887552+4*3                  #offset in WORDS (4 bytes) to the initial/final amp for the current channel
		self.DDSsamples_OFFSET           = 1076887552+4*2                  #offset in WORDS (4 bytes) to # of samples for the current channel

		self.DDSfreqs_OFFSET            = 1076887552+4*40                      #offset in WORDS to the first element of the current freq list
		self.DDScycles_OFFSET           = self.DDSfreqs_OFFSET  + 4*self.maxevents*2     #offset in WORDS to the first element of the current cyc. list
		self.DDSamps_OFFSET             = self.DDScycles_OFFSET + 4*self.maxevents*1     #offset in WORDS to the first element of the current cyc. list
		self.DDSamps_last_OFFSET        = self.DDScycles_OFFSET + 4*self.maxevents*2 - 1 #offset in WORDS to the last  element of the current cyc. list

		self.maxsendlen = 31*512  # most FIR coefficients we can send at a time
		self.DDSamp_fracbits = 14  # number of DDS bits to the right of the decimal point (all of them, of course!)
		self.DDSchannels = 16  # number of DDS freqs we can simultaneously output!

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
		aa = addr - self.RP_BASEADDRESS #since the offset of the mmap starts at RP_BASEADDRESS already, have to subtract it here?!
		self.m[aa:aa+4] = struct.pack('<I',val)


	def write_2cLong(self, addr, val): 
		"""Write a float that needs to be send in 2c form"""
		#addr is the address low word. addr+4*4 is where the high word goes! val is a float, that should be sent in 2c form!
		val2c = self.convert_2c(val,64)
		val2cH = val2c>>32
		val2cL = val&(0xffffffff)
		self.write(addr, val2cL)
		self.write(addr+4, val2cH)


	### This needs to be replaced! See below!!
	def HzToFTW(self, freq_hz): 
		"""Take a frequency in Hz, and convert it to a RP FTW FLOAT, to minimize rounding error down the line! NO BITSHIFTS FOR NOW!"""
		return freq_hz*(2.0**32)/self.fclk_Hz


	### Is fclk_Hz actually the right multiplier here? The DAC goes much slower than the DDS!!!
	def SecToCycles(self, t_sec): 
		"""Take a time in seconds and convert it to RP timesteps in cycles, without rounding, so we can do it later when we compute deltas!"""
		return t_sec*self.fclk_Hz


	def trigger(self):
		"""Trigger the DAC"""
		self.write(self.DDSsoftwaretrigger_OFFSET, 0)  # value sent doesn't matter
		print("Software triggered!")


	def queue_sequence(self, seq):
		"""Main method for writing sequences to the FPGA. Takes a seq with format
			[[chan, vIF, [t0, t1,...], [v0, v1,...]],...]
		Times should be in seconds and voltages should be in volts."""

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
			### THIS IS PROBABLY THE SOURCE OF THE WEIRD SCALING. ONCE I CONFIRM IT WORKS, FIX THIS
			vIF = HzToFTW(dat[1])
			vs = list(map(HzToFTW, dat[3]))  # vs in RP memory scale

			# Compute the change in voltage between given values
			dvs = [(vs[i+1] - vs[i]) for i in range(len(vs)-1)]
			dvs.insert(0, vs[0] - vIF)

			# Convert times to 
			ts = list(map(SecToCycles, dat[2]))  # ts in units of cycles

			# We use two cycles min, as the RAM might not be fast enough otherwise :(
			dts = [max(2, int(round(ts[i+1] - ts[i]))) for i in range(len(vs) - 1)] 
			dts.insert(0, max(1, int(round(ts[0]))))

			# Compute the change in voltage per cycle 
			dvdts = [int(round((2.0**32) * dv[i] / dts[i])) for i in range(len(dts))]

			# Start programming the FPGA for this run.
			# The data MUST be written in this order and with this exact data format!

			# Tell the FPGA which channel we are programming and how many samples it gets
			self.write(self.LEDADDRESS, 0)  ### Do we need to do this every time? 
			self.write(self.DDS_CHANNEL_OFFSET, chan)
			self.write(self.DDSsamples_OFFSET, len(vs))

			# Program this channel
			for i in range(dts):
				
				self.write_2cLong(self.DDSfreqs_OFFSET + 8*i, df_FTW[i])
				self.write_2cLong(self.DDSfreqs_OFFSET + 8*i, 0)  # this is leftover from an earlier version of the system
				self.write(self.DDScycles_OFFSET + 4*i, dts[i] )

			# Send the I/F values of the  channel
			### vIF is being scaled differently from dvdt!! factor of 2^32! Is this concerning?
			self.write(self.DDSftw_IF_OFFSET, int(vIF))
			self.write(self.DDSamp_IF_OFFSET, 0)  # another leftover
		
		# After preparing all the channels, await a trigger
		self.write(self.DDSawaittrigger_OFFSET, 0)  # value sent doesn't matter


if __name__ == "__main__":

	vmin=0
	vmax=(2**11)*(2**16-4500)
	vrng=(vmax-vmin)/2
	vavg=(vmax+vmin)/2
	npts=30
	ncyc=3
	Tmax=0.01
	dt=Tmax/npts
	w=Tmax

	seq = [
		[
			k, 
			vavg,
			[jj*dt for jj in range(ncyc*npts)],
			[vavg + 1.0*exp(-(jj-npts*ncyc/2)**2*dt**2/w**2)*vrng*sin(3.0*(k+1)*pi*jj/npts) for jj in range(ncyc*npts)]
		] 
		for k in range(16)]

