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
IP_RYDRAMEN = '127.0.0.1' # Loadlock control computer
IP_LABSERVER = '127.0.0.1' # Simonlab data backup server (lab office behind the sofa)
IP_RFSOC_0 = '127.0.0.1'
IP_RPDAC_0 = '127.0.0.1'
IP_RPDOG_0 = '127.0.0.1'

# RYDRAMEN PORTS 
PORT_REMOTECTRL = 50002

# RPDOG PORTS
PORT_DIGITAL      = 60001
# RPDAC PORTS
PORT_ANALOG       = 60002
# RFSOC PORTS
PORT_DDS          = 60003
