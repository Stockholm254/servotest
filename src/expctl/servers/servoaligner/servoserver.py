import sys
import math
import time
import numpy as np
from ..ServerClass import Server, logger
from pathlib import Path
from ..util.SequenceProcessor import *
from .servodriver import Servoset

class ServoalignerServer(Server):

	def __init__(self, name, port, message):
		super().__init__(name, port, message)
		self.servos=Servoset()
		self.servos.set_zero()
		#Here we probably don't need serial number for servo motors
		
	def __del__(self):
		self.servos.close()

	def updateSettings(self):
		value_list=[]
		for chan in self.seq.allChannels:
			#print(chan._TransValues)
			val = chan._TransValues[0][1] # find the first value
			value_list.append(int(val*4096/360)+2048)
			set = chan._TransValues[0]
			if set[1] != val or set[3] != val: # Check for non-identical values
				logger.warning('Servoalinger given multiple settings in same sequence, but only takes the first!!')

			# if chan.chanid == 0: # Waveplate angle
			# 	# angle = np.mod(val, 360.0)
			# 	angle = np.mod(val+180, 360.0) - 180.0
			# 	self.stage.moveToPosition(angle, eps=5)
			# 	logger.debug("Waveplate moved successfully")
			# else: # wtf?
			# 	logger.warning('WARNING: Sequence specified for unsupported channel...')
		print(value_list)
		self.servos.set_angle(value_list)


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


if __name__ == '__main__':

	message = """
	===========================================
	==           Servo Aligner Server 1      ==
	==                STS3032                ==
	==                                       ==
	===========================================
	"""
	server = ServoalignerServer("SA1", 60627, message=message)
	server.main_loop()