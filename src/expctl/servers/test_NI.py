#!/usr/bin/python
import sys
import math
import time
import numpy as np
from .ServerClass import Server, logger
from ..utilities.util import formatTimeUnits
import ctypes
from .util.NI_server import *

uInt8   = ctypes.c_ubyte
int16   = ctypes.c_short
uInt16  = ctypes.c_ushort
int32   = ctypes.c_long
uInt32  = ctypes.c_ulong
uInt64  = ctypes.c_ulonglong
float64 = ctypes.c_double
task_handle_type = uInt32

localMHz = 1e6
# seq_duration = float(seq.TIME_STOP) # microseconds
timeout = 10.0 # (seconds)
sample_rate = 10.0  # number of samples per microsecond (clock speed in MHz)
# samps_per_channel = int(math.ceil(sample_rate * seq_duration) + 1) # MHz * us (+1 for steady_state_value)
# buffer_size = samps_per_channel # number of samples
channel_num = 32

localMHz=1e6
autostart=1

seq_duration = float(100.) # microseconds
timeout = 10.0 # (seconds)
sample_rate = 10.0  # number of samples per microsecond (clock speed in MHz)
samps_per_channel = int(math.ceil(sample_rate*seq_duration)+1) # MHz * us (+1 for steady_state_value)
buffer_size = samps_per_channel # number of samples
params = NIParameters(autostart, timeout, buffer_size, sample_rate*localMHz, samps_per_channel, b'PCI6537/line0:31', b'OnboardClock')
device = NIDevice(params)

#invert logical values because of line driver
NI_OFF = 1
NI_ON = 0

allStartTimes = [] # will contain tuples (startTime, chanid, value)
final_state = 0 # should probably be 2^32-1

#seq_data = ParseData(seq, samps_per_channel)
seq_data = numpy.zeros((samps_per_channel,), dtype=uInt32)

# Send sequence data to the device
task_handle = device.CreateTask(0) # Create task
device.CreateDOChan(task_handle, b"all_channels") # Create all channels
device.ConfigureTiming(task_handle, params)
# device.ExportSampleClockSignal(task_handle, line="PFI4")
device.ExportStartTrigger(task_handle, line=b"PFI4") # Trigger output for other devices
device.ExternalSampleClock(task_handle, b"RTSI7", 10e6) # Define external clock frequency
device.DigitalWriteU32(task_handle, params, seq_data) # Upload sequence data
#print("  Starting task ID "+str(server.task_id)+" (task_handle: "+str(task_handle.value)+")...")
device.StartTask(task_handle) # Start the experiment
device.WaitUntilTaskDoneOrBreak(task_handle)
device.cleanupTask(task_handle)
print("  Finished task.")