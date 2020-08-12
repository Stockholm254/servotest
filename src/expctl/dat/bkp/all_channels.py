#!/usr/bin/python
# -*- coding: utf-8 -*-

from sequencer.sequence import Sequence # Sequence and Channel object
from config.config import * # All IP and port configuration
from utilities.util import * # Print error function
import transformations as tran # Channel value transformation function

###################################################################################################
###    ALL CHANNELS/SEQS ARE DEFINED HERE, AS ARE FEW ROUTINES THAT CRUNCH THEM (@ bottom)      ###
###################################################################################################

# ALL IP ADDRESS AND PORT NUMBERS ARE DEFINED IN /config/config.py

#=======================================Sequence Definitions=========================================
#FIRST DECLARE ALL SEQUENCES into the all_sequences array, and then give them names for easier assignment!
all_sequences = ([
  Sequence("Digital sequence",        host=IP_RYDNUGGET, port=PORT_DIGITAL,  max_channels=32, graph=1, seq_type="MASTER"),  
  Sequence("Analog sequence",         host=IP_RYDNUGGET, port=PORT_ANALOG,   max_channels=32, graph=1),  
  Sequence("Camera sequence",         host=IP_RYDFRIES,  port=PORT_CAMERA,   max_channels=1 , graph=0),
  Sequence("DDS 1 sequence",          host=IP_RYDNUGGET, port=PORT_DDS1,     max_channels=4 , graph=0),
  Sequence("DDS PDH sequence",        host=IP_RYDNUGGET, port=PORT_DDSPDH,   max_channels=7 , graph=0),
  Sequence("DDS 2 sequence",          host=IP_RYDNUGGET, port=PORT_DDS2,     max_channels=4 , graph=0),
  Sequence("Photon Timer sequence",   host=IP_RYDNUGGET, port=PORT_PTIMER,   max_channels=2 , graph=0),
  Sequence("Photon Counter sequence", host=IP_RYDNUGGET, port=PORT_PCOUNTER, max_channels=4 , graph=0),
  ])

digital_seq1, analog_seq1, cam, dds_1, dds_pdh, dds_2, photon_timer, photon_counter = all_sequences # WE DO IT IN THIS ORDER SO THAT ONE CANNOT GET AWAY WITH CREATING A NAMED SEQUENCE WHICH IS NOT IN THE ARRAY OF ALL SEQUENCES!!

#=======================================Channel Definitions=========================================
# NEXT ADD ALL OF THE CHANNELS TO THEM! ##Note: the name in quotes must have 1 < length < 31

