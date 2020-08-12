import os
import numpy as np
import h5py as h5
from readmv import *
from load_file import *

def __init__():
	__all__ = ['dat2hdf5', 'dats2hdf5']

def dat2hdf5(datadir, pmethod, arg, save_raw=False):
	# Create HDF5 file
	hdffname = datadir+'/'+os.path.split(datadir)[-1]+'.hdf5'
	f = h5.File(hdffname, 'w')
	infogrp = f.create_group("info")
	datgrp  = f.create_group("data")

	# Load MV information
	loopcodedir = datadir+'/MVs'
	for f in os.listdir(loopcodedir):
		if f.endswith('.txt'):
			MVfname = loopcodedir+'/'+f
	seqname, jrange, smvs, lmvs = readMV(MVfname)

	# Process the data
	rdata, pdata = pmethod(*arg)

	# Write HDF5 file
	infogrp.create_dataset('seq_name', data=[seqname])
	infogrp.create_dataset('MV_static', data=smvs)
	infogrp.create_dataset('MV_loop',   data=lmvs)
	if save_raw:
		rawdataset = datgrp.create_dataset('raw_data', data=rdata, dtype='float')
	pdataset = datgrp.create_dataset('processed_data', data=pdata, dtype='float')

def dats2hdf5(datadir, pmethod, arg, save_raw=False):
	# Create HDF5 file
	hdffname = datadir+'/'+os.path.split(datadir)[-1]+'.hdf5'
	f = h5.File(hdffname, 'w')
	infogrp = f.create_group("info")
	datgrp  = f.create_group("data")

	# Go through each sub-folder
	subdirs = [subdir for subdir in os.listdir(datadir)]
	for subdir in subdirs:
		if os.path.isdir(datadir+'/'+subdir):
			# Write data
			arg[0] = datadir+'/'+subdir
			rdat, pdat = pmethod(*arg)
			if save_raw:
				datgrp.create_dataset(subdir+'_raw',   data=rdat)
			datgrp.create_dataset(subdir,   data=pdat)
	# Get infos from all sub-directory
	seqnames, smvss, lmvss = get_infos(datadir)

	# Write HDF file
	infogrp.create_dataset('seq_name',  data=seqnames)
	infogrp.create_dataset('MV_static', data=smvss)
	infogrp.create_dataset('MV_loop',   data=lmvss)

if __name__ == '__main__':
	datadir = '/Users/ningyuanjia/Dropbox/code/testdat/CavityShaking'

	avg_num = 50
	avg_axis = 1

	args = [datadir, avg_num, avg_axis]

	dats2hdf5(datadir, avgdat, args, save_raw=False)




