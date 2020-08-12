#jGlobals.py

# import socket
# from dat.all_channels import all_sequences
# from uitl import *

RUN_FLAG = 1

def init(): # Initialize GUI
  # print "globals initialized!"
  # global RUN_FLAG
  # RUN_FLAG=1
  # global Unit
  # Unit=UnitsModule()
  # global dm
  # dm=DeviceManager()
  # global MHz
  # MHz = 1.0
  return
  
class UnitsModule:
  def __init__(self, Hz=1e-6, s=1e6):
    self._Hz = Hz
    self._s  = s
    
  # Time  
  def s(self):
    return self._s
  def ms(self):
    return 1e-3*self._s
  def us(self):
    return 1e-6*self._s
  def ns(self):
    return 1e-9*self._s

  # Frequency
  def GHz(self):
    return 1e9*self._Hz
  def MHz(self):
    return 1e6*self._Hz
  def kHz(self):
    return 1e3*self._Hz
  def Hz(self):
    return self._Hz
  def mHz(self):
    return 1e-3*self._Hz
    