#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np

#################
## Rubidium-87 ##
#################
class Rb87:
  def __init__(self):
    lambda_D1 = 795.9788509   # Wavelength for D1 line transition in nm
    lambda_D2 = 780.241209686 # Wavelength for D1 line transition in nm

    Gamma_D1 = 5.746 # Natural Line Width (FWHM) for D1 line in MHz
    Gamma_D2 = 6.065 # Natural Line Width (FWHM) for D2 line in MHz


## All numbers are in MHz
def groundHF():
  return 6834.68261090429
 
def excitedHF(F1, F2):
  F1 = int(F1)
  F2 = int(F2)
  # returns the splitting between the given excited state levels
  f01 = 72.218
  f12 = 156.947
  f23 = 266.65
  fs = [0, f01, f01+f12, f01+f12+f23]
  df = fs[F2] - fs[F1]
  return df

# Repumper beat node locking parameters 
Helical_REP = 600.3 # Helical filter frequency (repumper)
REPAOM_Freq = -80 # repumper aom frequency
REP_PLL     = 64. # repumper PLL ratio

# MOT beat node locking parameters
Helical_MOT        = 100 # Helical filter frequency (MOT)
MOTAOM_Freq        = -80 # MOT aom frequency
MOTLockingAOM_Freq = 200 # Freq shift per pass, double pass AOM

def DDS_REP_11(detuning):
  # returns the Repumper DDS frequency for a given detuning from 1->1'
  REPFREQ = (detuning-Helical_REP-REPAOM_Freq+groundHF()-0.5*excitedHF(2,3)-excitedHF(1,2))/REP_PLL
  return REPFREQ

def DDS_REP_12(detuning):
  # returns the Repumper DDS frequency for a given detuning from 1->2'
  REPFREQ = (detuning-Helical_REP-REPAOM_Freq+groundHF()-0.5*excitedHF(2,3))/REP_PLL
  return REPFREQ
  
def Calc_DDS_REP(Fe, detuning):
  # returns the repumper DDS frequency for a given detuning from 1->F'
  master = -Helical_REP - REPAOM_Freq #2 -> 2',3' crossover (LO frequency to beatlock box)
  freq23 = master + 0.5*excitedHF(2,3)
  freq13 = freq23 + groundHF()
  freq1e = freq13 - excitedHF(Fe,3)
  return (detuning + freq1e) / REP_PLL
 
def Calc_DDS_MOT(Fe, detuning):
  #returns the MOT DDS frequency for a given detuning from 2->F' (F'=Fe)
  det23 = detuning - excitedHF(Fe,3)
  return DDS_MOT_23(det23)
  
def DDS_MOT_22(detuning):
  det23 = detuning - excitedHF(2,3)
  return DDS_MOT_23(det23)
  
def DDS_MOT_23(detuning):
  DDS = detuning - MOTAOM_Freq + 2*MOTLockingAOM_Freq + 0.5*excitedHF(2,3) - Helical_MOT
  return DDS

def Calc_DDS_MOT_Blast(Fe, detuning):
  #returns the MOT DDS frequency for a given detuning from 2->F' (F'=Fe)
  det23 = detuning - excitedHF(Fe,3)
  return DDS_MOT_23(det23)
