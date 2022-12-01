import mmap
import struct
import os
#import time
import sys
import numpy as np
from pathlib import Path
from time import time, sleep
from pynq import Overlay
import xrfclk
from pynq import Xlnk
import xrfdc

# Driver for the RFSoc 2x2, for now static frequencies only
DIR_BITFILE = Path(__file__).parent

class RFSoc2x2:

    def __init__(self, bitfile="", fclk_Hz=125e6, nbins=1000, ncycles=1250, dac_scale=100):
        self.bitfile = bitfile

        if self.bitfile.exists():
            print(str(self.bitfile))
            self.ol = Overlay(str(self.bitfile), ignore_version=True)
        else:
            print("Couldn't load bitfile, exiting...")
            sys.exit()

        self.DDS_CLK = 409.6
        self.SAMPLE_CLK = self.DDS_CLK*16
        print("Starting RFSOC clocks...\n")
        xrfclk.set_ref_clks()
        print("Clocks Started\n")

        self.chan_map = {0: self.ol.DDS_0, 1: self.ol.DDS_1}
        self.set_amplitude(0, 0.999)
        self.set_amplitude(1, 0.999)
        self.set_waveform(0, 0)
        self.set_waveform(1, 0)

    def set_amplitude(self, chan, amp):
        amp = max(0, min(0.999, amp))
        self.chan_map[chan].write(0x10, np.uint32(amp*2**14).tobytes()) #amplitude

    def set_waveform(self, chan, waveform):
        self.chan_map[chan].write(0x2c, np.uint32(waveform).tobytes()) # 0 for sin, 1 for cos, 2 serrodyne, 3 serrodyne neg sign

    def set_frequency(self, chan, f_MHz):
        f_int = np.uint64((f_MHz)/(self.SAMPLE_CLK)*2**49)
        f_low = np.uint32(f_int)
        f_high = np.right_shift(f_int, np.uint(32), casting='unsafe').astype(np.uint32)
        reg = self.chan_map[chan]
        reg.write(0x20, f_low.tobytes())
        reg.write(0x24, f_high.tobytes())
        reg.write(0x2c, np.uint32(0).tobytes())
    

if __name__ == '__main__':
    bitfile_path = DIR_BITFILE/"dds_dbg_twosigns.bit"
    rf = RFSoc2x2(bitfile=bitfile_path)
    rf.set_frequency(0, 200.0)
    rf.set_frequency(1, 200.0)