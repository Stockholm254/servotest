#!/usr/bin/python
# -*- coding: utf-8 -*-
import copy
from math import floor

#### Modifiable Variables ####
# Note: values must be integers or floats.

# Tab:Init
Init_time_ms = 0.0
InitDrop = 0.0
# Tab:PDH_freq
MV(PDH1560_freq, min=0.0, max=2500.0, init=309.65, inc=0.1, digits=2)
MV(PDH960_freq, min=0.0, max=2500.0, init=580.6, inc=0.1, digits=2)
MV(PDH780_freq, min=0.0, max=2500.0, init=470.0, inc=0.1, digits=2)
MV(CavPrb_FreqOffset_MHz, min=0.0, max=2500.0, init=209.0, inc=1, digits=2)
# Tab:SPCM_setting
DetMode = 1.0
PC_save_switch = 0.0
PC_bin_number = 500.0
PC_max_rate_MHz = 5.0
MV(SPCM_offset_ms, min=0.0, max=25.0, init=0.0, inc=0.5, digits=2)
# Tab:E_Filter
MV(Ex, min=-5., max=5., init=-0.0253, inc=2.5e-3, digits=4)
MV(Ey, min=-5., max=5., init=0.0273, inc=2.5e-3, digits=4)
MV(Ez, min=-5., max=5., init=0.0604, inc=2.5e-3, digits=4)
MV(dxEx, min=-5., max=5., init=0.0, inc=1e-2, digits=6)
MV(dyEx, min=-5., max=5., init=0.0, inc=1e-2, digits=6)
MV(dzEx, min=-5., max=5., init=-0.02, inc=1e-2, digits=6)
MV(dyEy, min=-5., max=5., init=-0.01, inc=1e-2, digits=6)
MV(dzEy, min=-5., max=5., init=0.0, inc=1e-2, digits=6)
MV(ExTrim, min=-5., max=5., init=0, inc=2.5e-3, digits=4)
MV(EyTrim, min=-5., max=5., init=0, inc=2.5e-3, digits=4)
MV(EzTrim, min=-5., max=5., init=0, inc=2.5e-3, digits=4)
MV(dV1, min=-10., max=10., init=0, inc=1.e-2, digits=4)
MV(dV2, min=-15., max=15., init=0, inc=1.e-2, digits=4)
MV(dV3, min=-15., max=15., init=0, inc=1.e-2, digits=4)
MV(dV4, min=-15., max=15., init=0, inc=1.e-2, digits=4)
MV(dV5, min=-15., max=15., init=0, inc=1.e-2, digits=4)
MV(dV6, min=-15., max=15., init=0, inc=1.e-2, digits=4)
MV(dV7, min=-15., max=15., init=0, inc=1.e-2, digits=4)
MV(dV8, min=-15., max=15., init=0, inc=1.e-2, digits=4)
MV(dV9, min=-15., max=15., init=0, inc=1.e-2, digits=4)
MV(V1_SteadyState, min=-10, max=10, init=0, inc=1.e-2, digits=4)
V1_SS_ttl   = 1
V1_main_ttl = 0
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
LBT = 1.0
LTT = 1.0
LMP = 4.4
LBP = 4.8
LTP = 4.8
# LAT1_f_MHz = 80.0
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
# Tab:dRSC
dRSC_switch   = 1
dRSC1_repetitions = 1
dRSC_Dur_ms   = 5
dRSC_VLAT_ttl = 1
dRSC_VLATmain_pwr = 4.2
dRSC_HLAT_ttl = 1
dRSC_HLAT_pwr = 4.7
dRSC_ELAT_ttl = 0
dRSC_ELAT_pwr = 0.0
dRSC_Pump_ttl = 1
dRSC_Pump_pwr = 4.5
dRSC_LAT_rampON_us = 200 
dRSC_LAT_rampOFF_us = 500 
MV(dRSC_Bx_G, min=-5.0, max=5.0, init=0.20, inc=1e-3, digits=4)
MV(dRSC_By_G, min=-3.5, max=3.5, init=0.18, inc=1e-3, digits=4)
MV(dRSC_Bz_G, min=-5.0, max=5.0, init=0.00, inc=1e-3, digits=4)
dRSC_PGC_switch = 0
c1_hold_time_ms = 0.6
c1_VLAT_ttl = 1
c1_VLATmain_pwr = 4.6
c1_HLAT_ttl = 1
c1_HLAT_pwr = 5.0
c1_ELAT_ttl = 1
c1_ELAT_pwr = 5.0
c1_PGC_switch = 1
# Tab:TrapRamp
Ramp1_ODT_TTL = 1
Ramp1_Retro_TTL = 1
Ramp1_ELAT_TTL = 1
Ramp1_switch=1
Ramp1_steps = 20.0
Ramp1_dur_us = 500.0
Ramp1_ODT_pwr = 4
Ramp1_Retro_pwr = 0
Ramp1_ELAT_pwr =0 
Ramp2_switch = 1
Ramp2_steps = 20.0
Ramp2_dur_us = 5000.0
Ramp2_ODT_pwr = 4
Ramp2_Retro_pwr = 0
Ramp2_ELAT_pwr = 4.8 
Ramp3_switch = 1
Ramp3_steps = 20.0
Ramp3_dur_us = 5000.0
Ramp3_ODT_pwr = 0
Ramp3_Retro_pwr = 0
Ramp3_ELAT_pwr = 4.8 
RampFinal_ODT_TTL = 0
RampFinal_Retro_TTL = 0
RampFinal_ELAT_TTL = 1
TrapRamp_PGC_switch = 1
# Tab:BField_OP_DEP
BRamp1_ttl = 1
BRamp1_ms = 5
MV(Bx_1_G, min=-5.0, max=5.0, init=0.20, inc=1e-3, digits=4)
MV(By_1_G, min=-5.0, max=5.0, init=0.10, inc=1e-3, digits=4)
MV(Bz_1_G, min=-5.0, max=5.0, init=0.00, inc=1e-3, digits=4)
BRamp1_settle_ms = 0
OP_REP_ttl = 1
OP_REP_pwr = 5
OP_REP_ms = 1.0
OP_REP_RF_type = 1
BRamp2_ttl = 1
BRamp2_ms = 5
MV(Bx_2_G, min=-5.0, max=5.0, init=0.20, inc=1e-3, digits=4)
MV(By_2_G, min=-5.0, max=5.0, init=0.10, inc=1e-3, digits=4)
MV(Bz_2_G, min=-5.0, max=5.0, init=0.00, inc=1e-3, digits=4)
GDEP_ttl = 1
GDEP_ms = 0.1
GDEP_pwr = 5.0
MV(GDEP_det_MHz, min=-1000.0, max=1000.0, init=0.0, inc=0.1, digits=2)
# Tab:CavPrb
PRB_mode = 1.0
PRB_ttl = 1.0
PRB_SPCM_ttl = 1.0
#PRB_pwr = 4.5
PRBF_EOM = 5.0
PRBB_EOM = 0.0
PRB_delay_us = 10.0
PRB_repetitions = 10
PRB_OP_REP_total_ms = 0.04
PRB_gaps_ms = 0.005
PRB_time_ms = 1.95
#MV(PRB_f0_MHz, min=0, max=3e3, init=341.99, inc=0.1, digits=3)
#PRB_df_MHz = 10.0
PRB_sweep_num = 1
PRB_Ctrl_ttl = 0.0
PRB_Ctrl_gap_ttl = 0.0
MV(PRB_Ctrl_pwr, min=0.0, max=5.0, init=4.2, inc=5e-2, digits=2)
PRB_REP_ttl = 1.0
PRB_REP_pwr = 5.0
PRB_ELAT_ttl = 1.0
PRB_MOTcoil = 0.0
SPCM_alwayson = 0.0
PRB_gap_ttl = 0 
PRB_gap_pwr = 3.0
MV(ModeSort1_MHz, min=0.0, max=3e3, init=200.0, inc=0.1, digits=2)
MV(ModeSort3_MHz, min=0.0, max=3e3, init=400.0, inc=0.1, digits=2)
MV(PSC_lock1_MHz, min=0.0, max=3e3, init=300.0, inc=0.1, digits=2)
MV(PSC_lock2_MHz, min=0.0, max=3e3, init=300.0, inc=0.1, digits=2)
MV(PSC_ramp_ms,   min=0.0, max=1e3, init=10.0,  inc=0.1, digits=2)
PSC_output_offset_1 = 0
PSC_output_offset_2 = 0 
PRB_LATT_OFF = 0
# Tab:Imaging
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
Img_horz_pwr = 4.6
Img_vert_pwr = 5.0
Img_REP_pwr = 5.0
Img_det23_MHz = 0.0
Img_det12_MHz = 0.0
Img_ELAT_ttl = 1
Img_ELAT_pwr = 4.0
Img_GDEP_ttl = 1
Img_GDEP_pwr = 5.0
ImgSlice_time_us = 10.0
ImgSlice_LAT_ttl = 0.0
ImgSlice_slice_ttl = 1.0
ImgSlice_slice_pwr = 2.0
ImgSlice_REP_ttl = 1.0
ImgSlice_REP_pwr = 5.0
ImgSlice_absorp_ttl = 0.0
ImgSlice_absorp_pwr = 3.7
Blue_img_ttl = 0.0
Img_RF_ttl = 0
# Tab:Floquet
Floquet_AOM_TTL = 0
Floquet_Transport_TTL = 1
Floquet_dRSC_TTL = 0
Floquet_SteadyState_TTL = 1
Floquet_AOM_pwr = 5
MV(Floquet_PRB_fraction, min=0.0, max=1.0, init=1.0, inc=0.1, digits=2)
#MV(Floq_Lock_Detuning_MHz, min=5000, max=10000, init=7500, inc=1, digits=1)
#MV(Floq_Lock_RF_dBm, min=-10, max=10, init=5, inc=0.5, digits=1) 
MV(Floq_SB1_Freq_MHz, min=8000, max=12000, init=8500, inc=1, digits=1)
MV(Floq_SB1_pwr_dBm, min=-40, max=10, init=5, inc=0.5, digits=1) 
MV(Floq_SB2_Freq_MHz, min=5000, max=10000, init=8500, inc=1, digits=1)
MV(Floq_SB2_pwr_dBm, min=-40, max=10, init=5, inc=0.5, digits=1) 
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
MV(t_subrep_us, min=0, max=10000, init=50, inc=1, digits=3)
MV(Prb_P_wait_us, min=0, max=10000, init=0, inc=1, digits=3)
MV(Prb_P_dur_us, min=0, max=10000, init=25, inc=1, digits=3)
Prb_P_highp = 0
Prb_P_gate = 0
MV(Prb_U_wait_us, min=0, max=10000, init=0, inc=1, digits=3)
MV(Prb_U_dur_us, min=0, max=10000, init=0, inc=1, digits=3)
Prb_U_highp = 1
Prb_U_gate = 1
MV(Prb_L_wait_us, min=0, max=10000, init=0, inc=1, digits=3)
MV(Prb_L_dur_us, min=0, max=10000, init=0, inc=1, digits=3)
Prb_L_highp = 1
Prb_L_gate = 1
# Tab:REP_Durations
MV(REP_frac_1, min=0.0, max=0.5, init=0.5, inc=0.01, digits=2)
MV(REP_frac_2, min=0.0, max=0.5, init=0.5, inc=0.01, digits=2)
MV(REP_frac_3, min=0.0, max=0.5, init=0.5, inc=0.01, digits=2)
MV(REP_frac_4, min=0.0, max=0.5, init=0.5, inc=0.01, digits=2)
MV(REP_frac_5, min=0.0, max=0.5, init=0.5, inc=0.01, digits=2)
MV(REP_frac_6, min=0.0, max=0.5, init=0.5, inc=0.01, digits=2)
MV(REP_frac_7, min=0.0, max=0.5, init=0.5, inc=0.01, digits=2)
MV(REP_frac_8, min=0.0, max=0.5, init=0.5, inc=0.01, digits=2)
MV(REP_frac_9, min=0.0, max=0.5, init=0.5, inc=0.01, digits=2)
MV(REP_frac_10, min=0.0, max=0.5, init=0.5, inc=0.01, digits=2)
# If you add more pwrs here, make sure to add them to the list (GDEP_pwrs) below


