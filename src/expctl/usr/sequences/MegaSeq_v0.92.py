#!/usr/bin/python
# -*- coding: utf-8 -*-
import copy
from math import floor
from ..dat.Rubidium import groundHF
#### Modifiable Variables ####
# Note: values must be integers or floats.

# Tab:Init
Init_time_ms = 0.0
InitDrop = 0.0
time_FinalWait_ms = 3.0
UV_gap_ttl = 1
# Tab:PDH_freq
MV(PDH1560_freq, min=0.0, max=2500.0, init=309.65, inc=0.1, digits=2)
MV(PDH960_freq, min=0.0, max=2500.0, init=580.6, inc=0.1, digits=2)
MV(PDH780_freq, min=0.0, max=2500.0, init=470.0, inc=0.1, digits=2)
MV(CavPrb_FreqOffset_MHz, min=0.0, max=2500.0, init=209.0, inc=1, digits=2)
MV(PDH785_freq_MHz, min=1.0, max=2000.0, init=550.0, inc=0.1, digits=2)
MV(PDH960_SciCavOffs_MHz, min=0.0, max=3e3, init=324.4, inc=0.02, digits=2)
# Tab:SPCM_setting
DetMode = 1.0
PC_save_switch = 0.0
MV(PC_bin_number, min=100.0, max=30000.0, init=500, inc=100, digits=0)
PC_max_rate_MHz = 5.0
PC_num_channels = 1
MV(SPCM_offset_ms, min=0.0, max=25.0, init=0.0, inc=0.5, digits=2)
ADC_scope_sav = 0.0
ADC_ch_sav = 1.0
# Tab:E_Filter
MV(Ex, min=-12., max=12., init=-0.0253, inc=2.5e-3, digits=4)
MV(Ey, min=-12., max=12., init=0.0273, inc=2.5e-3, digits=4)
MV(Ez, min=-12., max=12., init=0.0604, inc=2.5e-3, digits=4)
MV(dxEx, min=-50., max=50., init=0.0, inc=1e0, digits=4)
MV(dxEy, min=-50., max=50., init=0.0, inc=1e0, digits=4)
MV(dyEy, min=-50., max=50., init=0.0, inc=1e0, digits=4)
MV(dxEz, min=-50., max=50., init=0.0, inc=1e0, digits=4)
MV(dyEz, min=-50., max=50., init=0.0, inc=1e0, digits=4)
MV(ExTrim, min=-5., max=5., init=0, inc=2.5e-3, digits=4)
MV(EyTrim, min=-5., max=5., init=0, inc=2.5e-3, digits=4)
MV(EzTrim, min=-5., max=5., init=0, inc=2.5e-3, digits=4)
MV(dV1, min=-40., max=40., init=0, inc=1.e-2, digits=4)
MV(dV2, min=-40., max=40., init=0, inc=1.e-2, digits=4)
MV(dV3, min=-40., max=40., init=0, inc=1.e-2, digits=4)
MV(dV4, min=-40., max=40., init=0, inc=1.e-2, digits=4)
MV(dV5, min=-40., max=40., init=0, inc=1.e-2, digits=4)
MV(dV6, min=-40., max=40., init=0, inc=1.e-2, digits=4)
MV(dV7, min=-40., max=40., init=0, inc=1.e-2, digits=4)
MV(dV8, min=-40., max=40., init=0, inc=1.e-2, digits=4)
MV(dV9, min=-40., max=40., init=0, inc=1.e-2, digits=4)
MV(V1_SSV, min=-48, max=48, init=0, inc=1.e-2, digits=4)
MV(V2_SSV, min=-48., max=48., init=0, inc=1.e-2, digits=4)
MV(V3_SSV, min=-48., max=48., init=0, inc=1.e-2, digits=4)
MV(V4_SSV, min=-48., max=48., init=0, inc=1.e-2, digits=4)
MV(V5_SSV, min=-48., max=48., init=0, inc=1.e-2, digits=4)
MV(V6_SSV, min=-48., max=48., init=0, inc=1.e-2, digits=4)
MV(V7_SSV, min=-48., max=48., init=0, inc=1.e-2, digits=4)
MV(V8_SSV, min=-48., max=48., init=0, inc=1.e-2, digits=4)
MV(V9_SSV, min=-48., max=48., init=0, inc=1.e-2, digits=4)
V1_SS_ttl   = 1
V1_main_ttl = 0
LN_switch = 1 # use least norm solution
ElMod_switch = 0
ElMod_Volt = 1.0
ElMod_freq_kHz = 1.0
# Tab:MOT
Loading_s = 0.0
MV(MOT_MOTPwr, min=0.0, max=5.0, init=5.0, inc=0.1, digits=4)
MV(MOT_REPPwr, min=0.0, max=5.0, init=5.0, inc=0.1, digits=4)
MV(MOT_Det23_MHz, min=-1000.0, max=1000.0, init=-23.0, inc=0.1, digits=2)
MV(REP_Det12_MHz, min=-1000.0, max=1000.0, init=0.0, inc=0.1, digits=2)
MOT_CoilCurr = 3.0
MV(MOT_BiasX_G, min=-3.0, max=3.0, init=0.032, inc=1e-3, digits=4)
MV(MOT_BiasY_G, min=-3.0, max=3.0, init=0.401, inc=1e-3, digits=4)
MV(MOT_BiasZ_G, min=-3.0, max=3.0, init=-0.693, inc=1e-3, digits=4)
MOT_SteadyState = 1
# Tab:PGC
PGC_switch = 1.0
PGC_BiasSetTime_ms = 0.01
PGC_FreqRamp_ms = 3.0
PGC_time_ms = 5.0
PGC_MOTCoilSetTime_ms = 3.0
MV(PGC_RepEarlyEndTime_ms, min=0.0, max=10.0, init=0.0, inc=1, digits=1)
MV(PGC_MOT_Det23_MHz, min=-1000.0, max=1000.0, init=-205.0, inc=0.1, digits=2)
MV(PGC_REP_Det12_MHz, min=-1000.0, max=1000.0, init=-7.0, inc=0.1, digits=2)
MV(PGC_MOTPwr, min=0.0, max=5.0, init=4.15, inc=0.005, digits=4)
MV(PGC_REPPwr, min=0.0, max=5.0, init=3.15, inc=0.005, digits=4)
MV(PGC_BiasX_G, min=-3.0, max=3.0, init=0.120, inc=1e-3, digits=4)
MV(PGC_BiasY_G, min=-3.0, max=3.0, init=0.0205, inc=1e-3, digits=4)
MV(PGC_BiasZ_G, min=-3.0, max=3.0, init=0.371, inc=1e-3, digits=4)
# Tab:MOTdRSC
MOT_dRSC_switch = 1.0
MOT_dRSC_reps = 1
MV(MOT_dRSC_time_ms, min=0.0, max=1e3, init=5.0, inc=0.1, digits=2)
MV(MOT_dRSC_initramptime_us, min=0.0, max=2e3,init=1000, inc=10, digits=1)
MV(MOT_dRSC_ramptime_us, min=0.0, max=2e3,init=500, inc=10, digits=1)
MV(MOT_dRSC_ctime_ms, min=0.0, max=1e3,init=5, inc=0.1, digits=2)
MOT_dRSC_FixTime = 0
MV(MOT_dRSC_FixedTime_ms, min=0.0, max=1e3, init=10.0, inc=0.1, digits=2)
MV(MOT_dRSC_pumpdelay_ms,min=0.0, max=1e3, init=0.0, inc=0.1, digits=2)
dRSC_MOT_LAT_ttl = 1.0
MV(dRSC_MOT_LAT_pwr, min=0.0, max=5.0, init=5.0, inc=0.1, digits=1)
dRSC_MOT_Pump_ttl = 1.0
MV(dRSC_MOT_Pump_pwr, min=0.0, max=5.0, init=5.0, inc=0.1, digits=1)
dRSC_MOT_VLAT_ttl = 1.0
dRSC_MOT_VLATmain_pwr = 4.6
dRSC_MOT_VLAT_endttl = 0.0
MV(PUMP_df_MHz, min=-100, max=100, init=0.0, inc=0.5, digits=1)
MV(dRSC_MOT_BiasX_G, min=-3.0, max=3.0, init=0.120, inc=5e-3, digits=4)
MV(dRSC_MOT_BiasY_G, min=-3.0, max=3.0, init=0.0205, inc=5e-3, digits=4)
MV(dRSC_MOT_BiasZ_G, min=-3.0, max=3.0, init=0.371, inc=5e-3, digits=4)
# Tab:Lattice
LAT_SWITCH = 1.0
LHT = 1.0
LVT = 1.0 
LMP = 4.4 
LHP = 4.8 
LVP = 4.8 
# Tab:Wait
Wait0_ms = 0.0
Wait1_ms = 0.0
Wait1p5_ms = 0.0
Wait2_ms = 0.0
Lat_TTL_Wait1 = 0.0
PGC_Wait1p5_switch = 0.0
PGC_Wait1p5_ontime_ms = 0.2
PGC_Wait1p5_offtime_ms = 5
PGC_Wait1p5_first = 1
PGC_Wait2_switch = 0.0
PGC_Wait2_ontime_ms = 2.0
PGC_Wait2_offtime_ms = 20
PGC_first = 0
# Tab:Transport
MV(Trans_dist_mm, min=-100.0, max=100.0, init=43.0, inc=1e-2, digits=2)
MV(Trans_dist_2_mm, min=-100.0, max=100.0, init=0.0, inc=1e-2, digits=2)
MV(Trans_dist_3_mm, min=-100.0, max=100.0, init=0.0, inc=1e-2, digits=2)
Trans_acc_g = 100.0
Trans_MaxF_MHz = 10.0
Trans_mode = 0
Trans_twoAom = 0
Trans_Npts = 32
Trans_hold_1_ms = 0.0
Trans_hold_2_ms = 0.0
Trans_Blue_ttl = 0.0
Trans_PGC_switch = 1
Trans_PGC_delay_ms = 3
MV(Trans_MOT_Det23_MHz, min=-1000.0, max=1000.0, init=-205.0, inc=0.1, digits=2)
MV(Trans_REP_Det12_MHz, min=-1000.0, max=1000.0, init=0.0, inc=0.1, digits=2)
MV(Trans_PGC_MOTpwr, min=0, max=5.0, init=4.15, inc=0.005, digits=4)
MV(Trans_PGC_REPPwr, min=0, max=5.0, init=2.8, inc=0.005, digits=4)
Trans_GDEP_ttl = 1
Trans_GDEP_pwr = 5
Trans_ParamHeat_switch = 0
MV(ParamHeat_freq_kHz, min=0, max=40000.0, init=110, inc=0.1, digits=3)
# Shutter_open_switch = 0
MV(Shutter_delay_ms, min=0, max=10, init=2.5, inc=0.1, digits=2)
# Tab:dRSC
dRSC_switch   = 1
dRSC_repetitions = 1
dRSC_Dur_ms   = 5
dRSC_VLAT_ttl = 1
dRSC_VLATmain_pwr = 4.2
dRSC_HLAT_ttl = 1
dRSC_HLAT_pwr = 4.7
dRSC_ELAT_ttl = 0
dRSC_ELAT_pwr = 0.0
dRSC_CODT_ttl = 0
dRSC_CODT_pwr = 0.0
dRSC_Pump_ttl = 1
dRSC_2to2p_ttl = 1
dRSC_Pump_pwr = 4.5
dRSC_Pump_ramp_ms = 1
dRSC_Pump_ramp_pwr = 3.0
dRSC_OP_REP_EarlyEnd_ms = 0.0
dRSC_LAT_rampON_us = 200 
dRSC_LAT_rampOFF_us = 500 
MV(dRSC_B_G, min=0, max=7.9, init=0.00, inc=1e-2, digits=4)
MV(dRSC_B_theta_deg, min=0, max=360, init=0.00, inc=1, digits=4)
MV(dRSC_B_phi_deg, min=0, max=720, init=0.00, inc=1, digits=4)
dRSC_PGC_switch = 0
dRSC_ParamHeat_switch = 0
c1_hold_time_ms = 0.6
c1_VLAT_ttl = 1
c1_VLATmain_pwr = 4.6
c1_HLAT_ttl = 1
c1_HLAT_pwr = 5.0
c1_ELAT_ttl = 1
c1_ELAT_pwr = 5.0
c1_PGC_switch = 1
c1_CODT_ttl = 0
c1_CODT_pwr = 0
# Tab:TrapRamp
Ramp1_switch=1
Ramp1_steps = 20.0
Ramp1_dur_us = 500.0
Ramp1_VLAT_TTL = 1
Ramp1_VLAT_pwr = 4
Ramp1_ELAT_TTL = 1
Ramp1_ELAT_pwr =0 
Ramp1_Retro_TTL = 1
Ramp1_Retro_pwr = 0
Ramp2_switch = 1
Ramp2_steps = 20.0
Ramp2_dur_us = 5000.0
Ramp2_VLAT_pwr = 4
Ramp2_ELAT_pwr = 4.8 
Ramp2_Retro_pwr = 0
Ramp3_switch = 1
Ramp3_steps = 20.0
Ramp3_dur_us = 5000.0
Ramp3_VLAT_pwr = 0
Ramp3_ELAT_pwr = 4.8
Ramp3_Retro_pwr = 0
RampFinal_VLAT_TTL = 0
RampFinal_Retro_TTL = 0
RampFinal_ELAT_TTL = 1
RampFinal_CODT_TTL = 0
# Tab:TRdRSC
TRdRSC_switch   = 1
TRdRSC_Dur_ms   = 5
TRdRSC_VLAT_ttl = 1
TRdRSC_VLATmain_pwr = 4.2
TRdRSC_HLAT_ttl = 1
TRdRSC_HLAT_pwr = 4.7
TRdRSC_ELAT_ttl = 0
TRdRSC_ELAT_pwr = 0.0
TRdRSC_Pump_ttl = 1
TRdRSC_2to2p_ttl = 1
TRdRSC_Pump_pwr = 4.5
TRdRSC_Pump_ramp_ms = 1
TRdRSC_Pump_ramp_pwr = 3.0
TRdRSC_OP_REP_EarlyEnd_ms = 0.0
TRdRSC_LAT_rampON_us = 200 
TRdRSC_LAT_rampOFF_us = 500 
MV(TRdRSC_B_G, min=0, max=7.9, init=0.00, inc=1e-2, digits=4)
MV(TRdRSC_B_theta_deg, min=0, max=360, init=0.00, inc=1, digits=4)
MV(TRdRSC_B_phi_deg, min=0, max=720, init=0.00, inc=1, digits=4)
# Tab:ELATdRSC
ELdRSC_switch   = 1
ELdRSC_repetitions = 1
ELdRSC_Dur_ms   = 5
ELdRSC_HLAT_ttl = 1
ELdRSC_HLAT_pwr = 4.7
ELdRSC_HLAT_low_pwr = 0.0
ELdRSC_HLAT_dutyc = 50
ELdRSC_ELAT_ttl = 0
ELdRSC_ELAT_pwr = 0.0
ELdRSC_CODT_ttl = 0
ELdRSC_CODT_pwr = 0.0
ELdRSC_Pump_ttl = 1
ELdRSC_Pump_pwr = 4.5
ELdRSC_Pump_ramp_ms = 1
ELdRSC_Pump_ramp_pwr = 3.0
ELdRSC_OP_REP_EarlyEnd_ms = 0.0
ELdRSC_LAT_rampON_us = 200 
ELdRSC_LAT_rampOFF_us = 500 
MV(ELdRSC_B_G, min=0, max=7.9, init=0.00, inc=1e-2, digits=4)
MV(ELdRSC_B_theta_deg, min=0, max=180, init=0.00, inc=1, digits=4)
MV(ELdRSC_B_phi_deg, min=0, max=360, init=0.00, inc=1, digits=4)
c2_hold_time_ms = 0.6
c2_ramp_time_ms = 10.0
c2_HLAT_ttl = 1
c2_HLAT_pwr = 5.0
c2_ELAT_ttl = 1
c2_ELAT_pwr = 5.0
c2_CODT_ttl = 1
c2_CODT_pwr = 4.4
ELAT_ParamHeat_switch = 0
# Tab:RampCODT
RampCODT_switch = 0
RampCODT_steps = 20.0
RampCODT_dur_us = 1000.0
RampCODT_ODT_TTL = 1
RampCODT_ODT_pwr = 4.0
RampCODT_VLAT_TTL = 1
RampCODT_VLAT_pwr = 4.0
RampCODT_VLAT_Retro_TTL = 0
RampCODT_VLAT_Retro_pwr = 0.0
RampCODT_ELAT_TTL = 1
RampCODT_ELAT_pwr = 4.0
RampCODT2_switch = 0
RampCODT2_steps = 20.0
RampCODT2_dur_us = 1000.0
RampCODT2_ODT_TTL = 1
RampCODT2_ODT_pwr = 4.0
RampCODT2_VLAT_TTL = 1
RampCODT2_VLAT_pwr = 4.0
RampCODT2_VLAT_Retro_TTL = 0
RampCODT2_VLAT_Retro_pwr = 0.0
RampCODT2_ELAT_TTL = 1
RampCODT2_ELAT_pwr = 4.0
RampCODT3_switch = 0
RampCODT3_steps = 20.0
RampCODT3_dur_us = 1000.0
RampCODT3_ODT_TTL = 1
RampCODT3_ODT_pwr = 4.0
RampCODT3_VLAT_TTL = 1
RampCODT3_VLAT_pwr = 4.0
RampCODT3_VLAT_Retro_TTL = 0
RampCODT3_VLAT_Retro_pwr = 0.0
RampCODT3_ELAT_TTL = 1
RampCODT3_ELAT_pwr = 4.0
RampCODTFinal_VLAT_TTL = 0
RampCODTFinal_Retro_TTL = 0
RampCODTFinal_ELAT_TTL = 0
RampCODTFinal_CODT_TTL = 1
RampCODT3_ParamHeat_switch = 0
# Tab:CdRSC
CdRSC_switch   = 1
CdRSC_repetitions = 1
CdRSC_Dur_ms   = 5
CdRSC_VLAT_ttl = 0
CdRSC_VLAT_pwr = 0.0
CdRSC_HLAT_ttl = 1
CdRSC_HLAT_pwr = 4.7
CdRSC_ELAT_ttl = 0
CdRSC_ELAT_pwr = 0.0
CdRSC_CODT_ttl = 0
CdRSC_CODT_pwr = 0.0
CdRSC_Pump_ttl = 1
# CdRSC_2to2p_ttl = 1
CdRSC_Pump_pwr = 4.5
CdRSC_OP_REP_EarlyEnd_ms = 0.0
CdRSC_LAT_rampON_us = 200 
CdRSC_LAT_rampOFF_us = 500 
MV(CdRSC_B_G, min=0, max=7.9, init=0.00, inc=1e-2, digits=4)
MV(CdRSC_B_theta_deg, min=0, max=180, init=0.00, inc=1, digits=4)
MV(CdRSC_B_phi_deg, min=0, max=360, init=0.00, inc=1, digits=4)
c3_hold_time_ms = 0.6
c3_ramp_time_ms = 10.0
c3_VLAT_ttl = 0
c3_VLAT_pwr = 0.0
c3_HLAT_ttl = 1
c3_HLAT_pwr = 5.0
c3_ELAT_ttl = 1
c3_ELAT_pwr = 5.0
c3_CODT_ttl = 1
c3_CODT_pwr = 4.4
CdRSC_strobe_switch = 0
CdRSC_strobe_on_us = 50.0
CdRSC_strobe_off_us = 50.0
CdRSC_strobe_Pump_ttl = 1
CdRSC_strobe_VLAT_ttl = 1
CdRSC_strobe_HLAT_ttl = 1
# Tab:BField_OP_DEP
BRamp1_switch = 1
BRamp1_ms = 5
MV(B_1_G, min=0, max=7.9, init=0.00, inc=1e-2, digits=4)
MV(B_1_theta_deg, min=0, max=360, init=0.00, inc=1, digits=4)
MV(B_1_phi_deg, min=0, max=720, init=0.00, inc=1, digits=4)
BRamp1_settle_ms = 0
BRamp1_settle_VLAT_pwr = 4.5
BRamp1_settle_ELAT_pwr = 4.5
OP_REP_switch = 1
OP_REP_pwr = 5
OP_REP_ms = 1.0
OP_REP_12_EarlyEnd_ms = 0
OP_REP_RF_type = 1
OP_REP_RF_freq_MHz = 0.0 #TODO MV
OP_REP_RF_pwr_dBm = 0.0
BRamp2_ttl = 1
BRamp2_ms = 5
MV(B_2_G, min=0, max=7.9, init=0.00, inc=1e-2, digits=4)
MV(B_2_theta_deg, min=0, max=360, init=0.00, inc=1, digits=4)
MV(B_2_phi_deg, min=0, max=720, init=0.00, inc=1, digits=4)
GDEP_switch = 1
GDEP_preOP_switch = 1
GDEP_ms = 0.1
GDEP_pwr = 5.0
MV(GDEP_det_MHz, min=-1000.0, max=1000.0, init=0.0, inc=0.1, digits=2)
OP_780_switch = 0
MV(OP_780_f0_MHz, min=0, max=3e3, init=300.0, inc=0.1, digits=3)
OP_780_pwr = 3.3
MV(WP_Lambda2_deg, min=0, max=359.999, init=355.5, inc=0.05, digits=3)
MV(WP_Lambda4_deg, min=0, max=359.999, init=351.3, inc=0.05, digits=3)
# Tab:CavPrb
PRB_mode = 1.0
PRB_ttl = 1.0
PRB_SPCM_ttl = 1.0
PRBF_EOM = 5.0
PRB_delay_us = 10.0
PRB_repetitions = 10
PRB_OP_REP_total_ms = 0.04
PRB_gaps_ms = 0.005
PRB_time_ms = 1.95
PRB_sweep_num = 1
PRB_Ctrl_ttl = 0.0
PRB_Ctrl_gap_ttl = 0.0
MV(PRB_Ctrl_pwr, min=0.0, max=5.0, init=4.2, inc=5e-2, digits=2)
PRB_REP_ttl = 1.0
PRB_REP_pwr = 5.0
PRB_ELAT_ttl = 1.0
PRB_CODT_ttl = 0.0
PRB_MOTcoil = 0.0
SPCM_alwayson = 0.0
PRB_gap_ttl = 0 
PRB_gap_pwr = 3.0
PRB_LATT_OFF = 0
PRB_CtrlAOM_f0_MHz = 200.0
MV(PRB_CtrlAOM_df_MHz, min=0, max=10, init=0.00, inc=0.1, digits=2)
Blue_ON_ms = 0.0
# Tab:Imaging
Img_save = 0.0
Img_switch = 0.0
Img_DEPMOT_time_us = 50.0
Img_DEPMOT_atend_us = 100.0
Img_FRAMP_switch = 1
Img_FRAMP_ms = 2 
Img_REP_atend_us = 100.0
Img_REP_atend_pwr = 2.0
Img_TOF_ms = 0.0
Img_prep_time_us = 2.0
Img_time_us = 11.5
Img_gain_dB = 24.0
Img_drop_time_ms = 100.0
Img_MOT_pwr = 4.6
Img_ABS_pwr = 5.0
Img_REP_pwr = 5.0
Img_det23_MHz = 0.0
Img_det12_MHz = 0.0
Img_ELAT_ttl = 1
Img_ELAT_pwr = 4.0
Img_GDEP_ttl = 1
Img_GDEP_pwr = 5.0
Img_CODT_ttl = 1
Img_CODT_pwr = 5.0
Blue_img_ttl = 0.0
Img_RF_ttl = 0
# Tab:Floquet
Floquet_AOM_TTL = 0
Floquet_Transport_TTL = 1
Floquet_dRSC_TTL = 0
Floquet_SteadyState_TTL = 1
Floquet_AOM_pwr = 5
MV(RFSOC1529_lock, min=1000, max=3200, init=2500.0, inc=0.1, digits=3)
MV(RFSOC1529_HF, min=1000, max=3200, init=2500.0, inc=0.1, digits=3)
MV(RFSOC1529_HF_att_dB, min=0.0, max=31.5, init=0.0, inc=0.5, digits=1)
MV(Floquet_PRB_fraction, min=0.0, max=1.0, init=1.0, inc=0.1, digits=2)
MV(LB1529_lock_MHz, min=10000, max=20000, init=15000, inc=0.1, digits=2)
MV(LB1529_lock_dBm, min=-40, max=10, init=5, inc=0.5, digits=1) 
# Tab:Subrep
PRB_pwr_low = 3.3
PRB_pwr_high = 3.6
PRB_ttl = 0
PRB_U_ttl = 0
PRB_L_ttl = 0
MV(PRB_f0_MHz, min=0, max=3e3, init=300.0, inc=0.1, digits=3)
PRB_df_MHz = 10.0
MV(PRB_U_f0_MHz, min=0, max=3e3, init=2200.0, inc=0.1, digits=3)
PRB_U_df_MHz = 10.0
MV(PRB_L_f0_MHz, min=0, max=3e3, init=2800.0, inc=0.1, digits=3)
PRB_L_df_MHz = 10.0
MV(t_subrep_us, min=0, max=100000, init=50, inc=1, digits=3)
MV(Prb_P_wait_us, min=0, max=100000, init=0, inc=1, digits=3)
MV(Prb_P_dur_us, min=0, max=100000, init=25, inc=1, digits=3)
MV(Prb_U_wait_us, min=0, max=10000, init=0, inc=1, digits=3)
MV(Prb_U_dur_us, min=0, max=10000, init=0, inc=1, digits=3)
MV(Prb_L_wait_us, min=0, max=10000, init=0, inc=1, digits=3)
MV(Prb_L_dur_us, min=0, max=10000, init=0, inc=1, digits=3)
# Tab:Microwaves
MV(MW_det_kHz, min=-1000000, max=1000000, init=0, inc=10, digits=1)
MV(MW_pwr_dBm, min=-40, max=10, init=0, inc=0.1, digits=2) 
MW_cw_ttl = 1
MV(MW_time_ms, min=0.0, max=100., init=0., inc=0.1, digits=2)
MV(MW_BiasX_G, min=-3.0, max=3.0, init=0.120, inc=1e-3, digits=4)
MV(MW_BiasY_G, min=-3.0, max=3.0, init=0.0205, inc=1e-3, digits=4)
MV(MW_BiasZ_G, min=-3.0, max=3.0, init=0.371, inc=1e-3, digits=4)
MV(MW_ramp_ms, min=0, max=100, init=10, inc=0.1, digits=2)
MV(MW_settle_ms, min=0, max=100, init=10, inc=0.1, digits=2) 
# Tab:REP_Durations
MV(REP_frac_1, min=0.0, max=0.5, init=0.5, inc=0.01, digits=3)
MV(REP_frac_2, min=0.0, max=0.5, init=0.5, inc=0.01, digits=3)
MV(REP_frac_3, min=0.0, max=0.5, init=0.5, inc=0.01, digits=3)
MV(REP_frac_4, min=0.0, max=0.5, init=0.5, inc=0.01, digits=3)
MV(REP_frac_5, min=0.0, max=0.5, init=0.5, inc=0.01, digits=3)
MV(REP_frac_6, min=0.0, max=0.5, init=0.5, inc=0.01, digits=3)
MV(REP_frac_7, min=0.0, max=0.5, init=0.5, inc=0.01, digits=3)
MV(REP_frac_8, min=0.0, max=0.5, init=0.5, inc=0.01, digits=3)
MV(REP_frac_9, min=0.0, max=0.5, init=0.5, inc=0.01, digits=3)
MV(REP_frac_10, min=0.0, max=0.5, init=0.5, inc=0.01, digits=3)
# Tab:DMD
MV(DMD_L, min=-25, max=100, init=0, inc=1, digits=0)
MV(DMD_P, min=0, max=30, init=0, inc=1, digits=0)
MV(DMD_Waist, min=0.0, max=3000, init=62, inc=0.5, digits=1)
MV(DMD_Defocus, min=100, max=10000, init=780, inc=10, digits=1)
MV(DMD_Center_X, min=-300, max=300, init=0, inc=0.1, digits=1)
MV(DMD_Center_Y, min=-300, max=300, init=0, inc=0.1, digits=1)
MV(DMD_Tilt_X, min=-15.0, max=15.0, init=0.0, inc=0.01, digits=2)
MV(DMD_Tilt_Y, min=-15.0, max=15.0, init=0.0, inc=0.01, digits=2)
MV(DMD_Phi, min=-5.0, max=5.0, init=0.0, inc=0.1, digits=2)
MV(DMD_Epsilon_Phi, min=-5.0, max=5.0, init=0.0, inc=0.1, digits=2)
MV(SmarAct_x_V, min=0, max=100, init=50, inc=0.1, digits=1)
MV(SmarAct_y_V, min=0, max=100, init=50, inc=0.1, digits=1)
# If you add more pwrs here, make sure to add them to the list (GDEP_pwrs) below


