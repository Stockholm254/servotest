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
	==           Lab Brick Server 4          ==
	==        Signal Generator 5-10 GHz      ==
	==              SN 5626                  ==
	===========================================
	"""
	server = LabbrickServer("LB4", 60618, message=message, serial_number=5626,external_pulse_mod=1)
	server.main_loop()