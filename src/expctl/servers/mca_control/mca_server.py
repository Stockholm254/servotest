import numpy as np
from ..ServerClass import Server, logger
from pathlib import Path
import serial
import time

def set_attenuation(attenuation, device):
    device.write((2*attenuation).to_bytes(1, 'little'))
    return device.read(1)

class MCAServer(Server):

    def __init__(self, name, port, message, comport):
        super().__init__(name, port, message)
        self.comport = comport
        self.arduino = serial.Serial(port=comport, baudrate=19200, timeout=0.5)

    def queue(self):
        atten = self.seq.allChannels[0].GetHardwareSSV()
        return set_attenuation(atten, self.arduino)

    def run(self):
        atten = self.seq.allChannels[0].GetHardwareSSV()
        return set_attenuation(atten, self.arduino)

    def plotdata(self):
        atten = self.seq.allChannels[0].GetHardwareSSV()
        return [0,], [atten,]


if __name__=="__main__":
    message = """
    ===============================================
    ==      Mini-Circuits ZX76 Server            ==
    ===============================================
    """
    server = MCAServer("MCA ZX76", 60631, message, "COM3")
    server.main_loop()