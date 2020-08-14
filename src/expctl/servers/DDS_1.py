#!/usr/bin/python
import sys
import math
import time
import numpy as np
from .ServerClass import Server, logger

from .util import ok
from .dds_common import *

#code1 = "C:/Users/simonlab/Documents/Lukas/Python/Py3Test/Control_Suite_X/servers/FPGA_bit_file/DDS_freq_out_ExtCLK.bit"
code1 = DIR_BITFILE/"DDS_freq_out_ExtCLK.bit"
logger.info(f"Using bitfile {code1}")

jdebug=0
FPGAclock = 100.0 #MHz is the default, but we'll get the actual frequency from the FPGA pll itself!
#FPGAsn = '12520004R7' #This must match the S/N of the FPGA inside the PDH DDS box. Can find the serial number via the Opal Kelly FrontPanel interface.
#Development test FPGA board
FPGAsn = '1840000NS8' #This must match the S/N of the FPGA inside the PDH DDS box. Can find the serial number via the Opal Kelly FrontPanel interface.

FPGA_TMPCLOCKIN = 40.0 #this is the fix for the DDS going nuts from sync errors with FPGA IGNORES PLL
FPGAclock = FPGA_TMPCLOCKIN



class DDSServer(Server):

	def queue(self):
		RunServer(self.seq, dev, LOADMODE, autostart=0)
		logger.debug("DDS Loaded")
		return RunServer(self.seq, dev, RUNMODE, autostart=0)

	def run(self):
		RunServer(self.seq, dev, LOADMODE)
		logger.debug("DDS Loaded")
		return RunServer(self.seq, dev, RUNMODE)

	def plotdata(self):
		return [0,], [0,]

if __name__ == '__main__':

	#instantiate okC structure
	dev = ok.okCFrontPanel()
	pll = ok.okCPLL22150()
	#print 'Connecting to FPGA...'  + ('success' if dev.OpenBySerial("")==0 else 'failure')
	logger.info('Connecting to PDH FPGA S/N '+FPGAsn+'...'  + ('success' if dev.OpenBySerial(FPGAsn)==0 else 'failure'))
	logger.info('Getting FPGA PLL Eeprom Config...'  + ('success' if dev.GetEepromPLL22150Configuration(pll)==0 else 'failure'))
	logger.info('Setting FPGA PLL Config to Eeprom vals...'  + ('success' if dev.SetPLL22150Configuration(pll)==0 else 'failure'))
	#FPGAclock=float(pll.GetOutputFrequency(0))
	#Configure FPGA with bit code
	logger.info('Loading Bitfile...' + ('success' if dev.ConfigureFPGA(code1)==0 else 'failure'))
	logger.info('FPGA Clock Frequency: ' + str(FPGAclock) + ' MHz (set in server)')

	dev.ActivateTriggerIn(DDSRESET, 0) #RESET DDS
	dev.ActivateTriggerIn(RAMWRITERESET, 0) #RESET RAM

	message = """
	===============================================
	==      DDS Profile Frequency Out Server     ==
	==        for FPGA with External Clock       ==
	===============================================
	"""

	server = DDSServer("DDS_1", 60617, message=message)
	server.main_loop()

