from signal import signal,SIGINT
import sys
from rfsocdriver import *
from pathlib import Path

def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    sys.exit(0)

#bitfile_name = '/home/xilinx/ash/ddsfinal/ddsfinal10k_tm_3.bit'
DIR_BITFILE = Path(__file__).parent
bitfile_path = str(DIR_BITFILE/"ddsfinal10k_tm_3.bit")
print(bitfile_path)

rf = rfdriver(bitfile_path, False)

if __name__ == "__main__":

    signal(SIGINT, handler)
    active_channels = [6,]
    CAL_DDS_CLK = 409.6025 #The actual calibrated clock. Calibrate with an accurate spectrum analyzer .
    #Actually I am not sure where the error comes from, The PLLs on ZCU111 board or those on DAC tiles.

    SEQUENCER_CLK = CAL_DDS_CLK/2 #This is the clock for sequencer. This clock is hardwired on the FPGA to be DDS_CLK/2
    SAMPLE_CLK = CAL_DDS_CLK*16 #This is the clock for the DACs. Again, hardwired to be DDS_CLK*16
    #Actually in hardware it goes the other way, The DDS clock is derived from sample clock by /16

    #seq = [[0,100*10**6,2*10**6,1*10**9],[2*10**6,500*10**6,2*10**9,20*10**6],[1*10**9,20*10**6,10*10**6,10*10**6]]
    #seq = [[0, 1e8, 2e6, 500e6],[2e6, 1e9, 10e6, 3e9], [10e6, 3e9, 20e6, 1e8]]
    seq = [[0, 1e9, 5e6, 3e9],[5e6, 3e9, 10e6, 1e9]] #high freq
    #seq = [[0, 0, 5e6, 1e9],[5e6, 1e9, 10e6, 0]] #low freq
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



    
