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

def OPREPAOMDelay(t):
  return t-1.5
  
def TopImgAOMDelay(t):
  return t-2.60

def ElectrodeGain0(V):
  return V*(-1)
  
def ElectrodeGain1(V):
  return (V-0.08589)/-4.99052
  
def ElectrodeGain2(V):
  return (V-0.09467)/-4.98856

def ElectrodeGain3(V):
  return (V-0.09644)/-5.01450
  
def ElectrodeGain4(V):
  return (V-0.08533)/-4.99493
  
def ElectrodeGain5(V):
  return (V-0.09033)/-5.03693
  
def ElectrodeGain6(V):
  return (V-0.09333)/-4.98482
  
def ElectrodeGain7(V):
  return (V-0.09300)/-4.98610

def ElectrodeGain8(V):
  return (V-0.08756)/-5.03772
  
def ElectrodeGain9(V):
  return (V-0.09189)/-4.99482

# def ElectrodeGain0(V):
#   return V*(-1)
  
# def ElectrodeGain1(V):
#   return (V - 0.007)/2.460
  
# def ElectrodeGain2(V):
#   return (V - 0.005)/2.465

# def ElectrodeGain3(V):
#   return (V - 0.0037)/2.459
  
# def ElectrodeGain4(V):
#   return (V - 0.0072)/2.466
  
# def ElectrodeGain5(V):
#   return (V - 0.0094)/2.460
  
# def ElectrodeGain6(V):
#   return (V - 0.004)/2.460
  
# def ElectrodeGain7(V):
#   return (V - 0.0056)/2.459

# def ElectrodeGain8(V):
#   return (V - 0.0055)/2.464
  
# def ElectrodeGain9(V):
#   return (V - 0.0102)/2.463

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

def ShutterDelay(t):
  return t-5000.0