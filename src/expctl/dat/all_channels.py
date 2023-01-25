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
  Sequence("Digital sequence",          host=IP_RYDNUGGET,   port=PORT_DIGITAL,   max_channels=32, graph=1, seq_type="MASTER"),  
  Sequence("Analog sequence",           host=IP_RYDNUGGET,   port=PORT_ANALOG,    max_channels=32, graph=1),
  Sequence("Camera sequence",           host=IP_RYDFRIES,    port=PORT_CAMERA,    max_channels=4 , graph=0),
  Sequence("Camera 2 sequence",         host=IP_RYDFRIES,    port=PORT_CAMERA2,   max_channels=4 , graph=0),
  Sequence("DDS 1 sequence",            host=IP_RYDNUGGET,   port=PORT_DDS1,      max_channels=4 , graph=0),
  Sequence("DDS PDH sequence",          host=IP_RYDNUGGET,   port=PORT_DDSPDH,    max_channels=7 , graph=0),
  Sequence("DDS 2 sequence",            host=IP_RYDNUGGET,   port=PORT_DDS2,      max_channels=4 , graph=0),
  Sequence("Photon Timer sequence",     host=IP_RYDNUGGET,   port=PORT_PTIMER,    max_channels=2 , graph=0),
  Sequence("Photon Timer 2 sequence",   host=IP_RYDNUGGET,   port=PORT_PTIMER2,   max_channels=2 , graph=0),
  Sequence("Photon Timer 3 sequence",   host=IP_RYDNUGGET,   port=PORT_PTIMER3,   max_channels=2 , graph=0),
  Sequence("Scope ADC 1 sequence",      host=IP_RYDNUGGET,   port=PORT_ADC,       max_channels=5 , graph=0),
  Sequence("Photon Counter sequence",   host=IP_RPCOUNTER,   port=PORT_PCOUNTER,  max_channels=5 , graph=0),
  Sequence("LabBrick 1 sequence",       host=IP_RYDFRIES,    port=PORT_LB1,       max_channels=3 , graph=0),
  Sequence("LabBrick 2 sequence",       host=IP_RYDFRIES,    port=PORT_LB2,       max_channels=3 , graph=0),
  Sequence("LabBrick 3 sequence",       host=IP_RYDFRIES,    port=PORT_LB3,       max_channels=3 , graph=0),
  Sequence("LabBrick 4 sequence",       host=IP_RYDFRIES,    port=PORT_LB4,       max_channels=3 , graph=0),
  Sequence("ADF435X sequence",          host=IP_RYDFRIES,    port=PORT_AD1,       max_channels=3 , graph=0),
  Sequence("RFSOC 1 sequence",          host=IP_RFSOC_1,     port=PORT_RFSOC,     max_channels=8 , graph=0),
  Sequence("RP DDS Transport sequence", host=IP_RPTR,        port=PORT_RPTR,      max_channels=2 , graph=0),
  Sequence("Kinesis Lambda 2",          host=IP_RYDFRIES,    port=PORT_KINESIS_2, max_channels=1 , graph=0),
  Sequence("Kinesis Lambda 4",          host=IP_RYDFRIES,    port=PORT_KINESIS_4, max_channels=1 , graph=0),
  Sequence("Attenuator sequence",       host=IP_RYDFRIES,    port=PORT_ATT,       max_channels=1 , graph=0),
  Sequence("DMD sequence",              host='192.168.1.34', port=PORT_DMD,       max_channels=10, graph=0),
  Sequence("SmarAct sequence",          host='192.168.1.34', port=PORT_SMARACT,   max_channels=2 , graph=0)
  ])

digital_seq1, analog_seq1, cam, cam2, dds_1, dds_pdh, dds_2, photon_timer, photon_timer_2, photon_timer_3, adc_1, photon_counter, lb_1, lb_2, lb_3, lb_4, ad_1, rfsoc_1, rp_ddds_1, kinesis_2, kinesis_4, atten_1, dmd, smaract = all_sequences # WE DO IT IN THIS ORDER SO THAT ONE CANNOT GET AWAY WITH CREATING A NAMED SEQUENCE WHICH IS NOT IN THE ARRAY OF ALL SEQUENCES!!

