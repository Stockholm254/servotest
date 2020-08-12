#!/usr/bin/python
# -*- coding: utf-8 -*-

from sequencer.sequence import Sequence
import transformations as tran

###################################################################################################
###    ALL CHANNELS/SEQS ARE DEFINED HERE, AS ARE FEW ROUTINES THAT CRUNCH THEM (@ bottom)      ###
###################################################################################################

#=======================================Sequence Definitions=========================================
#FIRST DECLARE ALL SEQUENCES into the all_sequences array, and then give them names for easier assignment!

all_sequences = ([
  Sequence("Digital sequence", host='192.168.1.105', port=60615, max_channels=32),
  Sequence("Analog sequence",  host='192.168.1.105', port=60616, max_channels=32),
  Sequence("Camera sequence",  host='192.168.1.106', port=60614, max_channels=1 ),
  ])

digital_seq1, analog_seq1, pg_cam = all_sequences # WE DO IT IN THIS ORDER SO THAT ONE CANNOT GET AWAY WITH CREATING A NAMED SEQUENCE WHICH IS NOT IN THE ARRAY OF ALL SEQUENCES!!

bright_sequences   = [digital_seq1] #THIS IS THE SEQUENCES THAT CAN BE CHANGED IN THE STEADY STATE VALUES
# MonitorSequences   = Monitor_seq    #THIS IS THE SEQUENCE FOR MONITORING THE MACHINE STATUS!
MasterSequence     = digital_seq1   #THIS IS THE SEQUENCE THAT PHYSICALLY TRIGGERS THE OTHERS!
# SEQUENCES_TO_GRAPH = [digital_seq1, analog_seq1, dds_freq_seq1, dds_freq_seq2, dds_PDH_freq_seq1] #This controls who is graphed!
SEQUENCES_TO_GRAPH = [digital_seq1] #This controls who is graphed!

#=======================================Channel Definitions=========================================
#NEXT ADD ALL OF THE CHANNELS TO THEM! ##Note: the name in quotes must have 1 < length < 31

#Digital card
MOT0_ttl       = digital_seq1.newChannel(0,  "MOT TTL",                 steady_state_value=1, max_value=1, graph=1)
REP0_ttl       = digital_seq1.newChannel(1,  "REP TTL",                 steady_state_value=1, max_value=1, graph=1)
Scope_Trig     = digital_seq1.newChannel(2,  "Scope Trig",              steady_state_value=0, max_value=1, graph=1)
Cam_Trig       = digital_seq1.newChannel(3,  "Cam Trig",                steady_state_value=1, max_value=1, graph=1)
DDS_Trig       = digital_seq1.newChannel(4,  "DDS FPGA Trig",           steady_state_value=0, max_value=1, graph=1)
LAT1_ttl       = digital_seq1.newChannel(6,  "Lat1 TTl",                steady_state_value=1, max_value=1, graph=1)
LAT2_ttl       = digital_seq1.newChannel(7,  "Lat2 TTl",                steady_state_value=1, max_value=1, graph=1)
MOT1_ttl       = digital_seq1.newChannel(8,  "Slicing TTL",             steady_state_value=0, max_value=1, graph=1)
LAT_MOD_Trig   = digital_seq1.newChannel(9,  "LAT Int Mod Trig",        steady_state_value=0, max_value=1, graph=1)
LAT0_ttl       = digital_seq1.newChannel(10, "LAT0 TTL",                steady_state_value=1, max_value=1, graph=1)
RF_ttl         = digital_seq1.newChannel(11, "RF TTL",                  steady_state_value=0, max_value=1, graph=1)
Blue_ttl       = digital_seq1.newChannel(12, "Blue TTL",                steady_state_value=0, max_value=1, graph=1)
Nufern0_ttl    = digital_seq1.newChannel(14, "Cav Prb AOM TTL",         steady_state_value=0, max_value=1, graph=1)
SPCM_trig      = digital_seq1.newChannel(17, "SPCM Trig",               steady_state_value=0, max_value=1, graph=1)
REP1_ttl       = digital_seq1.newChannel(18, "Vert REP TTL",            steady_state_value=0, max_value=1, graph=1)
OptPump_ttl    = digital_seq1.newChannel(20, "Opt Pump TTL",            steady_state_value=0, max_value=1, graph=1)
CavPrbEOM_ttl  = digital_seq1.newChannel(22, "Cav Prb EOM TTL",         steady_state_value=1, max_value=1, graph=1)
Nufern1_ttl    = digital_seq1.newChannel(24, "Vert Imag Prb TTL",       steady_state_value=0, max_value=1, graph=1)
RadDress_ttl   = digital_seq1.newChannel(25, "Radial Dressing AOM TTL", steady_state_value=0, max_value=1, graph=1)
test_chan      = digital_seq1.newChannel(30, "Dig Test",                steady_state_value=0, max_value=1, graph=1)
test_chan_2    = digital_seq1.newChannel(31, "Dig Test 2",              steady_state_value=0, max_value=1, graph=1)