#### End Modifiable Variables ###n

########################################################################va
#======================== Main Instance ===============================#
########################################################################
#### Other calculations ####
#Convert E-filter bases
V1, V2, V3, V4, V5, V6, V7, V8, V9 = electrodes.Field2Voltage([Ex+ExTrim, Ey+EyTrim, Ez+EzTrim, dxEx, dyEx, dzEx, dyEy, dzEy])+[dV1, dV2, dV3, dV4, dV5, dV6, dV7, dV8, dV9]
#print V1, V2, V3, V4, V5, V6, V7, V8, V9
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

		STP_PRB_PWR_TTL.append((t_gap2+subcy_time*i+start, Prb_P_highp, t_gap2+subcy_time*i+end, Prb_P_highp))
		STP_PRB_PWR_TTL.append((t_gap2+subcy_time*i+end, 0, t_gap2+subcy_time*(i+1), 0.))

		STP_PRB_freq.append((subcy_time*i+start, CavPrb_P_f0, subcy_time*i+end, CavPrb_P_f1))
		STP_GATE.append((t_gap2+subcy_time*i+start, 1-Prb_P_gate, t_gap2+subcy_time*i+end, 1-Prb_P_gate))
		STP_GATE.append((t_gap2+subcy_time*i+end, 1, t_gap2+subcy_time*(i+1), 1))

	if PRB_U_ttl:
		start, end = Prb_P_wait_us+Prb_P_dur_us+Prb_U_wait_us,  Prb_P_wait_us+Prb_P_dur_us+Prb_U_wait_us+Prb_U_dur_us
		STP_PRB_EOM.append((t_gap2+subcy_time*i+start, PRB_U_ttl, t_gap2+subcy_time*i+end, PRB_U_ttl))
		STP_PRB_EOM.append((t_gap2+subcy_time*i+end, 0, t_gap2+subcy_time*(i+1), 0.))

		STP_PRB_PWR_TTL.append((t_gap2+subcy_time*i+start, Prb_U_highp, t_gap2+subcy_time*i+end, Prb_U_highp))
		STP_PRB_PWR_TTL.append((t_gap2+subcy_time*i+end, 0, t_gap2+subcy_time*(i+1), 0.))

		STP_PRB_freq.append((subcy_time*i+start, CavPrb_U_f0, subcy_time*i+end, CavPrb_U_f1))
		STP_GATE.append((t_gap2+subcy_time*i+start, 1-Prb_U_gate, t_gap2+subcy_time*i+end, 1-Prb_U_gate))
		STP_GATE.append((t_gap2+subcy_time*i+end, 1, t_gap2+subcy_time*(i+1), 1))

	if PRB_L_ttl:
		start = Prb_P_wait_us+Prb_P_dur_us+Prb_U_wait_us+Prb_U_dur_us+Prb_L_wait_us
		end = Prb_P_wait_us+Prb_P_dur_us+Prb_U_wait_us+Prb_U_dur_us+Prb_L_wait_us+Prb_L_dur_us
		STP_PRB_EOM.append((t_gap2+subcy_time*i+start, PRB_L_ttl, t_gap2+subcy_time*i+end, PRB_L_ttl))
		STP_PRB_EOM.append((t_gap2+subcy_time*i+end, 0, t_gap2+subcy_time*(i+1), 0.))

		STP_PRB_PWR_TTL.append((t_gap2+subcy_time*i+start, Prb_L_highp, t_gap2+subcy_time*i+end, Prb_L_highp))
		STP_PRB_PWR_TTL.append((t_gap2+subcy_time*i+end, 0, t_gap2+subcy_time*(i+1), 0.))

		STP_PRB_freq.append((subcy_time*i+start, CavPrb_L_f0, subcy_time*i+end, CavPrb_L_f1))
		STP_GATE.append((t_gap2+subcy_time*i+start, 1-Prb_L_gate, t_gap2+subcy_time*i+end, 1-Prb_L_gate))
		STP_GATE.append((t_gap2+subcy_time*i+end, 1, t_gap2+subcy_time*(i+1), 1))

	#STP_PRB_PWR_TTL.append((t_gap2+subcy_time*i+Prb_P_wait_us+Prb_P_dur_us, (PRB_U_ttl or PRB_L_ttl), t_gap2+subcy_time*i+end, (PRB_U_ttl or PRB_L_ttl)))
	#STP_PRB_PWR_TTL.append((t_gap2+subcy_time*i+end, 0, t_gap2+subcy_time*(i+1), 0.))