#=======================================Channel Definitions=========================================
# NEXT ADD ALL OF THE CHANNELS TO THEM! ##Note: the name in quotes must have 1 < length < 31

# Digital card
MOT0_ttl      = digital_seq1.newChannel(0,  "MOT TTL",          system='MOT',     steady_state_value=1, max_value=1, graph=1)
REP0_ttl      = digital_seq1.newChannel(1,  "REP TTL",          system='MOT',     steady_state_value=1, max_value=1, graph=1)
Scope_trig    = digital_seq1.newChannel(2,  "Scope Trig",       system='Debug',   steady_state_value=0, max_value=1, graph=1)
Cam_trig      = digital_seq1.newChannel(3,  "Camera Trig",        system='IMG',     steady_state_value=1, max_value=1, graph=1)
DDS_trig      = digital_seq1.newChannel(4,  "DDS FPGA Trig",    system='Debug',   steady_state_value=0, max_value=1, graph=1, transform_v=tran.DigitalNot) #9/15/2020 added inverting line driver
UV_ttl        = digital_seq1.newChannel(5,  "Ultraviolet TTL",  system='EField',  steady_state_value=0, max_value=1, graph=1, transform_t=tran.CavPrbAOMDelay)
LAT1_ttl      = digital_seq1.newChannel(6,  "Lat Hori TTL",     system='LAT',     steady_state_value=1, max_value=1, graph=1)
LAT2_ttl      = digital_seq1.newChannel(7,  "Lat Vert TTL",     system='LAT',     steady_state_value=1, max_value=1, graph=1)
Sacher2_ttl   = digital_seq1.newChannel(8,  "ELAT_TTL",         system='dRSC',    steady_state_value=0, max_value=1, graph=1, transform_t=tran.SliceAOMDelay)
V1_ttl        = digital_seq1.newChannel(9,  "V1 TTL",           system='EField',  steady_state_value=0, max_value=1, graph=1)
LAT0_ttl      = digital_seq1.newChannel(10, "Lat Main TTL",     system='LAT',     steady_state_value=0, max_value=1, graph=1, transform_t=tran.LatAOMDelay)
MOT1_ttl      = digital_seq1.newChannel(11, "MOTdRSC Pump TTL", system='dRSC',    steady_state_value=0, max_value=1, graph=1)
Blue_ttl      = digital_seq1.newChannel(12, "Blue TTL",         system='Blue',    steady_state_value=0, max_value=1, graph=1, transform_t=tran.BlueAOMDelay)
ODT2_ttl      = digital_seq1.newChannel(13, "Cav DTrap TTL",    system='CavPrb',  steady_state_value=0, max_value=1, graph=1, transform_t=tran.LatAOMDelay)
Nufern0_ttl   = digital_seq1.newChannel(14, "Cav Prb TTL",      system='CavPrb',  steady_state_value=0, max_value=1, graph=1, transform_t=tran.CavPrbAOMDelay)
PRB_pwr_ttl   = digital_seq1.newChannel(15, "Cav Prb Power TTL",system='CavPrb',  steady_state_value=0, max_value=1, graph=1) #, transform_t=tran.CavPrbAOMDelay
Timer_trig    = digital_seq1.newChannel(16, "Timer Trig",       system='Debug',   steady_state_value=0, max_value=1, graph=1, ctype='Slave', master=Scope_trig)
SPCM_ttl      = digital_seq1.newChannel(17, "SPCM Gate TTL",    system='CavPrb',  steady_state_value=0, max_value=1, graph=1, transform_v=tran.DigitalNot)
dRSC_LAT2_ttl = digital_seq1.newChannel(18, "MOTdRSC Lat TTL",  system='dRSC',    steady_state_value=0, max_value=1, graph=1)
GATE_ttl      = digital_seq1.newChannel(19, "Timer Gate TTL",   system='CavPrb',  steady_state_value=0, max_value=1, graph=1)
D1Laser1_ttl  = digital_seq1.newChannel(20, "dRSC Pump TTL",    system='dRSC',    steady_state_value=1, max_value=1, graph=1, transform_t=tran.OPREPAOMDelay)
AUX2_ttl      = digital_seq1.newChannel(21, "Auxiliary 2 TTL",  system='dRSC',    steady_state_value=0, max_value=1, graph=1)
EITPrbEOM_ttl = digital_seq1.newChannel(22, "Cav Prb EOM TTL",  system='CavPrb',  steady_state_value=1, max_value=1, graph=1)
AUX_ttl       = digital_seq1.newChannel(23, "Auxiliary TTL",    system='dRSC',    steady_state_value=0, max_value=1, graph=1)
Nufern1_ttl   = digital_seq1.newChannel(24, "Vert Img Prb TTL", system='IMG',     steady_state_value=1, max_value=1, graph=1, transform_t=tran.TopImgAOMDelay)
Shut_HLAT_ttl = digital_seq1.newChannel(25, "HLAT shutter",      system='dRSC', steady_state_value=1, max_value=1, graph=1)
MOT2_ttl      = digital_seq1.newChannel(26, "Global DEP TTL",   system='Slice',   steady_state_value=0, max_value=1, graph=1, transform_t=tran.MOTPrbDelay)
dRSC_LAT_ttl  = digital_seq1.newChannel(27, "dRSC Lat TTL",     system='dRSC',    steady_state_value=0, max_value=1, graph=1)
MWaves_ttl    = digital_seq1.newChannel(29, "MWave switch TTL", system='MWaves',  steady_state_value=0, max_value=1, graph=1)
dRSC_OP_freq_ttl  = digital_seq1.newChannel(30, "dRSC OP RF Source TTL",  system='dRSC',   steady_state_value=0, max_value=1, graph=1)
Shut_MOT_ttl  = digital_seq1.newChannel(31, "MOT shutter",  system='Debug',   steady_state_value=0, max_value=1, graph=1, transform_t = tran.ShutterDelay)


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
EDFA_1529_pwr  = analog_seq1.newChannel(11, "Floquet Pwr",     system='Floquet', steady_state_value=4.25,  max_value=5.0,  graph=1)
ODT2_pwr       = analog_seq1.newChannel(12, "Cav DTrap Pwr",   system='CavPrb',  steady_state_value=4.80,  max_value=5.0,  graph=1)
PSC_outOff     = analog_seq1.newChannel(13, "PSC Output Offset",system='CavPrb', steady_state_value=0.0,   max_value=5.0,  graph=1)
Nufern0_pwr    = analog_seq1.newChannel(14, "Cav Prb Pwr",     system='CavPrb',  steady_state_value=0.0,   max_value=5.0,  graph=1)
CavPrbEOM_pwr  = analog_seq1.newChannel(15, "Prb F EOM Pwr",   system='CavPrb',  steady_state_value=2.0,   max_value=10.0,  graph=1)
VImg_pwr       = analog_seq1.newChannel(16, "Vert Img Pwr",    system='IMG',     steady_state_value=5.0,   max_value=5.0,  graph=1)
D1Laser1_pwr   = analog_seq1.newChannel(17, "dRSC Pump Pwr",   system='dRSC',    steady_state_value=4.6,   max_value=5.0,  graph=1)
dRSC_LAT2_pwr  = analog_seq1.newChannel(18, "MOTdRSC Lat Pwr", system='dRSC',    steady_state_value=5.0,   max_value=5.0,  graph=1)
MOT1_pwr       = analog_seq1.newChannel(19, "MOTdRSC Pump Pwr",system='dRSC',    steady_state_value=5.0,   max_value=5.0,  graph=1)
MOT2_pwr       = analog_seq1.newChannel(20, "Global DEP Pwr",  system='Slice',   steady_state_value=5.0,   max_value=5.0,  graph=1)
EF1            = analog_seq1.newChannel(21, "EFilter 1",       system='EField',  steady_state_value=0.0,   max_value=48.0, graph=0, transform_v=tran.ElectrodeGain1)
EF2            = analog_seq1.newChannel(22, "EFilter 2",       system='EField',  steady_state_value=0.0,   max_value=48.0, graph=0, transform_v=tran.ElectrodeGain2)
EF3            = analog_seq1.newChannel(23, "EFilter 3",       system='EField',  steady_state_value=0.0,   max_value=48.0, graph=0, transform_v=tran.ElectrodeGain3)
EF4            = analog_seq1.newChannel(24, "EFilter 4",       system='EField',  steady_state_value=0.0,   max_value=48.0, graph=0, transform_v=tran.ElectrodeGain4)
EF5            = analog_seq1.newChannel(25, "EFilter 5",       system='EField',  steady_state_value=0.0,   max_value=48.0, graph=0, transform_v=tran.ElectrodeGain5)
EF6            = analog_seq1.newChannel(26, "EFilter 6",       system='EField',  steady_state_value=0.0,   max_value=48.0, graph=0, transform_v=tran.ElectrodeGain6)
EF7            = analog_seq1.newChannel(27, "EFilter 7",       system='EField',  steady_state_value=0.0,   max_value=48.0, graph=0, transform_v=tran.ElectrodeGain7)
EF8            = analog_seq1.newChannel(28, "EFilter 8",       system='EField',  steady_state_value=0.0,   max_value=48.0, graph=0, transform_v=tran.ElectrodeGain8)
EF9            = analog_seq1.newChannel(29, "EFilter 9",       system='EField',  steady_state_value=0.0,   max_value=48.0, graph=0, transform_v=tran.ElectrodeGain9)
dRSC_LAT_pwr   = analog_seq1.newChannel(30, "dRSC LAT Pwr",    system='dRSC',    steady_state_value=0.0,   max_value=10.0, graph=1)
UV_pwr         = analog_seq1.newChannel(31, "Ultraviolet pwr", system='EField',  steady_state_value=0.0,   max_value=5.0,  graph=1)


