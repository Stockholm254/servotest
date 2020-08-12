#!/usr/bin/python
# -*- coding: utf-8 -*-

from .all_channels import *
from ..utilities import jGlobals

Unit = jGlobals.UnitsModule() # Global units

def DropAtoms(times, DropTime, Lat=1):
  # Time interval
  times_Drop = times.append(DropTime, 'DropAtoms')
  # Turn on/off beams
  if DropTime > 0:
    # Turn off/on MOT and repumper AOM
    MOT0_ttl.SetInterval(times_Drop,0)
    REP0_ttl.SetInterval(times_Drop,0)
    MOT0_ttl.SetInterval(times_Drop.afterward(0),1)
    REP0_ttl.SetInterval(times_Drop.afterward(0),1)
    # Turn off/on lattice AOM
    LAT0_ttl.SetInterval(times_Drop, 0)
    LAT1_ttl.SetInterval(times_Drop, 0)
    LAT2_ttl.SetInterval(times_Drop, 0)
    LAT0_ttl.SetInterval(times_Drop.afterward(0), Lat)
    LAT1_ttl.SetInterval(times_Drop.afterward(0), Lat)
    LAT2_ttl.SetInterval(times_Drop.afterward(0), Lat)
  return times_Drop

def MakeMOT(times, LoadTime, MOT_pwr=5., REP_pwr=5., CoilCurrent_A=3.):
  # Set time interval
  times_MOT = times.append(LoadTime, 'Make MOT')

  # Setup MOT beams
  MOT0_ttl.SetInterval(times_MOT, 1)
  REP0_ttl.SetInterval(times_MOT, 1)
  MOT0_pwr.SetInterval(times_MOT, MOT_pwr)
  REP0_pwr.SetInterval(times_MOT, REP_pwr)
  MOTCoil.SetInterval(times_MOT, CoilCurrent_A)

  return times_MOT

def PGC(times, t_Bias, t_Freq, t_PGC, t_Coil, Bx, By, Bz, MOT_pwr, REP_pwr, MOT_f, REP_f, t_rep_bef=0.0):
  # Set time interval
  times_CoilRamp = times.append(t_Bias, 'B Field Ramp') # Ramp the bias field
  times_FreqRamp = times.append(t_Freq, 'Freq Ramp') # Ramping the MOT and REP frequency
  times_Molasses = times.append(t_PGC,  'Molasses') # Time for cooling
  times_StepDown = times_CoilRamp.afterStart(t_Coil) # Time for ramping down the MOT coil
  
  # Turn off the laser during bias field set duration
  MOT0_ttl.SetInterval(times_CoilRamp, 0)
  REP0_ttl.SetInterval(times_CoilRamp, 0)
  # Set Bias Field
  BiasX.SetInterval(times_CoilRamp, Bx)
  BiasY.SetInterval(times_CoilRamp, By)
  BiasZ.SetInterval(times_CoilRamp, Bz)
  # MOT coil off
  MOTCoil.SetInterval(times_StepDown, MOTCoil.GetLastValue(), 0)
  # Ramp the detuning of MOT and REP beam
  MOT0_ttl.SetInterval(times_FreqRamp, 1)
  REP0_ttl.SetInterval(times_FreqRamp, 1)
  MOT0_pwr.SetInterval(times_FreqRamp, MOT_pwr)
  REP0_pwr.SetInterval(times_FreqRamp, REP_pwr)
  DDS_MOT.SetInterval(times_FreqRamp, MOT_f[0], MOT_f[1])
  DDS_REP.SetInterval(times_FreqRamp, REP_f[0], REP_f[1])
  # Molasses time
  MOT0_ttl.SetInterval(times_Molasses, 1)
  REP0_ttl.Set([(times_Molasses.start_t(),1,times_Molasses.end_t()-t_rep_bef,1)])  # Interval(times_Molasses, 1)
  # Turn off MOT and REP beams after molasses
  MOT0_ttl.SetInterval(times_Molasses.afterward(0), 0)
  # OLD: REP0_ttl.SetInterval(times_Molasses.afterward(0), 0)
  REP0_ttl.SetInterval(times_Molasses.beforeEnd(t_rep_bef), 0)

  return times_CoilRamp & times_FreqRamp & times_Molasses
  
