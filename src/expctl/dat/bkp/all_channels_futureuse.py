#!/usr/bin/python
# -*- coding: utf-8 -*-

from sequencer.sequence import Sequence
import transformations as tran

IP_RYDBURGER = '192.168.1.105'
IP_RYDFRIES  = '192.168.1.106'

###################################################################################################
###    ALL CHANNELS/SEQS ARE DEFINED HERE, AS ARE FEW ROUTINES THAT CRUNCH THEM (@ bottom)      ###
###################################################################################################

#=======================================Sequence Definitions=========================================
#FIRST DECLARE ALL SEQUENCES into the all_sequences array, and then give them names for easier assignment!

all_sequences = ([
  Sequence("Digital sequence",        host=IP_RYDBURGER, port=60615, max_channels=32),
  Sequence("Analog sequence",         host=IP_RYDBURGER, port=60616, max_channels=32),
  Sequence("Camera sequence",         host=IP_RYDFRIES,  port=60614, max_channels=1 ),
  Sequence("DDS 1 sequence",          host=IP_RYDBURGER, port=60617, max_channels=4 ),
  Sequence("DDS PDH sequence",        host=IP_RYDBURGER, port=60618, max_channels=7 ),
  Sequence("DDS 2 sequence",          host=IP_RYDBURGER, port=60619, max_channels=4 ),
  Sequence("Photon Timer sequence",   host=IP_RYDBURGER, port=60623, max_channels=2 ),
  Sequence("Photon Counter sequence", host=IP_RYDBURGER, port=60621, max_channels=4 ),
  ])

digital_seq1, analog_seq1, cam, dds_1, dds_pdh, dds_2, photon_counter, photon_timer = all_sequences # WE DO IT IN THIS ORDER SO THAT ONE CANNOT GET AWAY WITH CREATING A NAMED SEQUENCE WHICH IS NOT IN THE ARRAY OF ALL SEQUENCES!!

bright_sequences   = [digital_seq1] #THIS IS THE SEQUENCES THAT CAN BE CHANGED IN THE STEADY STATE VALUES
MasterSequence     = digital_seq1   #THIS IS THE SEQUENCE THAT PHYSICALLY TRIGGERS THE OTHERS!
SEQUENCES_TO_GRAPH = [digital_seq1] #This controls who is graphed!

#=======================================Channel Definitions=========================================
# NEXT ADD ALL OF THE CHANNELS TO THEM! ##Note: the name in quotes must have 1 < length < 31

# Digital card
MOT0_ttl      = digital_seq1.newChannel(0,  "MOT TTL",          system='MOT',     steady_state_value=1, max_value=1, graph=1, )
REP0_ttl      = digital_seq1.newChannel(1,  "REP TTL",          system='MOT',     steady_state_value=1, max_value=1, graph=1, )
Scope_trig    = digital_seq1.newChannel(2,  "Scope Trig",       system='Debug',   steady_state_value=0, max_value=1, graph=1, )
Cam_trig      = digital_seq1.newChannel(3,  "Came Trig",        system='IMG',     steady_state_value=1, max_value=1, graph=1, )
DDS_trig      = digital_seq1.newChannel(4,  "DDS FPGA Trig",    system='Debug',   steady_state_value=0, max_value=1, graph=1, )
LAT1_ttl      = digital_seq1.newChannel(6,  "Lat Hori TTL",     system='LAT',     steady_state_value=1, max_value=1, graph=1, )
LAT2_ttl      = digital_seq1.newChannel(7,  "Lat Vert TTL",     system='LAT',     steady_state_value=1, max_value=1, graph=1, )
MOT1_ttl      = digital_seq1.newChannel(8,  "Slicing TTL",      system='Slice',   steady_state_value=0, max_value=1, graph=1, transform_t=tran.SliceAOMDelay)
LAT_mod_trig  = digital_seq1.newChannel(9,  "Lat Int Mod Trig", system='LAT',     steady_state_value=0, max_value=1, graph=1, )
LAT0_ttl      = digital_seq1.newChannel(10, "Lat Main TTL",     system='LAT',     steady_state_value=0, max_value=1, graph=1, transform_t=tran.LatAOMDelay)
RF_ttl        = digital_seq1.newChannel(11, "RF ttl",           system='RF',      steady_state_value=0, max_value=1, graph=1, )
Blue_ttl      = digital_seq1.newChannel(12, "Blue TTL",         system='Blue',    steady_state_value=0, max_value=1, graph=1, transform_t=tran.BlueAOMDelay)
Nufern0_ttl   = digital_seq1.newChannel(14, "Cav Prb TTL",      system='CavPrb',  steady_state_value=0, max_value=1, graph=1, transform_t=tran.CavPrbAOMDelay)
SPCM_ttl      = digital_seq1.newChannel(17, "SPCM Gate TTL",    system='CavPrb',  steady_state_value=0, max_value=1, graph=1, )
REP1_ttl      = digital_seq1.newChannel(18, "Vert REP TTL",     system='Slice',   steady_state_value=0, max_value=1, graph=1, transform_t=tran.VertRepAOMDelay)
OptPump0_ttl  = digital_seq1.newChannel(20, "Opt Pump TTL",     system='OptPump', steady_state_value=1, max_value=1, graph=1, )
EITPrbEOM_ttl = digital_seq1.newChannel(22, "Cav Prb EOM TTL",  system='CavPrb',  steady_state_value=1, max_value=1, graph=1, )
Nufern1_ttl   = digital_seq1.newChannel(24, "Vert Img Prb TTL", system='IMG',     steady_state_value=1, max_value=1, graph=1, transform_t=tran.TopImgAOMDelay)
MOT2_ttl      = digital_seq1.newChannel(26, "Global DEP TTL",   system='Slice',   steady_state_value=0, max_value=1, graph=1, transform_t=tran.MOTPrbDelay)
Digi_test     = digital_seq1.newChannel(31, "Digital Test",     system='Debug',   steady_state_value=0, max_value=1, graph=1, )

