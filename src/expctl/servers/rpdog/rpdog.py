import mmap
import struct
import os
import time
import sys
import numpy as np
from pathlib import Path
import math

class RpDOG:

	def __init__(self, bitfile="", fclk_Hz=125e6, SWTrigger=False):
		self.bitfile = bitfile

		if self.bitfile.exists():
			os.system("cat {} > /dev/xdevcfg".format(self.bitfile))
			print("Successfully written bitfile.")
		else:
			print("Couldn't load bitfile, exiting...", e)
			sys.exit()

		self.DOGMAXSAMPLES = 65536*2
		self.maxsendlen=31*512  #most FIR coefficients we can send at a time
		self.fclk_Hz = 125*(10**6) #redpitaya clock frequency
		self.SWTrigger = SWTrigger

		#ADDRESSES IN THE MEMORY MAPPED ADDRESS SPACE
		self.RP_BASEADDRESS = 0x40000000
		self.RP_FPGARAMSIZE = 0x00800000

		self.LEDADDRESS              = 0x40000030    #address in FPGA memory map to control RP LEDS
		#DOG addresses (for writing)
		self.DOGnsamples_OFFSET          = 1076887552+4*2                  #number of samples
		self.DOGawaittrigger_OFFSET      = 1076887552+4*24                 #offset in WORDS (4 bytes) to address where we write ANYTHING to tell system to reset and await trigger
		self.DOGsoftwaretrigger_OFFSET   = 1076887552+4*25                 #offset in WORDS (4 bytes) to address where we write ANYTHING to give the system a software trigger!
		self.DOGsamples_OFFSET            = 1076887552+4*30                #offset in WORDS (4 bytes) to the zeroeth sample

		fd = os.open('/dev/mem', os.O_RDWR)
		self.m = mmap.mmap(fileno=fd, length=self.RP_FPGARAMSIZE, offset=self.RP_BASEADDRESS)

	@staticmethod
	def convert_2c(val, bits): #take a signed integer and return it in 2c form
		if (val>=0):
			return val
		return ((1 << bits)+val)

	@staticmethod
	def twoc32(val):
		numbits=32
		return RpDDS.convert_2c(val,numbits)

	def write(self, addr, val):
		aa = addr - self.RP_BASEADDRESS #since the offset of the mmap starts at RP_BASEADDRESS already, have to subtract it here?!
		#print("Writing at real addr {:X}, mmap addr {:X}".format(addr, aa))
		self.m[aa:aa+4] = struct.pack('<I',val)

	def write2c(self, addr, val):
		#m[msg[1]+4*kk:msg[1]+4*kk+4]=msg[2][4*kk:4*kk+4]
		self.m[addr:addr+4] = RpDDS.twoc32(val)

	def write_long(self, addr, val): #addr is the address low word. addr+4*4 is where the high word goes! val is a float, that should be sent in 2c form!
		val2c = RpDDS.convert_2c(val,64)
		val2cH = val2c>>32
		val2cL = val&(0xffffffff)
		self.write(addr,val2cL)
		self.write(addr+4,val2cH)

	def write_long_u(self, addr, val): #addr is the address low word. addr+4*4 is where the high word goes! val is a unsigned
		val2c = val
		val2cH = val2c>>32
		val2cL = val&(0xffffffff)
		self.write(addr,val2cL)
		self.write(addr+4,val2cH)

	def SecToCycles(self, t_sec): #take a time in seconds and convert it to RP timesteps in cycles, without rounding, so we can do it later when we compute deltas!
		return t_sec*self.fclk_Hz

	def trigger(self):
		self.write(self.DOGsoftwaretrigger_OFFSET, 0)
		print("Software triggered!")

	def sendsequence(self, seq):
		assert len(seq) <= self.DOGMAXSAMPLES, "TOO MANY SAMPLES FOR FPGA!" + str(self.DOGMAXSAMPLES)

		#send the number of samples
		self.write(self.DOGnsamples_OFFSET, np.uint32(len(seq))) # these must be sent as unsigned 32 bit numbers

		#send step sizes for each ramp!
		for i in range(len(seq)): 
			self.write(self.DOGsamples_OFFSET+4*i, np.uint32(seq[i]) ) # these must be sent as unsigned 32 bit numbers
	
		#reset the RP FSM and prepare it for a trigger!
		self.write(self.DOGawaittrigger_OFFSET, 0) #value sent doesn't affect anything

		#for now, give it a software trigger, for testing!
		if self.SWTrigger:
			self.trigger()

def funseq(digits):
    return [math.floor(math.log(j+1))%2 for j in range(digits)]

def funseq2(digits):
    return [math.floor(math.sqrt(j)*2)%512 for j in range(digits)]

if __name__ == "__main__":
	#numevents=12000
	#CHs_DATA = funseq2(numevents)
	N = 9000
	seq = np.zeros(N, dtype=np.uint8)
	seq[:] = np.arange(N)
	CHs_DATA = seq.view(np.uint32)
	DOG = RpDOG(bitfile=Path("SimonLab_DOG.bit"), fclk_Hz=125e6, SWTrigger=True)
	DOG.sendsequence(CHs_DATA)
	print("done")