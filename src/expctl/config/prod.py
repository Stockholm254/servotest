#!/usr/bin/python
# -*- coding: utf-8 -*-
from pathlib import Path

#########################
## Default Directories ##
#########################
DIR_SEQ  = Path(__file__).parent.parent/"usr/sequences" # defaulst sequences files
DIR_MV   = Path(__file__).parent.parent/"usr/snippets" # default MV files
DIR_TEMP = Path(__file__).parent.parent/"temp" # front panel temperary file directory
DIR_DATA = Path(__file__).parent.parent.parent.parent/"TestOutput/Data/" # experiment data
DIR_LOG  = Path(__file__).parent.parent.parent.parent/"TestOutput/Logs/" # experiment run log
DIR_REM  = Path(__file__).parent.parent/"usr/Remote"  #Path("./usr/Remote") # Remote uploaded file

# FNAME_SSV = r'/temp_MV.txt'
FNAME_SSV     = 'SetSSV.py'  # Set steady state value sequence
FNAME_TEMP_MV = 'temp_MV.txt' # File name for temporary mvs

####################################
## TCP/IP Information for the Lab ##
####################################
### REDICRECT TO LOCAL PC FOR TESTING
## IP address
IP_RYDBURGER = '10.108.56.6' # Experimental control computer (control room)
IP_RYDFRIES  = '10.108.56.4' # Data collection computer (laser room top racks)
IP_LABSERVER = '192.168.1.101' # Simonlab data backup server (lab office behind the sofa)
IP_RYDNUGGET = '10.108.56.5' # New rydberg polariton experiment control computer (control room)
IP_RPTR = '192.168.1.12'
IP_RFSOC_1 = '10.108.56.8'
IP_RYDSHAKE = '192.168.1.109'
IP_RPCOUNTER = 'simonlab-multimode-rpcounter0.stanford.edu'
IP_RYDFLURRY = '10.108.56.11' # Laptop controlling DMD and SmarAct

# IP_RYDBURGER = '192.168.1.105' # Experimental control computer (control room)
# IP_RYDFRIES  = '192.168.1.106' # Data collection computer (laser room top racks)
# IP_RYDCOKES  = '192.168.1.107' # Laptop (mobile, usually in the vacuum room cart)
# IP_LABSERVER = '192.168.1.101' # Simonlab data backup server (lab office behind the sofa)
# IP_RYDNUGGET = '192.168.1.120' # New rydberg polariton experiment control computer (control room)
# IP_RPTR = '192.168.1.12'
# IP_RFSOC_1 = '192.168.1.160'
# IP_RYDSHAKE = '192.168.1.109'
# IP_RPCOUNTER = '192.168.1.125'

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
PORT_ADC        = 60622 # GW Instek scope next to monitors for use as ADC

# RYDFRIES PORTS
PORT_CAMERA     = 60614 # Chameleon camera (side or vertical imaging system, chamber table)
PORT_CAMERA2    = 60613 # Chameleon camera (side or vertical imaging system, chamber table)
PORT_LB1        = 60615 # Lab Brick 1, for the detuning of the 1529 carrier
PORT_LB2        = 60616 # Lab Brick 1, for the detuning of the 1529 carrier
PORT_LB3        = 60617 # Lab Brick 1, for the detuning of the 1529 carrier
PORT_LB4        = 60618 # Lab Brick 4, for repump sideband of 795 OP
PORT_KINESIS_2  = 60641 # Thorlabs Kinesis stage for lambda/2 waveplates
PORT_KINESIS_4  = 60642 # Thorlabs Kinesis stage for lambda/4 waveplates
PORT_ATT = 60651 # Minicircuits attenuator

# RPDDS PORTS
PORT_RPTR       = 60631

#RFSOC PORTS
PORT_RFSOC = 60617 # RFSOC 1 Box

# RYDSHAKE PORTS
PORT_DMD = 60651
PORT_SMARACT = 60637
# RPCOUNTER PORTS
#PORT_RPTR       = 60621 # PORT_RPTR       = 60621  this line was here!!?! this is going to overwrite the port for the transport red pitaya!!!