#### End Modifiable Variables ###n

########################################################################va
#======================== Main Instance ===============================#
########################################################################
#### Other calculations ####
#Convert E-filter bases
if LN_switch:
    V1, V2, V3, V4, V5, V6, V7, V8, V9 = electrodes.Field2Voltage_ln([Ex+ExTrim, Ey+EyTrim, Ez+EzTrim, dxEx*100., dxEy*100., dyEy*100., dxEz*100., dyEz*100.])+[dV1, dV2, dV3, dV4, dV5, dV6, dV7, dV8, dV9]
    print('electrode voltages (least norm):', V1, V2, V3, V4, V5, V6, V7, V8, V9)
else:
    V1, V2, V3, V4, V5, V6, V7, V8 = electrodes.Field2Voltage([Ex+ExTrim, Ey+EyTrim, Ez+EzTrim, dxEx*100., dxEy*100., dyEy*100., dxEz*100., dyEz*100.])+[dV1, dV2, dV3, dV4, dV5, dV6, dV7, dV8]
    V9 = 0 + dV9 # body electrode
    print('electrode voltages (8-dim):', V1, V2, V3, V4, V5, V6, V7, V8, V9)
    
#MOT frequency conversion
MOTFREQ = Rb.DDS_MOT_23(MOT_Det23_MHz)
REPFREQ = Rb.DDS_REP_12(REP_Det12_MHz)
#Molasses frequency conversion
PGCMOTFreq = Rb.DDS_MOT_23(PGC_MOT_Det23_MHz)
PGCREPFreq = Rb.DDS_REP_12(PGC_REP_Det12_MHz)
#Transport Kicking frequency conversion
TMOTFreq = Rb.DDS_MOT_23(Trans_MOT_Det23_MHz)
TREPFreq = Rb.DDS_REP_12(Trans_REP_Det12_MHz)
#Imaging laser freq
IMGMOTFREQ = Rb.DDS_MOT_23(Img_det23_MHz)
IMGREPFREQ = Rb.DDS_REP_12(Img_det12_MHz)
#BField transformation
dRSC_Bx_G = dRSC_B_G*np.sin(np.deg2rad(dRSC_B_theta_deg))*np.cos(np.deg2rad(dRSC_B_phi_deg))
dRSC_By_G = dRSC_B_G*np.sin(np.deg2rad(dRSC_B_theta_deg))*np.sin(np.deg2rad(dRSC_B_phi_deg))
dRSC_Bz_G = dRSC_B_G*np.cos(np.deg2rad(dRSC_B_theta_deg))
#ELAT dRSC
ELdRSC_Bx_G = ELdRSC_B_G*np.sin(np.deg2rad(ELdRSC_B_theta_deg))*np.cos(np.deg2rad(ELdRSC_B_phi_deg))
ELdRSC_By_G = ELdRSC_B_G*np.sin(np.deg2rad(ELdRSC_B_theta_deg))*np.sin(np.deg2rad(ELdRSC_B_phi_deg))
ELdRSC_Bz_G = ELdRSC_B_G*np.cos(np.deg2rad(ELdRSC_B_theta_deg))
#CdRSC
CdRSC_Bx_G = CdRSC_B_G*np.sin(np.deg2rad(CdRSC_B_theta_deg))*np.cos(np.deg2rad(CdRSC_B_phi_deg))
CdRSC_By_G = CdRSC_B_G*np.sin(np.deg2rad(CdRSC_B_theta_deg))*np.sin(np.deg2rad(CdRSC_B_phi_deg))
CdRSC_Bz_G = CdRSC_B_G*np.cos(np.deg2rad(CdRSC_B_theta_deg))

Bx_1_G = B_1_G*np.sin(np.deg2rad(B_1_theta_deg))*np.cos(np.deg2rad(B_1_phi_deg))
By_1_G = B_1_G*np.sin(np.deg2rad(B_1_theta_deg))*np.sin(np.deg2rad(B_1_phi_deg))
Bz_1_G = B_1_G*np.cos(np.deg2rad(B_1_theta_deg))
Bx_2_G = B_2_G*np.sin(np.deg2rad(B_2_theta_deg))*np.cos(np.deg2rad(B_2_phi_deg))
By_2_G = B_2_G*np.sin(np.deg2rad(B_2_theta_deg))*np.sin(np.deg2rad(B_2_phi_deg))
Bz_2_G = B_2_G*np.cos(np.deg2rad(B_2_theta_deg))


#### PREPARE STAMPS ####
t_gap1 = PRB_gaps_ms*Unit.ms()
t_PRB_OP = t_gap1 + PRB_OP_REP_total_ms*Unit.ms()
t_gap2 = t_PRB_OP + PRB_gaps_ms*Unit.ms()
t_PRB = t_gap2 + PRB_time_ms*Unit.ms()
t_PRB_total = t_PRB*PRB_repetitions

# STP_PRB is calculated below to now incorporate PRB_subrep or "Probe Subrepitions" without changing any of the times above. Probe Subrepitions occur
# entirely within PRB_time_ms and was implemented to see Rabi oscillations of the dark polariton (which requires us to turn on the probe for some
# short amount of time - like 10us or so - then turn off the probe and watch the signal ringdown.

STP_PRB  =     [(0., PRB_gap_ttl, t_gap2, PRB_gap_ttl), (t_gap2, PRB_ttl, t_PRB, PRB_ttl)]
STP_BLUE =     [(0., PRB_Ctrl_gap_ttl, t_gap2, PRB_Ctrl_gap_ttl), (t_gap2, PRB_Ctrl_ttl, t_PRB, PRB_Ctrl_ttl)]
STP_PRB_pwr  = [(0., PRB_gap_pwr, t_gap2, PRB_gap_pwr), (t_gap2, PRB_pwr_low, t_PRB, PRB_pwr_low)]
STP_SPCM =     [(0., SPCM_alwayson*PRB_SPCM_ttl, t_gap2, SPCM_alwayson*PRB_SPCM_ttl), (t_gap2, PRB_SPCM_ttl, t_PRB, PRB_SPCM_ttl)]
STP_REP =      [(0., 0, t_gap1, 0),(t_gap1, PRB_REP_ttl, t_PRB_OP, PRB_REP_ttl), (t_PRB_OP, 0, t_PRB, 0)]
STP_PRB_freq = []
STP_GATE = [(0., 1., t_gap2, 1.),]