#Append ghost event to bringe the total length of the stamp to PRB_time in total, since timer.appendMod is a dumb function!
if PRB_ttl or PRB_U_ttl or PRB_L_ttl:
	STP_PRB_EOM.append((t_PRB-1, 0, t_PRB, 0.))
	STP_PRB_PWR_TTL.append((t_PRB-1, 0, t_PRB, 0.))
	STP_PRB_freq.append((t_PRB-1, CavPrb_P_f0, t_PRB, CavPrb_P_f0))
	STP_GATE.append((t_PRB-1, 1, t_PRB, 1))

#Exepriment: Trigger RFSoc with each STP_PRB_EOM (TTL) and only write three ramps to save cycle time

# AUX1 should always be zero during PRB; AUX2 switches between OP and DEP

time_FinalWait_ms = max([3.0,PSC_ramp_ms])

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

### TRANSPORT
#times_transport = Transport_DDSRampMode(times, Trans_acc_g, Trans_dist_mm, Max_df=Trans_MaxF_MHz)
#times_Wait1 = times.append(Wait1_ms*Unit.ms(), "Wait In Cav")
#if Trans_RoundTrip == 1:
#	times_transport_back = Transport_DDSRampMode(times, Trans_acc_g, -Trans_distance_mm, Max_df=Trans_MaxF_MHz)

#transport 1
times_transport = Transport(times, Trans_acc_g, Trans_dist_mm, Max_df=Trans_MaxF_MHz, mode=Trans_mode, twoAoms=Trans_twoAom, Npts=Trans_Npts)
#wait 1
#if Trans_hold_1_ms>0.:
times_Wait1 = times.append(Trans_hold_1_ms*Unit.ms(), "Wait after transport 1")
times_transport &= times_Wait1
#transport 2
if abs(Trans_dist_2_mm)>0.:
	times_transport_2 = Transport(times, Trans_acc_g, Trans_dist_2_mm, Max_df=Trans_MaxF_MHz, mode=Trans_mode, twoAoms=Trans_twoAom, Npts=Trans_Npts)
	times_transport &= times_transport_2
#wait 2
if Trans_hold_2_ms>0.:
	times_Wait11 = times.append(Trans_hold_2_ms*Unit.ms(), "Wait after transport 2")
#transport 3
if abs(Trans_dist_3_mm)>0.:
	times_transport_3 = Transport(times, Trans_acc_g, Trans_dist_3_mm, Max_df=Trans_MaxF_MHz, mode=Trans_mode, twoAoms=Trans_twoAom, Npts=Trans_Npts)
	times_transport &= times_transport_3

#times_transport = times_transport_1 #& times_transport_2&times_transport_3 HOW to fix this correctly

times_dRSC = []
if dRSC_switch == 1:
	for i in range(int(dRSC1_repetitions)):
		times_dRSC.append(times.append(dRSC_Dur_ms*Unit.ms(), 'dRSC1'))
		times_c1 = times.append(c1_hold_time_ms*Unit.ms(), 'Compress1')
