import os
import numpy as np
import h5py as h5
from readmv import *
from SPCM_analysor.load_file import *

def dat2hdf5(datadir, avg_num, avg_axis):
	# Load MV information
	loopcodedir = datadir+'/MVs'
	for f in os.listdir(loopcodedir):
		if f.endswith('.txt'):
			MVfname = loopcodedir+'/'+f
	seqname, jrange, smvs, lmvs = readMV(MVfname)

	# Process the data
	rdata = load_files(check_file(datadir))
	pdata = avg_data(rdata, avg_num, avg_axis)

	# Create HDF5 file
	hdffname = datadir+'/'+os.path.split(datadir)[-1]+'.hdf5'
	f = h5.File(hdffname, 'w')
	# Create info group
	infogrp = f.create_group("info")
	seqnameset = infogrp.create_dataset('seq_name', data=[seqname])
	# Create static MV table
	smv_arr = []
	for smv in smvs:
		smv_arr.append((smv[0], smv[1]))
	smv_arr = np.array(smv_arr, dtype=[('Name', 'S50'), ('Value', 'float')])
	infogrp.create_dataset('MV_static', data=smv_arr)
	# Create loop MV table
	lmv_arr = []
	lmv_arr.append(('j_min', str(jrange[0])))
	lmv_arr.append(('j_max', str(jrange[1])))
	for lmv in lmvs:
		lmv_arr.append((lmv[0], lmv[1]))
	lmv_arr = np.array(lmv_arr, dtype=[('Name', 'S50'), ('Value', 'S100')])
	infogrp.create_dataset('MV_loop', data=lmv_arr)
	# Write data
	datgrp = f.create_group("data")
	rawdataset = datgrp.create_dataset('raw_data',       data=rdata, dtype='float')
	avgdataset = datgrp.create_dataset('processed_data', data=pdata, dtype='float')

if __name__ == '__main__':
	datadir = '/Users/ningyuanjia/Dropbox/code/2016_02_02-CavityShaking/MOTBiasY0.0'

	avg_num = 50
	avg_axis = 1

	dat2hdf5(datadir, avg_num, avg_axis)
