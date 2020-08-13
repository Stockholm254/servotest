import coloredlogs, logging
from ..servers.ServerClass import Server
from ..DeviceManager.DeviceManager import DeviceManager, Device
from ..sequencer.sequence import Sequence
import time
import coloredlogs, logging

# Create a logger object.
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')

if __name__ == '__main__':
    s1 = Sequence("Digital", "127.0.0.1", 50001)
    s2 = Sequence("Analog", "127.0.0.1", 50002)
    s3 = Sequence("DDS", "127.0.0.1", 50003)
    MasterSequence = s1

    dm = DeviceManager(all_seqs=[s1, s2, s3], act_seqs=[s1, s2, s3])


    dm.connect()
    tstart = time.time()

    tqueue, tprep = dm.SendAndQueueSequences(MasterSequence, timeout=100)
    dm.Run(MasterSequence)
    dm.WaitForAllToFinish(timeout=100)
    tend = time.time()

    print("RunExperiment took "+str(tend-tstart)+" seconds")
    print("Sending data to servers took "+str(1000.0*(tqueue))+" milliseconds")
    print("Checking that servers have parsed took "+str(1000.0*(tprep))+" milliseconds")