import mmap
import struct
import os
#import time
import sys
import numpy as np
from pathlib import Path
from time import time, sleep
from pynq import Overlay

# New counter with two status bits and soft reset

class RpCounter:

    def __init__(self, bitfile="", fclk_Hz=125e6, nbins=1000, ncycles=1250, dac_scale=100):
        self.bitfile = bitfile

        if self.bitfile.exists():
            #os.system("cat {} > /dev/xdevcfg".format(self.bitfile))
            print(str(self.bitfile))
            overlay = Overlay(str(self.bitfile))
        else:
            print("Couldn't load bitfile, exiting...")
            sys.exit()

        self.fclk_Hz = fclk_Hz

        #ADDRESSES IN THE MEMORY MAPPED ADDRESS SPACE
        self.RP_BRAM = 0x40000000 # import adresses manually from Vivado
        self.RP_CFG = 0x43C10000
        self.RP_STS = 0x43C20000
        self.RP_BRAM_B = 0x80000000 # adress of the second block ram for channel B, is on different AXI Master interface
        self.RP_FPGARAMSIZE = self.RP_STS - self.RP_BRAM + 0xFFFF

        fd = os.open('/dev/mem', os.O_RDWR)
        self.m = mmap.mmap(fileno=fd, length=self.RP_FPGARAMSIZE, offset=self.RP_BRAM)

        self._nbins = nbins
        self._ncycles = ncycles
        self._dac_scale = dac_scale

        # call the setters to write hardware
        self.nbins = nbins
        self.ncycles = ncycles
        self.dac_scale = dac_scale

        #dbg
        self._last_done = -1

        self._set_nreset(1) # set the soft reset high to enable counter
    @property
    def nbins(self):
        return self._nbins

    @nbins.setter
    def nbins(self, value):
        self._nbins = int(value)
        val = struct.pack('<HH', self._ncycles, self._nbins)
        aa = self.RP_CFG - self.RP_BRAM
        self.m[aa:aa+4] = val

    @property
    def ncycles(self):
        return self._ncycles

    @ncycles.setter
    def ncycles(self, value):
        self._ncycles = int(value)
        val = struct.pack('<HH', self._ncycles, self._nbins)
        aa = self.RP_CFG - self.RP_BRAM
        self.m[aa:aa+4] = val

    @property
    def dac_scale(self):
        return self._dac_scale

    @dac_scale.setter
    def dac_scale(self, value):
        self._dac_scale = int(value)
        aa = self.RP_CFG - self.RP_BRAM
        #self.m[aa+4:aa+8] = struct.pack('<HH', self._dac_scale, self._dac_scale)
        self.m[aa+4:aa+6] = struct.pack('<H', self._dac_scale)

    def GetStatus(self):
        bb = self.RP_STS - self.RP_BRAM
        read = self.m[bb:(bb+4*3)]
        done, clk = struct.unpack('<IQ',read)
        # if done != self._last_done:
        #     print("done: {}".format(done))
        #     self._last_done = done
        return done, clk

    def _WaitForSts(self, sts, msg):
        while True:
            done, clk = self.GetStatus()
            if done==sts:
                print(done, msg)
                break
        return clk

    def _WaitForStsTimeout(self, sts, msg, timeout=1.0):
        t0 = time()
        while True:
            done, clk = self.GetStatus()
            t = time() - t0
            if t>timeout:
                raise TimeoutError
                break
            if done==sts:
                print(done, msg)
                break
        return clk

    def _set_nreset(self, bit):
        aa = self.RP_CFG - self.RP_BRAM
        val = struct.pack('<H', bit)
        #print("reset: ", val)
        self.m[aa+6:aa+8] = val


    def WaitForTrigger(self):
        # wait for the done signal to go low
        return self._WaitForSts(sts=2, msg='FPGA triggered')

    def WaitForEnd(self):
        # wait for the done signal to go high again
        return self._WaitForSts(sts=3, msg='FPGA done')

    def WaitForBoth(self):
        # wait for the done signal to go low and high again
        #self.WaitForTrigger() we are now only waiting for the done flag to go high (and the triggered flag being high)
        return self.WaitForEnd()

    def GetCounts(self):
        # read both counter channels
        data_a = np.frombuffer(self.m[0:(self.nbins*2)], dtype=np.dtype(np.uint16))
        self._set_nreset(0) #toggle reset after readout
        self._set_nreset(1)
        return data_a

if __name__ == "__main__":
    DIR_BITFILE = Path(__file__).parent
    bitfile_path = DIR_BITFILE/"counter_reset_single.bit"
    print("Using bitfile {}".format(bitfile_path))

    counter = RpCounter(bitfile=bitfile_path, fclk_Hz=125e6, nbins=1000, ncycles=1250, dac_scale=100)
    print(counter.nbins, counter.ncycles, counter.dac_scale)
    while True:
        #print(counter.WaitForBoth())
        #counter._WaitForSts(sts=2, msg='FPGA triggered')
        counter._WaitForSts(sts=3, msg='FPGA done')
        print(counter.GetStatus())
        data = counter.GetCounts()
        print(counter.GetStatus())
        print(len(data), data[0].shape, np.unique(data[0]), np.unique(data[1]))
        

    # counter.nbins=10000
    # print(counter.nbins, counter.ncycles, counter.dac_scale)
    # print(counter.WaitForBoth())
    # data = counter.GetCounts()
    # print(len(data), data[0].shape, np.unique(data[0]), np.unique(data[1]))

    # counter.nbins=1000
    # counter.ncycles=12500
    # print(counter.nbins, counter.ncycles, counter.dac_scale)
    # print(counter.WaitForBoth())
    # data = counter.GetCounts()
    # print(len(data), data[0].shape, np.unique(data[0]), np.unique(data[1]))

    print("done")