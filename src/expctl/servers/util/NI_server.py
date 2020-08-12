#!/usr/bin/python

import numpy

from utilities.util import *
from servers.util.server import *


def LoadDLL() :    # load the DLL with linux or windows specific invocations.
  message = ''
  if os.name == 'posix' :
      try:
          dll = ctypes.cdll.LoadLibrary("nicaiu.so")
      except :
          dll = 0
  elif os.name == 'nt' :
      # windll libraries call functions using the stdcall calling convention.
      try:
          dll = ctypes.windll.nicaiu
      except :
          dll = 0
  else :
      message = 'This operating system is not supported.'
      dll = 0
  if dll == 0 :
      message = 'The required dll nicaiu was not found.'
  return dll, message

    
#=======================================================#
#========= National Instruments Output Device ==========#
#=======================================================#
class NIDevice:
  def __init__(self, params) :
      dll, message = LoadDLL()
      if dll == 0 :
          print('Library not loadable.  ' + message)
          sys.exit()
      self.dll = dll
      # Define constants corresponding to values in  C:\Program Files\National Instruments\NI-DAQ\DAQmx ANSI C Dev\include\NIDAQmx.h
      # The following are control constants used by nidaqmx.
      self.Cfg_Default = numpy.int32(-1)
      self.Volts = 10348
      self.Rising = 10280
      self.FiniteSamps = 10178
      self.ContSamps = 10123
      self.CountUp = 10128
      self.CountDown = 10124
      self.ActiveHigh = 10095 
      self.Low = 10214
      self.SampleClock = 12487
      self.StartTrigger = 12491
      self.GroupByChannel = 0
      self.GroupByScanNumber = 1
      self.ChanPerLine = 0
      self.ChanForAllLines = 1
      self.RSE = 10083
      self.channel = params.channel # stores the channel string

      self.nWrittenSingle = ctypes.c_int32(0) # will store the number of bytes written
      print('Restart')
      
      
  ''' Utility Functions '''
  def _check(self, err):
    if err < 0:
        buf_size = 1000
        buf = ctypes.create_string_buffer('\000' * buf_size)
        self.dll.DAQmxGetErrorString(err, ctypes.byref(buf), buf_size)
        raise RuntimeError('Call failed with error %d: %s'%(err, repr(buf.value)))
    return err
 
  ''' Task Configuration/Control '''
  def CreateTask(self, task_id):
    task_handle = task_handle_type(task_id)
    self._check(self.dll.DAQmxCreateTask("", ctypes.byref(task_handle)))
    return task_handle

  def StartTask(self, task_handle):
    self._check(self.dll.DAQmxStartTask(task_handle))
    return
    
  def cleanupTask(self, task):
    self._check(self.dll.DAQmxStopTask(task))
    self._check(self.dll.DAQmxClearTask(task))
    return
    
  ''' Channel Configuration/Creation '''
  def CreateAOVoltageChan(self, task, name=''):
    # int32 DAQmxCreateAOVoltageChan (TaskHandle th, const char physicalChannel[], const char nameToAssignToChannel[], float64 minVal, float64 maxVal, int32 units, const char customScaleName[]);
    self._check(self.dll.DAQmxCreateAOVoltageChan(task, self.channel, name, float64(-10.0), float64(10.0), self.Volts, None))
    return

  def CreateDOChan(self, task, name=''):
    # int32 DAQmxCreateDOChan (TaskHandle taskHandle, const char lines[], const char nameToAssignToLines[], int32 lineGrouping);
    self._check(self.dll.DAQmxCreateDOChan(task, self.channel, name, self.ChanForAllLines))
    return
  
  def CreateCounterChan(self, task, counterName, name):
      #int32 DAQmxCreateCICountEdgesChan (TaskHandle taskHandle, const char counter[], const char nameToAssignToChannel[], int32 edge, uInt32 initialCount, int32 countDirection);
      counterName = ctypes.create_string_buffer(counterName)
      name = ctypes.create_string_buffer(name) # ! same
      self._check(self.dll.DAQmxCreateCICountEdgesChan(task, counterName, name, int32(self.Rising),uInt32(0), int32(self.CountUp)))
  
  ''' Timing and Triggering '''
  def ConfigureTiming(self, task_handle, params):
    self.dll.DAQmxCfgSampClkTiming(task_handle, params.clock_source, params.sample_rate,
                                   self.Rising, self.FiniteSamps, params.buffer_size)    # ContSamps instead of FiniteSamps?
    return

  def ConnectTerminals(self, source, dest, invert=False):
    #signalModifiers = int32(self.dll.DAQmx_Val_InvertPolarity) if invert else int32(self.dll.DAQmx_Val_DoNotInvertPolarity)
    signalModifiers = int32(1) if invert else int32(0)
    source = ctypes.create_string_buffer(source)
    dest = ctypes.create_string_buffer(dest)
    self._check(self.dll.DAQmxConnectTerms(source, dest, signalModifiers))
  
  def ExternalSampleTimbase(self, task_handle, src, rate):
    #int32 DAQmxSetSampClkTimebaseSrc(TaskHandle taskHandle, const char *data);
    #int32 DAQmxSetSampClkTimebaseRate(TaskHandle taskHandle, float64 data);
    self._check(self.dll.DAQmxSetSampClkTimebaseSrc(task_handle, ctypes.create_string_buffer(src)))
    self._check(self.dll.DAQmxSetSampClkTimebaseRate(task_handle, float64(rate)))
  
  def ExternalSampleClock(self, task_handle, src, rate):
    #int32 DAQmxSetSampClkSrc(TaskHandle taskHandle, const char *data);
    #int32 DAQmxSetSampClkRate(TaskHandle taskHandle, float64 data);
    self._check(self.dll.DAQmxSetSampClkSrc(task_handle, ctypes.create_string_buffer(src)))
    self._check(self.dll.DAQmxSetSampClkRate(task_handle, float64(rate)))
    
  def CounterInput(self, task_handle, src, counterName="Ctr1"):
    #int32 DAQmxSetCICountEdgesTerm(TaskHandle taskHandle, const char channel[], const char *data);
    self._check(self.dll.DAQmxSetCICountEdgesTerm(task_handle,  ctypes.create_string_buffer(src),  ctypes.create_string_buffer(counterName)))
    
  def ConfigureTrigger(self, task_handle, params, trigger_src="PFI0", silent=0):
    # int32 DAQmxCfgDigEdgeStartTrig (TaskHandle task_handle, const char triggerSource[], int32 triggerEdge);
    if silent == 0:
      print("  Waiting for start trigger on " + str(trigger_src) + ". Press 'b' to break.")
    self.dll.DAQmxCfgDigEdgeStartTrig(task_handle, ctypes.create_string_buffer(trigger_src), self.Rising)
    return
    
  def ConfPauseTrig(self, task_handle, src= "PFI5"):
    #int32 DAQmxSetDigLvlPauseTrigSrc(TaskHandle taskHandle, const char *data);
    self._check(self.dll.DAQmxSetDigLvlPauseTrigSrc(task_handle, ctypes.create_string_buffer(src)))
    
  def WaitUntilTaskDone(self, task_handle):
    # int32 DAQmxWaitUntilTaskDone (TaskHandle taskHandle, float64 timeToWait);
    self.dll.DAQmxWaitUntilTaskDone(task_handle, float64(-1)) # wait indefinitely
    return

  def IsTaskDone(self, task_handle):
    # int32 DAQmxIsTaskDone (TaskHandle taskHandle, bool32 *isTaskDone);
    task_is_done = int32(0)
    self.dll.DAQmxIsTaskDone(task_handle, ctypes.byref(task_is_done)) # wait indefinitely
    return task_is_done

  def WaitUntilTaskDoneOrBreak(self, task_handle):
    while(msvcrt.kbhit()):
      msvcrt.getch()
    while (not self.IsTaskDone(task_handle)):
      key_pressed = msvcrt.kbhit()
      if key_pressed:
        key_val = msvcrt.getch()
        if key_val == 'B' or key_val == 'b':
          print("  Waiting for task has been cancelled.")
          break
        
  ''' Write Functions '''
  def AnalogWriteF64(self, task_handle, params, data):    
    # print what we are writing:
    # numpy.set_printoptions(threshold=uInt32); print data; numpy.set_printoptions(threshold=5);
    
    # int32 DAQmxWriteAnalogF64  (TaskHandle taskHandle, int32 numSampsPerChan, bool32 autoStart, float64 timeout, bool32 dataLayout, float64 writeArray[], int32 *sampsPerChanWritten, bool32 *reserved);
    self._check(self.dll.DAQmxWriteAnalogF64(
      task_handle,                          # TaskHandle taskHandle,
      params.samples,                       # int32 numSampsPerChan
      params.autostart,                     # bool32 autoStart
      params.timeout,                       # float64 timeout
      self.GroupByChannel,                  # bool32 dataLayout: GroupByChannel (0) or GroupByScanNumber (1)
      data.ctypes.data,                     # float64 writeArray[]
      ctypes.byref(self.nWrittenSingle),    # int32 *sampsPerChanWritten ........ may be NULL
      None))                                # reserved
    return self.nWrittenSingle
  
  def DigitalWriteU32(self, task_handle, params, data):    
    # print what we are writing:
    # numpy.set_printoptions(threshold=uInt32); print data; numpy.set_printoptions(threshold=5);
  
    # int32 DAQmxWriteDigitalU32 (TaskHandle taskHandle, int32 numSampsPerChan, bool32 autoStart, float64 timeout, bool32 dataLayout, uInt32 writeArray[], int32 *sampsPerChanWritten, bool32 *reserved);
    print(task_handle)
    print((params.samples))
    print((params.timeout))
    print((self.GroupByScanNumber))
    print((data.ctypes.data))
    print((ctypes.byref(self.nWrittenSingle)))
    self._check(
      self.dll.DAQmxWriteDigitalU32(
      task_handle,                          # TaskHandle taskHandle,
      params.samples,                       # int32 numSampsPerChan
      0,                                    # bool32 autoStart
      params.timeout,                       # float64 timeout
      self.GroupByScanNumber,               # bool32 dataLayout: GroupByChannel (0) or GroupByScanNumber (1)
      # self.dataSingle.ctypes.data,        # uInt32 writeArray[]
      data.ctypes.data,                     # uInt32 writeArray[]
      ctypes.byref(self.nWrittenSingle),    # int32 *sampsPerChanWritten ........ may be NULL
      None)
      )                                # reserved
    return self.nWrittenSingle
  
  ''' Signaling '''
  def ExportSampleClockSignal(self, task_handle, line="PFI4"):
    # int32 DAQmxExportSignal (TaskHandle taskHandle, int32 signalID, const char outputTerminal[]);
    self._check(self.dll.DAQmxExportSignal(task_handle, int32(self.SampleClock), ctypes.create_string_buffer(line)))
    return
    
  def ExportStartTrigger(self, task_handle, line="PFI4"):
    # int32 DAQmxExportSignal (TaskHandle taskHandle, int32 signalID, const char outputTerminal[]);
    self._check(self.dll.DAQmxExportSignal(task_handle, int32(self.StartTrigger), ctypes.create_string_buffer(line)))
    return

#=======================================================#
#======= National Instruments Device Parameters ========#
#=======================================================#
class NIParameters:
  def __init__(self, autostart, timeout, buffer_size, sample_rate, samples, channel, clock):
    self.autostart = autostart # 1 unless we have are using a trigger
    self.timeout = float64(timeout)          # seconds to wait to write all samples
    self.buffer_size = uInt64(buffer_size)   # this actually seems to be taken from 'samples'
    self.sample_rate = float64(sample_rate)  # samples per sec per channel
    self.samples = int32(samples)            # samples per channel to write
    self.channel = ctypes.create_string_buffer(channel)     # 'Dev1/port#', 'Dev1/port#/line#:#' etc...
    self.clock_source = ctypes.create_string_buffer(clock)  # Source of clock
    