# DDS box 1 (MOT, REP, LAT)
DDS_REP   = dds_1.newChannel(1, "REP Lock Freq", system='MOT', steady_state_value=96.6,  max_value=2100, graph=1, transform_v=tran.MHzToHz)
# DDS_MOT   = dds_1.newChannel(1, "MOT Lock Freq", system='MOT', steady_state_value=490.0, max_value=2100, graph=1, transform_v=tran.MHzToHz)
# DDS_LAT1  = dds_1.newChannel(2, "Lat Hori Freq", system='LAT', steady_state_value=80.0,  max_value=2100, graph=1, transform_v=tran.MHzToHz)
DDS_OptPump1   = dds_1.newChannel(0, "OptPump AOM1 Freq", system='MOT', steady_state_value=490.0, max_value=2100, graph=1, transform_v=tran.MHzToHz)
DDS_LAT1  = dds_1.newChannel(3, "Lat Hori Freq", system='LAT', steady_state_value=80.0,  max_value=2100, graph=1, transform_v=tran.MHzToHz) ### CHANNEL 1 GOES NUTS ###
DDS1_2  = dds_1.newChannel(2, "Blue Cav 960 Offs Lock", system='CavPrb', steady_state_value=220.0,  max_value=2100, graph=1, transform_v=tran.MHzToHz)


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
DDS2_3  = dds_2.newChannel(3, "Mode Sorter 1 Freq",    system='CavPrb', steady_state_value=300.0, max_value=2100, graph=1, transform_v=tran.MHzToHz)

