#!/usr/bin/python
import sys
sys.path.append("C:/Users/simonlab/Documents/Lukas/Python/Py27Code/Control_Suite_X/") # Add utilities path

from .util.server import *
#from util.NI_server import *

import numpy
from utilities.util import *
from servers.util.server import *
import math
import time
import numpy as np


server = Server("DOut1", 50001)
server.message  = '===========================================\n'
server.message += '==         Digital Output Server 1       ==\n'
server.message += '==              for PCIe 6537            ==\n'
server.message += '==========================================='    

localMHz = 1e6
# seq_duration = float(seq.TIME_STOP) # microseconds
timeout = 10.0 # (seconds)
sample_rate = 10.0  # number of samples per microsecond (clock speed in MHz)
# samps_per_channel = int(math.ceil(sample_rate * seq_duration) + 1) # MHz * us (+1 for steady_state_value)
# buffer_size = samps_per_channel # number of samples
channel_num = 32
    
def ParseData(seq, samps_per_channel):
  time.sleep(0.01)
  return numpy.zeros((seq.max_channels*samps_per_channel,), dtype=float64)

# Convert the machine readable data to plot data
# !!!!!!!THIS NEED TO BE UPDATED EVERYTIME ParseData FUNCTION IS MODIFIED!!!!!!!
def DataForPlot(seq):
  # IMPORTANT: EVERY TIME THE DATA PARSING PROCESS IS MODIFIED (NEW CARD OR DRIVER INSTALLED), THIS MODULE 
  #            MUST BE REVISITED IN ORDER TO ENSURE THE PLOTTING IS CORRECT.
  # This module get the machine readable data from the ParseDate function, and then transform it into integer
  # value for 32 channels. The values are inverted due to the line driver. Only update points are returned 
  # because the plot memory limit. 
  
  seq_duration = float(seq.TIME_STOP) # microseconds
  samps_per_channel = int(math.ceil(sample_rate * seq_duration) + 1) # MHz * us (+1 for steady_state_value)
  
  parsedDatas = ParseData(seq, samps_per_channel) # Get the machine readable data
  parsedDatas = np.invert(parsedDatas) # Bitwise invert to correct the line driver inversion
  
  firstVal = format(parsedDatas[0], '#034b')[2:] # Add first value to the list
  chanData = [np.array(list(firstVal), dtype='int')]
  timeList = [0] # Add first time point to the time list
  ind_update = np.nonzero(np.diff(parsedDatas))[0] # Find the sample where the value is updated. Cannot plot all the data due to the memory limit
  for ind in ind_update:
    binData = format(parsedDatas[ind+1], '#034b')[2:] # Convert state integer to binary form
    chanData.append(np.array(list(binData), dtype='int'))
    timeList.append((ind+1)/sample_rate)
  finalVal = format(parsedDatas[-1], '#034b')[2:] # Add final value to the value list
  chanData.append(np.array(list(finalVal), dtype='int'))
  timeList.append((samps_per_channel-1)/sample_rate) # Add final time point to the time list
  
  chanData = np.array(chanData)
  chanData = np.transpose(np.fliplr(chanData)) # Transpose the matrix so that match the sequence format and channel indicies.
  
  return timeList, chanData
  
def RunServer(seq, autostart = 1):
  TIME_START = time.time()
  seq_data = ParseData(seq, 1000)
  time.sleep(0.03)
  TIME_STOP = time.time()
  return TIME_STOP-TIME_START
    
if __name__ == '__main__':
  server.Listen()
  
  while True:
    clientSocket, addr = server.sock.accept()
    
    while True:
      data = recv_msg(clientSocket) # Receive a command      
      data = printGrayDate(data)    # Print the full command  as received     
      tokens = data.strip().split(' ', 2)  # Isolate the command in case it contains extra info
      command = tokens[0]
      
      if command == "RUN":  # Run the sequence (if we've already received it)
        if server.seq == None:
          printError('Run() failed. Sequence has not been imported!')
          send_msg(clientSocket, server.ReplyHeader() + 'Run() failed. Sequence has not been imported!')
          break
        else:
          time_taken = RunServer(server.seq)
          success = time_taken
    
        time_taken = '%.2f' % success
        send_msg(clientSocket, server.ReplyHeader() + 'Successfully ran sequence (' + str(time_taken) + ' seconds).')
        break
        
      # Load in a sequence
      elif command == "SEQ":
        seq_data = recv_msg(clientSocket)
        server.seq = pickle.loads(seq_data)  # unpack the sequence
        numChannels = 0
        for chan in server.seq.allChannels:
          if chan != None: numChannels += 1
        printGreen("Received sequence ("+str(numChannels)+" channels): "+str(server.seq.name)+".")
        reply = "Received '"+str(server.seq.name)+"'; " + str(numChannels) + " channels defined."
        send_msg(clientSocket, server.ReplyHeader() + reply)
        break

      elif command == 'GETPLOTDATA':
        plt_data = pickle.dumps(DataForPlot(server.seq), 1)
        send_msg(clientSocket, plt_data)
        break
        
      else:
        reply = 'Unexpected command'
        send_msg(clientSocket, server.ReplyHeader() + reply)
        break
      
    clientSocket.close()
