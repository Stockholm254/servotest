import sys
import math
import time
import numpy as np
from ..ServerClass import Server, logger
from pathlib import Path
from ..util.SequenceProcessor import *
from .rpdac import RpDAC
import time


def run_server(seq, rp, autostart = 1):
	TIME_START = time.time()
	
	rpseq = []

	# Convert seq from Simonlab format to RpDAC format
	# The RpDAC format is [[chan, vIF, [t0, t1,...], [v0, v1,...]],...]
	for chan in seq.allChannels:
		if chan is None:
			continue
		if chan.chanid >= rp.NUM_CHANNELS:
			continue

		rpchan = [chan.chanid]

		rpchan.append(chan.GetHardwareSSV()) 

		# Next get the full sequence
		ramps = GenerateFullSeq(chan.GetHardwareValues(), chan.GetHardwareSSV())
		### Does this work??
		times = [r[2] for r in ramps]
		vals = [r[3] for r in ramps]

		# Convert times from microseconds to seconds
		times = [t*1e-6 for t in times]

		# Add times and voltages to this channel
		rpchan.append(times)
		rpchan.append(vals)

		# Add this channel to the sequence
		rpseq.append(rpchan)

	# Queue the sequence
	rp.queue_sequence(rpseq)

	# Trigger
	if autostart == 1:
		rp.trigger()
		logger.info("Software trigger sent!")
	else:
		logger.info("waiting for hardware trigger...")
		
	TIME_STOP = time.time()
	return TIME_STOP-TIME_START


class RpDACServer(Server):

	def __init__(self, name, port, message, bitfile):
		super().__init__(name, port, message)
		self.rp = RpDAC(bitfile=bitfile, SWTrigger=False)

	def queue(self):
		return run_server(self.seq, self.rp, autostart=0)

	def run(self):
		return run_server(self.seq, self.rp, autostart=1)

	def plotdata(self):
		return [0,], [0,]


if __name__ == '__main__':

	message = """
	===============================================
	==      DDS Profile Frequency Out Server     ==
	==                 for Red Pitaya            ==
	===============================================
	"""
	
	bitfile_path = Path(__file__).parent/"red_pitaya_top.bit"
	logger.info("Using bitfile {}".format(bitfile_path))
	server = RpDDSServer("RpDAC", 60632, message=message, bitfile=bitfile_path)
	server.main_loop()