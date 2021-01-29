import sys
import math
import time
import numpy as np
from ..ServerClass import Server, logger
from pathlib import Path
from ..util.SequenceProcessor import *
from .rpdog import *
import time

class RPDigitalServer(Server):

	def __init__(self, name, port, message):
		super().__init__(name, port, message)
		self.task_id = 0
		self.rp = RpDOG(bitfile="", fclk_Hz=125e6, maxevents=64, invertvals=False)

	def queue(self):
		return self.rp.run_server(self.seq, autostart=0)

	def run(self):
		return self.rp.run_server(self.seq, autostart=1)

	def plotdata(self):
		return self.rp.data_for_plot(self.seq)


if __name__ == '__main__':
	message = """
	===============================================
	==      Digital Output Generator Server      ==
	==                 for Red Pitaya            ==
	===============================================
	"""

	server = RPDigitalServer("DOut1", 50001, message=message)
	server.main_loop()