times_dRSC2 = []
if Ramp1_switch == 1:
	times_ramp1 = times.append(Ramp1_dur_us*Unit.us(), 'Ramp1')
if Ramp2_switch == 1:
	times_ramp2 = times.append(Ramp2_dur_us*Unit.us(), 'Ramp2')
if Ramp3_switch == 1:
	times_ramp3 = times.append(Ramp3_dur_us*Unit.us(), 'Ramp3')
times_rampall = times.append(0)
times_Wait1p5 = times.append(Wait1p5_ms*Unit.ms(), "Wait In Cav AFTER dRSC")


if BRamp1_ttl == 1:
	times_BRamp1 = times.append(BRamp1_ms*Unit.ms(),'B Ramp 1')
	times_BRamp1_settle = times.append(BRamp1_settle_ms*Unit.ms(),'B Ramp 1 Settle')
if OP_REP_ttl == 1:
	times_OP = times.append(OP_REP_ms*Unit.ms(),'Optical Pumping')
if BRamp2_ttl == 1:
	times_BRamp2 = times.append(BRamp2_ms*Unit.ms(),'B Ramp 2')
if GDEP_ttl == 1:
	times_GDEP = times.append(GDEP_ms*Unit.ms(), 'GDEP right before probe')

if PRB_mode == 1:
	times_delay = times.append(PRB_delay_us*Unit.us(), 'PRB_delay')
	#times_tmp = copy.deepcopy(times)
	times_Prb = times.appendMod(STP_PRB, PRB_repetitions, 'CavPrb')
	#Since RFSos is triggered by PRB_EOM_ttl start it's time interval at "zero" i.e. afer probe gap
	times_Prb_latetrig = TimeInterval(0, times_Prb.length())
	print(times_Prb_latetrig)
	#times_Prb_EOM = times_tmp.appendMod(STP_PRB_EOM, PRB_repetitions, 'CavPrbEOM')
elif PRB_mode == 2:
	times_CavPrb = times_transport.beforeEnd(PRB_time_ms*Unit.ms())
times_Wait2 = times.append(Wait2_ms*Unit.ms(), "Wait After Slice and Probe")


#### Sequence Actions ####
### Initiation ###
# Digital seq
MOT0_ttl.SetInterval(times_Init, 1)
REP0_ttl.SetInterval(times_Init, 1)
Scope_trig.SetInterval(times_Init, 0)
Cam_trig.SetInterval(times_Init, 1)
UV_ttl.SetInterval(times_Init, 0)
LAT1_ttl.SetInterval(times_Init, LTT)
LAT2_ttl.SetInterval(times_Init, LBT)
Sacher2_ttl.SetInterval(times_Init, 0)
V1_ttl.SetInterval(times_Init, V1_main_ttl)
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
EDFA_1529_ttl.SetInterval(times_Init, Floquet_AOM_TTL)
MOT2_ttl.SetInterval(times_Init, 0)
dRSC_LAT_ttl.SetInterval(times_Init, 0)
Digi_test.SetInterval(times_Init, 1)
# Analog seq
MOT0_pwr.SetInterval(times_Init, MOT_MOTPwr)
REP0_pwr.SetInterval(times_Init, MOT_REPPwr)
MOTCoil.SetInterval(times_Init, MOT_CoilCurr)
BiasX.SetInterval(times_Init, MOT_BiasX_G)
BiasY.SetInterval(times_Init, MOT_BiasY_G)
BiasZ.SetInterval(times_Init, MOT_BiasZ_G)
LAT1_pwr.SetInterval(times_Init, LBP)
LAT2_pwr.SetInterval(times_Init, LTP)
Sacher2_pwr.SetInterval(times_Init, 0)
LAT0_pwr.SetInterval(times_Init, LMP)
Blue_pwr.SetInterval(times_Init, PRB_Ctrl_pwr)
ODT2_pwr.SetInterval(times_Init, 0)
Nufern0_pwr.SetInterval(times_Init, PRB_pwr_low)
CavPrbEOM_pwr.SetInterval(times_Init, PRB_pwr_high)
VImg_pwr.SetInterval(times_Init, Img_vert_pwr)
MOT2_pwr.SetInterval(times_Init, 0)
D1Laser1_pwr.SetInterval(times_Init, dRSC_Pump_pwr)
EDFA_1529_pwr.SetInterval(times_Init, Floquet_AOM_pwr)
dRSC_LAT2_pwr.SetInterval(times_Init, 0)
MOT1_pwr.SetInterval(times_Init, 0)
MOT2_pwr.SetInterval(times_Init, 0)
EF1.SetInterval(times_Init, V1)
EF2.SetInterval(times_Init, V2)
EF3.SetInterval(times_Init, V3)
EF4.SetInterval(times_Init, V4)
EF5.SetInterval(times_Init, V5)
EF6.SetInterval(times_Init, V6)
EF7.SetInterval(times_Init, V7)
EF8.SetInterval(times_Init, V8)
EF9.SetInterval(times_Init, V9)
dRSC_LAT_pwr.SetInterval(times_Init, 0)
Anal_test.SetInterval(times_Init, 5.0) # Machine status trigger
#PSC_outOff.SetInterval(times_Init, PSC_output_offset_1)
# DDS seq 1
# DDS_REP.SetInterval(times_Init, DDS_REP.ssv, REPFREQ)
# DDS_MOT.SetInterval(times_Init, DDS_MOT.ssv, MOTFREQ)
DDS_REP.SetInterval(times_Init, REPFREQ)
DDS_MOT.SetInterval(times_Init, MOTFREQ)
#DDS_LAT1.SetInterval(times_Init, ModeSort3_MHz*Unit.MHz())
DDS1_2.SetInterval(times_Init, PSC_lock1_MHz*Unit.MHz())
# DDS seq 2
DDS_CavPrbAOM.SetInterval(times_Init, CavPrb_FreqOffset_MHz*Unit.MHz())
DDS_chan1.SetInterval(times_Init, 80.0+Img_det23_MHz)
DDS_OptPump1.SetInterval(times_Init, 80.0)
#DDS2_3.SetInterval(times_Init, ModeSort1_MHz*Unit.MHz())
# DDS PDH seqc
DDS_PDH1560.SetInterval(times_Init, PDH1560_freq*Unit.MHz())
DDS_PDH960.SetInterval(times_Init, PDH960_freq*Unit.MHz())
DDS_PDH780.SetInterval(times_Init, PDH780_freq*Unit.MHz())
RFSOC1_CavPrbEom.SetInterval(times_Init, PRB_f0_MHz*Unit.MHz())
DDS_HalfRng.SetInterval(times_Init, 0)
# SPCM seq
PC_bin_num.SetInterval(times_Init, PC_bin_number)
PC_max_rate.SetInterval(times_Init, PC_max_rate_MHz)
if DetMode == 1:
	PC_save.SetInterval(times_Init, PC_save_switch)
	PT_save.SetInterval(times_Init, 0)
