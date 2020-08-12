from . import util.ok as ok # OpalKelly library for (Python) wrappings (checking clk rate on, resetting, and grabbing data)
import time
import datetime
import os
import numpy as np
from inspect import getfile, currentframe
from .util.server import *
from utilities.util import *

DATA_DIR = "E:/Data/"

fullpath = os.path.abspath(getfile(currentframe()))

server = Server('PTIn1', 60623)
server.message = fullpath + '\n'
server.message += '===========================================\n'
server.message += '==         Photon Timer Server 1         ==\n'
server.message += '===========================================\n'
server.message += 'Number of RAM blocks used: 32\n'

# Variables for configuring Verilog to FPGA
dev = ok.okCFrontPanel()
pll = ok.okCPLL22150()
# code = "C:/Users/Simonlab/Programming/Control Suite/servers/photon_timer_new7.1/verilog/counters.bit"
code = r"C:\ExperimentSoftwares\Control_Suite_X\servers\FPGA_bit_file\PhotonTimers.bit"
FPGAsn = '1452000AQ7'

# Settings Used on the FPGA
N_blocks = 32 # number of RAM blocks instantiated
FPGAchan = 8 # number of bits assigned for each set of channels
L_t = 17 # number of bits assigned for each time value

# Set up bytearrays for piping out from blocks of RAM
data_byt = [bytearray(2048) for x in range(N_blocks)]

# Two Functions needed to convert RAM block data into readable data:
# Convert RAM block of byte arrays to bit string
def byt_to_bi(byt):
	bi = bin(byt)[2:].zfill(8)
	return bi
# Convert binary data back to channels and times
def bi_to_dat(array, T):
	dat = []
	for section in range(len(array)/32):
		ramO_din = array[section*32:(section+1)*32]
		if ramO_din == '0'*32:
			pass
		else:
			time_val = 0
			for digit in range(L_t):
				if ramO_din[31-digit] == '1':
					time_val += 2**digit
			time_val *= T
			channels = ''
			for ch in range(FPGAchan):
				if ramO_din[FPGAchan-1-ch] == '1':
					channels += str(ch)
			dat.append(channels+' '+str(time_val))
	return dat

## All the subroutines for the Main Function
# Subroutine 1: Configure the FPGA for Timr Program
def Config_FPGA():
	#Instantiate okC structure
	if dev.OpenBySerial(FPGAsn) == -1:
		print("I can't connect...")
		exit()
	dev.GetEepromPLL22150Configuration(pll)
	dev.SetPLL22150Configuration(pll)
	
	f = str(float(pll.GetOutputFrequency(0)) * (10 ** 6))
	T = 1 / float(f)
	print("Timing Resolution =", T*1e9, "ns")
	dev.ConfigureFPGA(code) # Configure FPGA with bit code
	
	return T
	
# Subroutine 2: Start the FPGA state machine and let it wait for the trigger
def RunServer(seq, autostart=0):
	TIME_START = time.time()
	chan = seq.getChannelByName("Photon Timer")
	thehardwarevalues = chan.GetHardwareValues()
	save_switch_chan = seq.getChannelByName("Photon Timer Save")
	save_switch = save_switch_chan.GetHardwareValues()[0][1] # Getting the save switch from the sequence
	
	if autostart == 0:
		# Start FPGA state machine
		dev.SetWireInValue(0x00, 1)
		dev.UpdateWireIns()
		dev.SetWireInValue(0x00, 0)
		dev.UpdateWireIns()
		
		newval = 0
		oldval = 0
		NumOfTrace = 0
		for interval in thehardwarevalues:
			if interval[1] == 1 and interval[3] == 1:
				newval = 1
				if newval != oldval:
					NumOfTrace += 1
			oldval = newval
		
		if NumOfTrace > 0:
			return 1, save_switch
		else:
			return 0, 0
			
	elif autostart == 1:
		TIME_STOP = time.time()
		return TIME_STOP-TIME_START
	
# Subroutine 3: Acquire Data from the FPGA
def Acquire(T, SeqFolderName='', SeqRunName='michael', save=0):
	# Get data from FPGA
	print('Waiting for trigger!')
	status = 'wait'
	while status == 'wait':
		dev.UpdateTriggerOuts()
		if dev.IsTriggered(0x60, 0x01) == True:
			status = 'grab data'
			print("FPGA finished recording, ready to pipe out data!")
	if status == 'grab data':
		for block in range(N_blocks):
			dev.ReadFromPipeOut(0xA0 + block, data_byt[block])
	dev.SetWireInValue(0x06, 1)
	dev.UpdateWireIns()
	dev.SetWireInValue(0x06, 0)
	dev.UpdateWireIns()
	
	# Convert the data from the PipeOut to string data
	if save == 1:
		print(SeqFolderName)
		if SeqFolderName.strip() == '':
			SeqFolderName = "PhotonCounter"
		date_dir = datetime.datetime.now().strftime("%Y/%m/%d/")
		full_dir = DATA_DIR+date_dir+SeqFolderName+"/"
		
		if not os.path.exists(full_dir):
			os.makedirs(full_dir)
		
		data_byt_np = np.array(data_byt)
		data_byt_np = np.reshape(data_byt_np, (2048*32))
		
		f = open(full_dir+"PT"+SeqRunName+'.bin', 'wb')
		for ii in range(N_blocks):
			f.write(data_byt[ii])
		f.close()
		
		print('Finish saving the data!')
	return 1

## MAIN FUNCTION
if __name__ == '__main__': 
  # Start the FPGA
  CLK_freq = Config_FPGA()
  
  server.Listen()
  
  while True:
    clientSocket, addr = server.sock.accept()
    
    while True:
      
      msg = recv_msg(clientSocket) # Receive a command
      msg = printGrayDate(msg)    # Print the full command  as received
      if msg != None:
        tokens = msg.strip().split(' ', 2)  # Isolate the command in case it contains extra info
        command = tokens[0]
      
      if command == "RUN":  # Run the sequence (if we've already received it)
        if server.seq == None:
          printError('Run() failed. Sequence has not been imported!')
          send_msg(clientSocket, server.ReplyHeader() + 'Run() failed. Sequence has not been imported!')
          break
        else:
          time_taken = RunServer(server.seq, 1)
          success = time_taken
    
        time_taken = '%.2f' % success
        send_msg(clientSocket, server.ReplyHeader() + 'Successfully ran sequence (' + str(time_taken) + ' seconds).')
        break
        
      if command == "QUEUE":  # Run the sequence (if we've already received it)
        if server.seq == None:
          printError('Queue() failed. Sequence has not been imported!')
          send_msg(clientSocket, server.ReplyHeader() + 'Queue() failed. Sequence has not been imported!')
          break
        else:
          try:
            acquire_data, save_data = RunServer(server.seq, autostart=0)
            # print "FPGA initiated!"
            send_msg(clientSocket, server.ReplyHeader() + 'Sequence has been queued... Trigger it whenever!')
            if acquire_data == 1:
              e = Acquire(CLK_freq, server.seq.foldername, server.seq.runname, save_data)
              # e = Acquire(CLK_freq, server.seq.foldername, server.seq.runname, 1)
          except:
            printError("Failed to acquire and save data!")
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
        
      else:
        reply = 'Unexpected command'
        send_msg(clientSocket, server.ReplyHeader() + reply)
        break
   
    clientSocket.close()