#Analog card
MOT0_pwr       = analog_seq1.newChannel(0,  "MOT Pwr",                   steady_state_value= 5.00, max_value=5.00, graph=1)
REP0_pwr       = analog_seq1.newChannel(1,  "REP Pwr",                   steady_state_value= 5.00, max_value=5.00, graph=1)
MOTCoil        = analog_seq1.newChannel(2,  "MOT Coil",                  steady_state_value= 3.00, max_value=5.00, graph=1)
BiasX          = analog_seq1.newChannel(3,  "Bias X",                    steady_state_value= 0.04, max_value=3.00, graph=1)
BiasY          = analog_seq1.newChannel(4,  "Bias Y",                    steady_state_value= 0.21, max_value=3.00, graph=1)
BiasZ          = analog_seq1.newChannel(5,  "Bias Z",                    steady_state_value= 0.52, max_value=3.00, graph=1)
LAT1_pwr       = analog_seq1.newChannel(6,  "LAT1 Pwr",                  steady_state_value= 4.90, max_value=5.00, graph=1)
LAT2_pwr       = analog_seq1.newChannel(7,  "LAT2 Pwr",                  steady_state_value= 4.90, max_value=5.00, graph=1)
MOT1_pwr       = analog_seq1.newChannel(8,  "Slicing Pwr",               steady_state_value= 4.90, max_value=5.00, graph=1)
LAT0_pwr       = analog_seq1.newChannel(9,  "LAT0 Pwr",                  steady_state_value= 4.90, max_value=5.00, graph=1)
Blue_pwr       = analog_seq1.newChannel(10, "Blue Pwr",                  steady_state_value= 4.60, max_value=5.00, graph=1)
RadDress_pwr   = analog_seq1.newChannel(11, "Radial Dressing AOM Gain",  steady_state_value= 0.00, max_value=5.00, graph=1)
Nufern0_pwr    = analog_seq1.newChannel(14, "Cav Prb AOM Pwr",           steady_state_value= 0.00, max_value=5.00, graph=1)
CavPrbEOM_pwr  = analog_seq1.newChannel(15, "Cav Prb EOM Pwr",           steady_state_value= 1.40, max_value=1.40, graph=1)
REP1_pwr       = analog_seq1.newChannel(16, "Vert REP Pwr",              steady_state_value= 0.00, max_value=5.00, graph=1)
OptPump1_pwr   = analog_seq1.newChannel(17, "Opt Pump 1 Pwr",            steady_state_value= 0.00, max_value=5.00, graph=1)
OptPump2_pwr   = analog_seq1.newChannel(18, "Opt Pump 2 Pwr",            steady_state_value= 0.00, max_value=5.00, graph=1)
analog_test    = analog_seq1.newChannel(31, "Analog Test",               steady_state_value= 0.00, max_value=5.00, graph=1)

#Chemeleon camera
CAMERA = pg_cam.newChannel(0, "Camera", steady_state_value=1, max_value=1, graph=1)
#=====================================End Channel Definitions=======================================

#====================================Slave Channel Definitions======================================
# Any channel appears in this section should NEVER be given any value in any sequence file.
# The value of these channels will be assigned automatically later.
# The properties of the channel (id, name, steady_state_value, max_value, and graph) should be set in this section

#=========================================Linked Channels===========================================
# List of channel pairs that would be copy and paste.
# To add a copy and paste pair, just add a new list of the form ["master_channel", "slave_channel"]
all_copyChans = ([
])
