# -*- coding: utf-8 -*-
"""
Class to manage a DDS core(Sequencer + DDS) in rfsoc and the main driver for 8 channel DDS.
Don't change this file unless you KNOW what you are doing.
Ash
"""
from pynq import Overlay
import xrfclk
import numpy as np
#from pynq import Xlnk
from pynq import allocate
import xrfdc
DDS_CLK = 409.6 #MHz #This is the clock of the DDS. Each DDS generates 16 samples per this clock.
#pynq needs this number specifically to start the clock.

CAL_DDS_CLK = 409.6 #025 #The actual calibrated clock. Calibrate with an accurate spectrum analyzer .
#Actually I am not sure where the error comes from, The PLLs on ZCU111 board or those on DAC tiles.

SEQUENCER_CLK = CAL_DDS_CLK/2 #This is the clock for sequencer. This clock is hardwired on the FPGA to be DDS_CLK/2
SAMPLE_CLK = CAL_DDS_CLK*16 #This is the clock for the DACs. Again, hardwired to be DDS_CLK*16
#Actually in hardware it goes the other way, The DDS clock is derived from sample clock by /16

def printClocks():
	print(f"DDS Clock is : {DDS_CLK} \nSequencer Clock is : {SEQUENCER_CLK}\nSample Clock is : {SAMPLE_CLK}\n")

def setLastBit(N,x):
	if x:
		return N | 1
	else:
		return N & (~1)
		
def getFTW(freq):
	#freq in MHz from Seq!
	#convert into Hz
	#return np.int64(((1e6*freq)/(10**6*SAMPLE_CLK)*(2**64)))
	return np.int64((freq/(SAMPLE_CLK)*(2**64)))

def getCycles(t):
	#t in us
	return np.int64((SEQUENCER_CLK*t))

def ConvertTupletoCountsandFTWs(tuplein): #converts ramp tuple (T0,f0,T1,f1) in microseconds and Hz to counts and FTWs for FPGA and DDS respectively
	return [getCycles(tuplein[0]),getFTW(tuplein[1]),getCycles(tuplein[2]),getFTW(tuplein[3])]

def ConvertSeqtoCountsandFTWs(seqin): #converts full sequence from microseconds and Hz to counts and FTWs
	seqout=[]
	for i in range(len(seqin)):
	  seqout.append(ConvertTupletoCountsandFTWs(seqin[i]))
	return seqout
		
	
	
class ddsmanager: #class to manage a dds channel.
	
	#Sequencer register addresses
	config_add = 0x10 
	fselect_add = 0x18 #DO NOT TOUCH this register
	debug_add = 0x20 #Read only
	done_add = 0x28 #Read Only
	
	#What is written to the config register to make sequencer do different stuff.
	CASE_RESET = 0 #Reset all counters, but keep last output
	CASE_FREQS = 1 #Write start frequency words for each ramp, last bit is phase reset
	CASE_DFREQS = 2 #Write delta frequency words for each ramp, last bit is trigger config
	CASE_CYCLES = 3 #Write number of SEQUENCER_CLK cycles for each ramp
	CASE_START = 5 #Ready to go based on triggers
	CASE_RESET_DONE = 6 #Reset done register
	CASE_KILL = 10 #Kill all output.
	
	#I am going to use self to reference class variables, so that they are overridable for individual instances
	def __init__(self, streamswitch, ss_add, ddscore, dma):
		self.ss=streamswitch
		self.sequencer=ddscore.sequencer_0
		self.dds=ddscore.DDS_0 #The actual DDS object. I am  exposing this, but use only if you know what you are doing.
		self.ss_add = ss_add
		self.dma = dma
		
		self.sequencer.write(self.fselect_add,0)
		
	def writeData(self,freqs,dfreqs,cycles):
		
		#Configure stream switch to direct data to this channel
		self.ss.write(0x40,0x80000000)
		self.ss.write(0x44,0x80000000)
		self.ss.write(0x48,0x80000000)
		self.ss.write(0x4C,0x80000000)
		self.ss.write(self.ss_add,0)
		self.ss.write(0x0,0x2)
		
		#Write start frequencies for each ramp, last bit is if the corresponding ramp requires a trigger (True/False)
		self.sequencer.write(self.config_add,self.CASE_RESET)
		self.sequencer.write(self.config_add,self.CASE_FREQS)
		self.dma.sendchannel.transfer(freqs)
		self.dma.sendchannel.wait()
		
		#Write delta frequencies for each ramp, last bit is if DDS phase should be reset (True/False)
		self.sequencer.write(self.config_add,self.CASE_RESET)
		self.sequencer.write(self.config_add,self.CASE_DFREQS)
		self.dma.sendchannel.transfer(dfreqs)
		self.dma.sendchannel.wait()
		
		#Write number of clock cycles for each ramp
		self.sequencer.write(self.config_add,self.CASE_RESET)
		self.sequencer.write(self.config_add,self.CASE_CYCLES)
		self.dma.sendchannel.transfer(cycles)
		self.dma.sendchannel.wait()
	
	def start(self):
		self.sequencer.write(self.config_add,self.CASE_START)
		
	def rampsFinished(self):
		return self.sequencer.read(self.done_add)
	
	def resetDoneRegister(self):
		self.sequencer.write(self.config_add,self.CASE_RESET_DONE)
		
	def killOutput(self): 
	#Don't use this. It kills the output whenever the register is updated, and resumes where it
	#left off when started again using start().
		self.sequencer.write(self.config_add,self.CASE_KILL)