# Digital card
MOT0_ttl      = digital_seq1.newChannel(0,  "MOT TTL",          system='MOT',     steady_state_value=1, max_value=1, graph=1)
REP0_ttl      = digital_seq1.newChannel(1,  "REP TTL",          system='MOT',     steady_state_value=1, max_value=1, graph=1)
Scope_trig    = digital_seq1.newChannel(2,  "Scope Trig",       system='Debug',   steady_state_value=0, max_value=1, graph=1)
Cam_trig      = digital_seq1.newChannel(3,  "Came Trig",        system='IMG',     steady_state_value=1, max_value=1, graph=1)
DDS_trig      = digital_seq1.newChannel(4,  "DDS FPGA Trig",    system='Debug',   steady_state_value=0, max_value=1, graph=1)
Nufern2_ttl   = digital_seq1.newChannel(5,  "OP TTL",           system='CavPrb',  steady_state_value=0, max_value=1, graph=1, transform_t=tran.CavPrbAOMDelay)
LAT1_ttl      = digital_seq1.newChannel(6,  "Lat Hori TTL",     system='LAT',     steady_state_value=1, max_value=1, graph=1)
LAT2_ttl      = digital_seq1.newChannel(7,  "Lat Vert TTL",     system='LAT',     steady_state_value=1, max_value=1, graph=1)
Sacher2_ttl   = digital_seq1.newChannel(8,  "ELAT_TTL",         system='dRSC',    steady_state_value=0, max_value=1, graph=1, transform_t=tran.SliceAOMDelay)
LAT_mod_trig  = digital_seq1.newChannel(9,  "Lat Int Mod Trig", system='LAT',     steady_state_value=0, max_value=1, graph=1)
LAT0_ttl      = digital_seq1.newChannel(10, "Lat Main TTL",     system='LAT',     steady_state_value=0, max_value=1, graph=1, transform_t=tran.LatAOMDelay)
MOT1_ttl      = digital_seq1.newChannel(11, "MOTdRSC Pump TTL", system='dRSC',    steady_state_value=0, max_value=1, graph=1)
Blue_ttl      = digital_seq1.newChannel(12, "Blue TTL",         system='Blue',    steady_state_value=0, max_value=1, graph=1, transform_t=tran.BlueAOMDelay)
ODT2_ttl      = digital_seq1.newChannel(13, "Cav DTrap TTL",    system='CavPrb',  steady_state_value=0, max_value=1, graph=1, transform_t=tran.BlueAOMDelay)
Nufern0_ttl   = digital_seq1.newChannel(14, "Cav Prb TTL",      system='CavPrb',  steady_state_value=0, max_value=1, graph=1, transform_t=tran.CavPrbAOMDelay)
EITPrbEOM2_ttl= digital_seq1.newChannel(15, "CavPrbEOM2 TTL",   system='CavPrb',  steady_state_value=0, max_value=1, graph=1)
SPCM_ttl      = digital_seq1.newChannel(17, "SPCM Gate TTL",    system='CavPrb',  steady_state_value=0, max_value=1, graph=1)
dRSC_LAT2_ttl = digital_seq1.newChannel(18, "MOTdRSC Lat TTL",  system='dRSC',    steady_state_value=0, max_value=1, graph=1)
D1Laser1_ttl  = digital_seq1.newChannel(20, "dRSC Pump TTL",    system='dRSC',    steady_state_value=1, max_value=1, graph=1)
EITPrbEOM_ttl = digital_seq1.newChannel(22, "Cav Prb EOM TTL",  system='CavPrb',  steady_state_value=1, max_value=1, graph=1)
AUX_ttl       = digital_seq1.newChannel(23, "Auxiliary TTL",    system='dRSC',    steady_state_value=0, max_value=1, graph=1)
Nufern1_ttl   = digital_seq1.newChannel(24, "Vert Img Prb TTL", system='IMG',     steady_state_value=1, max_value=1, graph=1, transform_t=tran.TopImgAOMDelay)
MOT3_ttl      = digital_seq1.newChannel(25, "Upper Blast TTL",  system='Slice',   steady_state_value=1, max_value=1, graph=1)
MOT2_ttl      = digital_seq1.newChannel(26, "Global DEP TTL",   system='Slice',   steady_state_value=0, max_value=1, graph=1, transform_t=tran.MOTPrbDelay)
dRSC_LAT_ttl  = digital_seq1.newChannel(27, "dRSC Lat TTL",     system='dRSC',    steady_state_value=0, max_value=1, graph=1)
Digi_test     = digital_seq1.newChannel(31, "Digital Test",     system='Debug',   steady_state_value=0, max_value=1, graph=1)