# Analog card
MOT0_pwr      = analog_seq1.newChannel(0,  "MOT Pwr",         system='MOT',     steady_state_value=3.3345, max_value=5.0,  graph=1, )
REP0_pwr      = analog_seq1.newChannel(1,  "REP Pwr",         system='MOT',     steady_state_value=3.801,  max_value=5.0,  graph=1, )
MOTCoil       = analog_seq1.newChannel(2,  "MOT Coil",        system='MOT',     steady_state_value=5.0,    max_value=5.0,  graph=1, )
BiasX         = analog_seq1.newChannel(3,  "Bias X",          system='MOT',     steady_state_value=0.04,   max_value=3.0,  graph=1, )
BiasY         = analog_seq1.newChannel(4,  "Bias Y",          system='MOT',     steady_state_value=0.66,   max_value=3.0,  graph=1, )
BiasZ         = analog_seq1.newChannel(5,  "Bias Z",          system='MOT',     steady_state_value=-0.56,  max_value=3.0,  graph=1, )
LAT1_pwr      = analog_seq1.newChannel(6,  "Lat Hori Pwr",    system='LAT',     steady_state_value=4.8,    max_value=5.0,  graph=1, )
LAT2_pwr      = analog_seq1.newChannel(7,  "Lat Vert Pwr",    system='LAT',     steady_state_value=4.8,    max_value=5.0,  graph=1, )
MOT1_pwr      = analog_seq1.newChannel(8,  "Slicing Pwr",     system='Slice',   steady_state_value=3.8,    max_value=5.0,  graph=1, )
LAT0_pwr      = analog_seq1.newChannel(9,  "Lat Main Pwr",    system='LAT',     steady_state_value=4.7,    max_value=5.0,  graph=1, )
Blue_pwr      = analog_seq1.newChannel(10, "Blue Pwr",        system='Blue',    steady_state_value=4.25,   max_value=5.0,  graph=1, )
Nufern0_ttl   = analog_seq1.newChannel(14, "Cav Prb Pwr",     system='CavPrb',  steady_state_value=0.0,    max_value=5.0,  graph=1, )
CavPrbEOM_pwr = analog_seq1.newChannel(15, "Cav Prb EOM Pwr", system='CavPrb',  steady_state_value=5.0,    max_value=5.0,  graph=1, )
REP1_pwr      = analog_seq1.newChannel(16, "Vert REP Pwr",    system='Slice',   steady_state_value=4.0,    max_value=5.0,  graph=1, )
OptPump0_pwr  = analog_seq1.newChannel(17, "Opt Pump Pwr",    system='OptPump', steady_state_value=4.6,    max_value=5.0,  graph=1, )
EF1           = analog_seq1.newChannel(21, "EFilter 1",       system='EField',  steady_state_value=0.0,    max_value=10.0, graph=1, transform_v=tran.ElectrodeGain1)
EF2           = analog_seq1.newChannel(22, "EFilter 2",       system='EField',  steady_state_value=0.0,    max_value=10.0, graph=1, transform_v=tran.ElectrodeGain2)
EF3           = analog_seq1.newChannel(23, "EFilter 3",       system='EField',  steady_state_value=0.0,    max_value=10.0, graph=1, transform_v=tran.ElectrodeGain3)
EF4           = analog_seq1.newChannel(24, "EFilter 4",       system='EField',  steady_state_value=0.0,    max_value=10.0, graph=1, transform_v=tran.ElectrodeGain4)
EF5           = analog_seq1.newChannel(25, "EFilter 5",       system='EField',  steady_state_value=0.0,    max_value=10.0, graph=1, transform_v=tran.ElectrodeGain5)
EF6           = analog_seq1.newChannel(26, "EFilter 6",       system='EField',  steady_state_value=0.0,    max_value=10.0, graph=1, transform_v=tran.ElectrodeGain6)
EF7           = analog_seq1.newChannel(27, "EFilter 7",       system='EField',  steady_state_value=0.0,    max_value=10.0, graph=1, transform_v=tran.ElectrodeGain7)
EF8           = analog_seq1.newChannel(28, "EFilter 8",       system='EField',  steady_state_value=0.0,    max_value=10.0, graph=1, transform_v=tran.ElectrodeGain8)
EF9           = analog_seq1.newChannel(29, "EFilter 9",       system='EField',  steady_state_value=0.0,    max_value=10.0, graph=1, transform_v=tran.ElectrodeGain9)
EF10          = analog_seq1.newChannel(30, "EFilter P0",      system='EField',  steady_state_value=0.0,    max_value=10.0, graph=1, transform_v=tran.ElectrodeGain0)
Anal_test     = analog_seq1.newChannel(31, "Analog Test",     system='Debug',   steady_state_value=0.0,    max_value=5.0,  graph=1, )

