from signal import signal,SIGINT
import sys
from pathlib import Path
from ..util.SequenceProcessor import *
from .rfsocdriver import *

def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    sys.exit(0)

#bitfile_name = '/home/xilinx/ash/ddsfinal/ddsfinal10k_tm_3.bit'
DIR_BITFILE = Path(__file__).parent
bitfile_path = str(DIR_BITFILE/"ddsfinal10k_serrodyne.bit")
print(bitfile_path)

rf = rfdriver(bitfile_path, False)

if __name__ == "__main__":

    signal(SIGINT, handler)
    #active_channels = [0,1,2,3,4,5,6,7]
    active_channels = [2,3]
    CAL_DDS_CLK = 409.6025 #The actual calibrated clock. Calibrate with an accurate spectrum analyzer .
    #Actually I am not sure where the error comes from, The PLLs on ZCU111 board or those on DAC tiles.

    SEQUENCER_CLK = CAL_DDS_CLK/2 #This is the clock for sequencer. This clock is hardwired on the FPGA to be DDS_CLK/2
    SAMPLE_CLK = CAL_DDS_CLK*16 #This is the clock for the DACs. Again, hardwired to be DDS_CLK*16
    #Actually in hardware it goes the other way, The DDS clock is derived from sample clock by /16

    #seq = [[0,100*10**6,2*10**6,1*10**9],[2*10**6,500*10**6,2*10**9,20*10**6],[1*10**9,20*10**6,10*10**6,10*10**6]]
    #seq = [[0, 1e8, 2e6, 500e6],[2e6, 1e9, 10e6, 3e9], [10e6, 3e9, 20e6, 1e8]]
    # seq = [[0, 1e9, 5e6, 3e9],[5e6, 3e9, 10e6, 1e9]] #high freq
    #seq = [[0, 300e6, 5e6, 2.5e9],[5e6, 2.5e9, 10e6, 300e6]] #low freq
    #seq = [[0, 1253.6e6, 5e6, 1553.6e6],[5e6, 953.6e6, 10e6, 1253.6e6]]
    seq = [[0, 10, 2e6, 80],[2e6,80, 4e6, 100],[4e6, 100, 6e6, 10]]
    convertedseq = ConvertSeqtoCountsandFTWs(seq)
    print(seq)
    triggers = [1,1,1]
    phase_resets = [0,0,0]

    rf.configureTriggerManager(config=0b0111111111)
    # rf.setOutputMode(channel=0,mode=2)
    #rf.setNyquistZone(channel = 0, zone = 2)
    for i, chan in enumerate(active_channels):
        #seq = seqs[i]
        #convertedseq = ConvertSeqtoCountsandFTWs(seq)
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



    