# Analog card
MOT0_pwr       = analog_seq1.newChannel(0,  "MOT Pwr",         system='MOT',     steady_state_value=5.0,   max_value=5.0,  graph=1)
REP0_pwr       = analog_seq1.newChannel(1,  "REP Pwr",         system='MOT',     steady_state_value=3.801, max_value=5.0,  graph=1)
MOTCoil        = analog_seq1.newChannel(2,  "MOT Coil",        system='MOT',     steady_state_value=5.0,   max_value=5.0,  graph=1)
BiasX          = analog_seq1.newChannel(3,  "Bias X",          system='MOT',     steady_state_value=0.04,  max_value=5.0,  graph=1, transform_v=tran.BiasXGauss)
BiasY          = analog_seq1.newChannel(4,  "Bias Y",          system='MOT',     steady_state_value=0.66,  max_value=3.0,  graph=1, transform_v=tran.BiasYGauss)
BiasZ          = analog_seq1.newChannel(5,  "Bias Z",          system='MOT',     steady_state_value=-0.56, max_value=3.0,  graph=1, transform_v=tran.BiasZGauss)
LAT1_pwr       = analog_seq1.newChannel(6,  "Lat Hori Pwr",    system='LAT',     steady_state_value=4.8,   max_value=5.0,  graph=1)
LAT2_pwr       = analog_seq1.newChannel(7,  "Lat Vert Pwr",    system='LAT',     steady_state_value=4.8,   max_value=5.0,  graph=1)
Sacher2_pwr    = analog_seq1.newChannel(8,  "ELAT_Pwr",        system='dRSC',    steady_state_value=3.8,   max_value=5.0,  graph=1)
LAT0_pwr       = analog_seq1.newChannel(9,  "Lat Main Pwr",    system='LAT',     steady_state_value=4.7,   max_value=5.0,  graph=1)
Blue_pwr       = analog_seq1.newChannel(10, "Blue Pwr",        system='Blue',    steady_state_value=4.25,  max_value=5.0,  graph=1)
MOT3_pwr       = analog_seq1.newChannel(11, "Upper Blast Pwr", system='Slice',   steady_state_value=4.25,  max_value=5.0,  graph=1)
ODT2_pwr       = analog_seq1.newChannel(12, "Cav DTrap Pwr",   system='CavPrb',  steady_state_value=4.80,  max_value=5.0,  graph=1)
Nufern2_pwr    = analog_seq1.newChannel(13, "OP Pwr",          system='CavPrb',  steady_state_value=0.0,   max_value=5.0,  graph=1)
Nufern0_pwr    = analog_seq1.newChannel(14, "Cav Prb Pwr",     system='CavPrb',  steady_state_value=0.0,   max_value=5.0,  graph=1)
CavPrbEOM_pwr  = analog_seq1.newChannel(15, "Prb F EOM Pwr",   system='CavPrb',  steady_state_value=5.0,   max_value=5.0,  graph=1)
CavPrbEOMB_pwr = analog_seq1.newChannel(16, "Prb B EOM Pwr",   system='CavPrb',  steady_state_value=5.0,   max_value=5.0,  graph=1)
D1Laser1_pwr   = analog_seq1.newChannel(17, "dRSC Pump Pwr",   system='dRSC',    steady_state_value=4.6,   max_value=5.0,  graph=1)
dRSC_LAT2_pwr  = analog_seq1.newChannel(18, "MOTdRSC Lat Pwr", system='dRSC',    steady_state_value=5.0,   max_value=5.0,  graph=1)
MOT1_pwr       = analog_seq1.newChannel(19, "MOTdRSC Pump Pwr",system='dRSC',    steady_state_value=5.0,   max_value=5.0,  graph=1)
MOT2_pwr       = analog_seq1.newChannel(20, "Global DEP Pwr",  system='Slice',   steady_state_value=5.0,   max_value=5.0,  graph=1)
EF1            = analog_seq1.newChannel(21, "EFilter 1",       system='EField',  steady_state_value=0.0,   max_value=10.0, graph=1, transform_v=tran.ElectrodeGain1)
EF2            = analog_seq1.newChannel(22, "EFilter 2",       system='EField',  steady_state_value=0.0,   max_value=10.0, graph=1, transform_v=tran.ElectrodeGain2)
EF3            = analog_seq1.newChannel(23, "EFilter 3",       system='EField',  steady_state_value=0.0,   max_value=10.0, graph=1, transform_v=tran.ElectrodeGain3)
EF4            = analog_seq1.newChannel(24, "EFilter 4",       system='EField',  steady_state_value=0.0,   max_value=10.0, graph=1, transform_v=tran.ElectrodeGain4)
EF5            = analog_seq1.newChannel(25, "EFilter 5",       system='EField',  steady_state_value=0.0,   max_value=10.0, graph=1, transform_v=tran.ElectrodeGain5)
EF6            = analog_seq1.newChannel(26, "EFilter 6",       system='EField',  steady_state_value=0.0,   max_value=10.0, graph=1, transform_v=tran.ElectrodeGain6)
EF7            = analog_seq1.newChannel(27, "EFilter 7",       system='EField',  steady_state_value=0.0,   max_value=10.0, graph=1, transform_v=tran.ElectrodeGain7)
EF8            = analog_seq1.newChannel(28, "EFilter 8",       system='EField',  steady_state_value=0.0,   max_value=10.0, graph=1, transform_v=tran.ElectrodeGain8)
EF9            = analog_seq1.newChannel(29, "EFilter 9",       system='EField',  steady_state_value=0.0,   max_value=10.0, graph=1, transform_v=tran.ElectrodeGain9)
dRSC_LAT_pwr   = analog_seq1.newChannel(30, "dRSC LAT Pwr",    system='dRSC',  steady_state_value=0.0,   max_value=10.0, graph=1)
Anal_test      = analog_seq1.newChannel(31, "Analog Test",     system='Debug',   steady_state_value=0.0,   max_value=5.0,  graph=1)


