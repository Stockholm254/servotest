import sys
import math
import time
import numpy as np
from ..ServerClass import Server, logger
from pathlib import Path
from ..util.SequenceProcessor import *
from .kinesis_driver import Kinesis

class KinesisServer(Server):

	def __init__(self, name, port, message, serial_number):
		super().__init__(name, port, message)
		self.stage = Kinesis(serial_number)
		

	def __del__(self):
		self.stage.close()

	def updateSettings(self):
		for chan in self.seq.allChannels:
			print(chan._TransValues)

			val = chan._TransValues[0][1] # find the first value
			set = chan._TransValues[0]
			if set[1] != val or set[3] != val: # Check for non-identical values
				logger.warning('Kinesis stage given multiple settings in same sequence, but only takes the first!!')

			if chan.chanid == 0: # Waveplate angle
				angle = np.mod(val, 360.0)
				self.stage.moveToPosition(angle, eps=2)
				logger.debug("Waveplate moved successfully")
			else: # wtf?
				logger.warning('WARNING: Sequence specified for unsupported channel...')

	def cmd_seq(self, data):
		self.seq = data # unpack the sequence
		numChannels = 0
		for chan in self.seq.allChannels:
			if chan != None: numChannels += 1
		logger.debug("Received sequence ({} channels): {}".format(numChannels, self.seq.name))
		# updateSettings(self.api, self.DEVID, self.seq)
		reply = "Received sequence ({} channels): {}".format(numChannels, self.seq.name)
		self.send_msg(self.ReplyHeader() + reply)

	def queue(self):
		self.updateSettings() # move the stage during the QUEUE phase
		return 1

	def run(self):
		return 1

	def plotdata(self):
		return [0,], [0,]