def SetLatTTL(interval, LMT, LHT, LVT):
  LAT0_ttl.SetInterval(interval, LMT)
  LAT1_ttl.SetInterval(interval, LHT)
  LAT2_ttl.SetInterval(interval, LVT)

def SetLatPWR(interval, LMP, LHP, LVP):
  LAT0_pwr.SetInterval(interval, LMP)
  LAT1_pwr.SetInterval(interval, LHP)
  LAT2_pwr.SetInterval(interval, LVP)
  
def TOF(times, TimeOfFly):
  times_TOF = times.append(TimeOfFly, 'TOF')
  
  if TimeOfFly > 0:
    # MOT and REP
    MOT0_ttl.SetInterval(times_TOF, 0)
    REP0_ttl.SetInterval(times_TOF, 0)
    # MOT coil
    MOTCoil.SetInterval(times_TOF, 0)
    # Lattice
    LAT0_ttl.SetInterval(times_TOF, 0)
    LAT1_ttl.SetInterval(times_TOF, 0)
    LAT2_ttl.SetInterval(times_TOF, 0)
    # ELAT
    # Sacher2_ttl.SetInterval(times_TOF, 0)
  
  return times_TOF
  
def Transport(times, acceleration, distance, Lat_Bot_Freq=80, Lat_Top_Freq=80, Max_det=5.):
  wavelength = 783*1e-9 #m
  g = 9.8 #m/s^2
  dfMax = Max_det * Unit.MHz() #maximum velocity = 3.91m/s
  MHz = 1e6
  
  #Calculating transporatation time and frequency difference
  if acceleration == 0. :
    acc = 100. * g
  else:
    acc = acceleration * g
  trans_time = (abs(distance)*1e-3/acc)**(0.5) * Unit.s()
  sign = 1. if distance >= 0 else -1.
  # df = -0.5*sign*(abs(distance)*1e-3*acc)**(0.5) / (wavelength/2) * Unit.Hz() # sweep both DDS channels
  df = 0.5*sign*(abs(distance)*1e-3*acc)**(0.5) / (wavelength/2.) * Unit.Hz() # sweep only top channel
  
  if abs(df) <= dfMax*MHz:
    '''It is only ramping one DDS channel because the other channel will introduce noise while ramping.'''
    '''To be modified after the DDS box being fixed'''
    # Add time interval
    times_acc   = times.append(trans_time, "Acc")
    times_deacc = times.append(trans_time, "Deac")
    # Frequency Ramp
    DDS_LB.SetInterval(times_acc, Lat_Bot_Freq, Lat_Bot_Freq+df)
    # DDS_LT.SetInterval(times_acc, Lat_Top_Freq, Lat_Top_Freq-df)
    DDS_LB.SetInterval(times_deacc, Lat_Bot_Freq+df, Lat_Bot_Freq)
    # DDS_LT.SetInterval(times_deacc, Lat_Top_Freq-df, Lat_Top_Freq)
    # Print parameters
    print("Total transport time:", trans_time*2/1000, "ms")
    return times_acc & times_deacc
  else:
    # Calculate maximum speed
    # Vmax = 4*dfMax*MHz*wavelength # sweep both DDS channels
    Vmax = 2*dfMax*MHz * wavelength/2 #Factor of 2 coming from the double pass AOM
    df = sign * dfMax
    trans_time_max = Vmax/acc
    trans_time_cv = (abs(distance)*1e-3-Vmax*trans_time_max)/Vmax
    # Add time interval
    times_acc = times.append(trans_time_max*Unit.s(), "Acc")
    times_cv = times.append(trans_time_cv*Unit.s(), "Vc")
    times_deacc = times.append(trans_time_max*Unit.s(), "Deac")
    # Frequency Ramp
    DDS_LB.SetInterval(times_acc, Lat_Bot_Freq, Lat_Bot_Freq+df)
    # DDS_LT.SetInterval(times_acc, Lat_Top_Freq, Lat_Top_Freq-df)
    DDS_LB.SetInterval(times_cv, Lat_Bot_Freq+df)
    # DDS_LT.SetInterval(times_cv, Lat_Top_Freq-df)
    DDS_LB.SetInterval(times_deacc, Lat_Bot_Freq+df, Lat_Bot_Freq)
    # DDS_LT.SetInterval(times_deacc, Lat_Top_Freq-df, Lat_Top_Freq)
    # Print parameters
    print("Total transport time:", (trans_time_max*2+trans_time_cv)*1000, "ms", "(Maximum speed reached!)")
    return times_acc & times_cv & times_deacc

