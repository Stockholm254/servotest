import serial
import time
import numpy as np

def set_attenuation(attenuation, device):
    device.write(int(2*attenuation).to_bytes(1, 'little'))
    return device.read(1)

arduino = serial.Serial(port='COM3', baudrate=19200, timeout=0.5)

while True:
    for atten in np.arange(0, 31.5, 0.5):
        time.sleep(1)
        print(set_attenuation(atten, arduino))