# ADC scope
ADC_scope_save = adc_1.newChannel(1, "ADC Save",     system='CavPrb', steady_state_value=0,   max_value=1,    graph=0)
ADC_ch_save  = adc_1.newChannel(2, "ADC Channel",  system='CavPrb', steady_state_value=1,   max_value=2,    graph=0)

# Photon counter
PC_bin_num  = photon_counter.newChannel(1, "Counter Bin Num",  system='CavPrb', steady_state_value=100, max_value=32767, graph=0)
PC_save     = photon_counter.newChannel(2, "Counter Save",     system='CavPrb', steady_state_value=0,   max_value=1,    graph=0)
PC_max_rate = photon_counter.newChannel(3, "Counter Max Rate", system='CavPrb', steady_state_value=20,  max_value=20,   graph=0)
PC_n_channels = photon_counter.newChannel(4, "Counter N Channels", system='CavPrb', steady_state_value=1,   max_value=2,    graph=0)

#Photon timer
PT_save = photon_timer.newChannel(0, "Photon Timer Save", system='CavPrb', steady_state_value=0, max_value=1, graph=0)


# Lab Brick 1
# note Freq is in 10*Hz
LB1_freq  = lb_1.newChannel(0, "Lab Brick 1 Freq",  system='MWaves', steady_state_value=7500, max_value=10000, graph=0) # transformation handled in server
LB1_pow   = lb_1.newChannel(1, "Lab Brick 1 Power", system='MWaves', steady_state_value=0,   max_value=40,    graph=0) # transformation handled in server
LB1_ttl   = lb_1.newChannel(2, "Lab Brick 1 TTL",   system='MWaves', steady_state_value=1,   max_value=1,   graph=0) # transformation handled in server

