## Machine parameters
## Last updated: Sep 14, 2018
## All numbers are in MHz

from .Rubidium import *

#####################################
### Narrow 780nm laser parameters ###
#####################################
N780_PDH_EOM_23 = 332.01    # For transfer cavity PDH locking to 2->3' transition. Blue sideband.
N780_Prob_AOM   = 2*200.0   # Cavity probe AOM frequence. Blue sideband. Double pass
N780_Prob_EOM   = -320.0    # Cavity probe EOM frequence. Red sideband

##########################################
### Blue Laser PDH Locking Frequencies ###
##########################################
# With 200 MHz blue AOM
Blue_PDH_40S  = 727.0 # Blue PDH locking freq for 40S
Blue_PDH_48S = 191.0  # Blue PDH locking freq for 48S, F'=3 (960.6269nm on wavemeter)
Blue_PDH_60S  = 228.0 # Blue PDH locking freq for 60S (left sideband), F'=3
Blue_PDH_60S  = 19.0  # Blue PDH locking freq for 60S (RIGHT sideband), F'=0
Blue_PDH_58D_3halves = 615.3		# Blue PDH locking freq for 58D_{3/2}, F'=0 (RIGHT sideband)
Blue_PDH_58D_5halves = 391.9 #397.9 # Blue PDH locking freq for 58D_{5/2}, F'=3   (RIGHT sideband)
Blue_PDH_58D_5halves = 645.8 # Blue PDH locking freq for 58D_{5/2}, F'=0   (RIGHT sideband)
Blue_PDH_70D_5halves = 629.26 #632.9 # Blue locking frequency for 70D_{5/2}, F' = 3 (RIGHT sideband, appears as left hand feature)
Blue_PDH_80D_5halves = 102.0  # 80D_{5/2}, F'=0, RIGHT sideband
Blue_PDH_80D_5halves = 151  # 80D_{5/2}, F'=3, LEFT sideband
Blue_PDH_90D_5halves = 465.0  # 90D_{5/2}, F'=3, RIGHT sideband (LEFT....)
Blue_PDH_98D_5halves = 205.0  # 98D_{5/2}, F'=3, LEFT sideband
Blue_PDH_100S = 580.7 # Blue PDH locking freq for 100S (left set of closest pairs)
Blue_PDH_105D_5halves = 307 # 105D_{5/2}, F'=3, RIGHT sideband (Might be 106)
Blue_PDH_111D_5halves = 127 # 111D_{5/2}, F'=3, RIGHT sideband


#######################################
### Experimental caivity parameters ###
#######################################
### Non planar cavity ###
Cav_1560_Carrier_00 = 733.8 # 476.2  # LEFT sideband. Lock here to put carrier of 780 on resonance with 00 mode of cavity
Cav_1560_Carrier_11 = 16.5  # RIGHT sideband. Lock here to put carrier of 780 on resonance with 11 mode of cavity

### Old parameters ###
Cav_PDH_23_TEM00 = 1260.0 # Cavity 1560 PDH locking frequency for 2->3' transition
Cav_Pol_split    = 43.0   # Cavity polarization mode spliting for TEM00
Cav_FSR_780      = 4431.0 # Cavity FSR for 780nm
Cav_df_TEM00TO01 = 1340.0 # Frequency difference between TEM00 and TEM01 mode (NOT SURE!!!)
Cav_df_TEM00TO20 = 1360.0 # Frequency difference between TEM00 and TEM20 mode (NOT SURE!!!)

##################################
### Transfer cavity parameters ###
##################################
TCav_FSR_780 = 1491.8 # Transfer cavity FSR for 780nm. (Measured on Apr 15th, 2016)

# Cavity probe EOM frequency
def Cav_Prob_EOM_23(det=0.0, pol=1):
  EOM_freq = N780_Prob_EOM+det+pol*Cav_Pol_split
  return abs(EOM_freq)
  
def Cav_Prob_EOM_22(det=0.0, pol=1):
  EOM_freq = N780_Prob_EOM+excitedHF(3,2)+det+pol*Cav_Pol_split
  return abs(EOM_freq)
    
# Cavity lock EOM frequency
def Cav_PDH_23(det):
  return Cav_PDH_23_TEM00+det

def Cav_PDH_22(det):
  return Cav_PDH_23_TEM00+excitedHF(3,2)+det

# Narrow 780nm transfer cavity lock EOM frequency
def N780_PDH_23(det):
  return N780_PDH_EOM_23+det
  
def N780_PDH_22(det):
  return N780_PDH_EOM_23+excitedHF(3,2)+det
  