elif DetMode == 2:
	PC_save.SetInterval(times_Init, 0)
	PT_save.SetInterval(times_Init, PC_save_switch)
# Lab Bricks 
LB2_freq.SetInterval(times_Init, Floq_SB1_Freq_MHz)
LB2_pow.SetInterval(times_Init, Floq_SB1_pwr_dBm)
LB2_ttl.SetInterval(times_Init, 1)
# LB3_freq.SetInterval(times_Init, MWaves_Freq_MHz)
# LB3_pow.SetInterval(times_Init, MWaves_pwr_dBm)
# LB3_ttl.SetInterval(times_Init, MW_CW_ttl)
# ADF435X
#AD1_freq.SetInterval(times_Init, MWaves_Freq_MHz)
#AD1_pow.SetInterval(times_Init, MWaves_pwr_dBm)
#AD1_ttl.SetInterval(times_Init, MWaves_AD_ttl)
#Camera
Camera_gain.SetInterval(times_Init, Img_gain_dB)


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
BiasX.SetInterval(times_transport.afterStart(times_transport.length()/2.0), PGC_BiasX_G, dRSC_Bx_G)
BiasY.SetInterval(times_transport.afterStart(times_transport.length()/2.0), PGC_BiasY_G, dRSC_By_G)
BiasZ.SetInterval(times_transport.afterStart(times_transport.length()/2.0), PGC_BiasZ_G, dRSC_Bz_G)

# MOT0_ttl.SetInterval(times_transport.afterward(0), 0)
#  	REP0_ttl.SetInterval(times_rt.afterward(0), 0)
# MOTCoil.SetInterval(times_transport.afterStart(Trans_PGC_delay_ms*Unit.ms()).afterward(0), MOT_CoilCurr)transpo


## Turn off Floquet beam during transport
EDFA_1529_ttl.SetInterval(times_transport, Floquet_Transport_TTL)


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


### Depump during transport
MOT2_ttl.SetInterval(times_transport, Trans_GDEP_ttl)
MOT2_ttl.SetInterval(times_transport.afterward(0), 0)
MOT2_pwr.SetInterval(times_transport, Trans_GDEP_pwr)

### degenerate Raman sideband cooling 
if dRSC_switch == 1:
	for this_time in times_dRSC:
		# turn off Floquet
		EDFA_1529_ttl.SetInterval(this_time, Floquet_dRSC_TTL)

		# Use proper RF source for driving the EOM
		AUX_ttl.SetInterval(this_time, 1) # dRSC
		AUX2_ttl.SetInterval(this_time, 1) # MUST BE ONE TO ENSURE THAT LAB BRICK IS TRIGGERED ON

		# PGC
		MOT0_ttl.SetInterval(this_time, dRSC_PGC_switch)
		REP0_ttl.SetInterval(this_time,dRSC_PGC_switch) 
		MOT0_ttl.SetInterval(this_time.afterward(0), c1_PGC_switch)
		REP0_ttl.SetInterval(this_time.afterward(0), c1_PGC_switch) 

		# Pump laser
		D1Laser1_ttl.SetInterval(this_time.afterStart(dRSC_LAT_rampON_us*Unit.us()), dRSC_Pump_ttl)
		D1Laser1_pwr.SetInterval(this_time, dRSC_Pump_pwr)
		D1Laser1_ttl.SetInterval(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()),0)
		# Horizontal lattice 
		dRSC_LAT_ttl.SetInterval(this_time.afterStart(0), dRSC_HLAT_ttl)
		dRSC_LAT_pwr.SetLogRamp(this_time.afterStart(dRSC_LAT_rampON_us*Unit.us()), 0, dRSC_HLAT_pwr)
		dRSC_LAT_pwr.SetLogRamp(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()), dRSC_HLAT_pwr, c1_HLAT_pwr)
		dRSC_LAT_ttl.SetInterval(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()), np.maximum(dRSC_HLAT_ttl,c1_HLAT_ttl))
		dRSC_LAT_ttl.SetInterval(this_time.afterward(0), c1_HLAT_ttl)
		# Vertical lattice
		LAT0_ttl.SetInterval(this_time.afterStart(0), dRSC_VLAT_ttl)
		LAT1_ttl.SetInterval(this_time.afterStart(0), dRSC_VLAT_ttl)
		LAT2_ttl.SetInterval(this_time.afterStart(0), dRSC_VLAT_ttl)
		LAT0_pwr.SetLogRamp(this_time.afterStart(dRSC_LAT_rampON_us*Unit.us()), LAT0_pwr.GetLastValue(), dRSC_VLATmain_pwr)
		LAT0_pwr.SetLogRamp(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()), dRSC_VLATmain_pwr, c1_VLATmain_pwr)
		LAT0_ttl.SetInterval(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()), np.maximum(dRSC_VLAT_ttl,c1_VLAT_ttl))
		LAT1_ttl.SetInterval(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()), np.maximum(dRSC_VLAT_ttl,c1_VLAT_ttl))
		LAT2_ttl.SetInterval(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()), np.maximum(dRSC_VLAT_ttl,c1_VLAT_ttl))
		LAT0_ttl.SetInterval(this_time.afterward(0), c1_VLAT_ttl)
		LAT1_ttl.SetInterval(this_time.afterward(0), c1_VLAT_ttl)
		LAT2_ttl.SetInterval(this_time.afterward(0), c1_VLAT_ttl)
		# ELAT lattice
		Sacher2_ttl.SetInterval(this_time.afterStart(0), dRSC_ELAT_ttl)
		Sacher2_pwr.SetLogRamp(this_time.afterStart(dRSC_LAT_rampON_us*Unit.us()), 0, dRSC_ELAT_pwr)
		Sacher2_pwr.SetLogRamp(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()), dRSC_ELAT_pwr, c1_ELAT_pwr)
		Sacher2_ttl.SetInterval(this_time.beforeEnd(dRSC_LAT_rampOFF_us*Unit.us()), np.maximum(c1_ELAT_ttl,dRSC_ELAT_ttl))
		Sacher2_ttl.SetInterval(this_time.afterward(0), c1_ELAT_ttl)
		# # "compression" stage; if duration is zero, this just sets the desired trap configuration
		# NOTHING HAPPENS DURING COMPRESSION! Just determines the endpoint of previous dRSC (and startpoint of next one)
		# as well as a holding time