# Lab Brick 2
# note Freq is in 10*Hz
# LB2_freq  = lb_2.newChannel(0, "Lab Brick 2 Freq",  system='CavPrb', steady_state_value=8500, max_value=12000, graph=0) # transformation handled in server
# LB2_pow   = lb_2.newChannel(1, "Lab Brick 2 Power", system='CavPrb', steady_state_value=0,   max_value=40,    graph=0) # transformation handled in server
# LB2_ttl   = lb_2.newChannel(2, "Lab Brick 2 TTL",   system='CavPrb', steady_state_value=1,   max_value=1,   graph=0) # transformation handled in server
LB2_freq  = lb_2.newChannel(0, "Lab Brick 2 Freq",  system='CavPrb', steady_state_value=10000, max_value=20000, graph=0) # transformation handled in server
LB2_pow   = lb_2.newChannel(1, "Lab Brick 2 Power", system='CavPrb', steady_state_value=0,   max_value=40,    graph=0) # transformation handled in server
LB2_ttl   = lb_2.newChannel(2, "Lab Brick 2 TTL",   system='CavPrb', steady_state_value=1,   max_value=1,   graph=0) # transformation handled in server

# Lab Brick 1
# note Freq is in 10*Hz
LB3_freq  = lb_3.newChannel(0, "Lab Brick 3 Freq",  system='CavPrb', steady_state_value=8500, max_value=10000, graph=0) # transformation handled in server
LB3_pow   = lb_3.newChannel(1, "Lab Brick 3 Power", system='CavPrb', steady_state_value=0,   max_value=40,    graph=0) # transformation handled in server
LB3_ttl   = lb_3.newChannel(2, "Lab Brick 3 TTL",   system='CavPrb', steady_state_value=1,   max_value=1,   graph=0) # transformation handled in server

# Lab Brick 4 for optical repumping
# note Freq is in 10*Hz
LB4_freq  = lb_4.newChannel(0, "Lab Brick 4 Freq",  system='dRSC', steady_state_value=8500, max_value=10000, graph=0) # transformation handled in server
LB4_pow   = lb_4.newChannel(1, "Lab Brick 4 Power", system='dRSC', steady_state_value=0,   max_value=40,    graph=0) # transformation handled in server
LB4_ttl   = lb_4.newChannel(2, "Lab Brick 4 TTL",   system='dRSC', steady_state_value=1,   max_value=1,   graph=0) # transformation handled in server

# Analog Devices ADF435X 1
# note Freq is in MHz
AD1_freq = ad_1.newChannel(0, "Microwave Freq",   system='MWaves', steady_state_value=1000, max_value=4400, graph=0)
AD1_pow  = ad_1.newChannel(1, "Microwave Power",  system='MWaves', steady_state_value=2, max_value=5, graph=0)
AD1_ttl  = ad_1.newChannel(2, "Microwave TTL",    system='MWaves', steady_state_value=0, max_value=1, graph=0)