def Transport_DDSRampMode(times, acc, dist, Lat1_f=80, Lat2_f=80, Max_df=5.):
  # Use computer front panel to control the DDS ramping frequency, and use the ramp
  # direction register to change ramp direction

  wavelength = 784e-9 # m
  g = 9.8 #m/s^2
  dfMax = Max_df*Unit.MHz() # Maximum velocity = 3.91m/s
  MHz = 1e6
  
  #Calculating transporatation time and frequency difference
  if acc == 0.:
    acc = 100.*g
  else:
    acc = acc*g
  trans_time = (abs(dist)*1e-3/acc)**(0.5)*Unit.s()
  sign = 1. if dist >= 0 else -1.
  # df = -0.5*sign*(abs(distance)*1e-3*acc)**(0.5) / (wavelength/2) * Unit.Hz() # sweep both DDS channels
  df = 0.5*sign*(abs(dist)*1e-3*acc)**(0.5)/(wavelength/2.)*Unit.Hz() # sweep only top channel
  
  if abs(df) <= dfMax:
    '''It is only ramping one DDS channel because the other channel will introduce noise while ramping.'''
    '''To be modified after the DDS box being fixed'''
    # Add time interval
    times_acc = times.append(trans_time, "Acc")
    times_dac = times.append(trans_time, "Dac")
    # Frequency Ramp
    Digi_test.SetInterval(times_acc, 0)
    Digi_test.SetInterval(times_dac, 1)
    # Print parameters
    print("Total transport time:", trans_time*2/1e3, "ms")
    print("Acceleration time:", trans_time/1e3, "ms")
    return times_acc & times_dac
  else:
    # Calculate maximum speed
    # Vmax = 4*dfMax*MHz*wavelength # sweep both DDS channels
    Vmax = 2*dfMax*MHz*wavelength/2 #Factor of 2 coming from the double pass AOM pre-04/27/18

    df = sign * dfMax
    trans_time_max = Vmax/acc
    trans_time_cv = (abs(dist)*1e-3-Vmax*trans_time_max)/Vmax
    # Add time interval
    times_acc = times.append(trans_time_max*Unit.s(), "Acc")
    times_cv  = times.append(trans_time_cv*Unit.s(),  "Vc")
    times_dac = times.append(trans_time_max*Unit.s(), "Dac")
    # Frequency Ramp
    Digi_test.SetInterval(times_acc, 0)
    Digi_test.SetInterval(times_dac, 1)
    # Print parameters
    print("Total transport time:", (trans_time_max*2+trans_time_cv)*1000, "ms", "(Maximum speed reached!)")
    print("Acceleration time:", trans_time_max*1e3, "ms")
    
    return times_acc & times_cv & times_dac

