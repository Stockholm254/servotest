def MHzToHz(v): #definition for the DDS board!
  return 1e6 * v
  
def SliceAOMDelay(t):
  return t-1.2
  
def VertRepAOMDelay(t):
  return t-1.73
  
def CavPrbAOMDelay(t):
  return t-1.45
  
def LatAOMDelay(t):
  return t-1.88
  
def MOTPrbDelay(t):
  return t-1.37
  
def BlueAOMDelay(t):
  return t-1.70
  
def TopImgAOMDelay(t):
  return t-2.60

def ElectrodeGain0(V):
  return V*(-1)
  
def ElectrodeGain1(V):
  return (-.009 - V)/2.081
  
def ElectrodeGain2(V):
  return (-.009 - V)/2.087

def ElectrodeGain3(V):
  return (-.008 - V)/2.090
  
def ElectrodeGain4(V):
  return (-.009 - V)/2.084
  
def ElectrodeGain5(V):
  return (-.009 - V)/2.084
  
def ElectrodeGain6(V):
  return (-.008 - V)/2.087
  
def ElectrodeGain7(V):
  return (-.008 - V)/2.091
  
def ElectrodeGain8(V):
  return (-.008 - V)/2.089
  
def ElectrodeGain9(V):
  return (-.007 - V)/2.078

def BiasXScale(V):
  return 16.0*V

def BiasXGauss(V):
  return 16.0*(V/7.62-0.0445)

def BiasYGauss(V):
  return V/0.66-0.0311

def BiasZGauss(V):
  return V/1.24+0.2989

def DigitalNot(TTL):
  if TTL < 0.5:
    OUT = 1
  else:
    OUT = 0
  return OUT