CavPrb_P_f0 = (PRB_f0_MHz+PRB_df_MHz)*Unit.MHz()
CavPrb_P_f1 = (PRB_f0_MHz-PRB_df_MHz)*Unit.MHz()
CavPrb_U_f0 = (PRB_U_f0_MHz+PRB_U_df_MHz)*Unit.MHz()
CavPrb_U_f1 = (PRB_U_f0_MHz-PRB_U_df_MHz)*Unit.MHz()
CavPrb_L_f0 = (PRB_L_f0_MHz+PRB_L_df_MHz)*Unit.MHz()
CavPrb_L_f1 = (PRB_L_f0_MHz-PRB_L_df_MHz)*Unit.MHz()

#### SUBREP STAMPS ####
N_subreps = int(floor(PRB_time_ms*Unit.ms()/t_subrep_us))
subcy_time = t_subrep_us*Unit.us()
print("DEBUG: N", N_subreps, Unit.ms(), Unit.us())
if N_subreps==0:
    print("ERROR: NO SUBREPS! Lower t_subrep_us below the total probe time!")

#Three "probe pulses", first real probe P and then two sidebands, U and then L (can be interchanged by freq)

STP_PRB_EOM = [(0., PRB_gap_ttl, t_gap2, PRB_gap_ttl), ]
STP_PRB_PWR_TTL = [(0., PRB_gap_ttl, t_gap2, PRB_gap_ttl), ]
for i in range(N_subreps):
    #pulse 1
    if PRB_ttl:
        start, end = Prb_P_wait_us, Prb_P_wait_us+Prb_P_dur_us
        STP_PRB_EOM.append((t_gap2+subcy_time*i+start, PRB_ttl, t_gap2+subcy_time*i+end, PRB_ttl))
        STP_PRB_EOM.append((t_gap2+subcy_time*i+end, 0, t_gap2+subcy_time*(i+1), 0.))
        STP_PRB_freq.append((subcy_time*i+start, CavPrb_P_f0, subcy_time*i+end, CavPrb_P_f1))

    if PRB_U_ttl:
        start, end = Prb_P_wait_us+Prb_P_dur_us+Prb_U_wait_us,  Prb_P_wait_us+Prb_P_dur_us+Prb_U_wait_us+Prb_U_dur_us
        STP_PRB_EOM.append((t_gap2+subcy_time*i+start, PRB_U_ttl, t_gap2+subcy_time*i+end, PRB_U_ttl))
        STP_PRB_EOM.append((t_gap2+subcy_time*i+end, 0, t_gap2+subcy_time*(i+1), 0.))
        STP_PRB_freq.append((subcy_time*i+start, CavPrb_U_f0, subcy_time*i+end, CavPrb_U_f1))
        STP_GATE.append((t_gap2+subcy_time*i+start, 0, t_gap2+subcy_time*i+end, 0))
        STP_GATE.append((t_gap2+subcy_time*i+end, 1, t_gap2+subcy_time*(i+1), 1))

    if PRB_L_ttl:
        start = Prb_P_wait_us+Prb_P_dur_us+Prb_U_wait_us+Prb_U_dur_us+Prb_L_wait_us
        end = Prb_P_wait_us+Prb_P_dur_us+Prb_U_wait_us+Prb_U_dur_us+Prb_L_wait_us+Prb_L_dur_us
        STP_PRB_EOM.append((t_gap2+subcy_time*i+start, PRB_L_ttl, t_gap2+subcy_time*i+end, PRB_L_ttl))
        STP_PRB_EOM.append((t_gap2+subcy_time*i+end, 0, t_gap2+subcy_time*(i+1), 0.))
        STP_PRB_freq.append((subcy_time*i+start, CavPrb_L_f0, subcy_time*i+end, CavPrb_L_f1))
        STP_GATE.append((t_gap2+subcy_time*i+start, 0, t_gap2+subcy_time*i+end, 0))
        STP_GATE.append((t_gap2+subcy_time*i+end, 1, t_gap2+subcy_time*(i+1), 1))

    STP_PRB_PWR_TTL.append((t_gap2+subcy_time*i+Prb_P_wait_us+Prb_P_dur_us, (PRB_U_ttl or PRB_L_ttl), t_gap2+subcy_time*i+end, (PRB_U_ttl or PRB_L_ttl)))
    STP_PRB_PWR_TTL.append((t_gap2+subcy_time*i+end, 0, t_gap2+subcy_time*(i+1), 0.))

#Append ghost event to bringe the total length of the stamp to PRB_time in total, since timer.appendMod is a dumb function!
if PRB_ttl or PRB_U_ttl or PRB_L_ttl:
    STP_PRB_EOM.append((t_PRB-10, 0, t_PRB-1, 0.))
    STP_PRB_PWR_TTL.append((t_PRB-10, 0, t_PRB-1, 0.))
    STP_PRB_freq.append((t_PRB-10, CavPrb_P_f0, t_PRB-1, CavPrb_P_f0))
    STP_GATE.append((t_PRB-10, 1, t_PRB-1, 1))

#Experiment: Trigger RFSoc with each STP_PRB_EOM (TTL) and only write three ramps to save cycle time

# CODT strobing
STP_CODT_ODT = [(0.0, CdRSC_CODT_ttl, CdRSC_strobe_on_us*Unit.us(), CdRSC_CODT_ttl), (CdRSC_strobe_on_us*Unit.us(), 0, CdRSC_strobe_on_us*Unit.us()+CdRSC_strobe_off_us*Unit.us(), 0)]
STP_CODT_PUMP = [(0.0, CdRSC_strobe_Pump_ttl, CdRSC_strobe_on_us*Unit.us(), CdRSC_strobe_Pump_ttl), (CdRSC_strobe_on_us*Unit.us(), 1, CdRSC_strobe_on_us*Unit.us()+CdRSC_strobe_off_us*Unit.us(), 1)]
STP_CODT_VLAT = [(0.0, CdRSC_strobe_VLAT_ttl, CdRSC_strobe_on_us*Unit.us(), CdRSC_strobe_VLAT_ttl), (CdRSC_strobe_on_us*Unit.us(), 1, CdRSC_strobe_on_us*Unit.us()+CdRSC_strobe_off_us*Unit.us(), 1)]
STP_CODT_HLAT = [(0.0, CdRSC_strobe_HLAT_ttl, CdRSC_strobe_on_us*Unit.us(), CdRSC_strobe_HLAT_ttl), (CdRSC_strobe_on_us*Unit.us(), 1, CdRSC_strobe_on_us*Unit.us()+CdRSC_strobe_off_us*Unit.us(), 1)]
# AUX1 should always be zero during PRB; AUX2 switches between OP and DEP



#### Set Time Intervals ####
times = Intervaler(0.) # THIS COMMAND IS REQUIRED TO CREATE THE TIME OBJECT!
times_InitDrop = DropAtoms(times, InitDrop*100.0*Unit.ms())
times_Init = times.append(Init_time_ms*Unit.ms(), 'Init')
times_MOT = MakeMOT(times, Loading_s*Unit.s(), MOT_MOTPwr, MOT_REPPwr, MOT_CoilCurr)
if PGC_switch == 1:
    times_PGC = PGC(times, PGC_BiasSetTime_ms*Unit.ms(), PGC_FreqRamp_ms*Unit.ms(), PGC_time_ms*Unit.ms(), PGC_MOTCoilSetTime_ms*Unit.ms(), 
                PGC_BiasX_G, PGC_BiasY_G, PGC_BiasZ_G, 
                PGC_MOTPwr, PGC_REPPwr, 
                [MOTFREQ, PGCMOTFreq], [REPFREQ, PGCREPFreq], t_rep_bef=PGC_RepEarlyEndTime_ms*Unit.ms())
if MOT_dRSC_switch == 1:
    times_MOTdRSC = []
    for i in range(int(MOT_dRSC_reps)):
        if i != MOT_dRSC_reps-1: #i.e. not the final rep
            times_MOTdRSC.append(times.append(MOT_dRSC_time_ms*Unit.ms(),"MOT dRSC"))
            times_MOTdRSC.append(times.append(MOT_dRSC_ctime_ms*Unit.ms(),"MOT dRSC compression"))
        else: #This is the final rep. Don't compress after and potentially extend cooling time
            if MOT_dRSC_FixTime == 0:
                times_MOTdRSC.append(times.append((MOT_dRSC_time_ms)*Unit.ms(),"MOT dRSC"))
            else:
                remainingtime_ms = MOT_dRSC_FixedTime_ms - (i-1)*(MOT_dRSC_time_ms+MOT_dRSC_ctime_ms)
                if remainingtime_ms < MOT_dRSC_time_ms:
                    remainingtime_ms = MOT_dRSC_time_ms
                times_MOTdRSC.append(times.append((remainingtime_ms)*Unit.ms(),"MOT dRSC"))
times_Wait0 = times.append(Wait0_ms*Unit.ms(), "Wait At MOT")

if MW_cw_ttl:
    times_MW_bramp = times.append(MW_ramp_ms*Unit.ms(), "MW B Ramp")
    times_MW_settle = times.append(MW_settle_ms*Unit.ms(), "MW B Settle")
    times_MW = times.append(MW_time_ms*Unit.ms(), "MW HFS")

### change MOT and REP frequencies
#times_changeMOTfreq = times.append("length variable","time to change freqs")

### TRANSPORT
#times_transport = Transport_DDSRampMode(times, Trans_acc_g, Trans_dist_mm, Max_df=Trans_MaxF_MHz)
#times_Wait1 = times.append(Wait1_ms*Unit.ms(), "Wait In Cav")
#if Trans_RoundTrip == 1:
#	times_transport_back = Transport_DDSRampMode(times, Trans_acc_g, -Trans_distance_mm, Max_df=Trans_MaxF_MHz)
# The transport sequence got modified to receive the two channel obejct instead of hardcoding them
# Since we are only using one RFsoc channel for now the other one gets set to None
#transport 1


#transport 1
times_transport = Transport(times, Trans_acc_g, -Trans_dist_mm, chanA=RFSOC1_VertTransAOM, chanB=RFSOC1_HorzTransAOM, Max_df=Trans_MaxF_MHz, mode=Trans_mode, twoAoms=Trans_twoAom, Npts=Trans_Npts)
#wait 1
#if Trans_hold_1_ms>0.:
times_Wait1 = times.append(Trans_hold_1_ms*Unit.ms(), "Wait after transport 1")
times_transport = times_transport & times_Wait1
#transport 2
if abs(Trans_dist_2_mm)>0.:
    times_transport_2 = Transport(times, Trans_acc_g, -Trans_dist_2_mm, chanA=RFSOC1_VertTransAOM, chanB=RFSOC1_HorzTransAOM, Max_df=Trans_MaxF_MHz, mode=Trans_mode, twoAoms=Trans_twoAom, Npts=Trans_Npts)
    times_transport &= times_transport_2
#wait 2
if Trans_hold_2_ms>0.:
    times_Wait11 = times.append(Trans_hold_2_ms*Unit.ms(), "Wait after transport 2")
#transport 3
if abs(Trans_dist_3_mm)>0.:
    times_transport_3 = Transport(times, Trans_acc_g, -Trans_dist_3_mm, chanA=RFSOC1_VertTransAOM, chanB=RFSOC1_HorzTransAOM, Max_df=Trans_MaxF_MHz, mode=Trans_mode, twoAoms=Trans_twoAom, Npts=Trans_Npts)
    times_transport &= times_transport_3

#times_transport = times_transport_1 #& times_transport_2&times_transport_3 HOW to fix this correctly

times_dRSC = []
if dRSC_switch == 1:
    for i in range(int(dRSC_repetitions)):
        times_dRSC.append(times.append(dRSC_Dur_ms*Unit.ms(), 'dRSC {:d}'.format(i+1)))
        if i<int(dRSC_repetitions)-1: # Dont compress on the last rep
            times_c1 = times.append(c1_hold_time_ms*Unit.ms(), 'Compress1')
#print(times_dRSC)
times_dRSC2 = []

times_Wait1 = times.append(Wait1_ms*Unit.ms(), "Wait after dRSC")

if Ramp1_switch == 1:
    times_ramp1 = times.append(Ramp1_dur_us*Unit.us(), 'Ramp1')
if Ramp2_switch == 1:
    times_ramp2 = times.append(Ramp2_dur_us*Unit.us(), 'Ramp2')
if Ramp3_switch == 1:
    times_ramp3 = times.append(Ramp3_dur_us*Unit.us(), 'Ramp3')
times_rampall = times.append(0, "After Ramps")


#TrapRamp dRSC
if TRdRSC_switch == 1:
    times_TRdRSC = times.append(TRdRSC_Dur_ms*Unit.ms(), 'TRdRSC')

times_Wait1p5 = times.append(Wait1p5_ms*Unit.ms(), "Wait In Cav AFTER dRSC")

#ELAT dRSC
times_ELdRSC = []
if ELdRSC_switch == 1:
    for i in range(int(ELdRSC_repetitions)):
        times_ELdRSC.append(times.append(ELdRSC_Dur_ms*Unit.ms(), 'ELATdRSC {:d}'.format(i+1)))
        if i<int(ELdRSC_repetitions)-1: # Dont compress on the last rep
            times_c2 = times.append(c2_ramp_time_ms*Unit.ms(), 'Compress2 Ramp')
            times_c2 = times.append(c2_hold_time_ms*Unit.ms(), 'Compress2 Hold')

# ramp on cavity ODT here
if RampCODT_switch == 1:
    times_ramp_odt = times.append(RampCODT_dur_us*Unit.us(), 'Ramp Cav ODT')

if RampCODT2_switch == 1:
    times_ramp_odt_2 = times.append(RampCODT2_dur_us*Unit.us(), 'Ramp Cav ODT 2')

if RampCODT3_switch == 1:
    times_ramp_odt_3 = times.append(RampCODT3_dur_us*Unit.us(), 'Ramp Cav ODT 3')

times_codt_rampall = times.append(0, "After CODT Ramps")

#CdRSC
times_CdRSC = []
if CdRSC_switch == 1:
    for i in range(int(CdRSC_repetitions)):
        times_CdRSC.append(times.append(CdRSC_Dur_ms*Unit.ms(), 'CdRSC {:d}'.format(i+1)))
        if i<int(CdRSC_repetitions):#-1: # Dont compress on the last rep
            times_c3 = times.append(c3_ramp_time_ms*Unit.ms(), 'Compress3 Ramp')
            times_c3 = times.append(c3_hold_time_ms*Unit.ms(), 'Compress3 Hold')


if BRamp1_switch == 1:
    times_BRamp1 = times.append(BRamp1_ms*Unit.ms(),'B Ramp 1')
    times_BRamp1_settle = times.append(BRamp1_settle_ms*Unit.ms(),'B Ramp 1 Settle')

if GDEP_preOP_switch == 1:
    times_preGDEP = times.append(GDEP_ms*Unit.ms(), 'GDEP right before OP')

if OP_REP_switch or OP_780_switch == 1:
    times_OP = times.append(OP_REP_ms*Unit.ms(),'Optical Pumping')

if BRamp2_ttl == 1:
    times_BRamp2 = times.append(BRamp2_ms*Unit.ms(),'B Ramp 2')
    times_BRamp2_settle = times.append(BRamp1_settle_ms*Unit.ms(),'B Ramp 2 Settle')

if GDEP_switch == 1:
    times_GDEP = times.append(GDEP_ms*Unit.ms(), 'GDEP right before probe')

times_blue = times.append(Blue_ON_ms*Unit.ms(), 'Blue light right before probe')

if PRB_mode == 1:
    times_delay = times.append(PRB_delay_us*Unit.us(), 'PRB_delay')
    #times_tmp = copy.deepcopy(times)
    times_Prb = times.appendMod(STP_PRB, PRB_repetitions, 'CavPrb')
    #Since RFSoc is triggered by PRB_EOM_ttl start it's time interval at "zero" i.e. afer probe gap
    times_Prb_latetrig = TimeInterval(0, times_Prb.length())
    #times_Prb_EOM = times_tmp.appendMod(STP_PRB_EOM, PRB_repetitions, 'CavPrbEOM')
elif PRB_mode == 2:
    times_CavPrb = times_transport.beforeEnd(PRB_time_ms*Unit.ms())
    #Since RFSoc is triggered by PRB_EOM_ttl start it's time interval at "zero" i.e. afer probe gap
    times_Prb_latetrig = TimeInterval(0, times_CavPrb.length())
    print(times_Prb_latetrig)
else:
    times_Prb_latetrig = TimeInterval(0, 1*Unit.ms())
times_Wait2 = times.append(Wait2_ms*Unit.ms(), "Wait After Slice and Probe")


