import numpy as np

#################################################
# Probe AOM Gain to Cavity Transmission on SPCM #
#################################################
def CavPrbV2R(V):
	'''
	Convert probe AOM control voltage to SPCM count rate on cavity peak 
	Calibrated at Mar 15, 2017

	In: Probe AOM control voltage
	Out: SPCM count rate in kHz
	'''
	P0   = -8.30150367
	gain = 5.73319346
	return np.exp(P0+gain*V)

########################
# Detection Efficiency #
########################
'''
Description: Efficiency of the detection optical system after the cavity, and the SPCM quantum efficiency
780/1560 dicroich, mirrors, lens, low pass filter, PBS, fiber coupling
'''
Eff_CavPrbOpt = 0.2673
Eff_SPCM      = 0.55

#####################
# Cavity Properties #
#####################
'''
Description: Nathan's planar cavity physical properties
'''
kappa = 1.5     # (MHz)
FSR   = 2.2e3   # (MHz)
T_mir = 0.00064 # Transmitivity of the top mirror
