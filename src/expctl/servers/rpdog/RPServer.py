import sys
import math
import time
import numpy as np
from ..ServerClass import Server, logger
from pathlib import Path
from ..util.SequenceProcessor import *
from .rpdds import *
import time

DIR_BITFILE = Path(__file__).parent

#A FEW HELPER FUNCTIONS
def ConvertTimeToSeconds(ttime): #time in microseconds, converted to seconds
	return ttime*1e-6

def ConvertTupleToSeconds(tuplein): #converts ramp tuple (T0,f0,T1,f1) in microseconds and Hz to seconds and Hz
	return [ConvertTimeToSeconds(tuplein[0]),tuplein[1],ConvertTimeToSeconds(tuplein[2]),tuplein[3]]

def ConvertSeqToSeconds(seqin): #converts full sequence from microseconds and Hz to seconds and Hz
	seqout=[]
	for i in range(len(seqin)):
		#remove zero length tuples
		if abs(seqin[i][0] - seqin[i][2])>0.0:
			seqout.append(ConvertTupleToSeconds(seqin[i]))
	return seqout

def ConvertSeqToDDDSFormat(seqin,ssval):
	seqout=[]
	seqout.append([seqin[0][startTIME],seqin[0][startVAL]])
	seqout.append([seqin[0][stopTIME],seqin[0][stopVAL]])
	for ii in range(1,len(seqin)):
		if seqin[ii][startVAL]!=seqout[-1][1]:
			print("ERROR: Red Pitaya DDDS can only do ramps, not jumps!")
		seqout.append([seqin[ii][stopTIME],seqin[ii][stopVAL]])
	return [ssval,seqout]

def RunServer(seq, rp, autostart = 1):
	TIME_START = time.time()
	#CONSTANTS TELLING US ABOUT SYSTEM CONFIGURATION
	numChan = 2

	## Convert seq to get all the times and frequencies, and save to buffers to pass to FPGA Block RAM
	FinalSeqs=[] #Final list of ramps (each composed of # of steps, & slope) for each channel
	NumRamps=[]  #Total Number of ramps for each channel
	IFfreqsHz = []; #Initial/final frequencies in Hz

	## Convert seq to get all the times and frequencies
	for chan in seq.allChannels:
		if chan == None:
			continue
		if chan.chanid >= 2: #Assume the first four channels of dds_PDH sequence in allchannels.py are the four dds frequencies
			continue

		ssvalHz=chan.GetHardwareSSV() #steady_state_value
		IFfreqsHz.append(ssvalHz)

		#Next get the full sequence
		fullSeq = GenerateFullSeq(chan.GetHardwareValues(),ssvalHz)
		convertedSeq = ConvertSeqToSeconds(fullSeq)
		formattedSeq = ConvertSeqToDDDSFormat(convertedSeq,ssvalHz)
		#fullseq is a list of ramps in time with a frequency at each endpoint of each ramp. The first interval starts at time zero.
		#we may need to convert the form to work with DDDS_Sequencer
		#finally we'll need to figure out how many total ramps there were!
		FinalSeqs.append(formattedSeq)
		NumRamps.append(len(fullSeq))

	
	# to take doubler into account multiply the freqs by 0.5
	rp.SendSequenceSimple(FinalSeqs[0],FinalSeqs[1], scale_freq=0.5)
	# send frequency ramps to Red Pitaya!
	print(FinalSeqs)
	#time.sleep(0.1)
	# await trigger
	if autostart == 1:
		rp.trigger()
		logger.info("Software trigger sent!")
	else:
		logger.info("waiting for hardware trigger...")
		
	TIME_STOP = time.time()
	return TIME_STOP-TIME_START

class RpDDSServer(Server):

	def __init__(self, name, port, message, bitfile, maxevents):
		super().__init__(name, port, message)
		self.rp = RpDDS(bitfile=bitfile, fclk_Hz=125e6, maxevents=maxevents, SWTrigger=False)

	def queue(self):
		return RunServer(self.seq, self.rp, autostart=0)

	def run(self):
		return RunServer(self.seq, self.rp, autostart=1)

	def plotdata(self):
		return [0,], [0,]


if __name__ == '__main__':

	message = """
	===============================================
	==      DDS Profile Frequency Out Server     ==
	==                 for Red Pitaya            ==
	===============================================
	"""
	#bitfile_path = DIR_BITFILE/"DDDS_xlnx_512.bit"
	bitfile_path = DIR_BITFILE/"SimonLab_DDDS.bit"
	logger.info("Using bitfile {}".format(bitfile_path))
	#server = RpDDSServer("RpDDS_1", 60631, message=message, bitfile=bitfile_path, maxevents=512)
	server = RpDDSServer("RpDDS_1", 60631, message=message, bitfile=bitfile_path, maxevents=64)
	server.main_loop()