#### Sequence Actions ####
### Initiation ###
# Digital seq
MOT0_ttl.SetInterval(times_Init, 1)
REP0_ttl.SetInterval(times_Init, 1)
Scope_trig.SetInterval(times_Init, 0)
Cam_trig.SetInterval(times_Init, 1)
UV_ttl.SetInterval(times_Init, 0)
LAT1_ttl.SetInterval(times_Init, LVT)
LAT2_ttl.SetInterval(times_Init, LHT)
Sacher2_ttl.SetInterval(times_Init, 0)
V1_ttl.SetInterval(times_Init, 0)
LAT0_ttl.SetInterval(times_Init.afterward(1.9*Unit.us()), LAT_SWITCH)
Blue_ttl.SetInterval(times_Init, 0)
ODT2_ttl.SetInterval(times_Init, 0)
Nufern0_ttl.SetInterval(times_Init, 0) 
PRB_pwr_ttl.SetInterval(times_Init, 0) 
MOT1_ttl.SetInterval(times_Init, 0)
SPCM_ttl.SetInterval(times_Init, 0)
GATE_ttl.SetInterval(times_Init, 1)
D1Laser1_ttl.SetInterval(times_Init, 0)
dRSC_LAT2_ttl.SetInterval(times_Init, 0)
EITPrbEOM_ttl.SetInterval(times_Init, 0)
AUX_ttl.SetInterval(times_Init,0)
Nufern1_ttl.SetInterval(times_Init, 0)
MOT2_ttl.SetInterval(times_Init, 0)
dRSC_LAT_ttl.SetInterval(times_Init, 0)
MWaves_ttl.SetInterval(times_Init, 0)
# Analog seq
MOT0_pwr.SetInterval(times_Init, MOT_MOTPwr)
REP0_pwr.SetInterval(times_Init, MOT_REPPwr)
MOTCoil.SetInterval(times_Init, MOT_CoilCurr)
BiasX.SetInterval(times_Init, MOT_BiasX_G)
BiasY.SetInterval(times_Init, MOT_BiasY_G)
BiasZ.SetInterval(times_Init, MOT_BiasZ_G)
LAT1_pwr.SetInterval(times_Init, LHP)
LAT2_pwr.SetInterval(times_Init, LVP)
Sacher2_pwr.SetInterval(times_Init, 0)
LAT0_pwr.SetInterval(times_Init, LMP)
Blue_pwr.SetInterval(times_Init, PRB_Ctrl_pwr)
ODT2_pwr.SetInterval(times_Init, 0)
Nufern0_pwr.SetInterval(times_Init, PRB_pwr_low)
CavPrbEOM_pwr.SetInterval(times_Init, PRB_pwr_high)
VImg_pwr.SetInterval(times_Init, Img_ABS_pwr)
D1Laser1_pwr.SetInterval(times_Init, 0)#dRSC_Pump_pwr
dRSC_LAT2_pwr.SetInterval(times_Init, 0)
MOT1_pwr.SetInterval(times_Init, 0)
MOT2_pwr.SetInterval(times_Init, 0)
# EF1.SetInterval(times_Init, V1)
# EF2.SetInterval(times_Init, V2)
# EF3.SetInterval(times_Init, V3)
# EF4.SetInterval(times_Init, V4)
# EF5.SetInterval(times_Init, V5)
# EF6.SetInterval(times_Init, V6)
# EF7.SetInterval(times_Init, V7)
# EF8.SetInterval(times_Init, V8)
# EF9.SetInterval(times_Init, V9)
EF1.SetInterval(times_Init, V1_SSV, V1)
EF2.SetInterval(times_Init, V2_SSV, V2)
EF3.SetInterval(times_Init, V3_SSV, V3)
EF4.SetInterval(times_Init, V4_SSV, V4)
EF5.SetInterval(times_Init, V5_SSV, V5)
EF6.SetInterval(times_Init, V6_SSV, V6)
EF7.SetInterval(times_Init, V7_SSV, V7)
EF8.SetInterval(times_Init, V8_SSV, V8)
EF9.SetInterval(times_Init, V9_SSV, V9)

dRSC_LAT_pwr.SetInterval(times_Init, 0)
Anal_test.SetInterval(times_Init, 5.0) # Machine status trigger
# DDS seq 1
DDS_REP.SetInterval(times_Init, REPFREQ)
DDS_MOT.SetInterval(times_Init, MOTFREQ)
DDS1_2.SetInterval(times_Init, PDH960_SciCavOffs_MHz*Unit.MHz())
# DDS seq 2
DDS_CavPrbAOM.SetInterval(times_Init, CavPrb_FreqOffset_MHz*Unit.MHz())
DDS_chan1.SetInterval(times_Init, 80.0+Img_det23_MHz)
DDS_OptPump1.SetInterval(times_Init, 80.0)
# DDS PDH seqc
DDS_PDH1560.SetInterval(times_Init, PDH1560_freq*Unit.MHz())
DDS_PDH960.SetInterval(times_Init, PDH960_freq*Unit.MHz())
DDS_PDH780.SetInterval(times_Init, PDH780_freq*Unit.MHz())
# RFSOC1
RFSOC1_VertTransAOM.SetInterval(times_Init, 80.0*Unit.MHz())
RFSOC1_HorzTransAOM.SetInterval(times_Init, 80.0*Unit.MHz())
RFSOC1_4.SetInterval(times_Init, PRB_CtrlAOM_f0_MHz*Unit.MHz())
RFSOC1_5.SetInterval(times_Init, RFSOC1529_HF*Unit.MHz())
RFSOC1_CavPrbEom.SetInterval(times_Prb_latetrig.afterStart(0), PRB_f0_MHz*Unit.MHz())
RFSOC1_784Lock.SetInterval(times_Init, PDH785_freq_MHz*Unit.MHz())
# Red Pitaya 1
#RP1_DDS_0.SetInterval(times_Init, ParamHeat_freq_kHz*Unit.kHz())
RP1_DDS_0.SetInterval(times_Init, 0.01*Unit.kHz())
DDS_HalfRng.SetInterval(times_Init, 0)
# SPCM seq
PC_bin_num.SetInterval(times_Init, PC_bin_number)
PC_max_rate.SetInterval(times_Init, PC_max_rate_MHz)
PC_n_channels.SetInterval(times_Init, PC_num_channels)
ADC_scope_save.SetInterval(times_Init, ADC_scope_sav)
ADC_ch_save.SetInterval(times_Init, ADC_ch_sav)

# Digital attenuator
ATT_1.SetInterval(times_Init, RFSOC1529_HF_att_dB)

if DetMode == 1:
    PC_save.SetInterval(times_Init, PC_save_switch)
    PT_save.SetInterval(times_Init, 0)
elif DetMode == 2:
    PC_save.SetInterval(times_Init, 0)
    PT_save.SetInterval(times_Init, PC_save_switch)
# Lab Bricks 
print(f'frequency we are trying for:{groundHF() + MW_det_kHz*Unit.kHz()}')
LB1_freq.SetInterval(times_Init, groundHF() + MW_det_kHz*Unit.kHz())
LB1_pow.SetInterval(times_Init, MW_pwr_dBm)
LB1_ttl.SetInterval(times_Init, MW_cw_ttl)
LB2_freq.SetInterval(times_Init, LB1529_lock_MHz)
LB2_pow.SetInterval(times_Init, LB1529_lock_dBm)
LB2_ttl.SetInterval(times_Init, 1)
# LB3_freq.SetInterval(times_Init, MWaves_Freq_MHz)
# LB3_pow.SetInterval(times_Init, MWaves_pwr_dBm)
# LB3_ttl.SetInterval(times_Init, MW_CW_ttl)
LB4_freq.SetInterval(times_Init, OP_REP_RF_freq_MHz)
LB4_pow.SetInterval(times_Init, OP_REP_RF_pwr_dBm)
LB4_ttl.SetInterval(times_Init, 1)
# ADF435X
#AD1_freq.SetInterval(times_Init, MWaves_Freq_MHz)
#AD1_pow.SetInterval(times_Init, MWaves_pwr_dBm)
#AD1_ttl.SetInterval(times_Init, MWaves_AD_ttl)
#Camera
Camera_gain.SetInterval(times_Init, Img_gain_dB)
Camera_save.SetInterval(times_Init, Img_save)
Shut_MOT_ttl.SetInterval(times_Init, 1) # TTL=1 is open
dRSC_OP_freq_ttl.SetInterval(times_Init, 0) # TTL=0 is 243 MHz for dRSC 2 -> 1', TTL=1 is 575 MHz tone for OP 2 -> 2'
Shut_HLAT_ttl.SetInterval(times_Init, 1)
# Kinesis stages
KINESIS_LAM_2.SetInterval(times_Init, WP_Lambda2_deg)
KINESIS_LAM_4.SetInterval(times_Init, WP_Lambda4_deg)

# DMD
DMD_waist.SetInterval(times_Init, DMD_Waist)
DMD_defocus.SetInterval(times_Init, DMD_Defocus)
DMD_l.SetInterval(times_Init, DMD_L)
DMD_p.SetInterval(times_Init, DMD_P)
DMD_center_x.SetInterval(times_Init, DMD_Center_X)
DMD_center_y.SetInterval(times_Init, DMD_Center_Y)
DMD_tilt_x.SetInterval(times_Init, DMD_Tilt_X)
DMD_tilt_y.SetInterval(times_Init, DMD_Tilt_Y)
DMD_phi.SetInterval(times_Init, DMD_Phi)
DMD_eps_phi.SetInterval(times_Init, DMD_Epsilon_Phi)

#SmarAct
SMARACT_vx.SetInterval(times_Init, SmarAct_x_V)
SMARACT_vy.SetInterval(times_Init, SmarAct_y_V)

#Shut_MOT_ttl.SetInterval(times_transport.afterward(1), 0)

# Microwaves for HFS spectroscopy
if MW_cw_ttl:
        #Ramp B field to dRSC pump direction
    BiasX.SetInterval(times_MW_bramp,PGC_BiasX_G,MW_BiasX_G)
    BiasY.SetInterval(times_MW_bramp,PGC_BiasY_G,MW_BiasY_G)
    BiasZ.SetInterval(times_MW_bramp,PGC_BiasZ_G,MW_BiasZ_G)
    MWaves_ttl.SetInterval(times_MW, 1)
    MWaves_ttl.SetInterval(times_MW.afterward(0), 0)
### Change MOT freq
#DDS_MOT.SetInterval(times_transport.afterStart(PGC_FreqRamp_ms*Unit.ms()),DDS_MOT.GetLastValue(),TMOTFreq)
#DDS_REP.SetInterval(times_transport.afterStart(PGC_FreqRamp_ms*Unit.ms()),DDS_REP.GetLastValue(),TREPFreq)

### dRSC in MOT ###
if MOT_dRSC_switch == 1:

    #Ensure MOT coil is off!
    if PGC_switch == 0:
        MOTCoil.SetInterval(times_MOTdRSC[0].afterStart(MOT_dRSC_initramptime_us*Unit.us()), MOTCoil.GetLastValue(), 0)
        MOT0_ttl.SetInterval(times_MOTdRSC[0].afterStart(MOT_dRSC_initramptime_us*Unit.us()).afterward(0), 0)
        REP0_ttl.SetInterval(times_MOTdRSC[0].afterStart(MOT_dRSC_initramptime_us*Unit.us()).afterward(0), 0)
    
    # Tune MOT to 2->2' line
    PUMP_det_MHz = Rb.DDS_MOT_22(PUMP_df_MHz)
    DDS_MOT.SetInterval(times_MOTdRSC[0].afterStart(MOT_dRSC_initramptime_us*Unit.us()), DDS_MOT.GetLastValue(), PUMP_det_MHz)
    
    # Vertical lattice
    LAT0_ttl.SetInterval(times_MOTdRSC[0].afterStart(0), dRSC_MOT_VLAT_ttl)
    LAT1_ttl.SetInterval(times_MOTdRSC[0].afterStart(0), dRSC_MOT_VLAT_ttl)
    LAT2_ttl.SetInterval(times_MOTdRSC[0].afterStart(0), dRSC_MOT_VLAT_ttl)
    LAT0_pwr.SetLogRamp(times_MOTdRSC[0].afterStart(MOT_dRSC_initramptime_us*Unit.us()), LAT0_pwr.GetLastValue(), dRSC_MOT_VLATmain_pwr)

    #Ramp B field to dRSC pump direction
    BiasX.SetInterval(times_MOTdRSC[0].afterStart(MOT_dRSC_initramptime_us*Unit.us()),PGC_BiasX_G,dRSC_MOT_BiasX_G)
    BiasY.SetInterval(times_MOTdRSC[0].afterStart(MOT_dRSC_initramptime_us*Unit.us()),PGC_BiasY_G,dRSC_MOT_BiasY_G)
    BiasZ.SetInterval(times_MOTdRSC[0].afterStart(MOT_dRSC_initramptime_us*Unit.us()),PGC_BiasZ_G,dRSC_MOT_BiasZ_G)

    ii = 0
    for this_time in times_MOTdRSC:
        if (ii%2) == 0: #This is a cooling stage
            #Ramp on and off the MOT dRSC Lattice
            dRSC_LAT2_ttl.SetInterval(this_time,dRSC_MOT_LAT_ttl)
            if ii > 0:
                dRSC_LAT2_pwr.SetInterval(this_time.afterStart(MOT_dRSC_ramptime_us*Unit.us()),0.0,dRSC_MOT_LAT_pwr)
            else:
                dRSC_LAT2_pwr.SetInterval(this_time.afterStart(MOT_dRSC_initramptime_us*Unit.us()),0.0,dRSC_MOT_LAT_pwr)
            dRSC_LAT2_pwr.SetInterval(this_time.beforeEnd(MOT_dRSC_ramptime_us*Unit.us()),dRSC_MOT_LAT_pwr,0.0)
            dRSC_LAT2_ttl.SetInterval(this_time.afterward(0),0)
            
            #Ramp on and off the MOT dRSC Pump
            if ii > 0:
                MOT1_ttl.SetInterval(this_time.afterStart((MOT_dRSC_ramptime_us+1000.0*MOT_dRSC_pumpdelay_ms)*Unit.us()).afterward(0),dRSC_MOT_Pump_ttl)
                MOT1_pwr.SetInterval(this_time.afterStart(MOT_dRSC_ramptime_us*Unit.us()),0.0,dRSC_MOT_Pump_pwr)
            else:
                MOT1_ttl.SetInterval(this_time.afterStart((MOT_dRSC_initramptime_us+1000.0*MOT_dRSC_pumpdelay_ms)*Unit.us()).afterward(0),dRSC_MOT_Pump_ttl)
                MOT1_pwr.SetInterval(this_time.afterStart(MOT_dRSC_initramptime_us*Unit.us()),0.0,dRSC_MOT_Pump_pwr)
            MOT1_pwr.SetInterval(this_time.beforeEnd(MOT_dRSC_ramptime_us*Unit.us()),dRSC_MOT_Pump_pwr,0.0)
            MOT1_ttl.SetInterval(this_time.beforeEnd(MOT_dRSC_ramptime_us*Unit.us()).afterStart(0),0)

            if ii == 2*MOT_dRSC_reps-2: # This is the last cooling stage
                LAT0_pwr.SetLogRamp(this_time.beforeEnd(MOT_dRSC_ramptime_us*Unit.us()), dRSC_MOT_VLATmain_pwr, LMP*dRSC_MOT_VLAT_endttl)
#		else: #this is a compression stage
            #Dont do anything during compression, left VLAT on. 
        ii += 1

### Turn blue on during transport if wanted
Blue_ttl.SetInterval(times_transport,Trans_Blue_ttl)


### Kick remaining MOT atoms upward for later recapture
if Trans_PGC_switch == 1:
    # Tune MOT and REP frequencies
    if Trans_PGC_delay_ms >= PGC_FreqRamp_ms:
        DDS_MOT.SetInterval(times_transport.afterStart(Trans_PGC_delay_ms*Unit.ms()),DDS_MOT.GetLastValue(),TMOTFreq)
        DDS_REP.SetInterval(times_transport.afterStart(Trans_PGC_delay_ms*Unit.ms()),DDS_REP.GetLastValue(),TREPFreq)
    else:
        DDS_MOT.SetInterval(times_transport.afterStart(PGC_FreqRamp_ms*Unit.ms()),DDS_MOT.GetLastValue(),TMOTFreq)
        DDS_REP.SetInterval(times_transport.afterStart(PGC_FreqRamp_ms*Unit.ms()),DDS_REP.GetLastValue(),TREPFreq)


    # Turn MOT and REP AOMs on
    MOT0_ttl.SetInterval(times_transport.afterStart(Trans_PGC_delay_ms*Unit.ms()).afterward(0), 1)
    REP0_ttl.SetInterval(times_transport.afterStart(Trans_PGC_delay_ms*Unit.ms()).afterward(0), 1)
    MOT0_pwr.SetInterval(times_transport.afterStart(Trans_PGC_delay_ms*Unit.ms()).afterward(0), Trans_PGC_MOTpwr)
    REP0_pwr.SetInterval(times_transport.afterStart(Trans_PGC_delay_ms*Unit.ms()).afterward(0), Trans_PGC_REPPwr)
    MOT0_ttl.SetInterval(times_transport.beforeEnd(1.5*Unit.ms()).afterStart(0), 0)
    REP0_ttl.SetInterval(times_transport.beforeEnd(1.5*Unit.ms()).afterStart(0), 0)
    # Tune Bz for atom kick
    BiasZ.SetInterval(times_transport.afterStart(Trans_PGC_delay_ms*Unit.ms()).afterward(1.0*Unit.ms()),PGC_BiasZ_G,dRSC_Bz_G)
    BiasX.SetInterval(times_transport.beforeEnd(1.5*Unit.ms()).afterStart(1.0*Unit.ms()),PGC_BiasX_G,dRSC_Bx_G)
    BiasY.SetInterval(times_transport.beforeEnd(1.5*Unit.ms()).afterStart(1.0*Unit.ms()),PGC_BiasY_G,dRSC_By_G)
#elif Img_switch == 0:
#else:
    # Tune MOT and REP frequencies
    # if Trans_PGC_delay_ms >= PGC_FreqRamp_ms:
    # 	DDS_MOT.SetInterval(times_transport.afterStart(Trans_PGC_delay_ms*Unit.ms()),DDS_MOT.GetLastValue(),TMOTFreq)
    # 	DDS_REP.SetInterval(times_transport.afterStart(Trans_PGC_delay_ms*Unit.ms()),DDS_REP.GetLastValue(),TREPFreq)
    # else:
    # 	DDS_MOT.SetInterval(times_transport.afterStart(PGC_FreqRamp_ms*Unit.ms()),DDS_MOT.GetLastValue(),TMOTFreq)
    # 	DDS_REP.SetInterval(times_transport.afterStart(PGC_FreqRamp_ms*Unit.ms()),DDS_REP.GetLastValue(),TREPFreq)

    ### Bias Field Ramp ###
