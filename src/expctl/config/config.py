#!/usr/bin/python
# -*- coding: utf-8 -*-
from pathlib import Path

#########################
## Default Directories ##
#########################
DIR_SEQ  = Path("./usr/sequences") # defaulst sequences files
DIR_MV   = Path("./usr/snippets") # default MV files
DIR_TEMP = Path("./temp/") # front panel temperary file directory
DIR_DATA = Path("../TestOutput/Data/")#r"E:/Data/" # experiment data
DIR_LOG  = Path("../TestOutput/Logs/")#r"E:/Logs/FrontPanel"    # experiment run log
# DIR_INFO = r"C:/Users/Simonlab/Documents/Info"   # experiment info
DIR_REM  = Path("./usr/Remote") # Remote uploaded file

# FNAME_SSV = r'/temp_MV.txt'
FNAME_SSV     = 'SetSSV.py'  # Set steady state value sequence
FNAME_TEMP_MV = 'temp_MV.txt' # File name for temporary mvs

####################################
## TCP/IP Information for the Lab ##
####################################
## IP address
# IP_RYDBURGER = '192.168.1.105' # Experimental control computer (control room)
# IP_RYDFRIES  = '192.168.1.106' # Data collection computer (laser room top racks)
# IP_RYDCOKES  = '192.168.1.107' # Laptop (mobile, usually in the vacuum room cart)
# IP_LABSERVER = '192.168.1.101' # Simonlab data backup server (lab office behind the sofa)
# IP_RYDNUGGET = '192.168.1.120' # New rydberg polariton experiment control computer (control room)

### REDICRECT TO LOCAL PC FOR TESTING
IP_RYDBURGER = '192.168.1.13' # Experimental control computer (control room)
IP_RYDFRIES  = '192.168.1.13' # Data collection computer (laser room top racks)
IP_RYDCOKES  = '192.168.1.13' # Laptop (mobile, usually in the vacuum room cart)
IP_LABSERVER = '192.168.1.13' # Simonlab data backup server (lab office behind the sofa)
IP_RYDNUGGET = '192.168.1.13' # New rydberg polariton experiment control computer (control room)

# RYDBURGER PORTS
PORT_REMOTECTRL = 60000 # Remote front panel control (disabled)
PORT_DIGITAL    = 50001 # 60615 # National Instrument digital card (in the control computer)
PORT_ANALOG     = 60616 # National Instrument analog card (in the control computer)
PORT_DDS1       = 60617 # DDS box 1 (laser room top rack)
PORT_DDS2       = 60624 # DDS box 2 (laser room top rack)
PORT_DDSPDH     = 60618 # DDS PHD locking box (vacuum room lower rack)
PORT_PCOUNTER   = 60621 # Photon counter FPGA (control room under table rack)
PORT_PTIMER     = 60623 # Photon timer FPGA (control room under table rack)
PORT_PTIMER2    = 60625 # Photon timer FPGA (control room under table rack); TimerMcTimeFace
PORT_PTIMER3    = 60626 # Photon timer FPGA (control room under table rack); TimerMcTimeFace
PORT_AD1		= 60701 # Analog Devices ADF435X, for microwave generation
# RYDFRIES PORTS
PORT_CAMERA     = 60614 # Chameleon camera (side or vertical imaging system, chamber table)
PORT_LB1        = 60615 # Lab Brick 1, for the detuning of the 1529 carrier
PORT_LB2        = 60616 # Lab Brick 1, for the detuning of the 1529 carrier
PORT_LB3        = 60617 # Lab Brick 1, for the detuning of the 1529 carrier
