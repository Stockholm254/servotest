#!/usr/bin/python
# -*- coding: utf-8 -*-
import operator

def __init__():
	return

# function for sorting the channels according to its catagory
def SortChan(all_seqs):
	_chans = []
	for seq in all_seqs: # Loop over all sequences
		for chan in seq.allChannels: # Loop over all channels
			if (chan!=None): # Check if the channel is being used
				if (chan.chantype!='Slave'):  # Check if it is slaved channel
					_chans.append(chan)
	_chans = sorted(_chans, key=operator.attrgetter('cat')) # Sort the channel list according to sub-system
	return _chans

# function for generating the sequence code setting the ssv
def GenSSVSeq(all_seqs):
	chan_sorted = SortChan(all_seqs) # Sort channels accoring to sub-system
	
	tab = "UNCAT"
	# Start writing the sequence file
	seq_txt  ="#!/usr/bin/python \n"
	seq_txt +="# -*- coding: utf-8 -*- \n\n"
	seq_txt +="#### Modifiable Variables #### \n"
	seq_txt +="# Note: values must be integers or floats. \n"
	for ii, _chan in enumerate(chan_sorted): # Loop over all sorted channels
		if _chan.cat!=tab: # Create a new tab
			seq_txt += "#Tab:"+_chan.cat+"\n"
			tab = _chan.cat
		seq_txt += _chan.VariableName()+' = '+str(_chan.ssv)+'\n' # MV line
	seq_txt += '#### End Modifiable Variables #### \n\n'
	seq_txt += 'dic = locals()\n\n'
	seq_txt += 'for seq in all_sequences:\n'
	seq_txt += '\tfor chan in seq.allChannels:\n'
	seq_txt += '\t\tif chan != None:\n'
	seq_txt += '\t\t\tif chan.chantype != \'Slave\':\n'
	seq_txt += '\t\t\t\tvalue = dic[chan.VariableName()]\n'
	seq_txt += '\t\t\t\tchan.SetSteadyStateValue(value)\n\n'

	'''TODO: USE PFI'''
	seq_txt += 'DDS_trig.Set([(0, 1, 10, 1), (10,0,10,0)])\n\n'

	return seq_txt
