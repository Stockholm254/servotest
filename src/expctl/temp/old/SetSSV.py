#!/usr/bin/python 
# -*- coding: utf-8 -*- 

#### Modifiable Variables #### 
# Note: values must be integers or floats. 
#Tab:Blue
BlueTTL_ = 0
BluePwr_ = 4.3
PDH960_ = 302.3
#Tab:CavPrb
CavDTrapTTL_ = 0
CavPrbTTL_ = 0
SPCMGateTTL_ = 0
CavPrbEOMTTL_ = 0
CavDTrapPwr_ = 4.8
PSCOutputOffset_ = 0.0
CavPrbPwr_ = 3.3
PrbFEOMPwr_ = 5.0
ModeSorter2Freq_ = 205.0
PDH1560_ = 312.8
PDH780_ = 465.6
CavPrbEOMFreq_ = 301.0
CavPrbAOMFreq_ = 185.0
ModeSorter1Freq_ = 571.07
PhotonTimerSave_ = 0.0
CounterBinNum_ = 100.0
CounterSave_ = 0.0
CounterMaxRate_ = 20.0
LabBrick2Freq_ = 8500.0
LabBrick2Power_ = 2.0
LabBrick2TTL_ = 1
LabBrick3Freq_ = 8598.0
LabBrick3Power_ = -10.0
LabBrick3TTL_ = 1
#Tab:Debug
ScopeTrig_ = 0
DDSFPGATrig_ = 0
AWGTrigger_ = 0
DigitalTest_ = 1
AnalogTest_ = 0.0
PDHHalfRange_ = 5
DDSBox2channel2_ = 80
#Tab:EField
UltravioletTTL_ = 1
V1TTL_ = 1.0
EFilter1_ = 10.0
EFilter2_ = -3.68574464963
EFilter3_ = 1.34475795292
EFilter4_ = -1.59592030235
EFilter5_ = 2.865652298
EFilter6_ = 0.3902169413
EFilter7_ = 0.26010484905
EFilter8_ = 3.38224405358
EFilter9_ = -2.1180650305
#Tab:Floquet
FloquetTTL_ = 1.0
FloquetPwr_ = 3.1
#Tab:IMG
CameTrig_ = 1
VertImgPrbTTL_ = 0
VertImgPwr_ = 5.0
#Tab:LAT
LatHoriTTL_ = 1
LatVertTTL_ = 1
LatMainTTL_ = 1.0
LatHoriPwr_ = 4.83
LatVertPwr_ = 4.7
LatMainPwr_ = 4.8
LatHoriFreq_ = 391.4
#Tab:MOT
MOTTTL_ = 1
REPTTL_ = 1
MOTPwr_ = 5.0
REPPwr_ = 5.0
MOTCoil_ = 3.0
BiasX_ = -0.225
BiasY_ = 0.17
BiasZ_ = 0.381
OptPumpAOM1Freq_ = 80
REPLockFreq_ = 96.578984375
MOTLockFreq_ = 490.325
#Tab:MWaves
MWaveswitchTTL_ = 0
LabBrick1Freq_ = 1483.0
LabBrick1Power_ = -4.0
LabBrick1TTL_ = 0
MicrowaveFreq_ = 1483.0
MicrowavePower_ = -4.0
MicrowaveTTL_ = 0
#Tab:Slice
GlobalDEPTTL_ = 0
GlobalDEPPwr_ = 0
#Tab:dRSC
ELAT_TTL_ = 0
MOTdRSCPumpTTL_ = 0
MOTdRSCLatTTL_ = 0
dRSCPumpTTL_ = 0
Auxiliary2TTL_ = 0.0
AuxiliaryTTL_ = 0
dRSCLatTTL_ = 0
ELAT_Pwr_ = 0
dRSCPumpPwr_ = 4.6
MOTdRSCLatPwr_ = 0
MOTdRSCPumpPwr_ = 0
dRSCLATPwr_ = 0.0
#### End Modifiable Variables #### 

dic = locals()

for seq in all_sequences:
	for chan in seq.allChannels:
		if chan != None:
			if chan.chantype != 'Slave':
				value = dic[chan.VariableName()]
				chan.SetSteadyStateValue(value)

DDS_trig.Set([(0, 1, 10, 1), (10,0,10,0)])