#RFSOC 1 DDS Box
#RFSOC1_0 = rfsoc_1.newChannel(0, "RFSOC 1 Chan 0",   system='CavPrb', steady_state_value=80, max_value=3200, graph=0) # HF
#RFSOC1_1 = rfsoc_1.newChannel(1, "RFSOC 1 Chan 1",   system='CavPrb', steady_state_value=80, max_value=3200, graph=0)
RFSOC1_VertTransAOM = rfsoc_1.newChannel(2, "RFSOC 1 Chan 2",   system='CavPrb', steady_state_value=80, max_value=3200, graph=0)
RFSOC1_HorzTransAOM = rfsoc_1.newChannel(3, "RFSOC 1 Chan 3",   system='CavPrb', steady_state_value=80, max_value=3200, graph=0)
RFSOC1_4 = rfsoc_1.newChannel(4, "RFSOC 1 Chan 4",   system='CavPrb', steady_state_value=2500, max_value=3200, graph=0)
RFSOC1_5 = rfsoc_1.newChannel(5, "RFSOC 1 Chan 5",   system='CavPrb', steady_state_value=2500, max_value=3200, graph=0)
RFSOC1_CavPrbEom = rfsoc_1.newChannel(6, "RFSOC 1 Chan 6",   system='CavPrb', steady_state_value=80, max_value=3200, graph=1)
RFSOC1_784Lock = rfsoc_1.newChannel(7, "RFSOC 1 Chan 7",   system='CavPrb', steady_state_value=80, max_value=3200, graph=0) # LF

#Red Pitaya Transport DDS
RP1_DDS_0 = rp_ddds_1.newChannel(0, "RedPitaya 1 Chan 0",   system='Debug', steady_state_value=10e6, max_value=40e6, graph=0)
RP1_DDS_1 = rp_ddds_1.newChannel(1, "RedPitaya 1 Chan 1",   system='Debug', steady_state_value=10e6, max_value=40e6, graph=0)

# Thorlabs Kinesis waveplate rotational stages
KINESIS_LAM_2 = kinesis_2.newChannel(0, "Lambda 2 angle", system='dRSC', steady_state_value=355.5, max_value=720.0, graph=0)
KINESIS_LAM_4 = kinesis_4.newChannel(0, "Lambda 4 angle", system='dRSC', steady_state_value=355.5, max_value=720.0, graph=0)

#Camera Gain channel
Camera_gain = cam.newChannel(0, "Camera gain", system='IMG', steady_state_value=24.0, max_value=24.0, graph=0)
Camera_save = cam.newChannel(2, "Camera save", system='IMG', steady_state_value=0, max_value=1, graph=0)

# DMD
DMD_waist     = dmd.newChannel(0, "DMD waist x",     system='CavPrb', steady_state_value=30, max_value=3000.0, graph=0)
DMD_defocus   = dmd.newChannel(1, "DMD defocus",     system='CavPrb', steady_state_value=2500, max_value=100000, graph=0)
DMD_l         = dmd.newChannel(2, "DMD L",           system='CavPrb', steady_state_value=0.0, max_value=100.0, graph=0)
DMD_p         = dmd.newChannel(3, "DMD P",           system='CavPrb', steady_state_value=0.0, max_value=30.0, graph=0)
DMD_center_x  = dmd.newChannel(4, "DMD center x",    system='CavPrb', steady_state_value=0, max_value=200, graph=0)
DMD_center_y  = dmd.newChannel(5, "DMD center y",    system='CavPrb', steady_state_value=0, max_value=200, graph=0)
DMD_tilt_x    = dmd.newChannel(6, "DMD tilt x",      system='CavPrb', steady_state_value=0.0, max_value=15.0, graph=0)
DMD_tilt_y    = dmd.newChannel(7, "DMD tilt y",      system='CavPrb', steady_state_value=0.0, max_value=15.0, graph=0)
DMD_phi       = dmd.newChannel(8, "DMD phi",         system='CavPrb', steady_state_value=0.0, max_value=10.0, graph=0)
DMD_eps_phi   = dmd.newChannel(9, "DMD epsilon phi", system='CavPrb', steady_state_value=0.0, max_value=10.0, graph=0)