# DDS box 1 (MOT, REP, LAT)
DDS_REP   = dds_1.newChannel(0, "REP Lock Freq", system='MOT', steady_state_value=96.6,  max_value=2100, graph=1, transform_v=tran.MHzToHz)
DDS_MOT   = dds_1.newChannel(1, "MOT Lock Freq", system='MOT', steady_state_value=490.0, max_value=2100, graph=1, transform_v=tran.MHzToHz)
DDS_LAT1  = dds_1.newChannel(2, "Lat Hori Freq", system='LAT', steady_state_value=80.0,  max_value=2100, graph=1, transform_v=tran.MHzToHz)
DDS_LAT2  = dds_1.newChannel(3, "Lat Vert Freq", system='LAT', steady_state_value=80.0,  max_value=2100, graph=1, transform_v=tran.MHzToHz)

# DDS PDH box (Ultra-stable cavity PDH locking, cavity probe)
DDS_PDH1560   = dds_pdh.newChannel(0, "PDH 1560",         system='CavPrb', steady_state_value=156.50, max_value=2100, graph=1, transform_v=tran.MHzToHz)
DDS_PDH960    = dds_pdh.newChannel(1, "PDH 960",          system='Blue',   steady_state_value=641.65, max_value=2100, graph=1, transform_v=tran.MHzToHz)
DDS_PDH780    = dds_pdh.newChannel(2, "PDH 780",          system='CavPrb', steady_state_value=470.00, max_value=2100, graph=1, transform_v=tran.MHzToHz)
DDS_CavPrbEOM = dds_pdh.newChannel(3, "Cav Prb EOM Freq", system='CavPrb', steady_state_value=322.14, max_value=2100, graph=1, transform_v=tran.MHzToHz)
DDS_HalfRng   = dds_pdh.newChannel(5, "PDH Half Range",   system='Debug',  steady_state_value=5.0,    max_value=100,  graph=0, transform_v=tran.MHzToHz)

# DDS box 2 (Cavity probe double pass AOM, optical pumping AOM)
DDS_CavPrbAOM = dds_2.newChannel(0, "Cav Prb AOM Freq",    system='CavPrb',  steady_state_value=500,  max_value=2100, graph=1, transform_v=tran.MHzToHz)
DDS_chan1     = dds_2.newChannel(1, "DDS Box 2 channel 2", system='Debug',   steady_state_value=100,  max_value=2100, graph=1, transform_v=tran.MHzToHz)
DDS_OptPump1  = dds_2.newChannel(2, "OptPump AOM1 Freq",   system='OptPump', steady_state_value=80.0, max_value=2100, graph=1, transform_v=tran.MHzToHz)
DDS_OptPump2  = dds_2.newChannel(3, "OptPump AOM2 Freq",   system='OptPump', steady_state_value=80.0, max_value=2100, graph=1, transform_v=tran.MHzToHz)

# Photon counter
PC_bin_num  = photon_counter.newChannel(1, "Counter Bin Num",  system='CavPrb', steady_state_value=100, max_value=1024, graph=0)
PC_save     = photon_counter.newChannel(2, "Counter Save",     system='CavPrb', steady_state_value=0,   max_value=1,    graph=0)
PC_max_rate = photon_counter.newChannel(3, "Counter Max Rate", system='CavPrb', steady_state_value=20,  max_value=20,   graph=0)

#Photon timer
PT_save = photon_timer.newChannel(0, "Photon Timer Save", system='CavPrb', steady_state_value=0, max_value=1, graph=0)
#=====================================End Channel Definitions=======================================

#====================================Slave Channel Definitions======================================
#Any channel appears in this section should NEVER be given any value in any sequence file.
#The value of these channels will be assigned automatically later.
#The properties of the channel (id, name, steady_state_value, max_value, and graph) should be set in this section

# Chemeleon camera
CAMERA = cam.newChannel(0, "Camera", steady_state_value=1, max_value=1, graph=0, ctype='Slave', master_chan=Cam_trig)

# Photon counter
PhotonCounter = photon_counter.newChannel(0, "Photon Counter", steady_state_value=0, max_value=1, graph=0, ctype='Slave', master_chan=SPCM_ttl)
# Photon timer
PhotonTimer = photon_timer.newChannel(0, "Photon Timer", steady_state_value=0, max_value=1, graph=0, ctype='Slave', master_chan=SPCM_ttl)