def Imaging(times, mode, 
            t_prep, t_tof, t_img, t_gap, 
            img_pwr, rep_pwr, img_f, rep_f,
            Lat=0,blue_img_ttl=0.0,img_dep_time=0):
  '''
  The fluorescence imaging is using the MOT beam, and the absorption imaging is
  using the narrow 780 nm beam. 
  '''

  # Preperation and time of fly
  times_Prep = times.append(t_prep, 'ImagePrep')
  times_Dep  = times.append(img_dep_time)
  times_TOF  = TOF(times, t_tof)

  # turn off MOT coil during prep time
  MOTCoil.SetInterval(times_Prep, 0)
  # turn off MOT and REP beams during prep time
  MOT0_ttl.SetInterval(times_Prep, 0)
  REP0_ttl.SetInterval(times_Prep, 0)

  LAT0_ttl.SetInterval(times_Prep.afterStart(0), 0)
  LAT1_ttl.SetInterval(times_Prep.afterStart(0), 0)
  LAT2_ttl.SetInterval(times_Prep.afterStart(0), 0)

  if mode == 1: # Fluorescence imaging
    times_img1 = times.append(t_img, 'ForeGnd')
    # times_gap1 = DropAtoms(times, t_gap)
    times_gap1 = times.append(t_gap, 'DropAtoms')
    times_img2 = times.append(t_img, 'BackGnd')
    # Imaging preperation
    DDS_MOT.SetInterval(times_Prep, DDS_MOT.GetLastValue(), img_f)
    DDS_REP.SetInterval(times_Prep, DDS_REP.GetLastValue(), rep_f)
    MOT0_pwr.SetInterval(times_Prep, img_pwr)
    REP0_pwr.SetInterval(times_Prep, rep_pwr)

    if img_dep_time > 0:
      MOT0_ttl.SetInterval(times_Dep,1)
      REP0_ttl.SetInterval(times_Dep,0)

    # Turn on/off the beams
    if img_pwr > 0:
      MOT0_ttl.SetInterval(times_img1, 1)
    else:
      MOT0_ttl.SetInterval(times_img1, 0)
    if rep_pwr > 0:
      REP0_ttl.SetInterval(times_img1, 1)
    else:
      REP0_ttl.SetInterval(times_img1, 0)
    # Set lattice during imaging time, it is turned off during drop atoms
    SetLatTTL(times_img1, Lat, Lat, Lat)
    SetLatTTL(times_img2, Lat, Lat, Lat)
    # Trigger the camera
    Cam_trig.SetInterval(times_img1, 0)
    Cam_trig.SetInterval(times_img1.afterward(0), 1)
    Cam_trig.SetInterval(times_img2, 0)
    Cam_trig.SetInterval(times_img2.afterward(0), 1)
    return times_Prep & times_Dep & times_TOF & times_img1 & times_gap1 & times_img2
  
  elif mode == 2: # Absoption imaging
    times_img1 = times.append(t_img, 'ForeGnd')
    times_gap1 = DropAtoms(times, t_gap, Lat=0)
    times_img2 = times.append(t_img, 'BackGnd')
    times_gap2 = DropAtoms(times, t_gap, Lat=0)
    times_img3 = times.append(t_img, 'DarkField')
    # Turn on/off beams
    Nufern1_ttl.SetInterval(times_img1, 1)
    Nufern1_ttl.SetInterval(times_img1.afterward(0), 0)
    Blue_ttl.SetInterval(times_img1, blue_img_ttl)
    Blue_ttl.SetInterval(times_img1.afterward(0), 0)
    Nufern1_ttl.SetInterval(times_img2, 1)
    Nufern1_ttl.SetInterval(times_img2.afterward(0), 0)
    Blue_ttl.SetInterval(times_img2, blue_img_ttl)
    Blue_ttl.SetInterval(times_img2.afterward(0), 0)

    # Trigger the camera
    Cam_trig.SetInterval(times_img1, 0)
    Cam_trig.SetInterval(times_img1.afterward(0), 1)
    Cam_trig.SetInterval(times_img2, 0)
    Cam_trig.SetInterval(times_img2.afterward(0), 1)
    Cam_trig.SetInterval(times_img3, 0)
    Cam_trig.SetInterval(times_img3.afterward(0), 1)
    return times_Prep & times_TOF & times_img1 & times_gap1 & times_img2 & times_gap2 & times_img3

  elif mode == 3: # Single shot image
    times_img1 = times.append(t_img)
    # Trigger the camera
    Cam_trig.SetInterval(times_img1, 0)
    Cam_trig.SetInterval(times_img1.afterward(0), 1)
    return times_img1




