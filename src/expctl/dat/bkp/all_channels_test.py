from sequencer.sequence import Sequence
import utilities.jGlobals as jGlobals
import transformations as tran
import socket
import time

###################################################################################################
###    ALL CHANNELS/SEQS ARE DEFINED HERE, AS ARE FEW ROUTINES THAT CRUNCH THEM (@ bottom)      ###
###################################################################################################

#=======================================Sequence Definitions=========================================

#FIRST DECLARE ALL SEQUENCES into the all_sequences array, and then give them names for easier assignment!

all_sequences = ([
  Sequence("Test sequence", host='192.168.1.105', port=60600, max_channels=1, modulename='test_server')
  ])

test_seq, = all_sequences #WE DO IT IN THIS ORDER SO THAT ONE CANNOT GET AWAY WITH CREATING A NAMED SEQUENCE WHICH IS NOT IN THE ARRAY OF ALL SEQUENCES!!

bright_sequences   = [test_seq] #THIS IS THE SEQUENCES THAT CAN BE CHANGED IN THE STEADY STATE VALUES
MasterSequence     = test_seq                #THIS IS THE SEQUENCE THAT TRIGGERS THE OTHERS!
# SEQUENCES_TO_GRAPH = [digital_seq1, analog_seq1, dds_freq_seq1, dds_freq_seq2, dds_PDH_freq_seq1] #This controls who is graphed!
SEQUENCES_TO_GRAPH = [test_seq] #This controls who is graphed!

#=======================================Channel Definitions=========================================

#NEXT ADD ALL OF THE CHANNELS TO THEM! ##Note: the name in quotes must have 1 < length < 31 
test_chan = test_seq.newChannel(0, "Test Channel", steady_state_value=0, max_value=9, graph=1)
#=====================================End Channel Definitions=======================================

#====================================Slave Channel Definitions======================================
#Any channel appears in this section should NEVER be given any value in any sequence file.
#The value of these channels will be assigned automatically later.
#The properties of the channel (id, name, steady_state_value, max_value, and graph) should be set in this section

#=========================================Linked Channels===========================================
#List of channel pairs that would be copy and paste.
#To add a copy and paste pair, just add a new list of the form ["master_channel", "slave_channel"]
all_copyChans = ([
])

#=======================================Processing Routines=========================================

def SetSSVtoFinalValue():
  for seq in all_sequences:
    for chan in seq.allChannels:
      if chan is not None and len(chan.values) > 0:
        chan.SetSteadyStateValue(chan.GetLastValue())

def CopyChans():
#Copy the values of one channel to another empty one. (The value of the target channel must be completely empty before the copy!)
  for chans in all_copyChans:
    copy_chan = chans[0]
    paste_chan = chans[1]
    # print "Copying ", copy_chan.name, " to ", paste_chan.name
    paste_chan.values = []
    paste_chan._transformedValues = []
    paste_chan.Set(copy_chan.values)
    
def SetSeqOffset():
  # Set sequence offset due to different trigger time
  for seq in all_sequences:
    seq.SetTimeOffset()

def DDSInitRamp():
  #=====================================================================#
  #  This will detect the DDS frequency change for the PDH locking and  #
  #  add a ramp time interval at the beginning of the sequency.         #
  #  If the ramp time is not zero (PDH frequency changed from           #
  #  the previous sequence), ALL channels will ramp from SSV to the     #
  #  first value in the sequence.                                       #
  #=====================================================================#
  DDSRampTime = []

  for chan in dds_PDH_freq_seq1.allChannels:
    if chan != None:
      lastVal = chan.GetPreviousValue()
      newVal = chan.GetFirstValue()
      DiffVal = abs(lastVal - newVal)
      MaxJumpValue = chan.max_jump_value
      RampSpeed = chan.max_ramp_speed
      if (DiffVal > MaxJumpValue) & (RampSpeed != 0.0):
        DDSRampTime.append(DiffVal/RampSpeed) # RampSpeed is in channel_value/us

  if len(DDSRampTime) > 0:
    MaxDDSRampTime = max(DDSRampTime)
  else:
    MaxDDSRampTime = 0

  print("DDS init ramp time: ", MaxDDSRampTime, "us")

  if MaxDDSRampTime > 0:
    for seq in all_sequences:
      seq.SetInitRamps(ramp_time=MaxDDSRampTime)

def DefineEndings():
  #Make sure all the sequences have the same length by adding time
  maxlength = 0
  for seq in all_sequences:
    maxlength = max(maxlength, seq.TIME_STOP)
  for seq in all_sequences:
    seq.SetFinalRamps(maxlength)

def UpdatePreviousValue():
  #=====================================================================#
  #  This will put the steady state value of channel as the memory of   #
  #  the channel. So it requires that the SSV should be defined by the  #
  #  end of the sequence.                                               #
  #=====================================================================#
  for seq in all_sequences:
    for chan in seq.allChannels:
      if chan != None:
        chan.SetPreviousValue(chan.steady_state_value)
  
def RunExperiment(): #This sends all sequences, queues all but the master, and runs the master! It should block until the master finishes!
  # DDSInitRamp()
  SetSeqOffset()
  DefineEndings()
  CopyChans() #Copy the bright sequence to the corresponding dark sequence
  
  socks = {} # Dict for sockets of different sequence. It's used to seperate queueing the server and acquire feedback for ready. 
  
  for seq in all_sequences:
    print(seq.name+" (Length: " + str(seq.TIME_STOP/1e6) + "s):")   ### mute for speed up ###
    print('\tSending...')   ### mute for speed up ###
    seq.Send()
    if(seq!=MasterSequence): #the one sequence that hardware triggers the rest should be RUN, not QUEUED!
      # print '\tQueueing...'
      socks[seq.name] = seq.Queue()      #QUEUE ALL OTHER SEQUENCES. note that queue won't block (eg it won't pause client execution until the sequences have been triggered and completely run), though the servers _themselves_ ought to block!
      if socks[seq.name] != -1:
        print(seq.name + " queued")   ### mute for speed up ###
    else:   ### mute for speed up ###
      print('\tMaster sequence, will run after all sequences have been queued...')   ### mute for speed up ###
  if jGlobals.RUN_FLAG != 0:
    for seq in all_sequences:
      if(seq!=MasterSequence):
        print("checking "+seq.name)
        if socks[seq.name] != -1:
          seq.PrepFinish(socks[seq.name])   #Check if the server has finished sending the data to the device
  print('Running the Master Sequence')   ### mute for speed up ###
  
  UpdatePreviousValue()
  MasterSequence.Run()       #RUN THE SEQUENCE THAT HARDWARE TRIGGERS THE OTHERS. this one does block until it is done, but since it may not be the longest sequence we need to query the others to be certain they are done!
  
def WaitForAllToFinish():
  allserversfinished=True
  print('Waiting for all sequences to end:')
  for seq in all_sequences:
    print('\tWaiting for ' + seq.name)
    allserversfinished &= seq.WaitTilDone()
  print('done with waiting')
  if (allserversfinished):
    print('all servers finished running')
  else:
    print('Some of the sequences failed to finish within the allotted time!')
  return allserversfinished
  
def ResetAll():
  for seq in all_sequences:
      seq.Reset()