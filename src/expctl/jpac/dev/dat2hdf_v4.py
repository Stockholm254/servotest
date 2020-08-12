import os
import inspect
import numpy as np
import h5py as h5
from readmv import *
from load_file import *

def __init__():
	__all__     = ['dat2hdf5', 'dats2hdf5', 'append2hdf5']
	__version__ = 4.0

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
	infogrp.create_dataset('seq_name',  data=[seqname])
	infogrp.create_dataset('MV_static', data=smvs)
	infogrp.create_dataset('MV_loop',   data=lmvs)
	if save_raw:
		rawdataset = datgrp.create_dataset('raw_data', data=rdata, dtype='float')
	pdataset = datgrp.create_dataset('processed_data', data=pdata, dtype='float')

def dats2hdf5(datadir, pmethod, arg, save_raw=False):
	hdffname = datadir+'/'+os.path.split(datadir)[-1]+'.hdf5'

	# Create HDF5 file
	f = h5.File(hdffname, 'w')
	infogrp = f.create_group("info")
	datgrp  = f.create_group("data")
	
	# Go through each sub-folder
	subdirs = [subdir for subdir in os.listdir(datadir)]
	for ii, subdir in enumerate(subdirs):
		if os.path.isdir(datadir+'/'+subdir):
			# Write data
			arg[0] = datadir+'/'+subdir
			rdat, pdat = pmethod(*arg)
			if save_raw:
				datgrp.create_dataset(subdir+'_raw', data=rdat)
			datgrp.create_dataset(subdir, data=pdat)
	
	# Get experiment infos from all sub-directory
	seqnames, smvss, lmvss = get_infos(datadir)

	# Write HDF file
	infogrp.create_dataset('seq_name',  data=seqnames)
	infogrp.create_dataset('MV_static', data=smvss)
	infogrp.create_dataset('MV_loop',   data=lmvss)

def append2hdf5(datadir, subdirs, hdf, pmethod, arg, save_raw=False):
	# Open the HDF5 file
	f = h5py.File(datadir+'/'+hdf, 'r+')
	datgrp = f['/data']

	# Go through the subdirectories
	for ii, subdir in enumerate(subdirs):
		if os.path.isdir(datadir+'/'+subdir):
			# Write data
			arg[0] = datadir+'/'+subdir
			rdat, pdat = pmethod(*arg)
			if save_raw:
				datgrp.create_dataset(subdir+'_raw', data=rdat)
			datgrp.create_dataset(subdir, data=pdat)

	'''TODO: Rewrite the info (need to be replaced by append)'''
	# Get infos from all sub-directory
	seqnames, smvss, lmvss = get_infos(datadir)
	# Write HDF file
	infogrp.create_dataset('seq_name',  data=seqnames)
	infogrp.create_dataset('MV_static', data=smvss)
	infogrp.create_dataset('MV_loop',   data=lmvss)

##########################
##   Helper functions   ##
##########################

def process_info(seqnames, method, arg):
	method_name = method.__name__
	method_args = inspect.getargspec(method)[0]

