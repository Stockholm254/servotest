#!/usr/bin/python
# -*- coding: utf-8 -*-

from ..sequencer.sequence import Sequence # Sequence and Channel object
from ..config.config import * # All IP and port configuration
from ..utilities.util import * # Print error function
from . import transformations as tran # Channel value transformation function

###################################################################################################
###    ALL CHANNELS/SEQS ARE DEFINED HERE, AS ARE FEW ROUTINES THAT CRUNCH THEM (@ bottom)      ###
###################################################################################################

# ALL IP ADDRESS AND PORT NUMBERS ARE DEFINED IN /config/config.py

#=======================================Sequence Definitions=========================================
#FIRST DECLARE ALL SEQUENCES into the all_sequences array, and then give them names for easier assignment!
all_sequences = ([
  Sequence("Digital sequence",        host=IP_RYDRAMEN, port=PORT_DIGITAL,  max_channels=15, graph=1, seq_type="MASTER"),  
  Sequence("Analog sequence",         host=IP_RYDRAMEN, port=PORT_ANALOG,   max_channels=16, graph=1),
  ])

digital_seq, analog_seq = all_sequences # WE DO IT IN THIS ORDER SO THAT ONE CANNOT GET AWAY WITH CREATING A NAMED SEQUENCE WHICH IS NOT IN THE ARRAY OF ALL SEQUENCES!!

#=======================================Channel Definitions=========================================
# NEXT ADD ALL OF THE CHANNELS TO THEM! ##Note: the name in quotes must have 1 < length < 31

# Digital card
TriggerOut  = digital_seq.newChannel(0,   "TriggerOut",       system='Ctrl',    steady_state_value=0, max_value=1, graph=0)
Digital01   = digital_seq.newChannel(1,   "Digital01",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Digital02   = digital_seq.newChannel(2,   "Digital02",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Digital03   = digital_seq.newChannel(3,   "Digital03",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Digital04   = digital_seq.newChannel(4,   "Digital04",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Digital05   = digital_seq.newChannel(5,   "Digital05",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Digital06   = digital_seq.newChannel(6,   "Digital06",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Digital07   = digital_seq.newChannel(7,   "Digital07",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Digital08   = digital_seq.newChannel(8,   "Digital08",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Digital09   = digital_seq.newChannel(9,   "Digital09",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Digital10   = digital_seq.newChannel(10,  "Digital10",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Digital11   = digital_seq.newChannel(11,  "Digital11",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Digital12   = digital_seq.newChannel(12,  "Digital12",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Digital13   = digital_seq.newChannel(13,  "Digital13",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Digital14   = digital_seq.newChannel(14,  "Digital14",        system='Test',    steady_state_value=0, max_value=1, graph=0)


# Analog card
Analog00   = analog_seq.newChannel(0,   "Analog00",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Analog01   = analog_seq.newChannel(1,   "Analog01",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Analog02   = analog_seq.newChannel(2,   "Analog02",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Analog03   = analog_seq.newChannel(3,   "Analog03",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Analog04   = analog_seq.newChannel(4,   "Analog04",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Analog05   = analog_seq.newChannel(5,   "Analog05",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Analog06   = analog_seq.newChannel(6,   "Analog06",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Analog07   = analog_seq.newChannel(7,   "Analog07",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Analog08   = analog_seq.newChannel(8,   "Analog08",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Analog09   = analog_seq.newChannel(9,   "Analog09",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Analog10   = analog_seq.newChannel(10,  "Analog10",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Analog11   = analog_seq.newChannel(11,  "Analog11",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Analog12   = analog_seq.newChannel(12,  "Analog12",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Analog13   = analog_seq.newChannel(13,  "Analog13",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Analog14   = analog_seq.newChannel(14,  "Analog14",        system='Test',    steady_state_value=0, max_value=1, graph=0)
Analog15   = analog_seq.newChannel(15,  "Analog15",        system='Test',    steady_state_value=0, max_value=1, graph=0)


#=====================================End Channel Definitions=======================================

#====================================Slave Channel Definitions======================================
# Any channel appears in this section should NEVER be given any value in any sequence file.
# The value of these channels will be assigned automatically later.
# The properties of the channel (id, name, steady_state_value, max_value, and graph) should be set in this section


###########################################################################################################
###   AUTO DETECT SEQUENCE AND CHANNEL TYPE AND CREATE HELPER LIST THAT IS USEFUL FOR THE FRONT PANEL   ###
###   IMPORTANT: NAMES ARE BEING CALLED BY OTHER MODULES, BE CAREFUL WHEN CHENGING THEM                 ###
###########################################################################################################

# Create slave and master channel pair for CopyChans() function in the processing routin
all_copyChans      = [] # List storing master-slave channel pairs
SEQUENCES_TO_GRAPH = [] # List of channels can be plotted
MasterSequence     = [] # Master sequence (it is a list instead of single variable to avoid double defined master channel)

for ii, _seq in enumerate(all_sequences):
  if _seq.seq_type == "MASTER":
    MasterSequence.append(_seq)

  for jj, _chan in enumerate(_seq.allChannels):
    if _chan != None:
      if _chan.chantype == 'Slave':
        master_chan = _chan.master
        all_copyChans.append([master_chan, _chan])
        _chan.master = None # This remove the dependence on unused modules. For example, camera slave to cam_trig, and cam_trig.seq is digital sequence which requires dat.transformation
      
  for jj, _chan in enumerate(_seq.channelsToGraph): # Graph channels
    SEQUENCES_TO_GRAPH.append(_chan)

# Check for the master channel
if len(MasterSequence) < 1:
  printError("No master sequence defined!")
elif len(MasterSequence) > 1:
  printError("Only one master sequence is allowed, "+str(len(MasterSequence))+" are defined!")
elif len(MasterSequence) == 1:
  MasterSequence = MasterSequence[0]
