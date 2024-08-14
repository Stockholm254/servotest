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
  Sequence("Digital sequence",        host=IP_RPDOG_0, port=PORT_DIGITAL,  max_channels=14, graph=1, seq_type="MASTER"),  
  Sequence("Analog sequence",         host=IP_RPDAC_0, port=PORT_ANALOG,   max_channels=16, graph=1),
  ])

digital_seq, analog_seq = all_sequences # WE DO IT IN THIS ORDER SO THAT ONE CANNOT GET AWAY WITH CREATING A NAMED SEQUENCE WHICH IS NOT IN THE ARRAY OF ALL SEQUENCES!!

#=======================================Channel Definitions=========================================
# NEXT ADD ALL OF THE CHANNELS TO THEM! ##Note: the name in quotes must have 1 < length < 31

# Digital card
MOT_AOM_TTL        = digital_seq.newChannel(0,   "MOT_AOM_TTL",           system='MOT',    steady_state_value=1, max_value=1, graph=0)
Repumper_AOM_TTL   = digital_seq.newChannel(1,   "Repumper_AOM_TTL",      system='MOT',    steady_state_value=1, max_value=1, graph=0)


# Analog card
MOT_Coil1_Current   = analog_seq.newChannel(0,   "MOT_Coil1_Current",   system='MOT',    steady_state_value=2, max_value=3, graph=0)
# MOT_Coil2_Current   = analog_seq.newChannel(1,   "MOT_Coil2_Current",   system='MOT',    steady_state_value=2, max_value=3, graph=0)
MOT_AOM_Gain        = analog_seq.newChannel(2,   "MOT_AOM_Gain",        system='MOT',    steady_state_value=5, max_value=5, graph=0)
Repumper_AOM_Gain   = analog_seq.newChannel(3,   "Analog01",            system='MOT',    steady_state_value=5, max_value=5, graph=0)


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
