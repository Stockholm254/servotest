#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import time
import wx
import sys
from threading import *
import numpy as np
import math
from multiprocessing import Pool, Process ################################################################
import shutil
from pathlib import Path
import pdb
import traceback
import random

from ..utilities import jGlobals # Unit module
from ..sequencer.sequence import SetError # Sequence set error
from ..sequencer.intervaler import Intervaler # Interval object
from ..utilities.util import *
from ..utilities.Feedback import FBControlMV


from ..config.config import * # System configuration (log directory, etc)
from ..utilities.FilenameGenerator import * # Generate formated file name

from ..dat.all_channels import *
from ..dat import Electrodes as electrodes ###TODO: MOVE INTO MACHINE PARAMETER FILE IN DAT###
from ..dat import Rubidium as Rb ###TODO: MOVE INTO MACHINE PARAMETER FILE IN DAT###
from ..dat.SharedFunctions import * # Standard code for varies sequence actions

Unit = jGlobals.UnitsModule() # Units used in sequence file

##########################
### Worker Thread Mode ###
##########################
# Running mode
RUNMODE_SINGLE = 0 # Single run
RUNMODE_REPEAT = 1 # Repeated run
RUNMODE_IDLE   = 4 # Repeated run without saving the log
RUNMODE_PRE    = 2 # Pre-run before loop run
RUNMODE_LOOP   = 3 # Loop run
RUNMODE_DEBUG  = 5 # Sequence debug mode



# # # TEMPORARY SOLUTION
#DIR_DATA = Path("../../TestOutput/Data/") #"E:/Data/"


############################
###     Event Result     ###
############################
EVT_RESULT_ID = wx.NewId()
EVT_UPDATE_ID = wx.NewId()

# Magic code binds events so our worker thread will return data and invoke a function
def EVT_RESULT(win, func):
  win.Connect(-1, -1, EVT_RESULT_ID, func)

def EVT_UPDATE(win, func):
  win.Connect(-1, -1, EVT_UPDATE_ID, func)

class ResultEvent(wx.PyEvent):
  """Simple event to carry arbitrary result data back to GUI."""
  def __init__(self, data, loop=False):
      wx.PyEvent.__init__(self)
      self.SetEventType(EVT_RESULT_ID)
      self.data = data
      self.loop = loop

class UpdateEvent(wx.PyEvent):
  """Simple event to carry arbitrary result data back to GUI."""
  def __init__(self, data, abort=False):
      wx.PyEvent.__init__(self)
      self.SetEventType(EVT_UPDATE_ID)
      self.data  = data
      self.abort = abort

