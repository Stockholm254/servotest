#!/usr/bin/python
import sys
import math
import time
import numpy as np
from .ServerClass import Server, logger
from pathlib import Path
from .util.SequenceProcessor import *
from .util import ok
#from .dds_common import *

DIR_BITFILE = Path(__file__).parent/"FPGA_bit_file/"

RUNMODE=1
LOADMODE=0
UPDATERAM=0 #GLOBAL VARIABLE DETERMINING WHETHER OR NOT WE SHOULD UPDATE THE DDS RAM EVERY CYCLE. 0 MEANS YES, 1 MEANS NO

RAMWRITERESET=0x41       #triggerIN address of the ram_write reset-- sets the ram write address to zero! We always use trigger 0
DDSRESET=0x40         #triggerIN address of the DDS reset-- UNCLEAR IF THIS JUST STARTS THE SEQUENCE OVER WAITING FOR A TRIGGER (and going to I/F value), OR RESETS THE DDS TOO, OR WHAT?! We always use trigger 0
SEQDONEFLAG=0x60       #triggerOUT address for flag telling us that the each channel has run through its sequence at least once since last reset trigger

#code1 = "C:/Users/simonlab/Documents/Lukas/Python/Py3Test/Control_Suite_X/servers/FPGA_bit_file/DDS_freq_out_ExtCLK.bit"
code1 = str(DIR_BITFILE/"DDS_freq_out_ExtCLK.bit")
logger.info(f"Using bitfile {code1}")

jdebug=0
FPGAclock = 25.0 #MHz is the default, but we'll get the actual frequency from the FPGA pll itself!
FPGAsn = '14290008UX' #This must match the S/N of the FPGA inside the PDH DDS box. Can find the serial number via the Opal Kelly FrontPanel interface.


