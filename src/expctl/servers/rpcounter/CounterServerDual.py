from math import ceil, floor
import sys
import os
import math
import time
import numpy as np
from ..ServerClass import Server, logger
from ...utilities.util import formatTimeUnits
import datetime
from pathlib import Path
import expdatabase.conf as conf
from expdatabase.db import insertCounter
from expdatabase.types import ShotCounter
from pymongo import MongoClient
from bson import ObjectId
from .rpcounter_dual import RpCounterDual

DIR_BITFILE = Path(__file__).parent

def SaveDataDB(client, run_id, counter, DataCLK, save):
    if client is not None:
        data, clk = DataCLK
        clk = int(clk)
        j = int(counter)
        run_id_bson = ObjectId(run_id)
        run_time = datetime.datetime.now()
        shot = ShotCounter(run_time, j, clk, data)
        insertCounter(client=client, run_id=run_id_bson, shot=shot, save=save)
        logger.info("Saved shot to DB")

class CounterServer(Server):

    def __init__(self, name, port, message, client):
        super().__init__(name, port, message)
        self.client = client
        bitfile_path = DIR_BITFILE/"dual_counter_3.bit"
        logger.info("Using bitfile {}".format(bitfile_path))
        self.fclk_Hz = 125e6
        self.counter = RpCounterDual(bitfile=bitfile_path, fclk_Hz=self.fclk_Hz)

    def cmd_queue(self):
        if self.seq is None:
            logger.error('QUEUE failed. Sequence has not been imported!')
        else:
            try:
                acquire_data, save_data = self._RunServer()
                logger.debug('Sequence has been queued... Trigger it whenever!')
                self.send_msg(self.ReplyHeader() + 'Sequence has been queued... Trigger it whenever!')
                logger.debug(f'Acquire: {acquire_data}, Save: {save_data}')
                # Get the save switch from the sequence
                save_switch = self.seq.saveswitch
                logger.info(f"Saving according to save_switch {save_switch}")
                if acquire_data == 1:
                    data = self._acquire()
                    if data == -1:
                        logger.error("FPGA returned nothing")
                    else:
                        if save_switch > 0:
                            #SaveDataWithCLK(self.seq.foldername, self.seq.runname, data)
                            save = True if save_switch==2 else False
                            SaveDataDB(client=self.client, run_id=self.seq.run_id, counter=self.seq.counter, DataCLK=data, save=save)
            except:
                logger.exception("Failed to acquire data from FPGA.")

    def run(self):
        return 0.0

    def plotdata(self):
        return 1

    def _RunServer(self):
        TIME_START = time.time()
        seq = self.seq

        chan = seq.getChannelByName("Photon Counter")
        sample_num_chan = seq.getChannelByName("Counter Bin Num")
        save_switch_chan = seq.getChannelByName("Counter Save")
        max_rate = seq.getChannelByName("Counter Max Rate")
        channels = seq.getChannelByName("Counter N Channels")
        # Get sample number and save switch
        sample_num_values = sample_num_chan.GetHardwareValues()
        save_switch_values = save_switch_chan.GetHardwareValues()
        max_rate_values = max_rate.GetHardwareValues()
        sample_num = sample_num_values[0][1]
        save_switch = save_switch_values[0][1]
        max_count_rate = max_rate_values[0][1]
        self.n_channels = int(channels.GetHardwareValues()[0][1])
        # Get trigger channel
        thehardwarevalues = chan.GetHardwareValues()
        run_name = seq.runname
        
        newval = 0
        oldval = 0
        NumOfTrace = 0
        TraceStart = 0
        TraceEnd = 0
        TraceLength = []
        
        BinSize = 0
        MaxTraceLength = 0
        
        # Load sequence data and calculate bin size
        for interval in thehardwarevalues:
            if interval[1] == 0 and interval[3] == 0:
                newval = 0
                if newval != oldval:
                    TraceEnd = interval[0]
                    TraceLength.append((TraceEnd-TraceStart))
                    NumOfTrace += 1
            else:
                newval = 1
                if newval != oldval:
                    TraceStart = interval[0]
            oldval = newval
                
        if NumOfTrace > 0:
            MaxTraceLength = max(TraceLength)
            MaxTraceLength = round(MaxTraceLength, 4)
            BinSize = MaxTraceLength / sample_num #the sequence code works in us!!
            # Do the actual timing calculation here
            # Make sure bin size is not too small!
            BinCycles = max(int(self.fclk_Hz*1e-6*BinSize),10)
            logger.debug("MaxTraceLength: {}, Bin size: {} us, Bin cycles: {} ".format(MaxTraceLength, BinSize, BinCycles))
            # maximum value of DAC reached at 2^16, so scale according to max_count_rate (in MHz)
            MaxCounts = max_count_rate*BinSize # expected number of counts in one bin
            DacScale = min(int(floor(2**13/MaxCounts)),2**16-1)
            logger.debug("DAC scale factor: {:d}".format(DacScale))
            self.counter.nbins = int(sample_num)
            self.counter.ncycles = BinCycles
            self.counter.dac_scale = DacScale

            if save_switch == 1:
                return 1, 1 # First argument is acquring switch, and the second one is saving switch
            else:
                return 1, 0
        else:
            return 0, 0
    def _acquire(self):
        # Wait for FPGA to be triggered and done!
        clockcount = self.counter.WaitForBoth()
        data = self.counter.GetCounts()
        # print(data.shape, np.unique(data))
        if self.n_channels==2:
            data = list(data)
            logger.info("Total counts: {} {}".format(np.sum(data[0]), np.sum(data[1])))
        elif self.n_channels==1:
            data = data[0]
            logger.info("Total counts: {}".format(np.sum(data)))
        else:
            logger.error("Only one or two channels allowed for this counter!")
        
        
        if len(data) == 0:
            return -1
    
        return data, clockcount

if __name__ == '__main__':
    message = """===========================================
    ==       Photon Counter Server 1         ==
    ===========================================
    Maximum Number of Data Points: 32768
    """
    #Initialize experiment database connection
    try:
        client = MongoClient(host=conf.DB_HOST, port=conf.DB_PORT, username=conf.USER_RAW_WRITER , password=conf.PASSWORD_RAW_WRITER, authSource=conf.DB_AUTH)
    except:
        logger.exception("Database connection could not be established!")
        client = None
    else:
        logger.info("Database connected.")

    server = CounterServer("SOut1", 60621, message=message, client=client)
    server.main_loop()