######################################################
###    Thread class that executes repeated runs    ###
######################################################
class WorkerThread(Thread):
  def __init__(
               self, notify_window, loop=0, delay=5.0, 
               prerun=0, startval=0, stopval=10, random=0, 
               runflag=0
               ):
      
      Thread.__init__(self)

      # Run parms
      self._notify_window = notify_window     # The front panel
      self._dm            = notify_window.dm  # Device manager
      self._want_abort    = 0                 # Abort indicator
      self._need_update   = 0                 # MV update indicator
      self.delay          = delay             # Time between each run in ms
      self.loop           = loop              # Run mode indicator
      self.prerun         = prerun            # Number of pre-runs in loop run mode
      self.startval       = startval          # Start value of loop run counter
      self.finalval       = stopval           # Stop value of loop run counter
      self.random         = random            # Randomize loop run order

      self.time_now = datetime.datetime.now() # Run time
      
      self.start() # This starts the thread running on creation

  # get current run time
  def __GetRunTime__(self):
    self.time_now = datetime.datetime.now()
    return 1

  # save mv used in the run to a log file
  def __SaveLog__(self, counter):
    log_dir = GenDTDir(DIR_LOG, dt=self.time_now)
    if not os.path.exists(log_dir):
      os.makedirs(log_dir)

    log_fname = log_dir/GenFname(header='LOGFP', dt=self.time_now, post=str(counter))
    
    # write log file
    MV_code = self._notify_window.GenerateMVCode(date_time=self.time_now) # Generate log text
    f = open(log_fname, 'w')
    f.write(MV_code)
    f.close()

    return 1

  def __UpdateRunName__(self, counter, FB=False):
    for seq in all_sequences:
        seq.foldername = self._notify_window.dir_data # Data folder
        if FB:
          seq.foldername+="/FB"
        seq.runname = GenFname(header='', dt=self.time_now, post=str(counter))
    return seq.foldername

  # execute the sequence code with real time mvs
  def __ExecSeqCode__(self, counter, FB=False):
    j = counter # Assign value for loop variable j

    print("Executing Sequence Code...")

    try: # try running the sequence unless there is an error
      # Update MV values
      for _mv in self._notify_window.metavariables:
          exec(_mv.name+"="+str(_mv.value))
      print("Executed Metavariables")
      if FB:
        for _mv in self._notify_window.metavariables_fb:
          exec(_mv.name+"="+str(_mv.value))
          print((_mv.name+"="+str(_mv.value)))
        print("Executed Feedback Measurement Metavariables")
      for _mv in self._notify_window.metavariables_controlled:
        if _mv.enabled_ctrl.GetValue():
          exec(_mv.name+"="+str(_mv.value))
      print("Executed FB Controlled Metavariables")
      # Execute sequence file
      exec(self._notify_window.preamble)
      print("Executed Preamble")

      if self.loop==RUNMODE_LOOP and not FB: # if FB shots, IGNORE loop code
        exec(self._notify_window.loop_code)
      exec(self._notify_window.staticcode)
      print("Executed Loop/Static Code")
      return 1
    except SetError as e:
      printError("SetError: "+e.msg)
      return 0
    except ValueError as e:
      printError("ValueError: "+e)
      return 0
    except:
      printError("Unexpected error: ")
      traceback.print_exc()
      for e in sys.exc_info():
        printError('\t'+str(e))
    
      return 0

  # function contains all steps of a single run
  def __RunExp__(self, counter, savelog=True, FB=False):
    tstart = time.time()
    ClearTerminal() # Clear terminal
    ResetAll(self._dm) # Reset all sequence
    
    

    if savelog: # do not save log for idle mode
      self.__SaveLog__(counter)
    self.__GetRunTime__() # Update time
    FolderName = self.__UpdateRunName__(counter, FB=FB) # Update runname in the sequence
    tprelim = time.time()
    e = self.__ExecSeqCode__(counter, FB=FB) # Execute sequence file and MV values
    
    if FB or self.FB_control_FLAG: # for feedback measurement or control runs
       # Determine directory
      run_time = datetime.datetime.now()
      trace_dir = run_time.strftime("%Y/%m/%d/")

      # import pdb; pdb.set_trace()

      if FolderName[-2:] == 'FB':
        trace_full_dir = DIR_DATA + trace_dir + FolderName + '/'
        FB_longterm_dir = DIR_DATA + trace_dir + FolderName[0:-3] + '/FBold/'
      else:
        trace_full_dir = DIR_DATA + trace_dir + FolderName + '/FB/'
        FB_longterm_dir = DIR_DATA + trace_dir + FolderName + '/FBold/'


      

    if FB: # when about to make a new FB measurement
      # Keep the FB folder clean; should only contain the latest shot
      # (so before putting in a new shot, clear out the old one)
      if not os.path.exists(trace_full_dir):
        os.makedirs(trace_full_dir)
      if not os.path.exists(FB_longterm_dir):
        os.makedirs(FB_longterm_dir)
      for file in os.listdir(trace_full_dir):
        shutil.move(trace_full_dir+file, FB_longterm_dir+file)


    texec = time.time()
    if e == 0:
      return -1
    finish = RunExperiment(self._dm) # Run experiment and check if all device finish running!

    if not finish: # Terminate the worker if something goes wrong during the run
      wx.PostEvent(self._notify_window, UpdateEvent(data="Failed to run the experiment! Check servers!", abort=True))
    


    # Should happen if we're still waiting to respond to the latest FB run   
    if self.FB_control_FLAG and int(self._notify_window.txtctrl_FeedShotsBet.GetValue())>0:
      # Since we took a feedback run, run the feedback control cycle as well
      print((os.listdir(trace_full_dir)))
      if len(os.listdir(trace_full_dir)) > 0:
        for FBMV in self._notify_window.metavariables_controlled:
          FBMV.feedbackIteration(trace_full_dir, MVs=self._notify_window.metavariables_fb)
          # passes FB MVs first, so that if the feedback function is looking for a particular MV, it finds the FB version first
        self.FB_control_FLAG = False
    elif self.FB_control_FLAG: # FeedForward Only
      for FBMV in self._notify_window.metavariables_controlled:
        if FBMV.FF_ctrl.GetValue():
          FBMV.feedbackIteration(trace_full_dir, MVs=self._notify_window.metavariables_fb)



    tend = time.time()
    print("__RunExp__ took "+str(tend-tstart)+" seconds")
    print("__ExecSeqCode__ took "+str(texec-tprelim)+" seconds")


     

    return finish

  # function for sequence debugging
  def __Debug__(self):
    ClearTerminal() # Clear concole
    ResetAll(self._dm) # Reset all sequence
    e = self.__ExecSeqCode__(0) # Execute sequence file and MV values
    if e==0: # Return if the sequence has a bug
      return -1
    else: # Send data to the server for parsing
      e = SendData(self._dm)
      return 1

  """ Runs the worker thread """
  def run(self):
    # This is the code executing in the new thread. One must structure the processing so that it periodically peeks at the abort variable
    START = time.time()
    loopstart = START
    self.FB_control_FLAG = False
    
    # Run counter for multiple runs
    if (self.loop==RUNMODE_REPEAT) or (self.loop==RUNMODE_IDLE): # Repeat and idle run counter
      sequence_run_counter = 0
    elif (self.loop==RUNMODE_PRE): # Loop run counter
      sequence_preruns = list(range(0, self.prerun))                 # Pre-run counter
      sequence_runs    = list(range(self.startval, self.finalval+1)) # Loop run counter
      if self.random: # Randomize loop run
        random.shuffle(sequence_runs)
      sequence_run_counter = sequence_runs.pop(0)
      sequence_finished_num = 0
    runs_for_FB = 0 # a new counter to determine when FB cycles occur
      
    while(1):
      loopprevstart = loopstart
      loopstart = time.time()

      ''' Debug mode '''
      if self.loop==RUNMODE_DEBUG:
        e = self.__Debug__()
        wx.PostEvent(self._notify_window, ResultEvent(-9))
        return

      ''' Single run '''
      if self.loop==RUNMODE_SINGLE:
        e = self.__RunExp__(0)
        wx.PostEvent(self._notify_window, ResultEvent(1))
        return

      ''' Loop run '''
      # Pre run
      if self.loop==RUNMODE_PRE:
        if not sequence_preruns: # change mode to loop run after the pre-running
          self.loop = RUNMODE_LOOP
        else:
          sequence_prerun_counter = sequence_preruns.pop(0)
          wx.PostEvent(self._notify_window, UpdateEvent("Pre-Running: "+str(sequence_prerun_counter+1)))
          e = self.__RunExp__(sequence_prerun_counter, savelog=False)
      # Looped run
      if self.loop==RUNMODE_LOOP:
        total_run_num = abs(self.startval-self.finalval)+1
        wx.PostEvent(self._notify_window, UpdateEvent("Running iteration"+" ("+"{0:.1f}%".format(1e2*sequence_finished_num/total_run_num)+" finished): "+"j="+str(sequence_run_counter)))
        # j = sequence_run_counter
        e = self.__RunExp__(sequence_run_counter, savelog=False)
        print("(* Finished run "+str(sequence_run_counter)+"/"+str(self.finalval)+", t = "+str(time.time()-START)+" *)")
        if not sequence_runs:
          wx.PostEvent(self._notify_window, ResultEvent(self.finalval-self.startval+1, loop=True))
          return
        sequence_run_counter = sequence_runs.pop(0)
        sequence_finished_num += 1
      
      ''' Repeated run '''
      if self.loop==RUNMODE_REPEAT: # run repeatedly
        sequence_run_counter += 1
        e = self.__RunExp__(sequence_run_counter)
        print("(* Finished run "+str(sequence_run_counter)+", t = "+str(time.time()-START)+"*)")
        
      ''' Idle run '''
      if self.loop==RUNMODE_IDLE: # Same as repeated run but not saving log files.
        sequence_run_counter += 1
        e = self.__RunExp__(sequence_run_counter, savelog=False)

      if not e: # If run experiment fail, abort the worker. 
        self.abort()

      loopend = time.time()

      print("Time between starts of loops:" + str(loopstart-loopprevstart) + " s")
      print("Time from start to end of loop:" + str(loopend-loopstart) + " s")

      ''' Abort run '''
      if self._want_abort:
        wx.PostEvent(self._notify_window, ResultEvent(sequence_run_counter-self.startval))
        return

      # Possible Feedback Run
      if self._notify_window.chkbox_FeedOn.GetValue(): # If checkbox is enabled
        FeedShotsBet = self._notify_window.txtctrl_FeedShotsBet.GetValue()
        if not is_int(FeedShotsBet):
          print("FB Error: shots between must be an integer!")
        elif int(FeedShotsBet) < 1:
          # Don't run a feedback shot, but update feedback MVs (FOR FEEDFORWARD)
          print("Ready for FF!")
          self.FB_control_FLAG = True
        else:
          FSB = int(FeedShotsBet)
          if FSB < 1:
            FSB = 1
          if runs_for_FB % FSB == 0: # time for a Feedback run
            print("FB Run!")
            self.FB_control_FLAG = True # stays true until the controller is able to RESPOND to the FB run (waits for SPCM data to appear)
            e=self.__RunExp__(runs_for_FB/FSB, FB=True)
      runs_for_FB += 1
      ''' Update MV values '''
      if self._need_update:
        for _mv in self._notify_window.metavariables:
          exec(_mv.name+"="+str(_mv.value))
        self._need_update = 0
      time.sleep(1e-3*self.delay) # Time gap between runs
  
  #Method for use by main thread to signal an abort
  def abort(self):
    self._want_abort = 1

