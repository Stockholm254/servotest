import numpy as np
from .load_file import *

fnames = check_file(data_dir, fmt='bin')

def bin2dat(fname):
	spcm_ind = [1, 0, 0, 0, 0, 0, 0, 0]

	datas = [[],[]]

	# Read the file
	f = open(fname, 'rb')
	bin_data = bytearray(f.read())

	for ii in range(len(bin_data)/4):
		if bin_data[4*ii+3] != 0x00:
			chan = '{0:08b}'.format(bin_data[ii*4+3])[::-1]
			tt = ['{0:08b}'.format(bin_data[4*ii+jj]) for jj in range(0, 3)][::-1]
			tt = int(''.join(tt), 2)
			
			for cc in range(len(chan)):
				if chan[cc] == '1':
					ind = spcm_ind[cc]
					datas[ind].append(tt)
		else:
			break

	return np.array(datas)