# trap ramping stage, if we want to adiabatically swap from VLAT to ELAT
if Ramp1_switch == 1:
	LAT0_ttl.SetInterval(times_ramp1.afterStart(0), Ramp1_ODT_TTL)
	LAT1_ttl.SetInterval(times_ramp1.afterStart(0), Ramp1_Retro_TTL)
	LAT2_ttl.SetInterval(times_ramp1.afterStart(0), Ramp1_Retro_TTL)
	Sacher2_ttl.SetInterval(times_ramp1.afterStart(0), Ramp1_ELAT_TTL)

	samprate = np.minimum(0.04, Ramp1_steps/Ramp1_dur_us)
	LAT0_pwr.SetLogRamp(times_ramp1, LAT0_pwr.GetLastValue(), Ramp1_ODT_pwr, sample_rate=samprate)
	LAT1_pwr.SetLogRamp(times_ramp1, LAT1_pwr.GetLastValue(), Ramp1_Retro_pwr, sample_rate=samprate)
	LAT2_pwr.SetLogRamp(times_ramp1, LAT2_pwr.GetLastValue(), Ramp1_Retro_pwr, sample_rate=samprate)
	Sacher2_pwr.SetLogRamp(times_ramp1, Sacher2_pwr.GetLastValue(), Ramp1_ELAT_pwr, sample_rate=samprate)
if Ramp2_switch == 1:
	samprate = np.minimum(0.04, Ramp1_steps/Ramp2_dur_us)
	#print samprate
	LAT0_pwr.SetLogRamp(times_ramp2, Ramp1_ODT_pwr, Ramp2_ODT_pwr, sample_rate=samprate)
	LAT1_pwr.SetLogRamp(times_ramp2, Ramp1_Retro_pwr, Ramp2_Retro_pwr, sample_rate=samprate)
	LAT2_pwr.SetLogRamp(times_ramp2, Ramp1_Retro_pwr, Ramp2_Retro_pwr, sample_rate=samprate)
	Sacher2_pwr.SetLogRamp(times_ramp2, Ramp1_ELAT_pwr, Ramp2_ELAT_pwr, sample_rate=samprate)
if Ramp3_switch == 1:
	samprate = np.minimum(0.04, Ramp1_steps/Ramp3_dur_us)
	LAT0_pwr.SetLogRamp(times_ramp3, Ramp2_ODT_pwr, Ramp3_ODT_pwr, sample_rate=samprate)
	LAT1_pwr.SetLogRamp(times_ramp3, Ramp2_Retro_pwr, Ramp3_Retro_pwr, sample_rate=samprate)
	LAT2_pwr.SetLogRamp(times_ramp3, Ramp2_Retro_pwr, Ramp3_Retro_pwr, sample_rate=samprate)
	Sacher2_pwr.SetLogRamp(times_ramp3, Ramp2_ELAT_pwr, Ramp3_ELAT_pwr, sample_rate=samprate)
if Ramp1_switch or Ramp2_switch or Ramp3_switch:
	LAT0_ttl.SetInterval(times_rampall.afterward(0), RampFinal_ODT_TTL)
	LAT1_ttl.SetInterval(times_rampall.afterward(0), RampFinal_Retro_TTL)
	LAT2_ttl.SetInterval(times_rampall.afterward(0), RampFinal_Retro_TTL)
	Sacher2_ttl.SetInterval(times_rampall.afterward(0), RampFinal_ELAT_TTL)



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
if BRamp1_ttl == 1:
	BiasX.SetInterval(times_BRamp1, dRSC_Bx_G, Bx_1_G)
	BiasY.SetInterval(times_BRamp1, dRSC_By_G, By_1_G)
	BiasZ.SetInterval(times_BRamp1, dRSC_Bz_G, Bz_1_G)


# optical pumping
if OP_REP_ttl == 1:
	D1Laser1_ttl.SetInterval(times_OP, 1)
	D1Laser1_pwr.SetInterval(times_OP, OP_REP_pwr)
	D1Laser1_ttl.SetInterval(times_OP.afterward(0), 0)
	#LabBrick Trigger
	#Switch REP beam to appropriate RF type
	if OP_REP_RF_type == 0: # typically for dRSC | strong repump (1->2') sideband (6831 MHz from LabBrick 5626 thru big amp) and relatively weak carrier (550 MHz detuned from 2->2') by zeroing BesselJ_0
		AUX_ttl.SetInterval(times_OP, 1)
		AUX2_ttl.SetInterval(times_OP, 1) # MUST BE ONE TO ENSURE THAT LAB BRICK IS TRIGGERED ON
	elif OP_REP_RF_type == 1: # typically for O P | want quite weak repump sideband and strong pumping carrier, use attenuated version of LabBrick 5626 signal.
		AUX_ttl.SetInterval(times_OP, 0)
		AUX2_ttl.SetInterval(times_OP, 1)
	elif OP_REP_RF_type == 2: # typically for depumping | turn off 1->2' sideband, turn on ~2->2' resonant light (crapbox RF @ 550 MHz)
		AUX_ttl.SetInterval(times_OP, 0)
		AUX2_ttl.SetInterval(times_OP, 0) 


# ramp B-field to probe value, AFTER optical pumping
if BRamp2_ttl == 1:
	if BRamp1_ttl == 1:
		#Ramp B fields to PRB values
		BiasX.SetInterval(times_BRamp2, Bx_1_G, Bx_2_G)
		BiasY.SetInterval(times_BRamp2, By_1_G, By_2_G)
		BiasZ.SetInterval(times_BRamp2, Bz_1_G, Bz_2_G)
	else:
		BiasX.SetInterval(times_BRamp2, dRSC_Bx_G, Bx_2_G)
		BiasY.SetInterval(times_BRamp2, dRSC_By_G, By_2_G)
		BiasZ.SetInterval(times_BRamp2, dRSC_Bz_G, Bz_2_G)

if GDEP_ttl == 1:
	DEP_det_MHz = Rb.DDS_MOT_22(GDEP_det_MHz)
	DDS_MOT.SetInterval(times_BRamp1, DDS_MOT.GetLastValue(), DEP_det_MHz) # DOES THIS DURING BRamp1!!!
	MOT2_ttl.SetInterval(times_GDEP, 1)
	MOT2_ttl.SetInterval(times_GDEP.afterward(0), 0)
	MOT2_pwr.SetInterval(times_GDEP, GDEP_pwr)