# DDS box 1 (MOT, REP, LAT)
DDS_REP   = dds_1.newChannel(1, "REP Lock Freq", system='MOT', steady_state_value=96.6,  max_value=2100, graph=1, transform_v=tran.MHzToHz)
# DDS_MOT   = dds_1.newChannel(1, "MOT Lock Freq", system='MOT', steady_state_value=490.0, max_value=2100, graph=1, transform_v=tran.MHzToHz)
# DDS_LAT1  = dds_1.newChannel(2, "Lat Hori Freq", system='LAT', steady_state_value=80.0,  max_value=2100, graph=1, transform_v=tran.MHzToHz)
DDS_OptPump1   = dds_1.newChannel(0, "OptPump AOM1 Freq", system='MOT', steady_state_value=490.0, max_value=2100, graph=1, transform_v=tran.MHzToHz)
DDS_LAT1  = dds_1.newChannel(3, "Lat Hori Freq", system='LAT', steady_state_value=80.0,  max_value=2100, graph=1, transform_v=tran.MHzToHz) ### CHANNEL 1 GOES NUTS ###
DDS_BlueCavAOD  = dds_1.newChannel(2, "Blue Cav Lock AOD", system='Blue', steady_state_value=220.0,  max_value=2100, graph=1, transform_v=tran.MHzToHz)


# DDS PDH box (Ultra-stable cavity PDH locking, cavity probe)
DDS_PDH1560   = dds_pdh.newChannel(0, "PDH 1560",         system='CavPrb', steady_state_value=156.50, max_value=2100, graph=1, transform_v=tran.MHzToHz)
DDS_PDH960    = dds_pdh.newChannel(1, "PDH 960",          system='Blue',   steady_state_value=641.65, max_value=2100, graph=1, transform_v=tran.MHzToHz)
DDS_PDH780    = dds_pdh.newChannel(2, "PDH 780",          system='CavPrb', steady_state_value=470.00, max_value=2100, graph=1, transform_v=tran.MHzToHz)
DDS_CavPrbEOM = dds_pdh.newChannel(3, "Cav Prb EOM Freq", system='CavPrb', steady_state_value=322.14, max_value=3000, graph=1, transform_v=tran.MHzToHz)
DDS_HalfRng   = dds_pdh.newChannel(5, "PDH Half Range",   system='Debug',  steady_state_value=5.0,    max_value=100,  graph=0, transform_v=tran.MHzToHz)

# DDS box 2 (Cavity probe double pass AOM, optical pumping AOM)
DDS_CavPrbAOM = dds_2.newChannel(0, "Cav Prb AOM Freq",    system='CavPrb',  steady_state_value=500,  max_value=2100, graph=1, transform_v=tran.MHzToHz)
DDS_chan1     = dds_2.newChannel(1, "DDS Box 2 channel 2", system='Debug',   steady_state_value=100,  max_value=2100, graph=1, transform_v=tran.MHzToHz)
DDS_MOT  = dds_2.newChannel(2, "MOT Lock Freq",            system='MOT', steady_state_value=490.0, max_value=2100, graph=1, transform_v=tran.MHzToHz)
# DDS_OptPump1  = dds_2.newChannel(2, "OptPump AOM1 Freq",   system='OptPump', steady_state_value=80.0, max_value=2100, graph=1, transform_v=tran.MHzToHz)
DDS2_3  = dds_2.newChannel(3, "DDS Box 2 Ch 3",            system='CavPrb', steady_state_value=80.0, max_value=2100, graph=1, transform_v=tran.MHzToHz)


# Photon counter
PC_bin_num  = photon_counter.newChannel(1, "Counter Bin Num",  system='CavPrb', steady_state_value=100, max_value=1024, graph=0)
PC_save     = photon_counter.newChannel(2, "Counter Save",     system='CavPrb', steady_state_value=0,   max_value=1,    graph=0)
PC_max_rate = photon_counter.newChannel(3, "Counter Max Rate", system='CavPrb', steady_state_value=20,  max_value=20,   graph=0)

#Photon timer
PT_save = photon_timer.newChannel(0, "Photon Timer Save", system='CavPrb', steady_state_value=0, max_value=1, graph=0)
#=====================================End Channel Definitions=======================================

#====================================Slave Channel Definitions======================================
# Any channel appears in this section should NEVER be given any value in any sequence file.
# The value of these channels will be assigned automatically later.
# The properties of the channel (id, name, steady_state_value, max_value, and graph) should be set in this section

# Chemeleon camera
CAMERA = cam.newChannel(0, "Camera", steady_state_value=1, max_value=1, graph=0, ctype='Slave', master=Cam_trig)
# Photon counter
PhotonCounter = photon_counter.newChannel(0, "Photon Counter", steady_state_value=0, max_value=1, graph=0, ctype='Slave', master=Scope_trig)
# Photon timer
PhotonTimer = photon_timer.newChannel(1, "Photon Timer", steady_state_value=0, max_value=1, graph=0, ctype='Slave', master=Scope_trig)



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