#print(times_transport)
#print(times_transport.afterStart(times_transport.length()/2.0))
else:
    BiasX.SetInterval(times_transport.afterStart(times_transport.length()/2.0), PGC_BiasX_G, dRSC_Bx_G)
    BiasY.SetInterval(times_transport.afterStart(times_transport.length()/2.0), PGC_BiasY_G, dRSC_By_G)
    BiasZ.SetInterval(times_transport.afterStart(times_transport.length()/2.0), PGC_BiasZ_G, dRSC_Bz_G)

# MOT0_ttl.SetInterval(times_transport.afterward(0), 0)
#  	REP0_ttl.SetInterval(times_rt.afterward(0), 0)
# MOTCoil.SetInterval(times_transport.afterStart(Trans_PGC_delay_ms*Unit.ms()).afterward(0), MOT_CoilCurr)transpo


### Wait ###
if PGC_Wait2_switch == 1: 
    if PGC_first == 1:
        tt = 0
    else:
        tt = PGC_Wait2_offtime_ms
    while (tt+PGC_Wait2_ontime_ms+PGC_Wait2_offtime_ms) <= Wait2_ms:
        MOT0_ttl.SetInterval(times_Wait2.afterStart(tt*Unit.ms()).afterward(PGC_Wait2_ontime_ms*Unit.ms()), 1)
        REP0_ttl.SetInterval(times_Wait2.afterStart(tt*Unit.ms()).afterward(PGC_Wait2_ontime_ms*Unit.ms()), 1)
        tt += PGC_Wait2_ontime_ms
        MOT0_ttl.SetInterval(times_Wait2.afterStart(tt*Unit.ms()).afterward(0), 0)
        REP0_ttl.SetInterval(times_Wait2.afterStart(tt*Unit.ms()).afterward(0), 0)
        tt += PGC_Wait2_offtime_ms

LAT0_ttl.SetInterval(times_Wait1, Lat_TTL_Wait1)
LAT1_ttl.SetInterval(times_Wait1, Lat_TTL_Wait1)
LAT2_ttl.SetInterval(times_Wait1, Lat_TTL_Wait1)

# Parametric heating during tranport
if Trans_ParamHeat_switch == 1:
    RP1_DDS_0.SetInterval(times_Wait1, ParamHeat_freq_kHz*Unit.kHz())
    RP1_DDS_0.SetInterval(times_Wait1.afterward(0), 0.01*Unit.kHz())

### Depump during transport
MOT2_ttl.SetInterval(times_transport, Trans_GDEP_ttl)
MOT2_ttl.SetInterval(times_transport.afterward(0), 0)
MOT2_pwr.SetInterval(times_transport, Trans_GDEP_pwr)

### Shutter to block MOT light
if times_transport.length() > 5*Unit.ms():
    #Shut_MOT_ttl.SetInterval(times_transport.afterStart(0).afterward(0), 1)
    Shut_MOT_ttl.SetInterval(times_transport.afterStart(Shutter_delay_ms*Unit.ms()).afterward(0), 0)

### degenerate Raman sideband cooling 
if dRSC_switch == 1:
    i = 0
    for this_time in times_dRSC:

        # Use proper RF source for driving the EOM
        AUX_ttl.SetInterval(this_time, dRSC_2to2p_ttl) # dRSC
        AUX_ttl.SetInterval(this_time.afterward(0), 0) # dRSC

        AUX2_ttl.SetInterval(this_time, 1) # MUST BE ONE TO ENSURE THAT LAB BRICK IS TRIGGERED ON
        AUX2_ttl.SetInterval(this_time.beforeEnd(dRSC_OP_REP_EarlyEnd_ms*Unit.ms()), 0)

        dRSC_OP_freq_ttl.SetInterval(this_time, 0) # TTL=0 is 243 MHz for dRSC 2 -> 1', TTL=1 is 575 MHz tone for OP 2 -> 2'

        # PGC
        MOT0_ttl.SetInterval(this_time, dRSC_PGC_switch)
        REP0_ttl.SetInterval(this_time,dRSC_PGC_switch) 
        MOT0_ttl.SetInterval(this_time.afterward(0), c1_PGC_switch)
        REP0_ttl.SetInterval(this_time.afterward(0), c1_PGC_switch) 

        # Pump laser
        D1Laser1_ttl.SetInterval(this_time.afterStart(dRSC_LAT_rampON_us*Unit.us()), dRSC_Pump_ttl)
        D1Laser1_ttl.SetInterval(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()),0)
        # D1Laser1_pwr.SetInterval(this_time, dRSC_Pump_pwr)
        # D1Laser1_pwr.SetInterval(this_time.beforeEnd(0), 0)
        D1Laser1_pwr.SetInterval(this_time.afterStart(dRSC_Pump_ramp_ms*Unit.ms()), dRSC_Pump_ramp_pwr, dRSC_Pump_pwr)
        D1Laser1_pwr.SetInterval(this_time.beforeEnd(dRSC_Pump_ramp_ms*Unit.ms()), dRSC_Pump_pwr, dRSC_Pump_ramp_pwr)
        D1Laser1_pwr.SetInterval(this_time.afterward(0), 0)



        # Horizontal lattice 
        dRSC_LAT_ttl.SetInterval(this_time.afterStart(0), dRSC_HLAT_ttl)
        dRSC_LAT_pwr.SetLogRamp(this_time.afterStart(dRSC_LAT_rampON_us*Unit.us()), dRSC_LAT_pwr.GetLastValue(), dRSC_HLAT_pwr)
        dRSC_LAT_pwr.SetLogRamp(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()), dRSC_HLAT_pwr, c1_HLAT_pwr if i<int(dRSC_repetitions)-1 else 0)
        dRSC_LAT_ttl.SetInterval(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()), np.maximum(dRSC_HLAT_ttl,c1_HLAT_ttl))
        dRSC_LAT_ttl.SetInterval(this_time.afterward(0), c1_HLAT_ttl if i<int(dRSC_repetitions)-1 else 0)
        # Parametric heating with HLAT
        if dRSC_ParamHeat_switch == 1:
            RP1_DDS_0.SetInterval(this_time, ParamHeat_freq_kHz*Unit.kHz())
            #RP1_DDS_0.SetInterval(this_time.afterward(0), 0.01*Unit.kHz())
        # Vertical lattice
        LAT0_ttl.SetInterval(this_time.afterStart(0), dRSC_VLAT_ttl)
        LAT1_ttl.SetInterval(this_time.afterStart(0), dRSC_VLAT_ttl)
        LAT2_ttl.SetInterval(this_time.afterStart(0), dRSC_VLAT_ttl)
        LAT0_pwr.SetLogRamp(this_time.afterStart(dRSC_LAT_rampON_us*Unit.us()), LAT0_pwr.GetLastValue(), dRSC_VLATmain_pwr)
        if i<int(dRSC_repetitions)-1: # Dont compress on the last rep
            LAT0_pwr.SetLogRamp(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()), dRSC_VLATmain_pwr, c1_VLATmain_pwr)
            LAT0_ttl.SetInterval(this_time.afterward(0), c1_VLAT_ttl)
            LAT1_ttl.SetInterval(this_time.afterward(0), c1_VLAT_ttl)
            LAT2_ttl.SetInterval(this_time.afterward(0), c1_VLAT_ttl)
        else:
            LAT0_ttl.SetInterval(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()), np.maximum(dRSC_VLAT_ttl,c1_VLAT_ttl))
            LAT1_ttl.SetInterval(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()), np.maximum(dRSC_VLAT_ttl,c1_VLAT_ttl))
            LAT2_ttl.SetInterval(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()), np.maximum(dRSC_VLAT_ttl,c1_VLAT_ttl))

        # ELAT lattice
        Sacher2_ttl.SetInterval(this_time.afterStart(0), dRSC_ELAT_ttl)
        Sacher2_pwr.SetLogRamp(this_time.afterStart(dRSC_LAT_rampON_us*Unit.us()), 0, dRSC_ELAT_pwr)
        Sacher2_pwr.SetLogRamp(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()), dRSC_ELAT_pwr, c1_ELAT_pwr)
        Sacher2_ttl.SetInterval(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()), np.maximum(c1_ELAT_ttl,dRSC_ELAT_ttl))
        Sacher2_ttl.SetInterval(this_time.afterward(0), c1_ELAT_ttl)

        # CODT
        ODT2_ttl.SetInterval(this_time.afterStart(0), dRSC_CODT_ttl)
        ODT2_pwr.SetLogRamp(this_time.afterStart(dRSC_LAT_rampON_us*Unit.us()), ODT2_pwr.GetLastValue(), dRSC_CODT_pwr)
        ODT2_ttl.SetInterval(this_time.afterward(0), c1_CODT_ttl)
        # ODT2_pwr.SetLogRamp(this_time.afterward(c1_ramp_time_ms*Unit.ms()), dRSC_CODT_pwr, c1_CODT_pwr)
        # # "compression" stage; if duration is zero, this just sets the desired trap configuration
        # NOTHING HAPPENS DURING COMPRESSION! Just determines the endpoint of previous dRSC (and startpoint of next one)
        # as well as a holding time
        i += 1


# trap ramping stage, if we want to adiabatically swap from VLAT to ELAT
if Ramp1_switch == 1:
    LAT0_ttl.SetInterval(times_ramp1.afterStart(0), Ramp1_VLAT_TTL)
    LAT1_ttl.SetInterval(times_ramp1.afterStart(0), Ramp1_Retro_TTL)
    LAT2_ttl.SetInterval(times_ramp1.afterStart(0), Ramp1_Retro_TTL)
    Sacher2_ttl.SetInterval(times_ramp1.afterStart(0), Ramp1_ELAT_TTL)

    samprate = np.minimum(0.04, Ramp1_steps/Ramp1_dur_us)
    LAT0_pwr.SetLogRamp(times_ramp1, LAT0_pwr.GetLastValue(), Ramp1_VLAT_pwr, sample_rate=samprate)
    LAT1_pwr.SetLogRamp(times_ramp1, LAT1_pwr.GetLastValue(), Ramp1_Retro_pwr, sample_rate=samprate)
    LAT2_pwr.SetLogRamp(times_ramp1, LAT2_pwr.GetLastValue(), Ramp1_Retro_pwr, sample_rate=samprate)
    Sacher2_pwr.SetLogRamp(times_ramp1, Sacher2_pwr.GetLastValue(), Ramp1_ELAT_pwr, sample_rate=samprate)
if Ramp2_switch == 1:
    samprate = np.minimum(0.04, Ramp2_steps/Ramp2_dur_us)
    #print samprate
    LAT0_pwr.SetLogRamp(times_ramp2, Ramp1_VLAT_pwr, Ramp2_VLAT_pwr, sample_rate=samprate)
    LAT1_pwr.SetLogRamp(times_ramp2, Ramp1_Retro_pwr, Ramp2_Retro_pwr, sample_rate=samprate)
    LAT2_pwr.SetLogRamp(times_ramp2, Ramp1_Retro_pwr, Ramp2_Retro_pwr, sample_rate=samprate)
    Sacher2_pwr.SetLogRamp(times_ramp2, Ramp1_ELAT_pwr, Ramp2_ELAT_pwr, sample_rate=samprate)
if Ramp3_switch == 1:
    samprate = np.minimum(0.04, Ramp3_steps/Ramp3_dur_us)
    LAT0_pwr.SetLogRamp(times_ramp3, Ramp2_VLAT_pwr, Ramp3_VLAT_pwr, sample_rate=samprate)
    LAT1_pwr.SetLogRamp(times_ramp3, Ramp2_Retro_pwr, Ramp3_Retro_pwr, sample_rate=samprate)
    LAT2_pwr.SetLogRamp(times_ramp3, Ramp2_Retro_pwr, Ramp3_Retro_pwr, sample_rate=samprate)
    Sacher2_pwr.SetLogRamp(times_ramp3, Ramp2_ELAT_pwr, Ramp3_ELAT_pwr, sample_rate=samprate)
if Ramp1_switch or Ramp2_switch or Ramp3_switch: #or RampCODT_switch:
    LAT0_ttl.SetInterval(times_rampall.afterward(0), RampFinal_VLAT_TTL)
    LAT1_ttl.SetInterval(times_rampall.afterward(0), RampFinal_Retro_TTL)
    LAT2_ttl.SetInterval(times_rampall.afterward(0), RampFinal_Retro_TTL)
    Sacher2_ttl.SetInterval(times_rampall.afterward(0), RampFinal_ELAT_TTL)
    #ODT2_ttl.SetInterval(times_rampall.afterStart(0), RampFinal_CODT_TTL)

### degenerate Raman sideband cooling during trap ramp
if TRdRSC_switch == 1:
    this_time = times_TRdRSC
    # Use proper RF source for driving the EOM
    AUX_ttl.SetInterval(this_time, TRdRSC_2to2p_ttl) # dRSC
    AUX_ttl.SetInterval(this_time.afterward(0), 0) # dRSC

    AUX2_ttl.SetInterval(this_time, 1) # MUST BE ONE TO ENSURE THAT LAB BRICK IS TRIGGERED ON
    AUX2_ttl.SetInterval(this_time.beforeEnd(TRdRSC_OP_REP_EarlyEnd_ms*Unit.ms()), 0)

    dRSC_OP_freq_ttl.SetInterval(this_time, 0) # TTL=0 is 243 MHz for dRSC 2 -> 1', TTL=1 is 575 MHz tone for OP 2 -> 2'

    # Pump laser
    D1Laser1_ttl.SetInterval(this_time.afterStart(TRdRSC_LAT_rampON_us*Unit.us()), TRdRSC_Pump_ttl)
    D1Laser1_ttl.SetInterval(this_time.beforeEnd(TRdRSC_LAT_rampOFF_us*Unit.us()),0)
    # D1Laser1_pwr.SetInterval(this_time, TRdRSC_Pump_pwr)
    # D1Laser1_pwr.SetInterval(this_time.beforeEnd(0), 0)
    D1Laser1_pwr.SetInterval(this_time.afterStart(TRdRSC_Pump_ramp_ms*Unit.ms()), TRdRSC_Pump_ramp_pwr, TRdRSC_Pump_pwr)
    D1Laser1_pwr.SetInterval(this_time.beforeEnd(TRdRSC_Pump_ramp_ms*Unit.ms()), TRdRSC_Pump_pwr, TRdRSC_Pump_ramp_pwr)
    D1Laser1_pwr.SetInterval(this_time.afterward(0), 0)


    samprate = 0.010
    # Horizontal lattice 
    dRSC_LAT_ttl.SetInterval(this_time.afterStart(0), TRdRSC_HLAT_ttl)
    dRSC_LAT_pwr.SetLogRamp(this_time.afterStart(TRdRSC_LAT_rampON_us*Unit.us()), dRSC_LAT_pwr.GetLastValue(), TRdRSC_HLAT_pwr, sample_rate=samprate)
    dRSC_LAT_pwr.SetLogRamp(this_time.beforeEnd(TRdRSC_LAT_rampOFF_us*Unit.us()), TRdRSC_HLAT_pwr, 0, sample_rate=samprate)
    dRSC_LAT_ttl.SetInterval(this_time.beforeEnd(TRdRSC_LAT_rampOFF_us*Unit.us()), TRdRSC_HLAT_ttl)
    dRSC_LAT_ttl.SetInterval(this_time.afterward(0), 0)

    # Vertical lattice
    LAT0_ttl.SetInterval(this_time.afterStart(0), TRdRSC_VLAT_ttl)
    LAT1_ttl.SetInterval(this_time.afterStart(0), TRdRSC_VLAT_ttl)
    LAT2_ttl.SetInterval(this_time.afterStart(0), TRdRSC_VLAT_ttl)
    _t_start = this_time.afterStart(TRdRSC_LAT_rampON_us*Unit.us())
    _t_main = _t_start.afterward(TRdRSC_Dur_ms*Unit.ms() - TRdRSC_LAT_rampON_us*Unit.us())
    LAT0_pwr.SetLogRamp(_t_start, LAT0_pwr.GetLastValue(), TRdRSC_VLATmain_pwr, sample_rate=samprate)
    LAT0_pwr.SetLogRamp(_t_main, TRdRSC_VLATmain_pwr, 0, sample_rate=samprate)

    LAT0_ttl.SetInterval(this_time.beforeEnd(TRdRSC_LAT_rampOFF_us*Unit.us()), TRdRSC_VLAT_ttl)
    LAT1_ttl.SetInterval(this_time.beforeEnd(TRdRSC_LAT_rampOFF_us*Unit.us()), TRdRSC_VLAT_ttl)
    LAT2_ttl.SetInterval(this_time.beforeEnd(TRdRSC_LAT_rampOFF_us*Unit.us()), TRdRSC_VLAT_ttl)
    
    LAT0_ttl.SetInterval(this_time.afterward(0), 0)
    LAT1_ttl.SetInterval(this_time.afterward(0), 0)
    LAT2_ttl.SetInterval(this_time.afterward(0), 0)
    # ELAT lattice
    Sacher2_ttl.SetInterval(this_time.afterStart(0), TRdRSC_ELAT_ttl)
    Sacher2_pwr.SetLogRamp(this_time.afterStart(dRSC_LAT_rampON_us*Unit.us()), Sacher2_pwr.GetLastValue(), TRdRSC_ELAT_pwr, sample_rate=samprate)
    #Sacher2_pwr.SetLogRamp(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()), dRSC_ELAT_pwr, c1_ELAT_pwr)
    # Sacher2_ttl.SetInterval(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()), dRSC_ELAT_ttl)
    Sacher2_ttl.SetInterval(this_time.afterward(0), TRdRSC_ELAT_ttl)



