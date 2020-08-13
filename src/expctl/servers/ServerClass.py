#!/usr/bin/python
import sys
from signal import signal, SIGINT
from sys import exit
import zmq
from pickle import dumps, loads
#from utilities.util import *
from ..sequencer import sequence
import math
import time
import numpy as np
import coloredlogs, logging

# Create ZeroMQ context
context = zmq.Context()

# Create a logger object.
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')

#=============================== Server Class ==================================#
class Server:
	def __init__(self, name, port, message=''):
		self.message = message
		self.name = name
		self.port = port
		self.seq = None
		self.sock = None
	
		if self.message:
			print((self.message))

		self.sock = context.socket(zmq.REP)
		try:
			self.sock.bind(f"tcp://*:{self.port}")
			logger.info(f"Server {self.name} started listening on {self.port}")
		except Exception as e:
			logger.exception("Bind failed!")
			sys.exit()

	def send_msg(self, msg, payload=None):
		# Send a message (command) to the client with an optional payload
		if payload is None:
			#only send a string as a command
			self.sock.send_multipart([msg.encode(),])
		else:
			#send command and python object
			self.sock.send_multipart([msg.encode(), dumps(payload)])

	def recv_msg(self):
		# Receive message, return string and (optional) payload (python object)
		multipart = self.sock.recv_multipart()
		msg = multipart[0].decode()
		if len(multipart)>1:
			payload = loads(multipart[1])
			return msg, payload
		else:
			return msg, None

	def ReplyHeader(self):
		return time.strftime('['+self.name+': %b %d %H:%M:%S]') + " "

	def cmd_unknown(self, cmd=''):
		logger.warning(f"Unknown command {cmd}!")
		self.send_msg(self.ReplyHeader() + f"Unknown command {cmd}")

	def cmd_ping(self):
		logger.info("Got Ping'd!")
		self.send_msg(self.ReplyHeader() + "Got PING'd!")

	def cmd_plotdata(self):
		logger.debug("Get Plotdata")
		plt_data = DataForPlot(self.seq)
		self.send_msg("DATA", plt_data)
	
	def cmd_seq(self, data):
		self.seq = data # unpack the sequence
		numChannels = 0
		for chan in self.seq.allChannels:
			if chan != None: numChannels += 1
		logger.debug(f"Received sequence ({numChannels} channels): {self.seq.name}")
		reply = f"Received {self.seq.name}, {numChannels} channels defined."
		self.send_msg(self.ReplyHeader() + reply)
	
	def cmd_queue(self):

		if self.seq == None:
			logger.error('QUEUE failed. Sequence has not been imported!')
			#self.send_msg(self.ReplyHeader() + 'QUEUE failed. Sequence has not been imported!')
		else:
			success = RunServer(self.seq, autostart=0)
			time_taken = '%.2f' % success
			logger.debug(f'Successfully ran sequence ({time_taken} seconds)')
			#DO not reply for QUEUE
			self.send_msg(self.ReplyHeader() + f'Successfully ran sequence ({time_taken} seconds)')

	def cmd_run(self):
		if self.seq == None:
			logger.error('Run() failed. Sequence has not been imported!')
			self.send_msg(self.ReplyHeader() + 'Run() failed. Sequence has not been imported!')
		else:
			success = RunServer(self.seq)
			time_taken = '%.2f' % success
			logger.debug(f'Successfully ran sequence ({time_taken} seconds)')
			self.send_msg(self.ReplyHeader() + f'Successfully ran sequence ({time_taken} seconds)')

	def main_loop(self):
		while True:
			try:
				command, data = self.recv_msg() # Receive a command
				print(command)
			except KeyboardInterrupt:
				logger.info("W: interrupt received, stopping…")
				break
			else:
				if command == "RUN":  # Run the sequence (if we've already received it)
					self.cmd_run()
				
				elif command == "SEQ": # Load in a sequence
					self.cmd_seq(data)

				elif command == "QUEUE": # Queue/arm for trigger
					self.cmd_queue()

				elif command == 'GETPLOTDATA': # Get plot data from server
					self.cmd_plotdata()
				
				elif command == 'PING':
					self.cmd_ping()
					
				else:
					self.cmd_unknown(command)

		# clean up
		self.sock.close()
		context.term()

def DataForPlot(seq):
	return np.zeros(10)

def RunServer(seq, autostart = 1):
	time.sleep(0.11)
	return 0.11

def handler(signal_received, frame):
	# Handle any cleanup here
	print('SIGINT or CTRL-C detected. Exiting gracefully')
	exit(0)

if __name__ == '__main__':

	message = """
	===========================================
	==       Dummy Digital Output Server     ==
	==              for PCIe 6537            ==
	=========================================== 
	"""
	server = Server("DOut1", 50001, message)
	server.main_loop()