###########################################################
###                 Processing Routines                 ###
###########################################################
def DefineEndings(all_sequences):
  '''Make sure all the sequences have the same length by adding time'''
  maxlength = 0
  for seq in all_sequences:
    maxlength = max(maxlength, seq.TIME_STOP)
  for seq in all_sequences:
    seq.SetFinalRamps(maxlength)
  return maxlength

def CopyChans():
  '''Copy values from bright channel to slave channel'''
  for chans in all_copyChans:
    copy_chan  = chans[0] # Master channel
    paste_chan = chans[1] # Slave channel
    # Clear values of the slave channel
    paste_chan._UserValues  = []
    paste_chan._TransValues = []
    # Set value from master channel to slave channel
    paste_chan.Set(copy_chan._UserValues)

def UpdatePreviousValue(all_sequences):
  '''Set the sequence end value as the previous run value.'''
  for seq in all_sequences:
    for chan in seq.allChannels:
      if chan != None:
        chan.SetPreviousValue(chan.ssv)

def WaitForAllToFinish(dm):
  '''Check if server finish running'''
  all_sequences = dm.seq_act # get all active sequence
  allserversfinished = True # Finish indicator
  print('Waiting for all sequences to end:')
  for seq in all_sequences:
    if seq != MasterSequence: 
      print('\tChecking '+seq.name)
      rtn = dm.Ping(seq)
      allserversfinished &= rtn
  print('Done with waiting!')
  if (allserversfinished):
    print('All servers finished running!')
  else:
    printError('Some of the sequences failed to finish within the allotted time!')
  return allserversfinished

