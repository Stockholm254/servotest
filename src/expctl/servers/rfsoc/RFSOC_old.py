#!/usr/bin/python
import sys
from signal import signal, SIGINT
from sys import exit
import os,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from util.server import *
#from util.NI_server import *

#from utilities.util import *
from utilities.util import *
#from servers.util.server import *
import math
import time
import numpy as np

#from . import util.ok as ok
# import util.ok as ok
from util.SequenceProcessor import *
from rfsoc.rfsocdriver import *



#server = Server("DOut1", 50001)
server = Server("DDS_1", 60617)
server.message  = '===============================================\n'
server.message += '==      DDS Profile Frequency Out Server     ==\n'
server.message += '==                for RFSOC                  ==\n'
server.message += '==============================================='

#RFSOC vars
bitfile_name = '/home/xilinx/ash/ddsfinal/ddsfinal10k_tm_3.bit'


chan_shuffler = [2,1,0,3,4,5,6,7]
#list index is the sequence channel and corresponding element is the DDS channel.

#These values are defined in rfsocdriver, override here.
CAL_DDS_CLK = 409.6025 #The actual calibrated clock. Calibrate with an accurate spectrum analyzer .
#Actually I am not sure where the error comes from, The PLLs on ZCU111 board or those on DAC tiles.

SEQUENCER_CLK = CAL_DDS_CLK/2 #This is the clock for sequencer. This clock is hardwired on the FPGA to be DDS_CLK/2
SAMPLE_CLK = CAL_DDS_CLK*16 #This is the clock for the DACs. Again, hardwired to be DDS_CLK*16
#Actually in hardware it goes the other way, The DDS clock is derived from sample clock by /16

numDDS = 8
first_trigger = 0
MAX_RAMPS= 10000 
trigger_config = 0b111111111 #if MSB is 0, a hardware trigger on the PMODs is required and the other bits don't matter
#if 1, then ramps can be triggered using the Central user switch or with software by using the method defined in rfdriver.
#Then the other bits determine which channels will be triggered. 


active_chans = []
fullSeqs = [] #list of sequences for all channels in original format, with holes filled and frequencies and times converted to FTWs and cycles
NumRamps = []  #Total Number of ramps for each channel

counter = 0
def RunServer(seq, rf, autostart=1, UPDATE_RAM=1):
  TIME_START = time.time()
  global counter
  
  ## Convert seq to get all the times and frequencies, and save to buffers to pass to FPGA Block RAM
  rf.configureTriggerManager(config = trigger_config)

  if(UPDATE_RAM):
    fullSeqs = [] 
    NumRamps = []
    active_chans = []

    for chan in seq.allChannels:
      chan.Print()
      chanid = chan.chanid
      if chan == None:
        continue
      elif chan.chanid >= 7:
        print(f"More channels than {numDDS}, ignoring...\n")
        continue

      active_chans.append(chan_shuffler[chanid])
      ssvalHz = chan.GetHardwareSSV() #steady_state_value
      ssvalFTW = getFTW(ssvalHz)
  
      convertedSeq = ConvertSeqtoCountsandFTWs(chan.GetHardwareValues()) #values)
      fullSeq = GenerateFullSeq(convertedSeq,ssvalFTW)
      N_Ramps = len(fullSeq)
      fullSeqs.append(fullSeq)
      NumRamps.append(N_Ramps)

      phase_reset_bits = [0]*N_Ramps
      #Should the phase be reset before starting a given ramp?

      trigger_bits = [first_trigger]+[int (not autostart)]*(N_Ramps > 1)+[0]*(N_Ramps-2)
      #Does a given ramp need to be triggered?

      #ADD RAMPS CHECK

      rf.writeData(chan_shuffler[chanid], fullSeq, trigger_bits, phase_reset_bits)
  
  for chan in active_chans: 
    rf.resetDoneRegister(chan)
    rf.startChannel(chan)

  TIME_DATA = time.time() 
  print("Ramp sequence started. I will output based on the trigger bits. \n")

  while(True):
    if(rf.isSequenceDone(active_chans)):
        counter = counter+1
        print(f"Sequence executed {counter} times\n")
        break

    
  TIME_STOP = time.time()
  return TIME_STOP - TIME_DATA
    
def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    server.sock.close()
    exit(0)

if __name__ == '__main__':
  # Tell Python to run the handler() function when SIGINT is recieved
  signal(SIGINT, handler)
  server.Listen()
  
  rf = rfdriver(bitfile_name, True)
  
  while True:
    while True:
      command, data = recv_msg(server.sock) # Receive a command     
      print(command)
      
      if command == "RUN":  # Run the sequence (if we've already received it)
        if server.seq == None:
          printError('Run() failed. Sequence has not been imported!')
          send_msg(server.sock, server.ReplyHeader() + 'Run() failed. Sequence has not been imported!')
          break
        else:
          time_taken = RunServer(server.seq, rf)
          success = time_taken
    
        time_taken = '%.2f' % success
        send_msg(server.sock, server.ReplyHeader() + 'Successfully ran sequence (' + str(time_taken) + ' seconds).')
        break

      elif command == "QUEUE":  # Run the sequence (if we've already received it)
        if server.seq == None:
          printError('Run() failed. Sequence has not been imported!')
          send_msg(server.sock, server.ReplyHeader() + 'Run() failed. Sequence has not been imported!')
          break
        else:
          time_taken = RunServer(server.seq, rf, autostart=0)
          success = time_taken
    
        time_taken = '%.2f' % success
        send_msg(server.sock, server.ReplyHeader() + 'Successfully ran sequence (' + str(time_taken) + ' seconds).')
        break
        
      # Load in a sequence
      elif command == "SEQ":
        server.seq = data # unpack the sequence
        numChannels = 0
        for chan in server.seq.allChannels:
          if chan != None: numChannels += 1
        printGreen("Received sequence ("+str(numChannels)+" channels): "+str(server.seq.name)+".")
        reply = "Received '"+str(server.seq.name)+"'; " + str(numChannels) + " channels defined."
        send_msg(server.sock, server.ReplyHeader() + reply)
        break

      # elif command == 'GETPLOTDATA':
        # plt_data = DataForPlot(server.seq)
        # send_msg(server.sock, "DATA", plt_data)
        # break
      
      elif command == 'PING':
        print("Got PING'd!")
        send_msg(server.sock, server.ReplyHeader() + "Got PING'd!")
        break
        
      else:
        reply = 'Unexpected command'
        send_msg(server.sock, server.ReplyHeader() + reply)
        break
