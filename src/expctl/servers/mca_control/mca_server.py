import numpy as np
from ..ServerClass import Server, logger
from pathlib import Path
import serial
import time

def set_attenuation(attenuation, device):
    word = int(2*attenuation).to_bytes(1, 'little')
    device.write(word)
    logger.info("Setting attenuation to {:.1f} dB, binary {:08b}".format(attenuation,int(word.hex(),16)))
    answer = device.read(1)
    logger.info("Got back {:08b}".format(int(answer.hex(),16)))
    return 

class MCAServer(Server):

    def __init__(self, name, port, message, comport):
        super().__init__(name, port, message)
        self.comport = comport
        self.arduino = serial.Serial(port=comport, baudrate=19200, timeout=0.5)

    def queue(self):
        #atten = self.seq.allChannels[0].GetHardwareSSV()
        chan = self.seq.getChannelByName("Attenuation")
        atten = chan.GetHardwareValues()[0][1]
        set_attenuation(atten, self.arduino)
        return 1

    def run(self):
        return 1

    def plotdata(self):
        atten = self.seq.allChannels[0].GetHardwareSSV()
        return [0,], [atten,]


if __name__=="__main__":
    message = """
    ===============================================
    ==      Mini-Circuits ZX76 Server            ==
    ===============================================
    """
    server = MCAServer("adu", 60651, message, "COM22")
    server.main_loop()