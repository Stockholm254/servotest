from sequencer.sequence import Sequence
import transformations as tran

###################################################################################################
###    ALL CHANNELS/SEQS ARE DEFINED HERE, AS ARE FEW ROUTINES THAT CRUNCH THEM (@ bottom)      ###
###################################################################################################

#=======================================Sequence Definitions=========================================
#FIRST DECLARE ALL SEQUENCES into the all_sequences array, and then give them names for easier assignment!
 
all_sequences = ([
  Sequence("Digital sequence", host='192.168.1.105', port=60615, max_channels=32),
  ])
digital_seq1, = all_sequences # WE DO IT IN THIS ORDER SO THAT ONE CANNOT GET AWAY WITH CREATING A NAMED SEQUENCE WHICH IS NOT IN THE ARRAY OF ALL SEQUENCES!!

MasterSequence = digital_seq1 #THIS IS THE SEQUENCE THAT PHYSICALLY TRIGGERS THE OTHERS!
SEQUENCES_TO_GRAPH = [digital_seq1]
#=======================================Channel Definitions=========================================
#NEXT ADD ALL OF THE CHANNELS TO THEM! ##Note: the name in quotes must have 1 < length < 31

#Digital card
ScopeTrig = digital_seq1.newChannel(2,  "Scope Trigger",        steady_state_value=0, max_value=1, graph=1, system='Debug')
Digi_test = digital_seq1.newChannel(31, "Digital Test Channel", steady_state_value=0, max_value=1, graph=1, system='Debug')

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
