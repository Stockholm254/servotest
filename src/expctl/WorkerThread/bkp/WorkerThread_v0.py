#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import time
import wx
from threading import *

LOGDIR = r'C:/Users/Simonlab/experiment_logs'

######################################################
###    Thread class that executes repeated runs    ###
######################################################

class WorkerThread(Thread):
  def __init__(self, notify_window, device_manager, loop=0, startval=0, stopval=10, prerun=0, runflag=0):
      Thread.__init__(self)
      
      jGlobals.RUN_FLAG = runflag # Setting runflag to 0 disables sequences calls to Send(), Run(), etc
      
      # Run parms
      self._notify_window = notify_window                   # GUI object
      self._dm            = device_manager                  # Device manager
      self._want_abort    = 0                               # Abort indicator
      self._need_update   = 0                               # MV update indicator
      self.loop           = loop                            # Run mode indicator
      self.startval       = startval                        # Start value of loop run counter
      self.finalval       = stopval                         # Stop value of loop run counter
      self.prerun         = prerun                          # Number of pre-runs in loop run mode
      self.delay          = notify_window.time_between_runs # Time between each run in ms
      # Log info
      self.log_dir = LOGDIR # Default log file directory
      
      self.start() # This starts the thread running on creation

  def save_log(self, file_counter):
    # Generate log file date directory
    log_time = datetime.datetime.now()
    date_dir = log_time.strftime('/%Y/%Y-%m/%Y-%m-%d')
    log_dir  = self.log_dir+datedirs
    if not os.path.exists(log_dir):
      os.makedirs(log_dir)
    # Generate log file name (this is also the runname in sequence properties)
    runname   = log_time.strftime('%Y-%m-%d T %H-%M-%S-%f')[:-3] + "_" + str(file_counter)
    log_fname = log_dir+"/log_"+runname + ".txt"
    # Write log file
    f = open(log_fname, 'w')
    f.write("#Log generated at " + log_time.strftime('%b %d, %Y %H:%M:%S.%f')[:-3] + '\n' + '\n')
    f.write("#seq_filename = "+self._notify_window.file_name+'\n')
    f.write("#seq_dirname = "+self._notify_window.dir_name+'\n')
    if self.loop == 0 or self.loop == 1: # Single and repeated run
      for var in self._notify_window.metavariables:
        f.write(var.name+" "+'='+" "+str(var.value)+'\n')
    elif self.loop == 2: # Loop run
      loop_code_split = self._notify_window.loop_code.split('\n')
      for line in loop_code_split:
        var_parse = line.split('=')
        if len(var_parse) > 1:
          if is_number(var_parse[1]):
            f.write(line + '\n')
          else:
            var_newValue = eval(var_parse[1].replace("j", str(file_counter)))
            f.write(var_parse[0] + '=' + " " + str(var_newValue) + '\n')
    f.close()

    # Write runname to each sequence
    for seq in all_sequences:
        seq.runname = runname
        
    return runname
  
  """ Runs the worker thread """
  def run(self):
    # This is the code executing in the new thread. One must structure the processing so that it periodically peeks at the abort variable
    
    START = time.time()
    
    for _mv in self._notify_window.metavariables:
      exec(_mv.name + "=" + str(_mv.value))
   
    ''' Single run '''
    if self.loop == 0:
      sequence_run_counter = 0
      self.save_log(sequence_run_counter)
      exec(self._notify_window.preamble)
      exec(self._notify_window.staticcode)
      wx.PostEvent(self._notify_window, ResultEvent(1))
      return
      
    elif (self.loop==1) or (self.loop==4): #repeat and idle run counter
      sequence_run_counter = 0
    elif self.loop == 2: #initialize the loop run counter
      sequence_preruns = list(range(0, self.prerun)) # pre-run counter
      sequence_runs    = list(range(self.startval, self.finalval + 1)) # loop run counter
      if self._notify_window.randomize_runorder:
        random.shuffle(sequence_runs)
      sequence_run_counter = sequence_runs.pop(0)
      sequence_finalvalished_num = 0.0
      
    while(1):
      ''' Pre run '''
      if self.loop == 2:
        self.save_log(sequence_run_counter)
        if not sequence_preruns:
          self.loop = 3
        else:
          sequence_prerun_counter = sequence_preruns.pop(0)
          self._notify_window.statusbar.SetStatusText("Pre-Running: "+str(sequence_prerun_counter+1))
          exec(self._notify_window.preamble)
          exec(self._notify_window.staticcode)
      ''' Looped run '''
      if self.loop == 3:
        self.save_log(sequence_run_counter)
        total_run_num = abs(self.startval - self.finalval)
        self._notify_window.statusbar.SetStatusText("Running iteration"+" ("+"{0:.1f}%".format(sequence_finalvalished_num/total_run_num*100)+" finalvalished): "+"j="+str(sequence_run_counter))
        exec(self._notify_window.preamble)
        j = sequence_run_counter
        exec(self._notify_window.loop_code)  
        exec(self._notify_window.staticcode)
        print("(* Finished run "+str(sequence_run_counter)+"/"+str(self.finalval)+", t = "+str(time.time()-START)+" *)")
        if not sequence_runs:
          wx.PostEvent(self._notify_window, ResultEvent(self.finalval-self.startval+1))
          return
        sequence_run_counter = sequence_runs.pop(0)
        sequence_finalvalished_num += 1
      
      ''' Repeated run '''
      if self.loop == 1:
        self.save_log(sequence_run_counter)
        exec(self._notify_window.preamble)
        exec(self._notify_window.staticcode)
        print("(* Finished run "+str(sequence_run_counter)+", t = "+str(time.time()-START)+"*)")
        sequence_run_counter += 1
        
      ''' Idle run '''
      if self.loop == 4: # Same as repeated run but not saving log files.
        exec(self._notify_window.preamble)
        exec(self._notify_window.staticcode)
        sequence_run_counter += 1
        
      if self._want_abort:
        wx.PostEvent(self._notify_window, ResultEvent(sequence_run_counter - self.startval + 1))
        return
      if self._need_update:
        for _mv in self._notify_window.metavariables:
          exec(_mv.name + "=" + str(_mv.value))
        self._need_update = 0
    
      time.sleep(self.delay/1e3) # Time gap between runs
      
  def abort(self):
    """ Method for use by main thread to signal an abort """
    self._want_abort = 1