### degenerate Raman sideband cooling in the ELAT
if ELdRSC_switch == 1:
    i = 0
    for this_time in times_ELdRSC:
        if i==0: # ramp fields from dRSC to ELdRSC
            BiasX.SetInterval(this_time.afterStart(1*Unit.ms()), dRSC_Bx_G, ELdRSC_Bx_G)
            BiasY.SetInterval(this_time.afterStart(1*Unit.ms()), dRSC_By_G, ELdRSC_By_G)
            BiasZ.SetInterval(this_time.afterStart(1*Unit.ms()), dRSC_Bz_G, ELdRSC_Bz_G)

        # Use proper RF source for driving the EOM
        # Use proper RF source for driving the EOM
        AUX_ttl.SetInterval(this_time, dRSC_2to2p_ttl) # dRSC
        AUX_ttl.SetInterval(this_time.afterward(0), 0) # dRSC

        #AUX_ttl.SetInterval(this_time, 0) # dRSC
        AUX2_ttl.SetInterval(this_time, 1) # MUST BE ONE TO ENSURE THAT LAB BRICK IS TRIGGERED ON
        AUX2_ttl.SetInterval(this_time.beforeEnd(ELdRSC_OP_REP_EarlyEnd_ms*Unit.ms()), 0)

        # PGC
        # MOT0_ttl.SetInterval(this_time, ELdRSC_PGC_switch)
        # REP0_ttl.SetInterval(this_time,ELdRSC_PGC_switch) 
        # MOT0_ttl.SetInterval(this_time.afterward(0), c1_PGC_switch)
        # REP0_ttl.SetInterval(this_time.afterward(0), c1_PGC_switch) 

        # Pump laser
        D1Laser1_ttl.SetInterval(this_time.afterStart(ELdRSC_LAT_rampON_us*Unit.us()), ELdRSC_Pump_ttl)
        D1Laser1_ttl.SetInterval(this_time.beforeEnd(ELdRSC_LAT_rampOFF_us*Unit.us()),0)
        # D1Laser1_pwr.SetInterval(this_time, ELdRSC_Pump_pwr)
        D1Laser1_pwr.SetInterval(this_time.afterStart(ELdRSC_Pump_ramp_ms*Unit.ms()), ELdRSC_Pump_ramp_pwr, ELdRSC_Pump_pwr)
        D1Laser1_pwr.SetInterval(this_time.beforeEnd(ELdRSC_Pump_ramp_ms*Unit.ms()), ELdRSC_Pump_pwr, ELdRSC_Pump_ramp_pwr)
        D1Laser1_pwr.SetInterval(this_time.afterward(0), 0)

        # Horizontal lattice 
        dRSC_LAT_ttl.SetInterval(this_time.afterStart(0), ELdRSC_HLAT_ttl)
        dRSC_LAT_ttl.SetInterval(this_time.beforeEnd(ELdRSC_LAT_rampOFF_us*Unit.us()), np.maximum(ELdRSC_HLAT_ttl,c2_HLAT_ttl))
        dRSC_LAT_ttl.SetInterval(this_time.afterward(0), c2_HLAT_ttl)

        # dRSC_LAT_pwr.SetLogRamp(this_time.afterStart(ELdRSC_LAT_rampON_us*Unit.us()), 0, ELdRSC_HLAT_pwr)
        # dRSC_LAT_pwr.SetLogRamp(this_time.beforeEnd(ELdRSC_LAT_rampOFF_us*Unit.us()), ELdRSC_HLAT_pwr, c2_HLAT_pwr)

        _tstart = this_time.afterStart(ELdRSC_LAT_rampON_us*Unit.us())
        dRSC_LAT_pwr.SetLogRamp(_tstart, dRSC_LAT_pwr.GetLastValue(), ELdRSC_HLAT_low_pwr)
        dRSC_LAT_pwr.SetInterval(_tstart.afterward(ELdRSC_HLAT_dutyc/100*(ELdRSC_Dur_ms-(2*ELdRSC_LAT_rampON_us + ELdRSC_LAT_rampOFF_us)*0.001)*Unit.ms()).afterward(ELdRSC_LAT_rampON_us*Unit.us()), ELdRSC_HLAT_low_pwr, ELdRSC_HLAT_pwr)
        dRSC_LAT_pwr.SetLogRamp(this_time.beforeEnd(ELdRSC_LAT_rampOFF_us*Unit.us()), ELdRSC_HLAT_pwr, c2_HLAT_pwr)

        
        # CODT
        ODT2_ttl.SetInterval(this_time.afterStart(0), ELdRSC_CODT_ttl)
        ODT2_pwr.SetLogRamp(this_time.afterStart(ELdRSC_LAT_rampON_us*Unit.us()), 0, ELdRSC_CODT_pwr)
        # Vertical lattice
        # LAT0_ttl.SetInterval(this_time.afterStart(0), dRSC_VLAT_ttl)
        # LAT1_ttl.SetInterval(this_time.afterStart(0), dRSC_VLAT_ttl)
        # LAT2_ttl.SetInterval(this_time.afterStart(0), dRSC_VLAT_ttl)
        # LAT0_pwr.SetLogRamp(this_time.afterStart(dRSC_LAT_rampON_us*Unit.us()), LAT0_pwr.GetLastValue(), dRSC_VLATmain_pwr)
        # if i<int(dRSC1_repetitions)-1: # Dont compress on the last rep
        # 	LAT0_pwr.SetLogRamp(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()), dRSC_VLATmain_pwr, c1_VLATmain_pwr)
        # LAT0_ttl.SetInterval(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()), np.maximum(dRSC_VLAT_ttl,c1_VLAT_ttl))
        # LAT1_ttl.SetInterval(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()), np.maximum(dRSC_VLAT_ttl,c1_VLAT_ttl))
        # LAT2_ttl.SetInterval(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()), np.maximum(dRSC_VLAT_ttl,c1_VLAT_ttl))
        
        # LAT0_ttl.SetInterval(this_time.afterward(0), c1_VLAT_ttl)
        # LAT1_ttl.SetInterval(this_time.afterward(0), c1_VLAT_ttl)
        # LAT2_ttl.SetInterval(this_time.afterward(0), c1_VLAT_ttl)
        # ELAT lattice
        Sacher2_ttl.SetInterval(this_time.afterStart(0), ELdRSC_ELAT_ttl)
        Sacher2_ttl.SetInterval(this_time.beforeEnd(ELdRSC_LAT_rampOFF_us*Unit.us()), np.maximum(c2_ELAT_ttl,ELdRSC_ELAT_ttl))
        Sacher2_ttl.SetInterval(this_time.afterward(0), c2_ELAT_ttl)
        Sacher2_pwr.SetLogRamp(this_time.afterStart(ELdRSC_LAT_rampON_us*Unit.us()), Sacher2_pwr.GetLastValue(), ELdRSC_ELAT_pwr)
        Sacher2_pwr.SetLogRamp(this_time.beforeEnd(ELdRSC_LAT_rampOFF_us*Unit.us()), ELdRSC_ELAT_pwr, c2_ELAT_pwr)
        




        # ramp the CODT on
        if i<len(times_ELdRSC)-1:
            ODT2_ttl.SetInterval(this_time.afterward(0), c2_CODT_ttl)
            ODT2_pwr.SetLogRamp(this_time.afterward(c2_ramp_time_ms*Unit.ms()), ELdRSC_CODT_pwr, c2_CODT_pwr)
        # # "compression" stage; if duration is zero, this just sets the desired trap configuration
        # NOTHING HAPPENS DURING COMPRESSION! Just determines the endpoint of previous dRSC (and startpoint of next one)
        # as well as a holding time
        i += 1

# Parametric heating in ELAT after ELdRSC
if ELAT_ParamHeat_switch == 1:
    RP1_DDS_0.SetInterval(times_Wait2, ParamHeat_freq_kHz*Unit.kHz())
    RP1_DDS_0.SetInterval(times_Wait2.afterward(0), 0.01*Unit.kHz())

# ramp cavity ODT on, ELAT should be still on there at 'c2' values
if RampCODT_switch == 1:
    LAT0_ttl.SetInterval(times_ramp_odt.afterStart(0), RampCODT_VLAT_TTL)
    LAT1_ttl.SetInterval(times_ramp_odt.afterStart(0), RampCODT_VLAT_Retro_TTL)
    LAT2_ttl.SetInterval(times_ramp_odt.afterStart(0), RampCODT_VLAT_Retro_TTL)
    Sacher2_ttl.SetInterval(times_ramp_odt.afterStart(0), RampCODT_ELAT_TTL)
    ODT2_ttl.SetInterval(times_ramp_odt.afterStart(0), RampCODT_ODT_TTL)

    samprate = np.minimum(0.04, RampCODT_steps/RampCODT_dur_us)
    # LAT0_pwr.SetLogRamp(times_ramp_odt, LAT0_pwr.GetLastValue(), RampCODT_VLAT_pwr, sample_rate=samprate)
    # LAT1_pwr.SetLogRamp(times_ramp_odt, LAT1_pwr.GetLastValue(), RampCODT_VLAT_Retro_pwr, sample_rate=samprate)
    # LAT2_pwr.SetLogRamp(times_ramp_odt, LAT2_pwr.GetLastValue(), RampCODT_VLAT_Retro_pwr, sample_rate=samprate)
    # ODT2_pwr.SetLogRamp(times_ramp_odt, ODT2_pwr.GetLastValue(), RampCODT_ODT_pwr, sample_rate=samprate)
    # Sacher2_pwr.SetLogRamp(times_ramp_odt, Sacher2_pwr.GetLastValue(), RampCODT_ELAT_pwr, sample_rate=samprate)

    LAT0_pwr.SetInterval(times_ramp_odt, LAT0_pwr.GetLastValue(), RampCODT_VLAT_pwr)
    LAT1_pwr.SetInterval(times_ramp_odt, LAT1_pwr.GetLastValue(), RampCODT_VLAT_Retro_pwr)
    LAT2_pwr.SetInterval(times_ramp_odt, LAT2_pwr.GetLastValue(), RampCODT_VLAT_Retro_pwr)
    ODT2_pwr.SetInterval(times_ramp_odt, ODT2_pwr.GetLastValue(), RampCODT_ODT_pwr)
    Sacher2_pwr.SetInterval(times_ramp_odt, Sacher2_pwr.GetLastValue(), RampCODT_ELAT_pwr)

if RampCODT2_switch == 1:
    LAT0_ttl.SetInterval(times_ramp_odt_2.afterStart(0), RampCODT2_VLAT_TTL)
    LAT1_ttl.SetInterval(times_ramp_odt_2.afterStart(0), RampCODT2_VLAT_Retro_TTL)
    LAT2_ttl.SetInterval(times_ramp_odt_2.afterStart(0), RampCODT2_VLAT_Retro_TTL)
    Sacher2_ttl.SetInterval(times_ramp_odt_2.afterStart(0), RampCODT2_ELAT_TTL)
    ODT2_ttl.SetInterval(times_ramp_odt_2.afterStart(0), RampCODT2_ODT_TTL)

    samprate = np.minimum(0.04, RampCODT2_steps/RampCODT2_dur_us)
    LAT0_pwr.SetLogRamp(times_ramp_odt_2, LAT0_pwr.GetLastValue(), RampCODT2_VLAT_pwr, sample_rate=samprate)
    LAT1_pwr.SetLogRamp(times_ramp_odt_2, LAT1_pwr.GetLastValue(), RampCODT2_VLAT_Retro_pwr, sample_rate=samprate)
    LAT2_pwr.SetLogRamp(times_ramp_odt_2, LAT2_pwr.GetLastValue(), RampCODT2_VLAT_Retro_pwr, sample_rate=samprate)
    ODT2_pwr.SetLogRamp(times_ramp_odt_2, ODT2_pwr.GetLastValue(), RampCODT2_ODT_pwr, sample_rate=samprate)
    Sacher2_pwr.SetLogRamp(times_ramp_odt_2, Sacher2_pwr.GetLastValue(), RampCODT2_ELAT_pwr, sample_rate=samprate)

if RampCODT3_switch == 1:
    LAT0_ttl.SetInterval(times_ramp_odt_3.afterStart(0), RampCODT3_VLAT_TTL)
    LAT1_ttl.SetInterval(times_ramp_odt_3.afterStart(0), RampCODT3_VLAT_Retro_TTL)
    LAT2_ttl.SetInterval(times_ramp_odt_3.afterStart(0), RampCODT3_VLAT_Retro_TTL)
    Sacher2_ttl.SetInterval(times_ramp_odt_3.afterStart(0), RampCODT3_ELAT_TTL)
    ODT2_ttl.SetInterval(times_ramp_odt_3.afterStart(0), RampCODT3_ODT_TTL)

    samprate = np.minimum(0.04, RampCODT3_steps/RampCODT3_dur_us)
    LAT0_pwr.SetLogRamp(times_ramp_odt_3, LAT0_pwr.GetLastValue(), RampCODT3_VLAT_pwr, sample_rate=samprate)
    LAT1_pwr.SetLogRamp(times_ramp_odt_3, LAT1_pwr.GetLastValue(), RampCODT3_VLAT_Retro_pwr, sample_rate=samprate)
    LAT2_pwr.SetLogRamp(times_ramp_odt_3, LAT2_pwr.GetLastValue(), RampCODT3_VLAT_Retro_pwr, sample_rate=samprate)
    ODT2_pwr.SetLogRamp(times_ramp_odt_3, ODT2_pwr.GetLastValue(), RampCODT3_ODT_pwr, sample_rate=samprate)
    Sacher2_pwr.SetLogRamp(times_ramp_odt_3, Sacher2_pwr.GetLastValue(), RampCODT3_ELAT_pwr, sample_rate=samprate)

# Parametric heating during tranport
if RampCODT3_ParamHeat_switch == 1:
    RP1_DDS_0.SetInterval(times_ramp_odt_3, ParamHeat_freq_kHz*Unit.kHz())
    RP1_DDS_0.SetInterval(times_ramp_odt_3.afterward(0), 0.01*Unit.kHz())
 

if RampCODT_switch or RampCODT2_switch or RampCODT3_switch:
    LAT0_ttl.SetInterval(times_codt_rampall.afterward(0), RampCODTFinal_VLAT_TTL)
    LAT1_ttl.SetInterval(times_codt_rampall.afterward(0), RampCODTFinal_Retro_TTL)
    LAT2_ttl.SetInterval(times_codt_rampall.afterward(0), RampCODTFinal_Retro_TTL)
    Sacher2_ttl.SetInterval(times_codt_rampall.afterward(0), RampCODTFinal_ELAT_TTL)
    ODT2_ttl.SetInterval(times_codt_rampall.afterStart(0), RampCODTFinal_CODT_TTL)

