from signal import signal,SIGINT
import sys
from .rfsocdriver import *


bitfile_name = '/home/xilinx/ash/ddsfinal/ddsfinal10k_tm_3.bit'
rf = rfdriver(bitfile_name, False)

def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    sys.exit(0)

signal(SIGINT, handler)
active_channels = [0,1]
CAL_DDS_CLK = 409.6025 #The actual calibrated clock. Calibrate with an accurate spectrum analyzer .
#Actually I am not sure where the error comes from, The PLLs on ZCU111 board or those on DAC tiles.

SEQUENCER_CLK = CAL_DDS_CLK/2 #This is the clock for sequencer. This clock is hardwired on the FPGA to be DDS_CLK/2
SAMPLE_CLK = CAL_DDS_CLK*16 #This is the clock for the DACs. Again, hardwired to be DDS_CLK*16
#Actually in hardware it goes the other way, The DDS clock is derived from sample clock by /16

seq = [[0,1*10**6,2,5*10**6],[2,5*10**6,5,2*10**6],[5,2*10**6,10,1*10**6]]
convertedseq = ConvertSeqtoCountsandFTWs(seq)
print(seq)
triggers = [1,0,0]
phase_resets = [0,0,0]

rf.configureTriggerManager(config=0b111111111)

for chan in active_channels:
    rf.writeData(chan,convertedseq,triggers,phase_resets)
    rf.resetDoneRegister(chan)
    rf.startChannel(chan)

counter = 0
while(True):
    if(rf.isSequenceDone(active_channels)):
        counter = counter+1
        for chan in active_channels:
            rf.resetDoneRegister(chan)
            rf.startChannel(chan)
        print(f"Sequence executed {counter} times\n")



    