# Reset all sequences
def ResetAll(dm):
  '''Reset all the sequences'''
  seqs = all_sequences
  for _seq in seqs:
      _seq.Reset()

# This will send data to the device and check if all servers finished running
def RunExperiment(dm):
  tstart = time.time()
  '''This sends all sequences, queues all but the master, and runs the master! It should block until the master finishes!'''

  seqs = dm.seq_act # Get all active devices from the DeviceManager

  # Wrap sequences
  seq_length = DefineEndings(seqs) # Match the end time of all sequences
  CopyChans() # Copy the bright sequence to the corresponding dark sequence
  
  # Start sending data to device servers and check if they finish parsing the data
  #_socks = {} # Dict for temporarily hold all the open sockets
  # Send and queue all sequence
  #tqueuestart = time.time()
  # for seq in seqs:
  #   print(seq.name+" (Length: "+str(seq.TIME_STOP/1e6)+"s):")
  #   print('\tSending...')
  #   r = dm.Send(seq)

  #   if seq != MasterSequence: # Queue the sequence unless is master sequence
  #     _socks[seq.name] = dm.Queue(seq) # Collect the open socket for later use
  #     if _socks[seq.name] != -1:
  #       print(seq.name + " queued")
  #   else:
  #     print('\tMaster sequence, will run after all sequences have been queued...')
  #tqueueend = time.time()

  # e_prep = True
  # for seq in seqs: # Check if sequence finish parsing the data
  #   if seq != MasterSequence:
  #     print("checking "+seq.name)
  #     if _socks[seq.name] != -1:
  #       e = dm.PrepFinish(_socks[seq.name])
  #       if e == 0: 
  #         printError(seq.name+' failed in the preperation!')
  #         e_prep = False
  # tcheckprepend = time.time()
  tsend = dm.SendSequences()
  e_prep, tqueue, tprep = dm.QueueSequences(MasterSequence, timeout=3.)

  UpdatePreviousValue(seqs) # UPDATE THE PREVIOUS VALUE WITH STEADY STATE VALUE AFTER THE SEQUENCE
  print('Running the Master Sequence')
  dm.Run(MasterSequence) # RUN THE SEQUENCE THAT HARDWARE TRIGGERS THE OTHERS.

  # If some server failed in the preperation process, then do not check for finish, quit with error
  if not e_prep:
    return e_prep

  #FinishRun = WaitForAllToFinish(dm) # Wait for all sequence to finish
  FinishRun = dm.WaitForAllToFinish() # Wait for all sequence to finish
  tend = time.time()

  print("RunExperiment took "+str(tend-tstart)+" seconds")
  print("Sending data to servers took "+str(1000.0*(tsend))+" milliseconds")
  print("Queing took "+str(1000.0*(tqueue))+" milliseconds")
  print("Checking that servers have parsed took "+str(1000.0*(tprep))+" milliseconds")

  return FinishRun

def SendData(dm):
  seqs = dm.seq_act # Get all active devices from the DeviceManager
  # Wrap sequences
  seq_length = DefineEndings(seqs) # Match the end time of all sequences
  CopyChans() # Copy the bright sequence to the corresponding dark sequence
  # Send and queue all sequence
  # for seq in seqs:
  #   print(seq.name+" (Length: "+str(seq.TIME_STOP/1e6)+"s):")
  #   print('\tSending...')
  #   dm.Send(seq)
  dm.SendSequences()
  return 1
