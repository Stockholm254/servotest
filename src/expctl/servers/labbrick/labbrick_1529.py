import sys
import math
import time
import numpy as np
from ..ServerClass import Server, logger
from pathlib import Path
from ..util.SequenceProcessor import *
import time
from . import lms
from .labbrick import LabbrickServer, MHzToLB, dBmToLB, interpretGetPower, updateSettings

if __name__ == '__main__':

	message = """
	===========================================
	==           Lab Brick Server 2          ==
	==      Signal Generator 10-20 GHz       ==
	==                SN 20604               ==
	===========================================
	"""
	server = LabbrickServer("LB2", 60616, message=message, serial_number=20604,external_pulse_mod=1)
	server.main_loop()