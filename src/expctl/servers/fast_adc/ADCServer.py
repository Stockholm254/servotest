from math import ceil, floor
import os, sys, time
import numpy as np
from pathlib import Path
from ..ServerClass import Server, logger
from ...utilities.util import formatTimeUnits
import datetime
import expdatabase.conf as conf
from expdatabase.db import insertADC
from expdatabase.types import ShotADC
from pymongo import MongoClient
from bson import ObjectId
from .adc_gds2k import ADCdso

def SaveDataDB(client, run_id, counter, data, meta, save):
    if client is not None:
        j = int(counter)
        run_id_bson = ObjectId(run_id)
        run_time = datetime.datetime.now()
        shot = ShotADC(date=run_time, j=j, data=data, meta=meta)
        insertADC(client=client, run_id=run_id_bson, shot=shot, save=save)
        logger.debug("Saved shot to DB")

class ADCServer(Server):

    def __init__(self, name, port, message, client, address):
        super().__init__(name, port, message)
        self.client = client
        self.dso = ADCdso(address=address)

    def cmd_queue(self):
        if self.seq is None:
            logger.error('QUEUE failed. Sequence has not been imported!')
        else:
            try:
                save_data, [acqCh1, acqCh2] = self._RunServer()
                logger.debug('Sequence has been queued... Trigger it whenever!')
                self.send_msg(self.ReplyHeader() + 'Sequence has been queued... Trigger it whenever!')
                logger.debug(f'[Acquire_Ch1, Acquire_Ch2]: [{acqCh1}, {acqCh2}], Save: {save_data}')
                # Get the save switch from the sequence
                logger.info(f"Saving according to save_switch: {save_data}")
                # Get the save switch from the sequence
                save_switch = self.seq.saveswitch
                if acqCh1 or acqCh2:
                    data, meta = self._acquire(acqCh1, acqCh2)
                    if save_data > 0:
                        save = True if save_switch==2 else False
                        SaveDataDB(client=self.client, run_id=self.seq.run_id, counter=self.seq.counter, data=data, meta=meta, save=save)
            except:
                logger.exception("Failed to acquire data from ADC.")

    def run(self):
        return 0.0

    def plotdata(self):
        return 1

    def _RunServer(self):
        TIME_START = time.time()
        seq = self.seq

        chan = seq.getChannelByName("fast ADC")
        save_switch_chan = seq.getChannelByName("ADC Save")
        chMode_chan = seq.getChannelByName("ADC Channel")




        # Get sample number and save switch
        save_switch_values = save_switch_chan.GetHardwareValues()
        chMode_values = chMode_chan.GetHardwareValues()
        save_switch = save_switch_values[0][1]
        chMode = save_switch_values[0][1]


        [acqCh1, acqCh2] = [False, False]
        if chMode == 1:
            acqCh1 = True
        if chMode == 2:
            acqCh2 = True
        if chMode == 3:
            acqCh1 = True
            acqCh2 = True

        return save_switch,  [acqCh1, acqCh2]

      
    def _acquire(self, acqCh1, acqCh2):
        try:
            data, meta = self.dso.get_data(getCH1=acqCh1, getCH2=acqCh2)
            logger.info("Total counts: {}".format(meta['num']))
        except:
            data, meta = np.array([]), {}
        return data, meta

if __name__ == '__main__':
	
    message = """
	===============================================
	==   fast ADC server using GW Instek scope   ==
	==                  GDS-2072E                ==
	===============================================
	"""
    
    #Initialize experiment database connection
    try:
        client = MongoClient(host=conf.DB_HOST, port=conf.DB_PORT, username=conf.USER_RAW_WRITER , password=conf.PASSWORD_RAW_WRITER, authSource=conf.DB_AUTH)
    except:
        logger.exception("Database connection could not be established!")
        client = None
    else:
        logger.info("Database connected.")

    server = ADCServer("GDS-2072E_1", 60622, message=message, client=client, address='192.168.1.99:3000')
    server.main_loop()