def RunServer(server, seq, dev, loadorrun, autostart=1):

	#CONSTANTS TELLING US ABOUT SYSTEM CONFIGURATION
	numDDS = 4
	statesPerCount = 2.0 #set by the state machine in the verilog code used to generate dds.bit. This is how many cycles needed to update each channel in memory
							 #the frequency outputting is separate!
	def countRate():  #NEEDS TO BE A FUNCTION SO THAT WE CAN GET THE CLOCK FREQUENCY FROM THE FPGA ITSELF RATHER THAN USING THE ABOVE VALUE
		return (FPGAclock/statesPerCount) #counts per us

	sysclock = ((3.5)*10**9) #3.5GHz, used for actually outputting signals!
	
	MAXDATA=18*1024 #The Maximum Amount of data that we can store in the memory!
	MAXRAMPS=511    #This should be equivalent! The maximum number of ramps we can store in memory for a given DDS!
	
	ADDRESSNumRAMPS=0           #address offset of the number of ramps for the wireINs
	ADDRESSStartFreqLOWER=1     #address offset of the lower two-bytes of the start frequency for the wireINs
	ADDRESSStartFreqUPPER=2     #address offset of the upper two-bytes of the start frequency for the wireINs
	ADDRESSPDHFreqSTEP=3        #address offset of the upper two-bytes of the PDH frequency step for wireINs
	ADDRESSPDHFreqHalfRANGE=4   #address offset of the upper two-bytes of the PDH frequency half-range for wireINs
	ADDRESSPDHStepRate= 5       #address offset of the upper two-bytes of the PDH step rate


	ADDRESSStepList=0     #address offset of the four-byte steps for the pipeINs
	ADDRESSFreqLList=1       #address offset of the lower four-bytes of the slopes for the pipeINs
	ADDRESSFreqHList=2     #address offset of the upper four-bytes of the slopes for the pipeINs

	NumStepBuffers=[] #the array of output buffers for the arrays containing the output frequencies on each channel, to be sent over the 8-bit pipe!
	StepSizeLowBuffers=[] #the array of output buffers for the arrays containing the lower 32, to be sent over the 8-bit pipe!

	#for debugging purposes
	freq1 = bytearray(2)
	freq2 = bytearray(2)
	count = bytearray(2)
	
	#A FEW HELPER FUNCTIONS
	def ConvertTimeToCount(ttime): #time in microseconds, converted to FPGA counts. No longer need to offset by the current DDS
		count = int(ttime*countRate())
		return count

	def ConvertFreqToFTW(freq): #convert freq in hz to frequency tuning word (FTW) for DDS
		return freq*(2**32)/sysclock

	def ExtractLowerandUpper16Bits(numIN): #splits a 32bit number into lower and upper 16 bit chunks
		num=int(numIN)
		numLower=num&0x0000ffff
		numUpper=num>>16
		return [numLower,numUpper]

	def ExtractLowerandUpper32Bits(numIN): #splits a 64bit number into lower and upper 32 bit chunks
		num=int(numIN)
		numLower=num&0x00000000ffffffff
		numUpper=num>>32
		return [numLower,numUpper]
		
	def ExtractLower32Bits(num): #grab the lower 32bits of a 32 bit number
		nL,nU=ExractLowerandUpper32Bits(num)
		return nL
	
	def ExtractUpper32Bits(num): #grab the upper 32bits of a 64 bit number
		nL,nU=ExractLowerandUpper32Bits(num)
		return nU
		
	def getBytes(numIN,numbytes):#extracts the lowest numbytes bytes from a number, starting with the lowest and working upwards
		num=int(numIN)
		return [(num>>(8*jj))&0xff for jj in range(0,numbytes)] #AMAZINGLY, THIS WORKS PROPERLY FOR THE TWOS COMPLEMENT REPRESENTATION OF NEGATIVE NUMBERS!

	def ConvertTupletoCountsandFTWs(tuplein): #converts ramp tuple (T0,f0,T1,f1) in microseconds and Hz to counts and FTWs for FPGA and DDS respectively
		return [ConvertTimeToCount(tuplein[0]),ConvertFreqToFTW(tuplein[1]),ConvertTimeToCount(tuplein[2]),ConvertFreqToFTW(tuplein[3])]

	def ConvertSeqtoCountsandFTWs(seqin): #converts full sequence from microseconds and Hz to counts and FTWs
		seqout=[];
		for i in range(len(seqin)):
			seqout.append(ConvertTupletoCountsandFTWs(seqin[i]))
		return seqout

	def ConvertSeqToNumStepsandStepSize(seqin):   #takes in a full sequence in counts and FTWs and converts it to numbers of steps and step sizes,
													#it even multiplies by 2**32 before converting step-size to an integer, as we need extra resolution!
		seqout=[];
		for ii in range(len(seqin)):
			timesteps=seqin[ii][stopTIME]-seqin[ii][startTIME]
			freqsteps=seqin[ii][stopVAL]-seqin[ii][startVAL]
			if timesteps==0:
				print("ERROR: TIMESTEP SHOULD BE LARGER THAN ZERO! THIS SHOULD NEVER HAPPEN!")
				input("PRESS ANY KEY TO CRASH! =D")
			slope=int(float(2**32)*float(freqsteps)/float(timesteps)) #shouldn't matter if we convert to int or long, but just in case we'll convert to long!
			seqout.append([timesteps,slope])
		return seqout


	FinalSeqs=[] #Final list of ramps (each composed of # of steps, & slope) for each channel
	NumRamps=[]  #Total Number of ramps for each channel

	#INITIAL/FINAL FREQUENCIES in various forms:
	IFfreqsHz = [];       #In Hz
	IFfreqsFTW = [];      #As DDS Frequency Tuning Words (FTWs)
	IFfreqsFTW_lower16=[];  #As lower...
	IFfreqsFTW_upper16=[];  #and upper 16 bits of FTW (for sending over FPGA wires which are 16 bits each)

		#PDH RAMPING CONTROL
	PDHFreqStepHz=[];              #Frequency Step per cycle, in Hz
	PDHFreqStep=[];                #Frequency Step per cycle, as DDS FTW
	PDHFreqStep_upper16=[];        #Frequency Step per cycle, upper 16bits
	PDHFreqHalfRangeHz=[];         #Frequency Sweep half range, in Hz
	PDHFreqHalfRange=[];           #Frequency Sweep half range, as DDS FTW
	PDHFreqHalfRange_upper16=[];   #Frequency Sweep half range, upper 16bits
	PDHStepRate = [];              #


	#These are not needed for profile mode, but don't hurt anyone by sitting here.
	currPDHStepHz       = 4908534 #Hardcoded in Verilog # seq.allChannels[4].GetHardwareSSV() #THIS DOES NOTHING NOW
	currPDHHalfRangeHz  = 10000000 #seq.allChannels[5].GetHardwareSSV() 
	PDHStepRate         = 0.01*10**-6 # Hardcoded in Verilog # seq.allChannels[6].GetHardwareSSV()  #THIS DOES NOTHING NOW#.01*10**-6 #.01 microseconds
	PDHStepRateValue = int(PDHStepRate*10**2) #The number the DDS wants is the time in units of 0.01 us and number coming in is in us
		
	## Convert seq to get all the times and frequencies, and save to buffers to pass to FPGA Block RAM
	for chan in seq.allChannels:
		if chan == None:
			continue
		if chan.chanid >= 4: #Assume the first four channels of dds_PDH sequence in allchannels.py are the four dds frequencies
			continue
		#First do the data conversions on the I/F value
		ssvalHz=chan.GetHardwareSSV() #steady_state_value
		ssvalFTW=ConvertFreqToFTW(ssvalHz)
		ssvalFTW_lowerbits,ssvalFTW_upperbits=ExtractLowerandUpper16Bits(ssvalFTW)

		IFfreqsHz.append(ssvalHz);
		IFfreqsFTW.append(ssvalFTW);
		IFfreqsFTW_lower16.append(ssvalFTW_lowerbits)
		IFfreqsFTW_upper16.append(ssvalFTW_upperbits)

		#Next do the data conversions on the full sequence, inserting the I/F value
		convertedSeq=ConvertSeqtoCountsandFTWs(chan.GetHardwareValues()) #values)
		fullSeq=GenerateFullSeq(convertedSeq,ssvalFTW)
		print(ssvalHz, ssvalFTW, fullSeq)

		#fullseq is a list of ramps in time (counts) with a FTW at each endpoint of each ramp. The first interval starts at time zero.
		#next we need to convert this into a list of ramps, in clock cycles and slopes. For now the slopes will be a signed float FTW/count, but eventually we will need to multiply by 2**32 and round it
		#finally we'll need to figure out how many total ramps there were!
		StepsandSlopeSeq=ConvertSeqToNumStepsandStepSize(fullSeq)
		FinalSeqs.append(StepsandSlopeSeq)
		NumRamps.append(len(StepsandSlopeSeq))
		
		# ########################################################################
		#Now deal with the PDH control:
		# currPDHStepHz=4.0*(10**6);      #4 MHz step size
		# currPDHHalfRangeHz=10*(10**6); #10 MHz full range 
		
		currPDHStepFTW=ConvertFreqToFTW(currPDHStepHz)
		currPDHStep_lower16,currPDHStep_upper16=ExtractLowerandUpper16Bits(currPDHStepFTW)
		PDHFreqStepHz.append(currPDHStepHz)
		PDHFreqStep.append(currPDHStepFTW)
		PDHFreqStep_upper16.append(currPDHStep_upper16)
		
		currPDHHalfRangeFTW=ConvertFreqToFTW(currPDHHalfRangeHz)
		currPDHHalfRange_lower16,currPDHHalfRange_upper16=ExtractLowerandUpper16Bits(currPDHHalfRangeFTW)
		PDHFreqHalfRangeHz.append(currPDHHalfRangeHz)
		PDHFreqHalfRange.append(currPDHHalfRangeFTW)
		PDHFreqHalfRange_upper16.append(currPDHHalfRange_upper16)
		
	
	## Program the FPGA Block RAM      
	if(loadorrun==LOADMODE):
		print("The number of Channels is: " + str(len(IFfreqsFTW_lower16)))
		#reset RAMWRITE pointer to prepare to load data
		dev.ActivateTriggerIn(RAMWRITERESET, 0) # ram_reset
		global UPDATERAM
		UPDATERAM=0 #for debugging, we can set it to NOT update the sequence in RAM by commenting out this line so it only sets the RAM once!
		if (UPDATERAM==0):
			UPDATERAM=1;
			#time.sleep(0.2);
			#set initial/final frequencies and number of steps, using wireINs
			for j in range(numDDS):
				# dev.SetWireInValue(0x03+5*j+ADDRESSStartFreqLOWER,   IFfreqsFTW_lower16[j])
				# dev.SetWireInValue(0x03+5*j+ADDRESSStartFreqUPPER,   IFfreqsFTW_upper16[j])
				# dev.SetWireInValue(0x03+5*j+ADDRESSNumRAMPS,         NumRamps[j])
				# dev.SetWireInValue(0x03+5*j+ADDRESSPDHFreqSTEP,      PDHFreqStep_upper16[j])
				# dev.SetWireInValue(0x03+5*j+ADDRESSPDHFreqHalfRANGE, PDHFreqHalfRange_upper16[j])
				
				dev.SetWireInValue(0x03+6*j+ADDRESSStartFreqLOWER,   IFfreqsFTW_lower16[j])
				dev.SetWireInValue(0x03+6*j+ADDRESSStartFreqUPPER,   IFfreqsFTW_upper16[j])
				dev.SetWireInValue(0x03+6*j+ADDRESSNumRAMPS,         NumRamps[j])
				dev.SetWireInValue(0x03+6*j+ADDRESSPDHFreqSTEP,      PDHFreqStep_upper16[j])
				dev.SetWireInValue(0x03+6*j+ADDRESSPDHFreqHalfRANGE, PDHFreqHalfRange_upper16[j])
				dev.SetWireInValue(0x03+6*j+ADDRESSPDHStepRate,      PDHStepRateValue)
				
				if jdebug==1: print("Num Ramps on Channel " + str(j) + " is " + str(NumRamps[j]))
				if jdebug==1: print("Upper 2 Bytes are: " + str(IFfreqsFTW_upper16[j]) + ", and Lower 2 Bytes are: " + str(IFfreqsFTW_lower16[j]))
			dev.UpdateWireIns()
			for i in range(numDDS):
				bufSteps=bytearray()
				bufFL=bytearray()
				bufFH=bytearray()
				for j in range(NumRamps[i]):
					if (NumRamps[i]>MAXRAMPS):
						print("TOO MANY RAMPS! GET A BIGGER FPGA!!")
					#extract the number of steps for each ramp, make a new list of these!
					if jdebug==1: print("Channel#:"+str(i)+", event#: "+str(j)+", numsteps: "+str(FinalSeqs[i][j][0])+", stepsize:" +str(FinalSeqs[i][j][1]))
					bufSteps.extend(getBytes(FinalSeqs[i][j][0],4))
					freqbytes=getBytes(FinalSeqs[i][j][1],8) #THIS WILL PROPERLY EXTRACT NEGATIVE NUMBERS IN TWOS COMPLEMENT FORM! HURRAH! FPGA CAN IGNORE IT NOW!
					bufFL.extend([freqbytes[k] for k in range(0,4)])
					bufFH.extend([freqbytes[k] for k in range(4,8)])
				#write sequence buffer to FPGA
				if jdebug==1: print("bufSteps,bufFH,bufFL")
				if jdebug==1:
					for k in range(len(bufSteps)):
						print(bufSteps[k],bufFH[k],bufFL[k])
				
				dataLength0=dev.WriteToPipeIn(0x80+3*i+ADDRESSStepList,bufSteps)
				dataLength1=dev.WriteToPipeIn(0x80+3*i+ADDRESSFreqLList,bufFL)
				dataLength2=dev.WriteToPipeIn(0x80+3*i+ADDRESSFreqHList,bufFH)
				if ((dataLength0*8>MAXDATA)|(dataLength1*8>MAXDATA)|(dataLength2*8>MAXDATA)):
					print("Too much data. You tried to send " + str(data1*8) + " bits but 18Kb is the max.")
		
		#activate dds reset
		if jdebug==1: dev.UpdateWireOuts(); print("ep22: " + str(dev.GetWireOutValue(0x22)))
		if jdebug==1: print("resetting")
		dev.ActivateTriggerIn(DDSRESET, 0) # RESET FPGA to initial state & AWAIT TRIGGER
		dev.UpdateWireOuts();
		if jdebug==1: print("ep22: " + str(dev.GetWireOutValue(0x22)))
		if autostart == 1:
			print("NOT SUPPORTED! YOU MUST PROVIDE A HARDWARE TRIGGER!")
			#dev.ActivateTriggerIn(0x40, 2) #software FPGA start-- NO LONGER SUPPORTED!
		else:
			print("hardware trigger mode!")
		
		return 0
	else: #RUNMODE
		TIME_START = time.time()
		logger.debug("waiting for Trigger...")

		while(True):
			dev.UpdateTriggerOuts()
			dev.UpdateWireOuts()
			if(dev.IsTriggered(SEQDONEFLAG, 0x01)): #wait for sequence to finish!
				break
			if jdebug==1: print("ep22: " + str(dev.GetWireOutValue(0x22)))
		#for debugging purposes -- THESE NUMBERS DONT MEAN MUCH RIGHT NOW!
		logger.debug("Done waiting for trigger!")
		dev.UpdateWireOuts()
		freq1 = dev.GetWireOutValue(0x20) 
		freq2 = dev.GetWireOutValue(0x21)
		count1 = dev.GetWireOutValue(0x22) 
		count2 = dev.GetWireOutValue(0x23)
		if jdebug==1: print("Freq1: " + str(freq1))
		if jdebug==1: print("Freq2: " + str(freq2))
		if jdebug==1: print("Count1: " + str(count1))
		if jdebug==1: print("Count2: " + str(count2))

		TIME_STOP = time.time()
		return TIME_STOP-TIME_START

