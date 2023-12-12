import sys
import math
import time
import numpy as np
from ..ServerClass import Server, logger
from pathlib import Path
from ..util.SequenceProcessor import *
from .rfsoc import *

DIR_BITFILE = Path(__file__).parent

class RFSocServer(Server):

    def __init__(self, name, port, message, bitfile_path):
        super().__init__(name, port, message)
        logger.info("Using bitfile {}".format(bitfile_path))
        self.rf = RFSoc2x2(bitfile=bitfile_path)

    def cmd_seq(self, data):
        self.seq = data # unpack the sequence
        numChannels = 0
        for chan in self.seq.allChannels:
            if chan != None: numChannels += 1
        logger.debug("Received sequence ({} channels): {}".format(numChannels, self.seq.name))
        reply = "Received sequence ({} channels): {}".format(numChannels, self.seq.name)
        self.send_msg(self.ReplyHeader() + reply)

    def queue(self):
        for chan in self.seq.allChannels:
            val = chan._TransValues[0][1] # find the first value
            tup = chan._TransValues[0]
            print(chan.chanid, tup)
            if tup[1] != val or tup[3] != val: # Check for non-identical values
                logger.warning('WARNING: RFsoc given multiple settings in same sequence, but only takes the first!!')

            if chan.chanid == 0: # Frequency
                self.rf.set_frequency(0, val)
                logger.debug('setting channel {} to {} MHz'.format(0, val))
            elif chan.chanid == 1: # Frequency
                self.rf.set_frequency(1, val)
                logger.debug('setting channel {} to {} MHz'.format(1, val))

            elif chan.chanid == 2: # Amplitude
                self.rf.set_amplitude(0, val)
                logger.debug('setting channel {} amplitude to {}'.format(0, val))
            elif chan.chanid == 3: # Amplitude
                self.rf.set_amplitude(1, val)
                logger.debug('setting channel {} amplitude to {}'.format(1, val))
            elif chan.chanid == 4: # waveform
                self.rf.set_waveform(0, val)
                logger.debug('setting channel {} waveform to {}'.format(0, val))
            elif chan.chanid == 5: # waveform
                self.rf.set_waveform(1, val)
                logger.debug('setting channel {} waveform to {}'.format(1, val))
            else: # wtf?
                logger.warning('WARNING: Sequence specified for unsupported channel...')

        return 1

    def run(self):
        return 1

    def plotdata(self):
        return [0,], [0,]


if __name__ == '__main__':

    message = """
    ===============================================
    ==      DDS Profile Frequency Out Server     ==
    ==                 for RFSOC                 ==
    ===============================================
    """
    bitfile_path = DIR_BITFILE/"dds_dbg_twosigns.bit"
    server = RFSocServer("RFSoc1", 60617, message=message, bitfile_path=bitfile_path)
    server.main_loop()