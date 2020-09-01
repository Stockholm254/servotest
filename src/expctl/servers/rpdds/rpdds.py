import mmap
import struct
import os
import time
import sys
import numpy as np
from pathlib import Path

class RpDDS:

	def __init__(self, bitfile="", fclk_Hz=125e6, maxevents=64, SWTrigger=False):
		self.bitfile = bitfile

		if self.bitfile.exists():
			os.system("cat {} > /dev/xdevcfg".format(self.bitfile))
		else:
			print("Couldn't load bitfile, exiting...", e)
			sys.exit()
		self.maxevents = maxevents
		self.fclk_Hz = fclk_Hz
		self.SWTrigger = SWTrigger

		#ADDRESSES IN THE MEMORY MAPPED ADDRESS SPACE
		self.RP_BASEADDRESS = 0x40000000
		self.RP_FPGARAMSIZE = 0x00800000

		self.LEDADDRESS              = 0x40000030    #address in FPGA memory map to control RP LEDS
		#DDS addresses (for writing)
		self.DDSftw_IF_A_OFFSET      = 1076887552+4*(8)         #address in memory map for the initial/final FTW for the A channel
		self.DDSftw_IF_B_OFFSET      = 1076887552+4*(12)        #address in memory map for the initial/final FTW for the B channel

		self.DDSsamplesA_OFFSET          = 1076887552+4*(16)        #address in memory map for # of A samples
		self.DDSsamplesB_OFFSET          = 1076887552+4*(20)        #address in memory map for # of B samples

		self.DDSawaittrigger_OFFSET      = 1076887552+4*(24)        #address in memory map where we write ANYTHING to tell system to reset and await trigger

		self.DDSsoftwaretrigger_OFFSET   = 1076887552+4*(36)        #address in memory map where we write ANYTHING to give the system a software trigger!

		#EXPECT LOW WORD AT LOWER MEMORY ADDRESS FOR FREQS (FTW) RAMS!
		self.DDSfreqsA_OFFSET            = 1076887552+4*(80)                                #address in memory map for the first element of the A freq list
		self.DDSfreqsB_OFFSET            = self.DDSfreqsA_OFFSET+4*( 4*self.maxevents*2) #address in memory map for the first element of the B freq list
		self.DDScyclesA_OFFSET           = self.DDSfreqsB_OFFSET+4*( 4*self.maxevents*2) #address in memory map for the first element of the A cyc. list
		self.DDScyclesB_OFFSET           = self.DDScyclesA_OFFSET+4*( 4*self.maxevents*1) #address in memory map for the first element of the B cyc. list
		self.DDScyclesBlast_OFFSET       = self.DDScyclesB_OFFSET+4*( 4*self.maxevents*1) #address in memory map for the last  element of the B cyc. list

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

	def HzToFTW(self, freq_hz): #take a frequency in Hz, and convert it to a RP FTW FLOAT, to minimize rounding error down the line! NO BITSHIFTS FOR NOW!
		return freq_hz*(2.0**32)/self.fclk_Hz

	def SecToCycles(self, t_sec): #take a time in seconds and convert it to RP timesteps in cycles, without rounding, so we can do it later when we compute deltas!
		return t_sec*self.fclk_Hz

	def trigger(self):
		self.write(self.DDSsoftwaretrigger_OFFSET, 0)
		print("Software triggered!")

	def sendsequence(self, IFfreqA_hz,IFfreqB_hz, timesA_sec, freqsA_hz, timesB_sec,freqsB_hz): #convert freqs and times to FTW/dFTWs, and cycles, and send to RP!
		assert len(timesA_sec) <= self.maxevents, "TOO MANY EDGES ON CHANNEL A-- EXCEEDS RED PITAYA RAM SPACE OF " + str(maxevents)
		assert len(timesB_sec) <= self.maxevents, "TOO MANY EDGES ON CHANNEL B-- EXCEEDS RED PITAYA RAM SPACE OF " + str(maxevents)

		timesA_sec = np.array(timesA_sec)
		timesB_sec = np.array(timesB_sec)
		freqsA_hz = np.array(freqsA_hz)
		freqsB_hz = np.array(freqsB_hz)

		#compute Freqs in Hz to FTWs
		IF_A_FTW = self.HzToFTW(IFfreqA_hz)
		IF_B_FTW = self.HzToFTW(IFfreqB_hz)
		
		freqsA_FTW = self.HzToFTW(freqsA_hz)
		freqsB_FTW = self.HzToFTW(freqsB_hz)

		#compute freq deltas as FTWs
		deltasA_FTW = np.empty_like(freqsA_FTW)
		deltasB_FTW = np.empty_like(freqsB_FTW)
		deltasA_FTW[1:] = freqsA_FTW[1:] - freqsA_FTW[:-1] #deltasA_FTW=[(freqsA_FTW[i+1]-freqsA_FTW[i]) for i in range(len(timesA_sec)-1)]
		deltasB_FTW[1:] = freqsB_FTW[1:] - freqsB_FTW[:-1] #deltasB_FTW=[(freqsB_FTW[i+1]-freqsB_FTW[i]) for i in range(len(timesB_sec)-1)]
		#prepend the first one!
		deltasA_FTW[0] = freqsA_FTW[0]-IF_A_FTW #deltasA_FTW.insert(0,freqsA_FTW[0]-IF_A_FTW)
		deltasB_FTW[0] = freqsB_FTW[0]-IF_B_FTW #deltasB_FTW.insert(0,freqsB_FTW[0]-IF_B_FTW)

		#compute ramp start/end times in cycles    
		timesA_cyc = self.SecToCycles(timesA_sec) #list(map(SecToCycles,timesA_sec))
		timesB_cyc = self.SecToCycles(timesA_sec) #list(map(SecToCycles,timesB_sec))
		
		#compute ramp times in cycles-- round to integers, and have each ramp be at least one cycle!
		dtA_cyc = np.empty(timesA_cyc.shape, dtype=np.uint32)
		dtB_cyc = np.empty(timesB_cyc.shape, dtype=np.uint32)
		dtA_cyc[1:] = np.maximum(1, np.round(timesA_cyc[1:] - timesA_cyc[:-1])).astype(np.uint32) #[max(1,int(round(timesA_cyc[i+1]-timesA_cyc[i]))) for i in range(len(timesA_sec)-1)]
		dtB_cyc[1:] = np.maximum(1, np.round(timesB_cyc[1:] - timesB_cyc[:-1])).astype(np.uint32) #[max(1,int(round(timesB_cyc[i+1]-timesB_cyc[i]))) for i in range(len(timesB_sec)-1)]
		#prepend the first one!
		dtA_cyc[0] = np.maximum(1, np.round(timesA_cyc[0])) #dtA_cyc.insert(0,max(1,int(round(timesA_cyc[0]))))
		dtB_cyc[0] = np.maximum(1, np.round(timesB_cyc[0])) #dtB_cyc.insert(0,max(1,int(round(timesB_cyc[0]))))

		#compute step sizes for each ramp!
		dfA_FTW = (np.round((2.0**32)*deltasA_FTW/dtA_cyc)).astype(np.int64) #[int(round((2.0**32)*deltasA_FTW[i]/dtA_cyc[i])) for i in range(len(dtA_cyc))]
		dfB_FTW = (np.round((2.0**32)*deltasB_FTW/dtB_cyc)).astype(np.int64) #[int(round((2.0**32)*deltasB_FTW[i]/dtB_cyc[i])) for i in range(len(dtB_cyc))]
		
		#send the number of samples on each channel
		self.write(self.DDSsamplesA_OFFSET, np.uint32(len(timesA_sec))) #JSocket.write_msg(sock,DDSsamplesA_OFFSET,len(timesA_sec))
		self.write(self.DDSsamplesB_OFFSET, np.uint32(len(timesB_sec))) #JSocket.write_msg(sock,DDSsamplesB_OFFSET,len(timesB_sec))

		#send step sizes for each ramp!
		for i in range(len(dtA_cyc)): #data must be sent as dftw, and corresponding cycles, as the latter is when all are written into the memory!
			self.write_long(self.DDSfreqsA_OFFSET+8*i,dfA_FTW[i]) #sendpitaya_long(DDSfreqsA_OFFSET+8*i,dfA_FTW[i]) #these must be sent as 2's complement 64 bit numbers
			self.write(self.DDScyclesA_OFFSET+4*i,dtA_cyc[i]) #JSocket.write_msg(sock,DDScyclesA_OFFSET+4*i,dtA_cyc[i]) #these must be sent as unsigned 32 bit numbers
		for i in range(len(dtB_cyc)):
			self.write_long(self.DDSfreqsB_OFFSET+8*i,dfB_FTW[i]) #these must be sent as 2's complement 64 bit numbers
			self.write(self.DDScyclesB_OFFSET+4*i,dtB_cyc[i]) #these must be sent as unsigned 32 bit numbers

		#send the I/F values of the two channels!
		self.write(self.DDSftw_IF_A_OFFSET, np.uint32(IF_A_FTW)) #JSocket.write_msg(sock,DDSftw_IF_A_OFFSET, int(IF_A_FTW)) #these must be sent as unsigned 32 bit numbers
		self.write(self.DDSftw_IF_B_OFFSET, np.uint32(IF_B_FTW))#JSocket.write_msg(sock,DDSftw_IF_B_OFFSET, int(IF_B_FTW)) #these must be sent as unsigned 32 bit numbers
	
		#print("IF A FTW: {}".format(np.uint32(IF_A_FTW)))
		
		#reset the RP FSM and prepare it for a trigger!
		self.write(self.DDSawaittrigger_OFFSET, 0) #value sent doesn't affect anything

		#for now, give it a software trigger, for testing!
		if self.SWTrigger:
			self.trigger()

	def SendSequenceSimple(self, A_dat, B_dat): #dummy that takes data in the form A_dat=[IF_A_hz,[[t1_A_sec,f1_A_hz],[t2_A_sec_,f2_A_hz]...]], and then the same thing for B_dat
		IFfreqA_hz=A_dat[0]
		timesA_sec=[d[0] for d in A_dat[1]]
		freqsA_hz= [d[1] for d in A_dat[1]]

		IFfreqB_hz=B_dat[0]
		timesB_sec=[d[0] for d in B_dat[1]]
		freqsB_hz= [d[1] for d in B_dat[1]]
		
		self.sendsequence(IFfreqA_hz,IFfreqB_hz, timesA_sec, freqsA_hz, timesB_sec,freqsB_hz)


if __name__ == "__main__":
	CH1_DATA=[40.0e6,[[10.0, 45e6],[20.0, 35e6],[30.0, 40e6]]]
	CH2_DATA= CH1_DATA#[40.0e6,[[1.0, 40e6]]]

	#DDS = RpDDS(bitfile="SimonLab_DDDS.bit", fclk_Hz=125e6, maxevents=64, SWTrigger=True)
	DDS = RpDDS(bitfile="DDDS_xlnx_512.bit", fclk_Hz=125e6, maxevents=512, SWTrigger=True)
	DDS.SendSequenceSimple(CH1_DATA, CH2_DATA)
	print("done")