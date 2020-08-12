from sequencer.sequence import Sequence
import transformations as tran

###################################################################################################
###    ALL CHANNELS/SEQS ARE DEFINED HERE, AS ARE FEW ROUTINES THAT CRUNCH THEM (@ bottom)      ###
###################################################################################################

#=======================================Sequence Definitions=========================================
#FIRST DECLARE ALL SEQUENCES into the all_sequences array, and then give them names for easier assignment!

all_sequences = ([
  Sequence("Dummy sequence 1", host='192.168.1.105', port=60000, max_channels=32, seq_type="MASTER"),
  # Sequence("Dummy sequence 2", host='192.168.1.105', port=60001, max_channels=32),
  ])

# dummy_seq1, dummy_seq2 = all_sequences # WE DO IT IN THIS ORDER SO THAT ONE CANNOT GET AWAY WITH CREATING A NAMED SEQUENCE WHICH IS NOT IN THE ARRAY OF ALL SEQUENCES!!
dummy_seq1, = all_sequences # WE DO IT IN THIS ORDER SO THAT ONE CANNOT GET AWAY WITH CREATING A NAMED SEQUENCE WHICH IS NOT IN THE ARRAY OF ALL SEQUENCES!!

bright_sequences   = [dummy_seq1] #THIS IS THE SEQUENCES THAT CAN BE CHANGED IN THE STEADY STATE VALUES
# MonitorSequences   = Monitor_seq    #THIS IS THE SEQUENCE FOR MONITORING THE MACHINE STATUS!
MasterSequence     = dummy_seq1   #THIS IS THE SEQUENCE THAT PHYSICALLY TRIGGERS THE OTHERS!
# SEQUENCES_TO_GRAPH = [digital_seq1, analog_seq1, dds_freq_seq1, dds_freq_seq2, dds_PDH_freq_seq1] #This controls who is graphed!
SEQUENCES_TO_GRAPH = [dummy_seq1] #This controls who is graphed!

#=======================================Channel Definitions=========================================
#NEXT ADD ALL OF THE CHANNELS TO THEM! ##Note: the name in quotes must have 1 < length < 31

#Dummy card
d1_0 = dummy_seq1.newChannel(0,  "Dummy_0", steady_state_value=0, max_value=1, graph=1, system='sys_0')
d1_1 = dummy_seq1.newChannel(1,  "Dummy_1", steady_state_value=0, max_value=1, graph=1, system='sys_1')
d1_2 = dummy_seq1.newChannel(2,  "Dummy_2", steady_state_value=0, max_value=1, graph=1, system='sys_0')

# d2_0 = dummy_seq2.newChannel(0,  "d2_0", steady_state_value=0, max_value=1, graph=1, system='sys_0')
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
