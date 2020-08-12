import numpy as np

#####################################################
###   Binvary Data to Numerical Data Convertion   ###
###           with ~8ns Time Resolution           ###
#####################################################
def bin2dat_lr(fname):
	# This index book acounts for different line driver setup
	spcm_ind = [1, 0]

	datas = [[],[]]

	# Read the file
	f = open(fname, 'rb')
	bin_data = bytearray(f.read())

	for ii in range(len(bin_data)/4):
		if bin_data[4*ii+3] != 0x00:
			chan = '{0:08b}'.format(bin_data[ii*4+3])[::-1]
			time = ['{0:08b}'.format(bin_data[4*ii+jj]) \
					for jj in range(0, 3)][::-1]
			time = int(''.join(time), 2)
			
			for cc in range(2):
				if chan[cc] == '1':
					ind = spcm_ind[cc]
					datas[ind].append(time)
		else:
			break

	return np.array(datas)

def bin2dat_4c(fname):
    """
    Convert binary data to numerical data for 4 channels

    Parameters
    ----------
    fname: str
        Full file name with path. 

    Returns
    -------
    datas: list
        FPGA clock cycle of the events
    """
    datas = [[], [], [], []] # data array for storing the time
    chan_num = 4

    f = open(fname, 'rb') # open binary file
    data_bin = bytearray(f.read()) # read all data

    # Loop over all events
    # Each event uses 4 byte: 1 for channel identification and 3 for time
    # Event data format: time byte 3, time byte 2, time byte 1, channels
    # Need to reverse the order of the 3 time byte. The bits is in order within
    # each time byte and should NOT be reversed. 
    for ii in range(len(data_bin)/4):
        if data_bin[4*ii+3] != 0x00:
            chan = '{0:08b}'.format(data_bin[ii*4+3])[::-1]
            time = ['{0:08b}'.format(data_bin[4*ii+jj]) for jj in range(0, 3)][::-1]
            time = int(''.join(time), 2) # Convert time to base 10 number
            
            for cc in range(chan_num):
                if chan[cc] == '1': # If channel is triggered, append to the data
                    datas[cc].append(time)

        else: # Stop the loop if no channel is triggered to save time
            break
    return np.array(datas)
	

#####################################################
###   Binvary Data to Numerical Data Convertion   ###
###           with Super Time Resolution          ###
#####################################################
def sub_int(c0, c1, clk): # Calculate sub interval time.
	if (c0=='1000') and (c1=='0111'):
		return clk*4+3
	elif (c0=='1100') and (c1=='0011'):
		return clk*4+2
	elif (c0=='1110') and (c1=='0001'):
		return clk*4+1
	elif (c0=='1111'):
		return clk*4
	else:
		return -1

def bin2dat_hr(fname):
	"""
	Convert binary data to numerical data
	This apply to the super time resolution setup with 4 photon channel 
	associate to each SPCM.

	Parameters
	----------
	fname: str
		File name with directory.
	
	Returns
	-------
	dat: list
		FPGA clock cycle of the events (in 0.01 clock cycle unit).
	"""

	# Load data from binary file into a byte array
	f = open(fname, 'rb') # Open file
	bin_data = bytearray(f.read()) # Read all bytes
	f.close() # Close the file

	dat = [[], []] # Output data
	for ii in range((len(bin_data)-1)/4): # Loop over binary data
		if bin_data[4*ii+3] != 0x00:
			# Get event for current and next clock cycle
			chan_0 = '{0:08b}'.format(bin_data[ii*4+3])[::-1]
			chan_1 = '{0:08b}'.format(bin_data[(ii+1)*4+3])[::-1]
			# ca0 = chan_0[::2]; cb0 = chan_0[1::2];
			# ca1 = chan_1[::2]; cb1 = chan_1[1::2];
			ca0 = chan_0[:4]; cb0 = chan_0[4:];
			ca1 = chan_1[:4]; cb1 = chan_1[4:];

			cyl = ['{0:08b}'.format(bin_data[4*ii+jj]) \
					for jj in range(0, 3)][::-1] # Current time byte
			cyl = int(''.join(cyl), 2) # Convert byte to int

			# Get sub-interval time for both SPCMs
			cyl_a = sub_int(ca0, ca1, cyl)
			cyl_b = sub_int(cb0, cb1, cyl)
			# Add to event list if the event is recorded in the corrected form
			# If not all channels are trigger, the event is disgarded
			if cyl_a!=-1: dat[0].append(cyl_a)
			if cyl_b!=-1: dat[1].append(cyl_b)
			
		else: # If the memory byte has no event, break the loop
			break

	return np.array(dat)