###########################################################
###                 Processing Routines                 ###
###########################################################
def CopyChans():
  '''Copy values from bright channel to slave channel'''
  for chans in all_copyChans:
    copy_chan = chans[0]
    paste_chan = chans[1]
    # print "Copying ", copy_chan.name, " to ", paste_chan.name
    paste_chan.values = []
    paste_chan._transformedValues = []
    paste_chan.Set(copy_chan.values)

def DefineEndings(all_sequences):
  '''Make sure all the sequences have the same length by adding time'''
  maxlength = 0
  for seq in all_sequences:
    maxlength = max(maxlength, seq.TIME_STOP)
  for seq in all_sequences:
    seq.SetFinalRamps(maxlength)
  return maxlength

def UpdatePreviousValue(all_sequences):
  '''Set the sequence end value as the previous run value.'''
  for seq in all_sequences:
    for chan in seq.allChannels:
      if chan != None:
        chan.SetPreviousValue(chan.steady_state_value)

def RunExperiment(dm):
  '''This sends all sequences, queues all but the master, and runs the master! It should block until the master finishes!'''
  
  all_sequences = dm.seq_use

  '''TODO: DETECT MASTER SEQUENCE'''
  MasterSequence = all_sequences[0]

  seq_length = DefineEndings(all_sequences) # Match the end time of all sequences
  # CopyChans(all_sequences) # Copy the bright sequence to the corresponding dark sequence
  
  # Send and queue all sequence
  for seq in all_sequences:
    print('\tSending...')
    dm.Send(seq)
    if seq != MasterSequence:
      r = dm.Queue(seq)
      if r == 1:
        print(seq.name+" queued")
      else:
        '''TODO: setup a RunError() message and quit the run!'''
        print("Failed to queue sequence "+seq.name)
        return -1
    else:
      print('\tMaster sequence, will run after all sequences have been queued...')

  # Check if all sequence finished parsing the data
  for seq in all_sequences:
    if seq != MasterSequence:
      print("Checking "+seq.name)
      r = dm.Recv(seq)
      if r == -1:
        printError(seq.name+" failed to finish parsing the data!")
        '''TODO: setup a RunError() message and quit the run!'''
        return -1

  UpdatePreviousValue(all_sequences) #UPDATE THE PREVIOUS VALUE WITH STEADY STATE VALUE AFTER THE SEQUENCE
  print('Running the Master Sequence')
  dm.Run(MasterSequence)  #RUN THE SEQUENCE THAT HARDWARE TRIGGERS THE OTHERS.

  return seq_length

def WaitForAllToFinish(dm, all_sequences, seq_length):
  allserversfinished = True
  print('Waiting for all sequences to end:')
  # time.sleep(1.0*seq_length/1e6)
  MasterSequence = all_sequences[1]
  for seq in all_sequences:
    if seq != MasterSequence:
      print('\tChecking '+seq.name)
      rtn = dm.Recv(seq)
      allserversfinished &= rtn
  print('Done with waiting!')
  if (allserversfinished):
    print('All servers finished running!')
  else:
    print('Some of the sequences failed to finish within the allotted time!')
  return allserversfinished
  
def ResetAll():
  for seq in all_sequences:
      seq.Reset()