class rfdriver: #This is the main driver. You shouldn't need to touch ddsmanager itself.
	#xlnk=Xlnk()
	
	#Trigger manager addresses
	
	tm_select_add = 0x10
	tm_pulselength_add = 0x20
	tm_soft_trigger_add = 0x18
	
	def __init__(self, bitfile_name, start_clks = True):
	
		if(start_clks):
			self.startClocks()
			
		self.overlay = Overlay(bitfile_name, ignore_version=True)
		self.corestrings = ["self.overlay.DDS_core_"+str(i) for i in range(0,8)]
		self.rf = self.overlay.usp_rf_data_converter_0
		scope = locals()
		self.ddscores = [eval(corestring,scope) for corestring in self.corestrings]
		#The following code is for assigning the right DMA and stream switch to the right sequencer core.
		self.dmas = [self.overlay.axi_dma_0,self.overlay.axi_dma_1]
		self.sss = [self.overlay.stream_switch_0,self.overlay.stream_switch_1]
		self.ssadds = [0x40,0x44,0x48,0x4C]
		
		#trigger manager
		self.tm = self.overlay.triggermanager_0
		
		#This is the list of objects that allow control over each DDS channel
		self.ddss = [ddsmanager(self.sss[i//4],self.ssadds[i%4],self.ddscores[i],self.dmas[i//4]) for i in range(0,8)]
		#What is the plural of DDS?!!
		
		self.configureTriggerManager()
		
	def startClocks(self):
		print("Starting RFSOC clocks...\n")
		# xrfclk.set_all_ref_clks(DDS_CLK)
		xrfclk.set_ref_clks(lmk_freq=122.88, lmx_freq=409.6)
		print("Clocks Started\n")
	
	def configureTriggerManager(self, config = 0b1011111111, pulselength = 50000000):
	#MSB of config indicates if to use trigger from PMOD0s (0) or switch/soft trigger. 
	#In the latter case bits 0 to 7 determine which channels are triggered.
	#If using PMODs the inputs at PMOD0s is just passed through. 
	#Pulse length determines the length of trigger when using switch or soft trigger.
	
		self.tm.write(self.tm_select_add, config)
		self.tm.write(self.tm_pulselength_add, pulselength)
	
	
	def writeData(self,channel, seqin, trigger_bits, phase_reset_bits):
		
		N_ramps = len(seqin)
		# freqsbuffer = self.xlnk.cma_array(shape=(N_ramps,), dtype=np.int64)
		# cyclesbuffer = self.xlnk.cma_array(shape=(N_ramps,), dtype=np.int64)
		# dfreqsbuffer = self.xlnk.cma_array(shape=(N_ramps,), dtype=np.int64)
		freqsbuffer = allocate(shape=(N_ramps,), dtype=np.int64)
		cyclesbuffer = allocate(shape=(N_ramps,), dtype=np.int64)
		dfreqsbuffer = allocate(shape=(N_ramps,), dtype=np.int64)
		
		seqout = []
		for i in range(0,N_ramps):
			tstart, fstart, tend, fend = seqin[i]
			freqsbuffer[i] = setLastBit(fstart,phase_reset_bits[i])
			cycles = tend-tstart
			cyclesbuffer[i] = cycles
			if cycles<=1:
				dfreq = np.int64(0)
			else:
				dfreq  = (np.int64)((fend-fstart)/(cycles-1))
			dfreqsbuffer[i] = setLastBit(dfreq,trigger_bits[i])
			seqout.append([fstart,dfreq,cycles])
			
		
		self.ddss[channel].writeData(freqsbuffer,dfreqsbuffer,cyclesbuffer)
		freqsbuffer.close()
		dfreqsbuffer.close()
		cyclesbuffer.close()        
		
		return seqout
		
	def startChannel(self, channel): 
	#This means the DDS is ready to execute based on the data (which includes trigger configuration)
		self.ddss[channel].start()
	
	def reset(self, channel_list, freq): 
	#Clear ramp count and output given freq. That is, write only one ramp with the given initial frequency
	#and a length of 1, with phase reset and trigger bits set to 0. Even a ramp of 1 cycle will output a
	#tone because the sequencer will just keep repeating that ramp. This is only true if phase reset bit is 0.
	#Otherwise, the sequencer will reset the phase at the beginning of the ramp and you get zero.
		
		# freqsbuffer = self.xlnk.cma_array(shape=(1,), dtype=np.int64)
		# cyclesbuffer = self.xlnk.cma_array(shape=(1,), dtype=np.int64)
		# dfreqsbuffer = self.xlnk.cma_array(shape=(1,), dtype=np.int64)
		freqsbuffer = allocate(shape=(1,), dtype=np.int64)
		cyclesbuffer = allocate(shape=(1,), dtype=np.int64)
		dfreqsbuffer = allocate(shape=(1,), dtype=np.int64)
		
		FTW = getFTW(freq)
		freqsbuffer[0]=setLastBit(FTW,0)
		cyclesbuffer[0]=(np.int64)(1)
		dfreqsbuffer[0]=(np.int64)(0)
		
		for i in channel_list:
			self.ddss[i].writeData(freqsbuffer,dfreqsbuffer,cyclesbuffer)
			self.startChannel(i)
		
		freqsbuffer.close()
		dfreqsbuffer.close()
		cyclesbuffer.close()
		
	def resetDoneRegister(self,channel):
		self.ddss[channel].resetDoneRegister()

	def isSequenceDone(self,channel_list):
		isdone = 1
		#check if all channels are done.
		for i in channel_list:
			isdone = isdone and self.ddss[i].rampsFinished()
		
		return isdone
	
	def setNyquistZone(self, channel, zone=1):
		block = self.rf.dac_tiles[channel//4].blocks[channel%4]
		assert zone < 3	
		block.NyquistZone = int(zone)
	
		
		