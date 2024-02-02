import sys
import math
import time
import numpy as np
from ..ServerClass import Server, logger
from pathlib import Path
from ..util.SequenceProcessor import *
from .rfsocdriver import *

DIR_BITFILE = Path(__file__).parent
bitfile_path = str(DIR_BITFILE/"ddsfinal10k_serrodyne.bit")
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
trigger_config = 0b1011111111 #if MSB-1 is 0, a hardware trigger on the PMODs is required and the other bits don't matter
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
	global counter

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
			
			if chan.chanid > 15:
				logger.info(f"More channels than {numDDS}, ignoring...\n")
				continue

			active_chans.append(chan_shuffler[chanid])
			ssvalHz = chan.GetHardwareSSV() #steady_state_value
			ssvalFTW = getFTW(ssvalHz)
			#seq = chan.GetHardwareValues()
			chanValues = chan.GetHardwareValues()

			

			if chan.chanid > 7 and chan.chanid <= 15:
				logger.info(f"Channel {chan.chanid} sets output mode for output {chan.chanid-numDDS}, ignoring...\n")
				output_id = chan.chanid-numDDS
				assert 0<=output_id<8
				# set output mode
				val = int(chanValues[0][1])
				if 0<=val<4:
					logger.info(f"setting output {output_id} to mode {val}")
					rf.setOutputMode(channel=output_id,mode=val)
				else:
					logger.info(f"Invalid output mode {val}, must be 0, 1, 2 or 3")

				continue


			parsed_chan = []
			for interval in chanValues:
				# Note: had to invert logical values because of the line driver
				if len(interval) == 4: # Regular interval
					parsed_chan.append(interval)
				elif len(interval) == 7: # Modulation stamps
					stamps = interval[4]
					stamp_length = interval[5]
					mod_num = int(interval[6])
					for ii in range(mod_num):
						for stamp in stamps:
							parsed_chan.append((interval[0]+stamp[0]+stamp_length*ii, stamp[1], interval[0]+stamp[2]+stamp_length*ii, stamp[3]))

			#print(seq)
			convertedSeq = ConvertSeqtoCountsandFTWs(parsed_chan) #values)
			fullSeq = GenerateFullSeq(convertedSeq,ssvalFTW)
			#print(fullSeq)
			N_Ramps = len(fullSeq)
			fullSeqs.append(fullSeq)
			NumRamps.append(N_Ramps)

			phase_reset_bits = [0]*N_Ramps
			#Should the phase be reset before starting a given ramp?

			trigger_bits = [first_trigger]+[int (not autostart)]*(N_Ramps > 1)+[0]*(N_Ramps-2)
			#Does a given ramp need to be triggered?

			#ADD RAMPS CHECK

			rf.writeData(chan_shuffler[chanid], fullSeq, trigger_bits, phase_reset_bits)

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


CLOCKTIME = 1
def _compute_next(time, val, last_time, last_val, times, vals):
	"""Appends the corrent time and value to the list, while 
	returning the updated lasttime and lastval.
	"""
	if last_time >= time:
		if last_val != val:
			times.append(last_time + CLOCKTIME)
			vals.append(val)
			return last_time + CLOCKTIME, val
		else:
			return last_time, val
	else:
		times.append(time)
		vals.append(val)
		return time, val


def DataForPlot(seq):

	# derived from RPDACServer.py

	parsed_seq = []

	for chan in seq.allChannels:
		if chan == None:
			continue
		parsed_chan = [chan.chanid, chan.ssv]
		last_time = 0
		last_val = chan.ssv
		times = [last_time]
		vals = [last_val]

		for interval in chan._UserValues:
			# Regular time interval. 
			# Format (start_time, start_value, stop_time, stop_value)
			if len(interval) == 4:
				last_time, last_val = _compute_next(
					interval[0], interval[1], last_time, last_val, times, vals)
				last_time, last_val = _compute_next(
					interval[2], interval[3], last_time, last_val, times, vals)
			# Repeat stamps. 
			# Format: (start_time, start_value, stop_time, stop_value, 
			# stamp, stamp_length, modulation_number)
			elif len(interval) == 7:
				t0 = interval[0]
				stamps = interval[4]
				stamp_length = interval[5]
				mod_num = int(interval[6])
				for ii in range(mod_num):
					for stamp in stamps:
						last_time, last_val = _compute_next(
							stamp[0] + t0 + stamp_length*ii, stamp[1], 
							last_time, last_val, times, vals)
						last_time, last_val = _compute_next(
							stamp[2] + t0 + stamp_length*ii, stamp[3], 
							last_time, last_val, times, vals)
		
		parsed_chan.append(times)
		parsed_chan.append(vals)
		parsed_seq.append(parsed_chan)

	alltimes = set()
	for chan in parsed_seq:
		for t in chan[2]:
			alltimes.add(t)
	alltimes = sorted(alltimes)

	allvals = np.empty([8, len(alltimes)])
	allvals[:] = np.nan
	for chan in parsed_seq:
		id = chan[0]
		times = chan[2]
		vals = chan[3]
		for i, t in enumerate(alltimes):
			if t in times:
				allvals[id, i] = vals[times.index(t)]

	alltimes = np.asarray(alltimes)

	print(alltimes)
	print(allvals)

	return alltimes, allvals



class RfSocServer(Server):

	def __init__(self, name, port, message, bitfile):
		super().__init__(name, port, message)
		self.rf = rfdriver(bitfile, True)

		#Set properties for different channels
		#self.rf.setOutputMode(channel=0,mode=2)


	def queue(self):
		return RunServer(self.seq, self.rf, autostart=0)

	def run(self):
		return RunServer(self.seq, self.rf)

	def plotdata(self):
		return DataForPlot(self.seq)


if __name__ == '__main__':

	message = """
	===============================================
	==      DDS Profile Frequency Out Server     ==
	==                 for RFSOC                 ==
	===============================================
	"""

	server = RfSocServer("RfSoc_1", 60617, message=message, bitfile=bitfile_path)
	server.main_loop()