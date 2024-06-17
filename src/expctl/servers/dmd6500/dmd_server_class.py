import sys
import math
import time
import numpy as np
from ..ServerClass import Server, logger
from pathlib import Path
from ..util.SequenceProcessor import *
# from PIL import Image
import io
import os
from dataclasses import dataclass
from typing import Tuple, List, Union


@dataclass(frozen=True, eq=True)
class DMDsettings:
    waist: Tuple[float]
    p: int
    l: int
    rotation: int
    center: Tuple[float]
    defocus: float
    tilt: Tuple[float]

class DMDServer(Server):
    

    def __init__(self, name, port, message):
        super().__init__(name, port, message)
        #self.holomaker = initHolomaker(waveperiod=4, verbose=True)
        self.settings = None

    def update(self, settings):
        # the last DMD setting is cached in self.settings to not repeatedly set the same settings
        if settings != self.settings:
            logger.info(f"Detected new set of parameters {settings}, making new hologram")
            # save new settings
            self.settings = settings
            s = settings
            self.holomaker.resetTargetFunction()
            #holomaker.addNPC((0.6, 0.55), 0, 0, 75, center=(60,45), defocus=-0.45, tilt=(-0.05,0.35))
            self.holomaker.addNPC((s.waist[0], s.waist[1]), s.p, s.l, s.rotation, center=(s.center[0], s.center[1]), defocus=s.defocus, tilt=(s.tilt[0], s.tilt[1]))
            hologram = self.holomaker.makeHologram()
            # save the image as a BMP to a BytesIO ("ramdisk") instead of to disk
            #im = Image.fromarray(hologram.astype(np.uint8))
            buf = io.BytesIO()
            #im.save(buf, format='BMP')
            byte_im = buf.getvalue()
            logger.debug("Generated Hologram")
            # Display on DMD
            #DMDwrapper.display_data(byte_im)
            logger.debug("Sending Hologram to DMD done!")


    def parse(self):
        for chan in self.seq.allChannels:
            print(chan._TransValues)

            val = chan._TransValues[0][1] # find the first value
            set = chan._TransValues[0]
            if set[1] != val or set[3] != val: # Check for non-identical values
                print('WARNING: DMD given multiple settings in same sequence, but only takes the first!!')

            if chan.chanid == 0: # waist x
                waist_x = float(val)
            elif chan.chanid == 1: # waist y
                waist_y = float(val)
            elif chan.chanid == 2: # p
                p = int(val)
            elif chan.chanid == 3: # l
                l = int(val)
            elif chan.chanid == 4: # rotation
                rotation = int(val)
            elif chan.chanid == 5: # center x
                center_x = int(val)
            elif chan.chanid == 6: # center y
                center_y = int(val)
            elif chan.chanid == 7: # defocus
                defocus = float(val)
            elif chan.chanid == 8: # tilt x
                tilt_x = float(val)
            elif chan.chanid == 9: # tilt y
                tilt_y = float(val)
            else: # wtf?
                logger.warning('WARNING: Sequence specified for unsupported channel...')
        try:
            settings = DMDsettings(waist=(waist_x, waist_y), p=p, l=l, rotation=rotation, center=(center_x, center_y), defocus=defocus, tilt=(tilt_x, tilt_y))
        except NameError:
            logger.exception("Not all args for DMDsettings specified!")
        else:
            self.update(settings)
            

    def cmd_seq(self, data):
        self.seq = data # unpack the sequence
        numChannels = 0
        for chan in self.seq.allChannels:
            if chan != None: numChannels += 1
        logger.debug("Received sequence ({} channels): {}".format(numChannels, self.seq.name))
        #updateSettings(self.api, self.DEVID, self.seq)
        reply = "Received sequence ({} channels): {}".format(numChannels, self.seq.name)
        self.send_msg(self.ReplyHeader() + reply)

    def queue(self):
        self.parse()
        return 1

    def run(self):
        return 1

    def plotdata(self):
        return [0,], [0,]


if __name__ == '__main__':

    message = """
    ===========================================
    ==              DMD Server 1             ==
    ==        TI DLP Lightcrafter 3000       ==
    ===========================================
    """
    server = DMDServer("LB1", 60651, message=message)
    server.main_loop()