# Digital attenuator
ATT_1 = atten_1.newChannel(0, "Attenuation",  system='Floquet', steady_state_value=0.0, max_value=31.5, graph=0)

#SmarAct MKS2 controller
# so far only voltage scans are implemented
SMARACT_vx = smaract.newChannel(0, "SmarAct Vx", system='CavPrb', steady_state_value=50, max_value=100.0, graph=0)
SMARACT_vy = smaract.newChannel(1, "SmarAct Vy", system='CavPrb', steady_state_value=50, max_value=100.0, graph=0)
#=====================================End Channel Definitions=======================================

#====================================Slave Channel Definitions======================================
# Any channel appears in this section should NEVER be given any value in any sequence file.
# The value of these channels will be assigned automatically later.
# The properties of the channel (id, name, steady_state_value, max_value, and graph) should be set in this section

# THERE IS A DIGITAL SLAVE CHANNEL, DEFINED ABOVE SO NO ONE THINGS THE CHANNEL IS AVAILABLE
# Chemeleon camera
CAMERA = cam.newChannel(1, "Camera", steady_state_value=1, max_value=1, graph=0, ctype='Slave', master=Cam_trig)
# Photon counter
PhotonCounter = photon_counter.newChannel(0, "Photon Counter", steady_state_value=0, max_value=1, graph=0, ctype='Slave', master=Scope_trig)
# Photon timers
PT_save_2 = photon_timer_2.newChannel(0, "Photon Timer 2 Save", system='CavPrb', steady_state_value=0, max_value=1, graph=0, ctype='Slave', master=PT_save)
PT_save_3 = photon_timer_3.newChannel(0, "Photon Timer 3 Save", system='CavPrb', steady_state_value=0, max_value=1, graph=0, ctype='Slave', master=PT_save)
PhotonTimer = photon_timer.newChannel(1, "Photon Timer", steady_state_value=0, max_value=1, graph=0, ctype='Slave', master=Scope_trig)
PhotonTimer2 =photon_timer_2.newChannel(1, "Photon Timer 2", steady_state_value=0, max_value=1, graph=0, ctype='Slave', master=Scope_trig)
PhotonTimer3 =photon_timer_3.newChannel(1, "Photon Timer 3", steady_state_value=0, max_value=1, graph=0, ctype='Slave', master=Scope_trig)
# Pass Img_horz_pwr also to the camera server for computing the atom number
Camera_Img_horz_pwr =cam.newChannel(3, "Camera Img_horz_pwr", system='IMG', steady_state_value=5.0, max_value=5.0, graph=0, ctype='Slave', master=MOT0_pwr)

#Camera 2
Camera2_gain = cam2.newChannel(0, "Camera gain", system='IMG', steady_state_value=24.0, max_value=24.0, graph=0, ctype='Slave', master=Camera_gain)
Camera2_save = cam2.newChannel(2, "Camera save", system='IMG', steady_state_value=0, max_value=1, graph=0, ctype='Slave', master=Camera_save)
CAMERA2 = cam2.newChannel(1, "Camera", steady_state_value=1, max_value=1, graph=0, ctype='Slave', master=Cam_trig)
Camera_Img_horz_pwr = cam2.newChannel(3, "Camera Img_horz_pwr", system='IMG', steady_state_value=5.0, max_value=5.0, graph=0, ctype='Slave', master=MOT0_pwr)

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
      
  # for jj, _chan in enumerate(_seq.channelsToGraph): # Graph channels
  #   SEQUENCES_TO_GRAPH.append(_chan)
  SEQUENCES_TO_GRAPH.append(_seq)

# Check for the master channel
if len(MasterSequence) < 1:
  printError("No master sequence defined!")
elif len(MasterSequence) > 1:
  printError("Only one master sequence is allowed, "+str(len(MasterSequence))+" are defined!")
elif len(MasterSequence) == 1:
  MasterSequence = MasterSequence[0]