### Probe cycle ###
if PRB_mode == 1: # Static cloud in the cavity
	# # # # For now, let the final compression stage determine the trap during probing


	# Ramp the PSC lock point starting 10 ms after 
	DDS1_2.SetInterval(times_Prb.afterStart(10*Unit.ms()).afterward(PSC_ramp_ms*Unit.ms()), PSC_lock1_MHz*Unit.MHz(), PSC_lock2_MHz*Unit.MHz())
	#PSC_outOff.SetInterval(times_Prb.afterStart(10*Unit.ms()).afterward(PSC_ramp_ms*Unit.ms()),PSC_output_offset_1,PSC_output_offset_2)

	# Turn on Floquet beam if desired
	floq_dur = Floquet_PRB_fraction*PRB_repetitions*(PRB_time_ms+PRB_OP_REP_total_ms+2*PRB_gaps_ms)
	EDFA_1529_ttl.SetInterval(times_Prb.afterStart(0), Floquet_AOM_TTL)
	# If relevant, turn it off after a fraction of the probe cycle
	EDFA_1529_ttl.SetInterval(times_Prb.afterStart(floq_dur*Unit.ms()).afterward(0), 0)

	
	# ELAT
	Sacher2_ttl.SetInterval(times_Prb, PRB_ELAT_ttl)

	#MOT
	MOTCoil.SetInterval(times_Prb, PRB_MOTcoil)
	# trigger the AWG for probing (sometimes applicable)
	AWG_trig.SetInterval(times_Prb, 1)
	
	# AUX1 should always be zero during PRB; AUX2 switches between OP and DEP
	AUX_ttl.SetInterval(times_Prb, 0)
	# AUX2 switches between REP and OP; its timing is determined by DepumpForPrb tab
	REP_fracs = [REP_frac_1, REP_frac_2, REP_frac_3, REP_frac_4, REP_frac_5, REP_frac_6, REP_frac_7, REP_frac_8, REP_frac_9, REP_frac_10]
	for ii in range(int(np.round(PRB_repetitions))): # there will be one pumping cycle in each PRB repetition
		if ii >= len(REP_fracs): # need to add more fractions if you use more repetitions and want repumping!
			break
		this_time_REP = times_Prb.afterStart(t_PRB*ii+t_gap1).afterward(PRB_OP_REP_total_ms*Unit.ms()*REP_fracs[ii])
		this_time_OP = this_time_REP.afterward(PRB_OP_REP_total_ms*Unit.ms()*(1-REP_fracs[ii]))
		AUX2_ttl.SetInterval(this_time_REP, 1)
		AUX2_ttl.SetInterval(this_time_OP, 0) # will stay this way until the next brief REP pulse


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
	else:
		swp_len = times_Prb.length()/PRB_sweep_num
		for sn in range(int(PRB_sweep_num)):
			RFSOC1_CavPrbEom.SetInterval(times_Prb_latetrig.afterStart(sn*swp_len).afterward(swp_len), CavPrb_f0, CavPrb_f1)
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
	Nufern0_pwr.SetInterval(times_CavPrb, PRB_pwr)
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
	RFSOC1_CavPrbEom.SetInterval(times_CavPrb, CavPrb_f0, CavPrb_f1)
	# Trigger the scope
	Scope_trig.SetInterval(times_CavPrb, 1)
	Scope_trig.SetInterval(times_CavPrb.afterward(0), 0)
	# Trigger the SPCM
	SPCM_ttl.SetInterval(times_CavPrb.beforeStart(SPCM_offset_ms*Unit.ms()), PRB_SPCM_ttl)
	SPCM_ttl.SetInterval(times_CavPrb.afterward(0), 0)

# CANT PUT THIS EARLIER BECAUSE GetLastValue calls in Imaging end up wrong if you do.

if Img_switch == 1: # Fluorescence imaging
	times_IMG = Imaging(times, 1, Img_prep_time_us*Unit.us(), Img_TOF_ms*Unit.ms(), Img_time_us*Unit.us(), Img_drop_time_ms*Unit.ms(), Img_horz_pwr, Img_REP_pwr, IMGMOTFREQ, IMGREPFREQ, img_dep_time = Img_DEPMOT_time_us*Unit.us())
	AUX_ttl.SetInterval(times_IMG.afterStart((Img_prep_time_us+Img_DEPMOT_time_us+1000.0*Img_TOF_ms)*Unit.us()).afterward(0),Img_RF_ttl)
	AUX_ttl.SetInterval(times_IMG.afterward(0),0)
if Img_switch == 2: # Absorption imaging
	times_IMG_DEPMOT = times_transport.beforeEnd(Img_DEPMOT_time_us*Unit.us())
	if Img_FRAMP_switch == 1:
		times_IMG_FRAMP = times.append(Img_FRAMP_ms*Unit.ms(), 'MOT Frequency Ramp')
	times_IMG_DEP = times.append(Img_DEPMOT_atend_us*Unit.us(), 'DEP')
	times_IMG_REP = times.append(Img_REP_atend_us*Unit.us(), 'REP')
	times_IMG = Imaging(times, 2, Img_prep_time_us*Unit.us(), Img_TOF_ms*Unit.ms(), Img_time_us*Unit.us(), Img_drop_time_ms*Unit.ms(), Img_horz_pwr, 0., None, None, blue_img_ttl=Blue_img_ttl)
if Img_switch == 3: # Single shot imaging
	times_IMG = Imaging(times, 3, Img_prep_time_us*Unit.us(), Img_TOF_ms*Unit.ms(), Img_time_us*Unit.us(), 0., 0., 0., 0., 0.)
times_FinalWait = times.append(time_FinalWait_ms*Unit.ms(), 'Final Ramp')
DDS_trig.Set([(0, 1, 10*Unit.us(), 1),(10*Unit.us(),0,times_FinalWait[1],0)])

### Depump the MOT for vertical absorption imaging ###
if Img_switch == 2:
	# 
	if Img_FRAMP_switch == 1:
		DDS_MOT.SetInterval(times_IMG_FRAMP,TMOTFreq,IMGMOTFREQ)
		DDS_REP.SetInterval(times_IMG_FRAMP,TREPFreq,IMGREPFREQ)
		
	# depump at end of transport
	MOT0_ttl.SetInterval(times_IMG_DEPMOT, 1)
	MOT0_ttl.SetInterval(times_IMG_DEPMOT.afterward(0), 0)
	# turn off ELAT during imaging
	Sacher2_ttl.SetInterval(times_IMG, 0)
	Sacher2_pwr.SetInterval(times_IMG, 0)
	# depump all (esp. MOT) just before imaging
	if Img_DEPMOT_atend_us > 0.0:
		MOT0_ttl.SetInterval(times_IMG_DEP, 1)
		MOT0_ttl.SetInterval(times_IMG_DEP.afterward(0), 0)
	# repump with dRSC beam just before imaging
	if Img_REP_atend_us > 0.0:
		D1Laser1_ttl.SetInterval(times_IMG_REP, 1)
		D1Laser1_pwr.SetInterval(times_IMG_REP, Img_REP_atend_pwr)
		D1Laser1_ttl.SetInterval(times_IMG_REP.afterward(0), 0)
	


