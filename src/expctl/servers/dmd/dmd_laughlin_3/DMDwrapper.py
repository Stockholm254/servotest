#!/usr/bin/python2.7
# -*- coding: utf8 -*-
"""
    This file is part of DLPLC Interface.

    DLPLC Interface is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    DLPLC Interface is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with DLPLC Interface.  If not, see <http://www.gnu.org/licenses/>.
"""

from .dlplc_tcp import *
import argparse
import sys

def connect():
    """Connect to a dlplc or exit"""
    dlplc = LightCrafterTCP()
    if not dlplc.connect():
        print("Unable to connect to device.")
        sys.exit(1)
    return dlplc

def get_version():
    dlplc = connect()
    v = dlplc.cmd_version_string(0x00)
    print("DM365 SW Revision: %s"%v.data)
    v = dlplc.cmd_version_string(0x10)
    print("FPGA Firmware Revision: %s"%v.data)
    v = dlplc.cmd_version_string(0x20)
    print("MSP430 SW Revision: %s"%v.data)
    dlplc.close()
    return 0

def display_bitmap(filename,color):
    dlplc = connect()
    v = dlplc.cmd_current_display_mode(0x00)
    dlplc.cmd(Packet.PT_H_WRITE, 0x02, 0x01, "%c%c%c"%(60,1,color)) #60 hz, 1 bit color, monochrome
    print("Current display mode: %s"%":".join(c.encode('hex') for c in v.data))

    with open(filename, mode="rb") as f:
        data = f.read()
    #print ":".join(c.encode('hex') for c in data)
    print("Loading image...")
    response = dlplc.cmd_static_image(data)
    print("    Done.")

    try:
        response.raise_if_error()
    except:
        print("Error:")
        response.show()
        return 1

    dlplc.close()
    return 0

def display_data(data):
    dlplc = connect()
    v = dlplc.cmd_current_display_mode(0x00)
    color=1
    dlplc.cmd(Packet.PT_H_WRITE, 0x02, 0x01, "%c%c%c"%(60,1,color)) #60 hz, 1 bit color, monochrome
    print("Current display mode: %s"%":".join(c.encode('hex') for c in v.data))

    print("Loading image...")
    response = dlplc.cmd_static_image(data.decode('latin-1'))
    print("    Done.")

    try:
        response.raise_if_error()
    except:
        print("Error:")
        response.show()
        return 1

    dlplc.close()
    return 0

def main(argv):
    get_version()
    for jcolor in range(4,0,-1):#range(1,5):
        ret= display_bitmap('outfile2.bmp',jcolor) #        ret= display_bitmap('patterns/number01.bmp',jcolor)
    return ret

if __name__ == "__main__":
    ret = main(sys.argv)
    sys.exit(ret)