### degenerate Raman sideband cooling after loading into CODT
if CdRSC_switch == 1:
    i = 0
    for this_time in times_CdRSC:
        if i==0: # ramp fields from dRSC to CdRSC
            BiasX.SetInterval(this_time.afterStart(1*Unit.ms()), dRSC_Bx_G, CdRSC_Bx_G)
            BiasY.SetInterval(this_time.afterStart(1*Unit.ms()), dRSC_By_G, CdRSC_By_G)
            BiasZ.SetInterval(this_time.afterStart(1*Unit.ms()), dRSC_Bz_G, CdRSC_Bz_G)

        # Use proper RF source for driving the EOM
        AUX_ttl.SetInterval(this_time, 0) # dRSC
        AUX2_ttl.SetInterval(this_time, 1) # MUST BE ONE TO ENSURE THAT LAB BRICK IS TRIGGERED ON
        AUX2_ttl.SetInterval(this_time.beforeEnd(CdRSC_OP_REP_EarlyEnd_ms*Unit.ms()), 0)

        # PGC
        # MOT0_ttl.SetInterval(this_time, CdRSC_PGC_switch)
        # REP0_ttl.SetInterval(this_time,CdRSC_PGC_switch) 
        # MOT0_ttl.SetInterval(this_time.afterward(0), c1_PGC_switch)
        # REP0_ttl.SetInterval(this_time.afterward(0), c1_PGC_switch) 

        
        # Strobing
        if CdRSC_strobe_switch:
            ODT2_ttl.SetModulation(this_time, STP_CODT_ODT)
            LAT0_ttl.SetModulation(this_time, STP_CODT_VLAT)
            LAT1_ttl.SetModulation(this_time, STP_CODT_VLAT)
            LAT2_ttl.SetModulation(this_time, STP_CODT_VLAT)
            dRSC_LAT_ttl.SetModulation(this_time, STP_CODT_HLAT)
            D1Laser1_ttl.SetModulation(this_time, STP_CODT_PUMP)
        else:
            ODT2_ttl.SetInterval(this_time.afterStart(0), CdRSC_CODT_ttl)
            LAT0_ttl.SetInterval(this_time.afterStart(0), CdRSC_VLAT_ttl)
            LAT1_ttl.SetInterval(this_time.afterStart(0), CdRSC_VLAT_ttl)
            LAT2_ttl.SetInterval(this_time.afterStart(0), CdRSC_VLAT_ttl)
            LAT0_ttl.SetInterval(this_time.beforeEnd(CdRSC_LAT_rampOFF_us*Unit.us()), np.maximum(CdRSC_VLAT_ttl,c3_VLAT_ttl))
            LAT1_ttl.SetInterval(this_time.beforeEnd(CdRSC_LAT_rampOFF_us*Unit.us()), np.maximum(CdRSC_VLAT_ttl,c3_VLAT_ttl))
            LAT2_ttl.SetInterval(this_time.beforeEnd(CdRSC_LAT_rampOFF_us*Unit.us()), np.maximum(CdRSC_VLAT_ttl,c3_VLAT_ttl))

            dRSC_LAT_ttl.SetInterval(this_time.afterStart(0), CdRSC_HLAT_ttl)
            dRSC_LAT_ttl.SetInterval(this_time.beforeEnd(CdRSC_LAT_rampOFF_us*Unit.us()), np.maximum(CdRSC_HLAT_ttl,c3_HLAT_ttl))
            dRSC_LAT_ttl.SetInterval(this_time.afterward(0), c3_HLAT_ttl)
            D1Laser1_ttl.SetInterval(this_time.afterStart(CdRSC_LAT_rampON_us*Unit.us()), CdRSC_Pump_ttl)
            D1Laser1_ttl.SetInterval(this_time.beforeEnd(CdRSC_LAT_rampOFF_us*Unit.us()),0)
        
        # Pump laser
        D1Laser1_pwr.SetInterval(this_time, CdRSC_Pump_pwr)
        
        # Horizontal lattice 
        dRSC_LAT_pwr.SetLogRamp(this_time.afterStart(CdRSC_LAT_rampON_us*Unit.us()), dRSC_LAT_pwr.GetLastValue(), CdRSC_HLAT_pwr)
        dRSC_LAT_pwr.SetLogRamp(this_time.beforeEnd(CdRSC_LAT_rampOFF_us*Unit.us()), CdRSC_HLAT_pwr, c3_HLAT_pwr)
        
        # CODT
        ODT2_pwr.SetLogRamp(this_time.afterStart(CdRSC_LAT_rampON_us*Unit.us()), ODT2_pwr.GetLastValue(), CdRSC_CODT_pwr)
        # Vertical lattice
        LAT0_pwr.SetLogRamp(this_time.afterStart(CdRSC_LAT_rampON_us*Unit.us()), LAT0_pwr.GetLastValue(), CdRSC_VLAT_pwr)
        # if i<int(CdRSC_repetitions)-1: # Dont compress on the last rep
        LAT0_pwr.SetLogRamp(this_time.beforeEnd(CdRSC_LAT_rampOFF_us*Unit.us()), CdRSC_VLAT_pwr, c3_VLAT_pwr)

        
        LAT0_ttl.SetInterval(this_time.afterward(0), c3_VLAT_ttl)
        LAT1_ttl.SetInterval(this_time.afterward(0), c3_VLAT_ttl)
        LAT2_ttl.SetInterval(this_time.afterward(0), c3_VLAT_ttl)
        # Elliptical lattice
        Sacher2_ttl.SetInterval(this_time.afterStart(0), CdRSC_ELAT_ttl)
        Sacher2_pwr.SetLogRamp(this_time.afterStart(CdRSC_LAT_rampON_us*Unit.us()), Sacher2_pwr.GetLastValue(), CdRSC_ELAT_pwr)
        Sacher2_pwr.SetLogRamp(this_time.beforeEnd(CdRSC_LAT_rampOFF_us*Unit.us()), CdRSC_ELAT_pwr, c3_ELAT_pwr)
        Sacher2_ttl.SetInterval(this_time.beforeEnd(CdRSC_LAT_rampOFF_us*Unit.us()), np.maximum(c3_ELAT_ttl,CdRSC_ELAT_ttl))
        Sacher2_ttl.SetInterval(this_time.afterward(0), c3_ELAT_ttl)
        # ramp the CODT on
        # if i<len(times_CdRSC)-1:
        ODT2_ttl.SetInterval(this_time.afterward(0), c3_CODT_ttl)
        ODT2_pwr.SetLogRamp(this_time.afterward(c3_ramp_time_ms*Unit.ms()), CdRSC_CODT_pwr, c3_CODT_pwr)
        # # "compression" stage; if duration is zero, this just sets the desired trap configuration
        # NOTHING HAPPENS DURING COMPRESSION! Just determines the endpoint of previous dRSC (and startpoint of next one)
        # as well as a holding time
        i += 1

# wait after dRSC
if PGC_Wait1p5_switch == 1: 
    if PGC_Wait1p5_first == 1:
        tt = 0
    else:
        tt = PGC_Wait1p5_offtime_ms
    while (tt+PGC_Wait1p5_ontime_ms+PGC_Wait1p5_offtime_ms) <= Wait1p5_ms:
        MOT0_ttl.SetInterval(times_Wait1p5.afterStart(tt*Unit.ms()).afterward(PGC_Wait1p5_ontime_ms*Unit.ms()), 1)
        REP0_ttl.SetInterval(times_Wait1p5.afterStart(tt*Unit.ms()).afterward(PGC_Wait1p5_ontime_ms*Unit.ms()), 1)
        tt += PGC_Wait1p5_ontime_ms
        MOT0_ttl.SetInterval(times_Wait1p5.afterStart(tt*Unit.ms()).afterward(0), 0)
        REP0_ttl.SetInterval(times_Wait1p5.afterStart(tt*Unit.ms()).afterward(0), 0)
        tt += PGC_Wait1p5_offtime_ms


# ramp to the B-field for optical pumping (generally along blue cavity, which is optical pumping axis)
if BRamp1_switch == 1:
    BiasX.SetInterval(times_BRamp1, BiasX.GetLastValue(), Bx_1_G)
    BiasY.SetInterval(times_BRamp1, BiasY.GetLastValue(), By_1_G)
    BiasZ.SetInterval(times_BRamp1, BiasZ.GetLastValue(), Bz_1_G)
    if (LAT0_pwr.GetLastValue() != BRamp1_settle_VLAT_pwr) or (Sacher2_pwr.GetLastValue() != BRamp1_settle_ELAT_pwr):
        LAT0_pwr.SetLogRamp(times_BRamp1_settle, LAT0_pwr.GetLastValue(), BRamp1_settle_VLAT_pwr, sample_rate=0.001)
        Sacher2_pwr.SetLogRamp(times_BRamp1_settle, Sacher2_pwr.GetLastValue(), BRamp1_settle_ELAT_pwr, sample_rate=0.001)

if GDEP_preOP_switch == 1:
    DEP_det_MHz = Rb.DDS_MOT_22(GDEP_det_MHz)
    MOT2_ttl.SetInterval(times_preGDEP, 1)
    MOT2_ttl.SetInterval(times_preGDEP.afterward(0), 0)
    MOT2_pwr.SetInterval(times_preGDEP, GDEP_pwr)
    MOT2_pwr.SetInterval(times_preGDEP.afterward(0), 0)
    if BRamp1_switch == 1:
        DDS_MOT.SetInterval(times_BRamp1, DDS_MOT.GetLastValue(), DEP_det_MHz) # DOES THIS DURING BRamp1!!!

# optical pumping
if OP_REP_switch == 1:
    D1Laser1_ttl.SetInterval(times_OP, 1)
    D1Laser1_pwr.SetInterval(times_OP, OP_REP_pwr)
    D1Laser1_ttl.SetInterval(times_OP.afterward(0), 0)
    D1Laser1_pwr.SetInterval(times_OP.afterward(0), 0)
    # ODT2_ttl.SetInterval(times_OP, PRB_CODT_ttl)
    # Sacher2_ttl.SetInterval(times_OP, PRB_ELAT_ttl)

    dRSC_OP_freq_ttl.SetInterval(times_OP, 1) # TTL=0 is 243 MHz for dRSC 2 -> 1', TTL=1 is 575 MHz tone for OP 2 -> 2'
    
    #LabBrick Trigger
    #Switch REP beam to appropriate RF type
    if OP_REP_RF_type == 0: # typically for dRSC | strong repump (1->2') sideband (6831 MHz from LabBrick 5626 thru big amp) and relatively weak carrier (550 MHz detuned from 2->2') by zeroing BesselJ_0
        AUX_ttl.SetInterval(times_OP, 0)
        AUX2_ttl.SetInterval(times_OP, 1) # MUST BE ONE TO ENSURE THAT LAB BRICK IS TRIGGERED ON
    elif OP_REP_RF_type == 1: # typically for OP | want quite weak repump sideband and strong pumping carrier, use attenuated version of LabBrick 5626 signal.
        AUX_ttl.SetInterval(times_OP, 1)
        AUX_ttl.SetInterval(times_OP.afterward(0), 0)
        AUX2_ttl.SetInterval(times_OP, 1)
        AUX2_ttl.SetInterval(times_OP.beforeEnd(OP_REP_12_EarlyEnd_ms*Unit.ms()), 0)
    elif OP_REP_RF_type == 2: # typically for depumping | turn off 1->2' sideband, turn on ~2->2' resonant light (crapbox RF @ 550 MHz)
        AUX_ttl.SetInterval(times_OP, 0)
        AUX2_ttl.SetInterval(times_OP, 0) 

# 780 optical pumping
if OP_780_switch == 1:

    PRB_pwr_ttl.SetInterval(times_OP, 1)
    PRB_pwr_ttl.SetInterval(times_OP.afterward(0), 0)
    RFSOC1_CavPrbEom.SetInterval(times_OP.beforeStart(1.0*Unit.ms()), PRB_f0_MHz*Unit.MHz(),OP_780_f0_MHz*Unit.MHz())
    Nufern0_pwr.SetInterval(times_OP.beforeStart(1.0*Unit.ms()),OP_780_pwr)
    Nufern0_pwr.SetInterval(times_OP.afterward(0.),PRB_pwr_low)
    Nufern0_ttl.SetInterval(times_OP,OP_780_switch)
    Nufern0_ttl.SetInterval(times_OP.afterward(0),0)
    RFSOC1_CavPrbEom.SetInterval(times_OP.afterward(0.), OP_780_f0_MHz*Unit.MHz(), PRB_f0_MHz*Unit.MHz())


# ramp B-field to probe value, AFTER optical pumping
if BRamp2_ttl == 1:
    if BRamp1_switch == 1:
        #Ramp B fields to PRB values
        BiasX.SetInterval(times_BRamp2, Bx_1_G, Bx_2_G)
        BiasY.SetInterval(times_BRamp2, By_1_G, By_2_G)
        BiasZ.SetInterval(times_BRamp2, Bz_1_G, Bz_2_G)
    else:
        BiasX.SetInterval(times_BRamp2, dRSC_Bx_G, Bx_2_G)
        BiasY.SetInterval(times_BRamp2, dRSC_By_G, By_2_G)
        BiasZ.SetInterval(times_BRamp2, dRSC_Bz_G, Bz_2_G)

if GDEP_switch == 1:
    DEP_det_MHz = Rb.DDS_MOT_22(GDEP_det_MHz)
    MOT2_ttl.SetInterval(times_GDEP, 1)
    MOT2_ttl.SetInterval(times_GDEP.afterward(0), 0)
    MOT2_pwr.SetInterval(times_GDEP, GDEP_pwr)
    MOT2_pwr.SetInterval(times_GDEP.afterward(0), 0)
    if BRamp1_switch == 1 and GDEP_preOP_switch!=1: # don't ramp frequency again if pre GDEP did it already
        DDS_MOT.SetInterval(times_BRamp1, DDS_MOT.GetLastValue(), DEP_det_MHz) # DOES THIS DURING BRamp1!!!


if Blue_ON_ms>0.0:
    # Blue beam
    Blue_ttl.SetInterval(times_blue, 1)
    Blue_pwr.SetInterval(times_blue, PRB_Ctrl_pwr)
    Blue_ttl.SetInterval(times_blue.afterward(0), 0)
    


### Probe cycle ###
if PRB_mode == 1: # Static cloud in the cavity
    # # # # For now, let the final compression stage determine the trap during probing
    Shut_HLAT_ttl.SetInterval(times_Prb, 0)
    # Turn off the lattice 
    if PRB_LATT_OFF:
        LAT0_ttl.SetInterval(times_Prb, 0)
        LAT1_ttl.SetInterval(times_Prb, 0)
        LAT2_ttl.SetInterval(times_Prb, 0)

    #turn off cavity dipole trap
    ODT2_ttl.SetInterval(times_Prb.beforeStart(PRB_delay_us*Unit.us()), PRB_CODT_ttl)

    # ELAT
    Sacher2_ttl.SetInterval(times_Prb.beforeStart(PRB_delay_us*Unit.us()), PRB_ELAT_ttl)
    # Sacher2_ttl.SetInterval(times_Prb, PRB_ELAT_ttl)

    #MOT
    MOTCoil.SetInterval(times_Prb, PRB_MOTcoil)
    # trigger the AWG for probing (sometimes applicable)
    #AWG_trig.SetInterval(times_Prb, 1)

    # Experiment Electrode modulation
    if ElMod_switch>0:
        # _tau = 0.25*Unit.ms()/ElMod_freq_kHz
        # STP_EL_MOD = [(0., V2, _tau, V2+ElMod_Volt),(_tau, V2+ElMod_Volt, 3*_tau, V2-ElMod_Volt),(3*_tau, V2-ElMod_Volt, 4*_tau, V2), ] #triangle wave
        # EF2.SetModulation(times_Prb, STP_EL_MOD)
        V1_ttl.SetModulation(times_Prb, STP_PRB)
        V1_ttl.SetInterval(times_Prb.afterward(0), 0)
    
    # AUX1 should always be zero during PRB; AUX2 switches between OP and DEP
    # TODO: with new switch wiring this is presumably no longer correct?
    # Want to have the PUMP on all the time and only switch the REP on for the fraction time?!
    # AUX_ttl.SetInterval(times_Prb, 1)
    # AUX2 switches between REP and OP; its timing is determined by DepumpForPrb tab
    REP_fracs = [REP_frac_1, REP_frac_2, REP_frac_3, REP_frac_4, REP_frac_5, REP_frac_6, REP_frac_7, REP_frac_8, REP_frac_9, REP_frac_10]
    for ii in range(int(np.round(PRB_repetitions))): # there will be one pumping cycle in each PRB repetition
        if ii >= len(REP_fracs): # need to add more fractions if you use more repetitions and want repumping!
            break
        this_time_REP = times_Prb.afterStart(t_PRB*ii+t_gap1).afterward(PRB_OP_REP_total_ms*Unit.ms()*REP_fracs[ii])
        this_time_OP = this_time_REP.afterward(PRB_OP_REP_total_ms*Unit.ms()*(1-REP_fracs[ii]))
        AUX2_ttl.SetInterval(this_time_REP, 1)
        AUX2_ttl.SetInterval(this_time_OP, 0) # will stay this way until the next brief REP pulse
        AUX_ttl.SetInterval(this_time_REP, 1)
        AUX_ttl.SetInterval(this_time_OP, 1)
        AUX_ttl.SetInterval(this_time_OP.afterward(0), 0)

    # Repump D1 laser
    D1Laser1_ttl.SetModulation(times_Prb, STP_REP)
    D1Laser1_pwr.SetInterval(times_Prb.afterStart(0), PRB_REP_pwr)
    D1Laser1_ttl.SetInterval(times_Prb.afterward(0), 0)

    # Probe the cavity
    Nufern0_ttl.SetModulation(times_Prb, STP_PRB)
    Nufern0_ttl.SetInterval(times_Prb.afterward(0), 0)
    Nufern0_pwr.SetModulation(times_Prb, STP_PRB_pwr)
    # Probe EOM modulation
    EITPrbEOM_ttl.SetModulation(times_Prb, STP_PRB_EOM)
    EITPrbEOM_ttl.SetInterval(times_Prb.afterward(0), 0)
    # Probe AOM power TTL switch
    PRB_pwr_ttl.SetModulation(times_Prb, STP_PRB_PWR_TTL) 
    PRB_pwr_ttl.SetInterval(times_Prb.afterward(0), 0)
    

    # Blue beam
    Blue_ttl.SetInterval(times_delay, PRB_Ctrl_ttl)
    Blue_ttl.SetModulation(times_Prb, STP_BLUE)
    Blue_ttl.SetInterval(times_Prb.afterward(0), 0)
    Blue_pwr.SetInterval(times_Prb, PRB_Ctrl_pwr)
    # Sweep Probe Freq (using red side band, so higher DDS frequency means lower actual frequency)
    CavPrb_f0 = (PRB_f0_MHz+PRB_df_MHz)*Unit.MHz()
    CavPrb_f1 = (PRB_f0_MHz-PRB_df_MHz)*Unit.MHz()
    if PRB_sweep_num == 1:
        if N_subreps>1:	
            RFSOC1_CavPrbEom.SetModulation(times_Prb, STP_PRB_freq) # scam probe frequency according to stamp (3 ramps per subrep)
        else:
            RFSOC1_CavPrbEom.SetInterval(times_Prb_latetrig, CavPrb_f0, CavPrb_f1) # do one sweep over whole sequence, for Plotter compatibility
            if PRB_CtrlAOM_df_MHz > 0:
                BluePrbSweep_f0 = (PRB_CtrlAOM_f0_MHz - PRB_CtrlAOM_df_MHz/2.)*Unit.MHz()
                BluePrbSweep_f1 = (PRB_CtrlAOM_f0_MHz + PRB_CtrlAOM_df_MHz/2.)*Unit.MHz()
                RFSOC1_4.SetInterval(times_Prb_latetrig, BluePrbSweep_f0, BluePrbSweep_f1) # do one sweep over whole sequence
    else:
        swp_len = times_Prb.length()/PRB_sweep_num
        for sn in range(int(PRB_sweep_num)):
            RFSOC1_CavPrbEom.SetInterval(times_Prb_latetrig.afterStart(sn*swp_len).afterward(swp_len-10*Unit.us()), CavPrb_f0, CavPrb_f1)
        # RFSOC1_CavPrbEom.SetInterval(times_Prb_latetrig.afterStart(0).afterward(PRB_time_ms*Unit.ms()-10*Unit.us()), CavPrb_f0, CavPrb_f1)
    # Trigger the scope
    Scope_trig.SetInterval(times_Prb, 1)
    # Scope_trig.SetInterval(times_Prb.beforeEnd(PRB_time_us*Unit.us()), 1)
    Scope_trig.SetInterval(times_Prb.afterward(0), 0)
    # Trigger the SPCM
    SPCM_ttl.SetInterval(times_Prb.beforeStart(SPCM_offset_ms*Unit.ms()), 1)
    SPCM_ttl.SetModulation(times_Prb, STP_SPCM)
    SPCM_ttl.SetInterval(times_Prb.afterward(0), 0)
    # Gate the SPCM pulses during sidebands
    GATE_ttl.SetModulation(times_Prb, STP_GATE)