# Imaging the beam
if Img_switch == 3:
	# Lattice beam
	LAT0_ttl.SetInterval(times_IMG, ImgSlice_LAT_ttl)
	LAT1_ttl.SetInterval(times_IMG, ImgSlice_LAT_ttl)
	LAT2_ttl.SetInterval(times_IMG, ImgSlice_LAT_ttl)
	# Vertical REP beam
	D1Laser1_ttl.SetInterval(times_IMG, ImgSlice_REP_ttl)
	D1Laser1_pwr.SetInterval(times_IMG, ImgSlice_REP_pwr)
	# Absorption beam
	Nufern1_ttl.SetInterval(times_IMG, ImgSlice_absorp_ttl)
	# Elliptical lattice
	Sacher2_ttl.SetInterval(times_IMG, Img_ELAT_ttl)
	Sacher2_pwr.SetInterval(times_IMG, Img_ELAT_pwr)
	# Elliptical lattice
	MOT2_ttl.SetInterval(times_IMG, Img_GDEP_ttl)
	MOT2_pwr.SetInterval(times_IMG, Img_GDEP_pwr)
	
	
### Final Frequency Ramp ###
# Set DDS back to original frequency
DDS_MOT.SetInterval(times_FinalWait, DDS_MOT.GetLastValue(), MOTFREQ)
DDS_REP.SetInterval(times_FinalWait, DDS_REP.GetLastValue(), REPFREQ)
# Turn up MOT coil again at end
MOTCoil.SetInterval(times_FinalWait, MOTCoil.GetLastValue(), MOT_CoilCurr)

#DDS1_2.SetInterval(times_FinalWait, PSC_lock2_MHz*Unit.MHz(), PSC_lock1_MHz*Unit.MHz())
#PSC_outOff.SetInterval(times_FinalWait, PSC_output_offset_2, PSC_output_offset_1)

#### Set steady state values ####
#### Logan 10/19/18: This is now ALSO where we sort the commands for each channel and check for timing conflicts (i.e. ONCE per channel, at the end of the sequence)
# Ditital seq
MOT0_ttl.SetSteadyStateValue(1)
REP0_ttl.SetSteadyStateValue(1)
Scope_trig.SetSteadyStateValue(0)
Cam_trig.SetSteadyStateValue(1)
UV_ttl.SetSteadyStateValue(1)
DDS_trig.SetSteadyStateValue(0)
LAT1_ttl.SetSteadyStateValue(1)
LAT2_ttl.SetSteadyStateValue(1)
Sacher2_ttl.SetSteadyStateValue(0)
V1_ttl.SetSteadyStateValue(V1_SS_ttl)
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
EDFA_1529_ttl.SetSteadyStateValue(Floquet_SteadyState_TTL)
MOT2_ttl.SetSteadyStateValue(0)
dRSC_LAT_ttl.SetSteadyStateValue(0)
AWG_trig.SetSteadyStateValue(0)
Digi_test.SetSteadyStateValue(1)
# Analog Seq
MOT0_pwr.SetSteadyStateValue(MOT_MOTPwr)
REP0_pwr.SetSteadyStateValue(MOT_REPPwr)
MOTCoil.SetSteadyStateValue(MOT_CoilCurr)
BiasX.SetSteadyStateValue(MOT_BiasX_G)
BiasY.SetSteadyStateValue(MOT_BiasY_G)
BiasZ.SetSteadyStateValue(MOT_BiasZ_G)
LAT1_pwr.SetSteadyStateValue(LTP)
LAT2_pwr.SetSteadyStateValue(LBP)
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
EF1.SetSteadyStateValue(V1_SteadyState)
EF2.SetSteadyStateValue(V2)
EF3.SetSteadyStateValue(V3)
EF4.SetSteadyStateValue(V4)
EF5.SetSteadyStateValue(V5)
EF6.SetSteadyStateValue(V6)
EF7.SetSteadyStateValue(V7)
EF8.SetSteadyStateValue(V8)
EF9.SetSteadyStateValue(V9)
Anal_test.SetSteadyStateValue(0.0)
#PSC_outOff.SetSteadyStateValue(PSC_output_offset_1)
# DDS seq 1
DDS_REP.SetSteadyStateValue(REPFREQ)
DDS_MOT.SetSteadyStateValue(MOTFREQ)
#DDS_LAT1.SetSteadyStateValue(ModeSort3_MHz*Unit.MHz())
#DDS1_2.SetSteadyStateValue(PSC_lock1_MHz*Unit.MHz())
# DDS PDH seq
DDS_PDH1560.SetSteadyStateValue(PDH1560_freq)
DDS_PDH960.SetSteadyStateValue(PDH960_freq)
DDS_PDH780.SetSteadyStateValue(PDH780_freq)
RFSOC1_CavPrbEom.SetSteadyStateValue(PRB_f0_MHz)
DDS_HalfRng.SetSteadyStateValue(5)
# DDS seq 2
DDS_CavPrbAOM.SetSteadyStateValue(CavPrb_FreqOffset_MHz*Unit.MHz())
DDS_chan1.SetSteadyStateValue(80)
DDS_OptPump1.SetSteadyStateValue(80)
#DDS2_3.SetSteadyStateValue(ModeSort1_MHz*Unit.MHz())
# Lab Bricks
#LB1_freq.SetSteadyStateValue(MWaves_Freq_MHz)
#LB1_pow.SetSteadyStateValue(MWaves_pwr_dBm)
LB1_ttl.SetSteadyStateValue(0)
LB2_freq.SetSteadyStateValue(Floq_SB1_Freq_MHz)
LB2_pow.SetSteadyStateValue(Floq_SB1_pwr_dBm)
LB2_ttl.SetSteadyStateValue(1)
# LB3_freq.SetSteadyStateValue(MWaves_Freq_MHz)
# LB3_pow.SetSteadyStateValue(MWaves_pwr_dBm)
# LB3_ttl.SetSteadyStateValue(0)
# MWaves_ttl.SetSteadyStateValue(0)
# ADF435X
#AD1_freq.SetSteadyStateValue(MWaves_Freq_MHz)
#AD1_pow.SetSteadyStateValue(MWaves_pwr_dBm)
AD1_ttl.SetSteadyStateValue(0)