class DDSServer(Server):

	def cmd_queue(self):
		if self.seq is None:
			logger.error('QUEUE failed. Sequence has not been imported!')
			self.send_msg(self.ReplyHeader() + 'QUEUE failed. Sequence has not been imported!')
		else:
			RunServer(self, self.seq, dev, LOADMODE, autostart=0)
			logger.debug("DDS Loaded")
			self.send_msg(self.ReplyHeader() + 'Sequence has been queued... Trigger it whenever!')
			ret = RunServer(self, self.seq, dev, RUNMODE, autostart=0)
			logger.debug("DDS Qeued")

	def run(self):
		RunServer(self, self.seq, dev, LOADMODE)
		logger.debug("DDS Loaded")
		server.send_msg(server.ReplyHeader() + 'Sequence has been queued... Trigger it whenever!')
		ret = RunServer(self, self.seq, dev, RUNMODE)
		logger.debug("DDS ran")
		return ret
		

	def plotdata(self):
		return [0,], [0,]

if __name__ == '__main__':

	#instantiate okC structure
	dev = ok.okCFrontPanel()
	pll = ok.okCPLL22150()
	#print 'Connecting to FPGA...'  + ('success' if dev.OpenBySerial("")==0 else 'failure')
	logger.info('Connecting to PDH FPGA S/N '+FPGAsn+'...'  + ('success' if dev.OpenBySerial(FPGAsn)==0 else 'failure'))
	logger.info('Getting FPGA PLL Eeprom Config...'  + ('success' if dev.GetEepromPLL22150Configuration(pll)==0 else 'failure'))
	logger.info('Setting FPGA PLL Config to Eeprom vals...'  + ('success' if dev.SetPLL22150Configuration(pll)==0 else 'failure'))
	#FPGAclock=float(pll.GetOutputFrequency(0))
	#Configure FPGA with bit code
	logger.info('Loading Bitfile...' + ('success' if dev.ConfigureFPGA(code1)==0 else 'failure'))
	logger.info('FPGA Clock Frequency: ' + str(FPGAclock) + ' MHz (set in server)')

	dev.ActivateTriggerIn(DDSRESET, 0) #RESET DDS
	dev.ActivateTriggerIn(RAMWRITERESET, 0) #RESET RAM

	message = """
	===============================================
	==      DDS Profile Frequency Out Server     ==
	==        for FPGA with External Clock       ==
	===============================================
	"""

	server = DDSServer("DDS_PDH", 60618, message=message)
	server.main_loop()

