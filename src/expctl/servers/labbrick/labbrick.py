import sys
import math
import time
import numpy as np
from ..ServerClass import Server, logger
from pathlib import Path
from ..util.SequenceProcessor import *
import time
from . import lms

def MHzToLB(v): # lab brick accepts Hz/10, for some reason
  return int(1e5 * v)

def dBmToLB(v): # lab brick takes powers in multiples of 0.25 dBm (and has 0.5 dBm resolution...)
  return int(4 * v)

def interpretGetPower(v): # return the actual power in dBm
	return 10 - v/4.0

def updateSettings(api, DEVID, seq): # update LabBrick based on the seq
	for chan in seq.allChannels:
		#print('\n' + str(chan.chanid) +':')
		print(chan._TransValues)

		val = chan._TransValues[0][1] # find the first value
		# print(str(val))
		#for set in chan._TransValues:
		set = chan._TransValues[0]
		if set[1] != val or set[3] != val: # Check for non-identical values
			print('WARNING: LabBrick given multiple settings in same sequence, but only takes the first!!')

		if chan.chanid == 0: # Frequency
			result_1 = api.set_frequency(DEVID, MHzToLB(val))
			logger.debug('set_frequency returned error {}'.format(result_1))
		elif chan.chanid == 1: # Power
			result_1 = api.set_power_level(DEVID, dBmToLB(val))
			logger.debug('set_power_level returned error {}'.format(result_1))
		elif chan.chanid == 2: # TTL
			result_1 = api.set_rf_on(DEVID, val)
			logger.debug('set_rf_on returned error {}'.format(result_1))
		else: # wtf?
			logger.warning('WARNING: Sequence specified for unsupported channel...')

	logger.info('Lab Brick Freq = ' + str(float(api.get_frequency(DEVID))/10**5) + ' MHz')
	logger.info('Lab Brick Power = ' + str(float(interpretGetPower(api.get_power_level(DEVID)))) + ' dBm')
	logger.info('Lab Brick TTL = ' + str(api.get_rf_on(DEVID)))


class LabbrickServer(Server):

	def __init__(self, name, port, message, serial_number, external_pulse_mod=0):
		super().__init__(name, port, message)
		self.SERIAL_NUMBER = serial_number
		self.external_pulse_mod = external_pulse_mod
		self.api = lms.VNX_LMS_API()
		logger.info('Num available devices = ' + str(self.api.get_num_devices()) + '\n') # Returns the number of UNCONNECTED
		logger.info('Available Device Serial Numbers:')
		devices = self.api.get_dev_info()

		DEVID = -1
		for device in devices:
			logger.info(self.api.get_serial_number(device))
			if self.api.get_serial_number(device) == self.SERIAL_NUMBER:
				DEVID = device
				logger.info("Found device {}".format(DEVID))
				break

		if DEVID == -1:
			logger.info('ERROR: device with serial number ' + str(self.SERIAL_NUMBER) + ' not found or already in use')
		else:
			logger.info('Device ' + str(DEVID) + ' Found, Connecting...')
			self.api.init_device(DEVID)
			# ARE THERE OTHER IMPORTANT SETTINGS (besides freq, power, and ttl) TO VERIFY HERE?!
			self.DEVID = DEVID
			min_power = self.api.get_min_pwr(self.DEVID)
			max_power = self.api.get_max_pwr(self.DEVID)

			min_pow = min_power / 4
			max_pow = max_power / 4
			logger.info('Minimum power for LMS device: {}'.format(min_pow))
			logger.info('Maximum power for LMS device: {}'.format(max_pow))

			result_1 = self.api.set_external_pulse_mod(self.DEVID, self.external_pulse_mod)
			logger.debug('set_external_pulse_mod returned error {}'.format(result_1))
			time.sleep(0.5)

	def __del__(self):
		self.api.close_device(self.DEVID)
		logger.info('Device Connection Closed')

	def cmd_seq(self, data):
		self.seq = data # unpack the sequence
		numChannels = 0
		for chan in self.seq.allChannels:
			if chan != None: numChannels += 1
		logger.debug("Received sequence ({} channels): {}".format(numChannels, self.seq.name))
		updateSettings(self.api, self.DEVID, self.seq)
		reply = "Received sequence ({} channels): {}".format(numChannels, self.seq.name)
		self.send_msg(self.ReplyHeader() + reply)

	def queue(self):
		return 1

	def run(self):
		return 1

	def plotdata(self):
		return [0,], [0,]


if __name__ == '__main__':

	message = """
	===========================================
	==           Lab Brick Server 1          ==
	==        Signal Generator 5-10 GHz      ==
	==              SN 1200                  ==
	===========================================
	"""
	server = LabbrickServer("LB1", 60615, message=message, serial_number=1200, external_pulse_mod=1)
	server.main_loop()