elif PRB_mode == 2: # for hot wire, Moving the cloud through the cavity waist (ONLY WORKS WITHOUT dRSC!)
    # Turn off the lattice 
    if PRB_LATT_OFF:
        LAT0_ttl.SetInterval(times_CavPrb, 0)
        LAT1_ttl.SetInterval(times_CavPrb, 0)
        LAT2_ttl.SetInterval(times_CavPrb, 0)
    # Turn on/off the cavity probe beam
    Nufern0_ttl.SetInterval(times_CavPrb, PRB_ttl)
    Nufern0_ttl.SetInterval(times_CavPrb.afterward(0), 0)
    Nufern0_pwr.SetInterval(times_CavPrb, PRB_pwr_low)
    # Turn on/off the cavity probe EOM
    EITPrbEOM_ttl.SetInterval(times_CavPrb, 1)
    EITPrbEOM_ttl.SetInterval(times_CavPrb.afterward(0), 0)
    # Turn on/off the vertical repumper
    D1Laser1_ttl.SetInterval(times_CavPrb, PRB_REP_ttl)
    D1Laser1_ttl.SetInterval(times_CavPrb.afterward(0), 0)
    D1Laser1_pwr.SetInterval(times_CavPrb, PRB_REP_pwr)
    # Sweep Probe Freq
    CavPrb_f0 = (PRB_f0_MHz+PRB_df_MHz)*Unit.MHz()
    CavPrb_f1 = (PRB_f0_MHz-PRB_df_MHz)*Unit.MHz()
    #RFSOC1_CavPrbEom.SetInterval(times_CavPrb, CavPrb_f0, CavPrb_f1)
    RFSOC1_CavPrbEom.SetInterval(times_Prb_latetrig, CavPrb_f0, CavPrb_f1)
    # Trigger the scope
    Scope_trig.SetInterval(times_CavPrb, 1)
    Scope_trig.SetInterval(times_CavPrb.afterward(0), 0)
    # Trigger the SPCM
    SPCM_ttl.SetInterval(times_CavPrb.beforeStart(SPCM_offset_ms*Unit.ms()), PRB_SPCM_ttl)
    SPCM_ttl.SetInterval(times_CavPrb.afterward(0), 0)

# CANT PUT THIS EARLIER BECAUSE GetLastValue calls in Imaging end up wrong if you do.

if Img_switch == 1: # Fluorescence imaging
    times_IMG = Imaging(times, 1, Img_prep_time_us*Unit.us(), Img_TOF_ms*Unit.ms(), Img_time_us*Unit.us(), Img_drop_time_ms*Unit.ms(), Img_MOT_pwr, Img_REP_pwr, IMGMOTFREQ, IMGREPFREQ, img_dep_time = Img_DEPMOT_time_us*Unit.us())
    Shut_MOT_ttl.SetInterval(times_transport.beforeEnd(2.5*Unit.ms()), 1)
    # Shut_MOT_ttl.SetInterval(times_IMG.beforeStart(2.5*Unit.ms()), 1)
    AUX_ttl.SetInterval(times_IMG.afterStart((Img_prep_time_us+Img_DEPMOT_time_us+1000.0*Img_TOF_ms)*Unit.us()).afterward(0),Img_RF_ttl)
    AUX_ttl.SetInterval(times_IMG.afterward(0),0)
if Img_switch == 2: # Absorption imaging
    times_IMG_DEPMOT = times_transport.beforeEnd(Img_DEPMOT_time_us*Unit.us())
    # if Img_FRAMP_switch == 1:
    #     times_IMG_FRAMP = times.append(Img_FRAMP_ms*Unit.ms(), 'MOT Frequency Ramp')
    times_IMG_DEP = times.append(Img_DEPMOT_atend_us*Unit.us(), 'DEP')
    times_IMG_REP = times.append(Img_REP_atend_us*Unit.us(), 'REP')
    times_IMG = Imaging(times, 2, Img_prep_time_us*Unit.us(), Img_TOF_ms*Unit.ms(), Img_time_us*Unit.us(), Img_drop_time_ms*Unit.ms(), Img_MOT_pwr, 0., None, None, blue_img_ttl=Blue_img_ttl)
    # Elliptical lattice
    # for time_IMG in times_IMG:
    #     Sacher2_ttl.SetInterval(time_IMG, Img_ELAT_ttl)
    #     Sacher2_pwr.SetInterval(time_IMG, Img_ELAT_pwr)


if Img_switch == 3: # Single shot imaging
    times_IMG = Imaging(times, 3, Img_prep_time_us*Unit.us(), Img_TOF_ms*Unit.ms(), Img_time_us*Unit.us(), 0., 0., 0., 0., 0., blue_img_ttl=Blue_img_ttl)
    # Elliptical lattice
    Sacher2_ttl.SetInterval(times_IMG, Img_ELAT_ttl)
    Sacher2_pwr.SetInterval(times_IMG, Img_ELAT_pwr)
    MOT2_ttl.SetInterval(times_IMG, Img_GDEP_ttl)
    MOT2_pwr.SetInterval(times_IMG, Img_GDEP_pwr)
if Img_switch == 4: # Image during probe
    Cam_trig.SetInterval(times_Prb, 0)
    Cam_trig.SetInterval(times_Prb.afterward(0), 1)
times_FinalWait = times.append(time_FinalWait_ms*Unit.ms(), 'Final Ramp')
DDS_trig.Set([(0, 1, 10*Unit.us(), 1),(10*Unit.us(),0,times_FinalWait[1],0)])

### Depump the MOT for vertical absorption imaging ###
if Img_switch == 2:
    #close HLAT shutter
    Shut_HLAT_ttl.SetInterval(times_IMG, 0)

    # open MOT shutter
    #Shut_MOT_ttl.SetInterval(times_IMG_DEP.beforeStart(2.5*Unit.ms()), 1)
    #Shut_MOT_ttl.SetInterval(times_transport.beforeEnd(0*Unit.ms()), 1)

    # Turn off CODT/ELAT right before imaging
    ODT2_ttl.SetInterval(times_IMG.afterStart(Img_prep_time_us*Unit.us()), Img_CODT_ttl)
    ODT2_pwr.SetInterval(times_IMG.afterStart(Img_prep_time_us*Unit.us()), Img_CODT_pwr)
    #Sacher2_ttl.SetInterval(times_IMG.afterStart(Img_prep_time_us*Unit.us()), 0)

    if Img_FRAMP_switch == 1:
        #DDS_MOT.SetInterval(times_IMG_FRAMP,DDS_MOT.GetLastValue(),IMGMOTFREQ)
        #DDS_REP.SetInterval(times_IMG_FRAMP,DDS_MOT.GetLastValue(),IMGREPFREQ)
        DDS_MOT.SetInterval(times_IMG_DEPMOT.beforeStart(Img_FRAMP_ms*Unit.ms()),DDS_MOT.GetLastValue(),IMGMOTFREQ)
        DDS_REP.SetInterval(times_IMG_DEPMOT.beforeStart(Img_FRAMP_ms*Unit.ms()),DDS_MOT.GetLastValue(),IMGREPFREQ)
        
    # depump at end of transport
    if Img_DEPMOT_time_us > 0.0:
        MOT0_ttl.SetInterval(times_IMG_DEPMOT, 1)
        MOT0_ttl.SetInterval(times_IMG_DEPMOT.afterward(0), 0)
        MOT0_pwr.SetInterval(times_IMG_DEPMOT, Img_MOT_pwr)
        MOT0_pwr.SetInterval(times_IMG_DEPMOT.afterward(0), 0)
    # turn off ELAT during imaging
    #Sacher2_ttl.SetInterval(times_IMG, 0)
    #Sacher2_pwr.SetInterval(times_IMG, 0)

    # depump all (esp. MOT) just before imaging
    if Img_DEPMOT_atend_us > 0.0:
        MOT0_ttl.SetInterval(times_IMG_DEP, 1)
        MOT0_ttl.SetInterval(times_IMG_DEP.afterward(0), 0)
    # repump with dRSC beam just before imaging
    if Img_REP_atend_us > 0.0:
        D1Laser1_ttl.SetInterval(times_IMG_REP, 1)
        D1Laser1_pwr.SetInterval(times_IMG_REP, Img_REP_atend_pwr)
        D1Laser1_ttl.SetInterval(times_IMG_REP.afterward(0), 0)
        
### Final Frequency Ramp ###
# Set DDS back to original frequency
DDS_MOT.SetInterval(times_FinalWait, DDS_MOT.GetLastValue(), MOTFREQ)
DDS_REP.SetInterval(times_FinalWait, DDS_REP.GetLastValue(), REPFREQ)
# Turn up MOT coil again at end
MOTCoil.SetInterval(times_FinalWait, MOTCoil.GetLastValue(), MOT_CoilCurr)

BiasX.SetInterval(times_FinalWait, BiasX.GetLastValue(), MOT_BiasX_G)
BiasY.SetInterval(times_FinalWait, BiasY.GetLastValue(), MOT_BiasY_G)
BiasZ.SetInterval(times_FinalWait, BiasZ.GetLastValue(), MOT_BiasZ_G)
# ramp to SSV E fields
EF1.SetInterval(times_FinalWait, V1, V1_SSV)
EF2.SetInterval(times_FinalWait, V2, V2_SSV)
EF3.SetInterval(times_FinalWait, V3, V3_SSV)
EF4.SetInterval(times_FinalWait, V4, V4_SSV)
EF5.SetInterval(times_FinalWait, V5, V5_SSV)
EF6.SetInterval(times_FinalWait, V6, V6_SSV)
EF7.SetInterval(times_FinalWait, V7, V7_SSV)
EF8.SetInterval(times_FinalWait, V8, V8_SSV)
EF9.SetInterval(times_FinalWait, V9, V9_SSV)

#### Set steady state values ####
#### Logan 10/19/18: This is now ALSO where we sort the commands for each channel and check for timing conflicts (i.e. ONCE per channel, at the end of the sequence)
# Ditital seq
MOT0_ttl.SetSteadyStateValue(MOT_SteadyState)
REP0_ttl.SetSteadyStateValue(MOT_SteadyState)
Scope_trig.SetSteadyStateValue(0)
Cam_trig.SetSteadyStateValue(1)
UV_ttl.SetSteadyStateValue(UV_gap_ttl)
DDS_trig.SetSteadyStateValue(0)
LAT1_ttl.SetSteadyStateValue(1)
LAT2_ttl.SetSteadyStateValue(1)
Sacher2_ttl.SetSteadyStateValue(0)
V1_ttl.SetSteadyStateValue(0)
LAT0_ttl.SetSteadyStateValue(LAT_SWITCH)
Blue_ttl.SetSteadyStateValue(0)
ODT2_ttl.SetSteadyStateValue(0)
Nufern0_ttl.SetSteadyStateValue(0) # 
PRB_pwr_ttl.SetSteadyStateValue(0)
MOT1_ttl.SetSteadyStateValue(0)
SPCM_ttl.SetSteadyStateValue(0)
GATE_ttl.SetSteadyStateValue(1)
dRSC_LAT2_ttl.SetSteadyStateValue(0)
D1Laser1_ttl.SetSteadyStateValue(0)
EITPrbEOM_ttl.SetSteadyStateValue(0)
AUX_ttl.SetSteadyStateValue(0)
Nufern1_ttl.SetSteadyStateValue(0)
MOT2_ttl.SetSteadyStateValue(0)
dRSC_LAT_ttl.SetSteadyStateValue(0)
Shut_MOT_ttl.SetSteadyStateValue(1)
dRSC_OP_freq_ttl.SetSteadyStateValue(0)
Shut_HLAT_ttl.SetSteadyStateValue(1)
#AWG_trig.SetSteadyStateValue(0)
#Digi_test.SetSteadyStateValue(1)
# Analog Seq
MOT0_pwr.SetSteadyStateValue(MOT_MOTPwr if MOT_SteadyState else 0)
REP0_pwr.SetSteadyStateValue(MOT_REPPwr if MOT_SteadyState else 0)
MOTCoil.SetSteadyStateValue(MOT_CoilCurr)
BiasX.SetSteadyStateValue(MOT_BiasX_G)
BiasY.SetSteadyStateValue(MOT_BiasY_G)
BiasZ.SetSteadyStateValue(MOT_BiasZ_G)
LAT1_pwr.SetSteadyStateValue(LVP)
LAT2_pwr.SetSteadyStateValue(LHP)
Sacher2_pwr.SetSteadyStateValue(0)
LAT0_pwr.SetSteadyStateValue(LMP)
Blue_pwr.SetSteadyStateValue(PRB_Ctrl_pwr)
EDFA_1529_pwr.SetSteadyStateValue(Floquet_AOM_pwr)
Nufern0_pwr.SetSteadyStateValue(PRB_pwr_low)
CavPrbEOM_pwr.SetSteadyStateValue(PRB_pwr_high)
D1Laser1_pwr.SetSteadyStateValue(dRSC_Pump_pwr)
dRSC_LAT2_pwr.SetSteadyStateValue(0)
MOT1_pwr.SetSteadyStateValue(0)
MOT2_pwr.SetSteadyStateValue(0)
# EF1.SetSteadyStateValue(V1_SteadyState)
EF1.SetSteadyStateValue(V1_SSV)
EF2.SetSteadyStateValue(V2_SSV)
EF3.SetSteadyStateValue(V3_SSV)
EF4.SetSteadyStateValue(V4_SSV)
EF5.SetSteadyStateValue(V5_SSV)
EF6.SetSteadyStateValue(V6_SSV)
EF7.SetSteadyStateValue(V7_SSV)
EF8.SetSteadyStateValue(V8_SSV)
EF9.SetSteadyStateValue(V9_SSV)
Anal_test.SetSteadyStateValue(0.0)
# DDS seq 1
DDS_REP.SetSteadyStateValue(REPFREQ)
DDS_MOT.SetSteadyStateValue(MOTFREQ)
#DDS_LAT1.SetSteadyStateValue(ModeSort3_MHz*Unit.MHz())
DDS1_2.SetSteadyStateValue(PDH960_SciCavOffs_MHz*Unit.MHz())
# DDS PDH seq
RP1_DDS_0.SetSteadyStateValue(ParamHeat_freq_kHz*Unit.kHz())
RP1_DDS_1.SetSteadyStateValue(10*Unit.MHz())
DDS_PDH1560.SetSteadyStateValue(PDH1560_freq)
DDS_PDH960.SetSteadyStateValue(PDH960_freq)
DDS_PDH780.SetSteadyStateValue(PDH780_freq)
RFSOC1_4.SetSteadyStateValue(PRB_CtrlAOM_f0_MHz*Unit.MHz())
RFSOC1_5.SetSteadyStateValue(RFSOC1529_HF*Unit.MHz())
RFSOC1_CavPrbEom.SetSteadyStateValue(PRB_f0_MHz)
RFSOC1_784Lock.SetSteadyStateValue(PDH785_freq_MHz*Unit.MHz())
DDS_HalfRng.SetSteadyStateValue(5)
# DDS seq 2
DDS_CavPrbAOM.SetSteadyStateValue(CavPrb_FreqOffset_MHz*Unit.MHz())
DDS_chan1.SetSteadyStateValue(80)
DDS_OptPump1.SetSteadyStateValue(80)
#DDS2_3.SetSteadyStateValue(ModeSort1_MHz*Unit.MHz())
# Lab Bricks
LB1_freq.SetSteadyStateValue(groundHF() + MW_det_kHz*Unit.kHz())
LB1_pow.SetSteadyStateValue(MW_pwr_dBm)
LB1_ttl.SetSteadyStateValue(MW_cw_ttl)
LB2_freq.SetSteadyStateValue(LB1529_lock_MHz)
LB2_pow.SetSteadyStateValue(LB1529_lock_dBm)
LB2_ttl.SetSteadyStateValue(1)
# LB3_freq.SetSteadyStateValue(MWaves_Freq_MHz)
# LB3_pow.SetSteadyStateValue(MWaves_pwr_dBm)
# LB3_ttl.SetSteadyStateValue(0)
MWaves_ttl.SetSteadyStateValue(0)
# ADF435X
#AD1_freq.SetSteadyStateValue(MWaves_Freq_MHz)
#AD1_pow.SetSteadyStateValue(MWaves_pwr_dBm)
AD1_ttl.SetSteadyStateValue(0)
# DMD
DMD_waist.SetSteadyStateValue(DMD_Waist)
DMD_defocus.SetSteadyStateValue(DMD_Defocus)
DMD_l.SetSteadyStateValue(DMD_L)
DMD_p.SetSteadyStateValue(DMD_P)
DMD_center_x.SetSteadyStateValue(DMD_Center_X)
DMD_center_y.SetSteadyStateValue(DMD_Center_Y)
DMD_tilt_x.SetSteadyStateValue(DMD_Tilt_X)
DMD_tilt_y.SetSteadyStateValue(DMD_Tilt_Y)
DMD_phi.SetSteadyStateValue(DMD_Phi)
DMD_eps_phi.SetSteadyStateValue(DMD_Epsilon_Phi)

#SmarAct
SMARACT_vx.SetSteadyStateValue(SmarAct_x_V)
SMARACT_vy.SetSteadyStateValue(SmarAct_y_V)