import sys
import math
import time
import numpy as np
from ..ServerClass import Server, logger
from pathlib import Path
from ..util.SequenceProcessor import *
from .servodriver import Servoset
import argparse
import logging
logging.basicConfig(level=logging.INFO)

class STSServer(Server):

	def __init__(self, name, port, message,board_id=0,servo_channel_list=[]):
		super().__init__(name, port, message)
		self.servo_channel_list=servo_channel_list
		self.servos=Servoset(board_id,servo_channel_list)
		self.servos.torques_enable()
		#self.servos.set_zero()
		#Here we probably don't need serial number for servo motors

	def __del__(self):
		self.servos.close()

	def set_angle(self):
		value_list=[]
		pos_mask = [0 for i in range(len(self.servo_channel_list))]
		if len(self.servo_channel_list) != len(self.seq.allChannels):
			logger.error("Servoaligner received sequence with {} channels, but only {} channels are connected".format(len(self.seq.allChannels), len(self.servo_channel_list)))
			return
		for i in range(len(self.servo_channel_list)):
			chan = self.seq.allChannels[i]
			if chan is not None:
				pos_mask[i] = 1
				set_val = chan._TransValues[0]
				val = set_val[1] # find the first value
				value_list.append(float(val))
				if set_val[3] != val: # Check for non-identical values
					logger.warning('Servoalinger given multiple settings in same sequence, but only takes the first!!')
			else:
				value_list.append(0)

		print(pos_mask)
		print(value_list)
		self.servos.set_angle(value_list)


	def cmd_seq(self, data):
		self.seq = data # unpack the sequence
		numChannels = 0
		for chan in self.seq.allChannels:
			if chan != None: numChannels += 1
		logger.debug("Received sequence ({} channels): {}".format(numChannels, self.seq.name))
		# self.set_angle()
		reply = "Received sequence ({} channels): {}".format(numChannels, self.seq.name)
		self.send_msg(self.ReplyHeader() + reply)


	def queue(self):
		self.set_angle() # move the stage during the QUEUE phase
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
	===========================================`
	"""
	server = STSServer("STS1", 60627, message=message, board_id=0, servo_channel_list=[0,1,2,3,4,5,6,7])
	# Create a servozero subcommand
	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers()

	# set_zero
	parser_zero = subparsers.add_parser('set_zero', help='Set the current position as zero')
	parser_zero.set_defaults(func=server.servos.set_zero_args)
	# go home
	parser_home = subparsers.add_parser('home', help='Move to the home position')
	parser_home.set_defaults(func=server.servos.home_args)
	# set_angle
	parser_angle = subparsers.add_parser('set_angle', help='Move to the specified angle')
	parser_angle.add_argument('angle', nargs='+', type=float, help='Angle to move to')
	parser_angle.set_defaults(func=server.servos.set_angle_args)
	# set single angle
	parser_single = subparsers.add_parser('set_single', help='Move a single servo to the specified angle')
	parser_single.add_argument('index', type=int, help='Channel to move')
	parser_single.add_argument('angle', type=float,help='Angle to move to')
	parser_single.set_defaults(func=server.servos.set_single_args)

	# if len(sys.argv) <= 1:
	# 	sys.argv.append('--help')
	try:
		options = parser.parse_args()
		options.func(options)
	except:
		pass

	server.main_loop()