# testing 08/07/18, temporary
def ImagingTest(times, mode, 
            t_prep, t_tof, t_img, t_gap, 
            img_pwr, rep_pwr, img_f, rep_f,
            Lat=0):
  '''
  The fluorescence imaging is using the MOT beam, and the absorption imaging is
  using the narrow 780 nm beam. 
  '''

  # Preperation and time of fly
  times_Prep = times.append(t_prep, 'ImagePrep')
  times_TOF  = TOF(times, t_tof)

  if mode == 1: # Fluorescence imaging
    times_img1 = times.append(t_img, 'ForeGnd')
    # times_gap1 = DropAtoms(times, t_gap)
    times_gap1 = times.append(t_gap, 'DropAtoms')
    times_img2 = times.append(t_img, 'BackGnd')
    # Imaging preperation
    ##DDS_MOT.SetInterval(times_Prep, DDS_MOT.GetLastValue(), img_f)
    DDS_REP.SetInterval(times_Prep, DDS_REP.GetLastValue(), rep_f)
    MOT0_pwr.SetInterval(times_Prep, img_pwr)
    REP0_pwr.SetInterval(times_Prep, rep_pwr)
    # Turn on/off the beams
    MOT0_ttl.SetInterval(times_img1, 1)
    REP0_ttl.SetInterval(times_img1, 1)
    # Set lattice during imaging time, it is turned off during drop atoms
    SetLatTTL(times_img1, Lat, Lat, Lat)
    SetLatTTL(times_img2, Lat, Lat, Lat)
    # Trigger the camera
    Cam_trig.SetInterval(times_img1, 0)
    Cam_trig.SetInterval(times_img1.afterward(0), 1)
    Cam_trig.SetInterval(times_img2, 0)
    Cam_trig.SetInterval(times_img2.afterward(0), 1)
    return times_Prep & times_TOF & times_img1 & times_gap1 & times_img2
  
  elif mode == 2: # Absoption imaging
    times_img1 = times.append(t_img, 'ForeGnd')
    times_gap1 = DropAtoms(times, t_gap)
    times_img2 = times.append(t_img, 'BackGnd')
    times_gap2 = DropAtoms(times, t_gap)
    times_img3 = times.append(t_img, 'DarkField')
    # Turn on/off beams
    Nufern1_ttl.SetInterval(times_img1, 1)
    Nufern1_ttl.SetInterval(times_img1.afterward(0), 0)
    Nufern1_ttl.SetInterval(times_img2, 1)
    Nufern1_ttl.SetInterval(times_img2.afterward(0), 0)
    # Trigger the camera
    Cam_trig.SetInterval(times_img1, 0)
    Cam_trig.SetInterval(times_img1.afterward(0), 1)
    Cam_trig.SetInterval(times_img2, 0)
    Cam_trig.SetInterval(times_img2.afterward(0), 1)
    Cam_trig.SetInterval(times_img3, 0)
    Cam_trig.SetInterval(times_img3.afterward(0), 1)
    return times_Prep & times_TOF & times_img1 & times_gap1 & times_img2 & times_gap2 & times_img3

  elif mode == 3: # Single shot image
    times_img1 = times.append(t_img)
    # Trigger the camera
    Cam_trig.SetInterval(times_img1, 0)
    Cam_trig.SetInterval(times_img1.afterward(0), 1)
    return times_img1

