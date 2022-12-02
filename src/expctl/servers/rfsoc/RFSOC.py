import sys
import math
import time
import numpy as np
from ..ServerClass import Server, logger
from pathlib import Path
from ..util.SequenceProcessor import *
from .rfsocdriver import *

DIR_BITFILE = Path(__file__).parent
bitfile_path = str(DIR_BITFILE/"ddsfinal10k_tm_4.bit")
logger.info(f"Using bitfile {bitfile_path}")

chan_shuffler =  [0,1,2,3,4,5,6,7]#[2,1,0,3,4,5,6,7]
#list index is the sequence channel and corresponding element is the DDS channel.

#These values are defined in rfsocdriver, override here.
CAL_DDS_CLK = 409.6025 #The actual calibrated clock. Calibrate with an accurate spectrum analyzer .
#Actually I am not sure where the error comes from, The PLLs on ZCU111 board or those on DAC tiles.

SEQUENCER_CLK = CAL_DDS_CLK/2 #This is the clock for sequencer. This clock is hardwired on the FPGA to be DDS_CLK/2
SAMPLE_CLK = CAL_DDS_CLK*16 #This is the clock for the DACs. Again, hardwired to be DDS_CLK*16
#Actually in hardware it goes the other way, The DDS clock is derived from sample clock by /16

numDDS = 8
first_trigger = 0
MAX_RAMPS= 10000 
#trigger_config = 0b1011111111 #if MSB-1 is 0, a hardware trigger on the PMODs is required and the other bits don't matter
trigger_config = 0b0011111111
# MSB | MSB-1
#-------------
#  0  |   0     separate HW triggers
#  1  |   0     global HW trigger at PMOD_0_0 (white cable)
#  0  |   1     SW/Switch (central, SW11) trigger, remaining bits select channels to be triggered
#  1  |   1     -"-

active_chans = []
fullSeqs = [] #list of sequences for all channels in original format, with holes filled and frequencies and times converted to FTWs and cycles
NumRamps = []  #Total Number of ramps for each channel

counter = 0
def RunServer(seq, rf, autostart=1, UPDATE_RAM=1):
	TIME_START = time.time()
	global counter, active_chans

	## Convert seq to get all the times and frequencies, and save to buffers to pass to FPGA Block RAM
	rf.configureTriggerManager(config = trigger_config)

	if(UPDATE_RAM):
		fullSeqs = [] 
		NumRamps = []
		active_chans = []

		for chan in seq.allChannels:
			if chan == None:
				continue
			chan.Print()
			chanid = chan.chanid
			if chan.chanid > 7:
				logger.info(f"More channels than {numDDS}, ignoring...\n")
				continue

			active_chans.append(chan_shuffler[chanid])
			ssvalMHz = chan.GetHardwareSSV() #steady_state_value
			logger.debug(f"Steady state value  {ssvalMHz}")
			ssvalFTW = getFTW(ssvalMHz)
			#seq = chan.GetHardwareValues()
			chanValues = chan.GetHardwareValues()
			seq = []
			for interval in chanValues:
				# Note: had to invert logical values because of the line driver
				if len(interval) == 4: # Regular interval
					seq.append(interval)
				elif len(interval) == 7: # Modulation stamps
					stamps = interval[4]
					stamp_length = interval[5]
					mod_num = int(interval[6])
					# for ii in range(mod_num):
					# 	for stamp in stamps:
					# 		seq.append((interval[0]+stamp[0]+stamp_length*ii, stamp[1], interval[0]+stamp[2]+stamp_length*ii, stamp[3]))
					# HACK for now just append the stamp ones and hint that repeated trigger is required!
					# TODO fix stamp beginning and end times to start right after trigger, to check when substamps repeat, check start value and end value
					init_vals = (stamps[0][1], stamps[0][3])
					n=0
					for stamp in stamps:
						if (stamp[1], stamp[3])==init_vals and n>0:
							print("pattern repeated after {} cycles, breaking".format(n))
							break
						seq.append(stamp)
						n+=1
			# HACK
			# seq.pop()
			print(seq)
			print("Interpreting seq took {:.3f} s".format(time.time()-TIME_START))
			convertedSeq = ConvertSeqtoCountsandFTWs(seq) #values)
			fullSeq = GenerateFullSeq(convertedSeq,ssvalFTW)
			print(fullSeq)
			print("Converting seq took {:.3f} s".format(time.time()-TIME_START))
			N_Ramps = len(fullSeq)
			fullSeqs.append(fullSeq)
			NumRamps.append(N_Ramps)

			phase_reset_bits = [0]*N_Ramps
			#Should the phase be reset before starting a given ramp?

			trigger_bits = [first_trigger]+[int (not autostart)]*(N_Ramps > 1)+[0]*(N_Ramps-2)
			#Does a given ramp need to be triggered?

			#ADD RAMPS CHECK

			rf.writeData(chan_shuffler[chanid], fullSeq, trigger_bits, phase_reset_bits)
			print("Writing seq took {:.3f} s".format(time.time()-TIME_START))

	for chan in active_chans: 
		rf.resetDoneRegister(chan)
		rf.startChannel(chan)

	TIME_DATA = time.time() 
	logger.info("Ramp sequence started. I will output based on the trigger bits. \n")

	#creates a deadlock since frontpanel waits for Queue to finish
	#while(True):
	#	if(rf.isSequenceDone(active_chans)):
	#		counter = counter+1
	#		logger.debug(f"Sequence executed {counter} times\n")
	#		break

	TIME_STOP = time.time()
	return TIME_STOP - TIME_DATA

class RfSocServer(Server):

	def __init__(self, name, port, message, bitfile):
		super().__init__(name, port, message)
		self.rf = rfdriver(bitfile, True)
		for channel in active_chans:
			self.rf.setNyquistZone(self, channel, zone=1)
		self.counter = 0

	# def queue(self):
	# 	return RunServer(self.seq, self.rf, autostart=0)
	def cmd_queue(self):
		if self.seq is None:
			logger.error('QUEUE failed. Sequence has not been imported!')
			self.send_msg(self.ReplyHeader() + 'QUEUE failed. Sequence has not been imported!')
		else:
			ret = RunServer(self.seq, self.rf, autostart=0)
			self.send_msg(self.ReplyHeader() + 'Sequence has been queued... Trigger it whenever!')

			# This waits for the RFsoc to finish it's ramp, 
			# was useful for finding right trigger port but slows down sequence since it waits for the whole sequence to have finished
			# This has to be implemented in some kinf POST command
			print(active_chans)
			# t0 = time.time()
			# while(True):
			# 	if(self.rf.isSequenceDone(active_chans)):
			# 		self.counter += 1
			# 		logger.debug(f"Sequence executed {self.counter} times\n")
			# 		break
			# 	if (time.time()-t0 > 1.0):
			# 		logger.debug("Seqeunce timed out! No trigger received")
			# 		break
			

	def run(self):
		return RunServer(self.seq, self.rf)

	def plotdata(self):
		return [0,], [0,]


if __name__ == '__main__':

	message = """
	===============================================
	==      DDS Profile Frequency Out Server     ==
	==                 for RFSOC                 ==
	===============================================
	"""

	server = RfSocServer("RfSoc_1", 60617, message=message, bitfile=bitfile_path)
	server.main_loop()