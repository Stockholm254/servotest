## Machine parameters
## Last updated: Apr 15, 2016
## All numbers are in MHz

from .Rubidium import *

# Narrow 780nm laser parameters
N780_PDH_EOM_23 = 332.01    # For transfer cavity PDH locking to 2->3' transition. Blue sideband.
N780_Prob_AOM   = 2*200.0   # Cavity probe AOM frequence. Blue sideband. Double pass
N780_Prob_EOM   = -320.0    # Cavity probe EOM frequence. Red sideband

# Blue laser parameters (These nmbers might change due to the EM field)
Blue_PDH_40S = 682.5   # Blue PDH locking freq for 40S
Blue_PDH_48S = 51.5    # Blue PDH locking freq for 48S
Blue_PDH_60S = 166.75  # Blue PDH locking freq for 60S (left sideband)
Blue_PDH_62S = 644.0   # Blue PDH locking freq for 62S
Blue_PDH_75S = 240.0   # Blue PDH locking freq for 75S (left sideband)
Blue_PDH_85S = 581.5   # Blue PDH locking freq for 85S (right sideband)

# Experimental caivity parameters
Cav_PDH_23_TEM00 = 1260.0 # Cavity 1560 PDH locking frequency for 2->3' transition
Cav_Pol_split    = 43.0   # Cavity polarization mode spliting for TEM00
Cav_FSR_780      = 4431.0 # Cavity FSR for 780nm
Cav_df_TEM00TO01 = 1340.0 # Frequency difference between TEM00 and TEM01 mode (NOT SURE!!!)
Cav_df_TEM00TO20 = 1360.0 # Frequency difference between TEM00 and TEM20 mode (NOT SURE!!!)

# Transfer cavity parameters
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

