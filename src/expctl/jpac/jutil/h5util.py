import os
import h5py
import inspect
import numpy as np

def __init__():
	__all__ = ['getf', 'hdf5dat']

######################################################################
#                           Helper functions                         #
######################################################################
def getf(path):
	dirs = os.listdir(path)
	h5f = []
	for f in dirs:
		if f.endswith('.hdf5'):
			h5f.append(path+'/'+f)
	return h5f

######################################################################
#                    HDF5 file manipulation class                    #
######################################################################
class hdf5dat:
	def __init__(self, fname, read_only=False):
		if not read_only:
			self.f = h5py.File(fname, 'r+')
		else:
			self.f = h5py.File(fname, 'r')
		self.infogrp   = self.f['/info']
		self.seqname   = self.f['/info/seq_name']
		self.mv_static = self.f['/info/MV_static']
		self.mv_loop   = self.f['/info/MV_loop']
		self.mvs_name  = self.mv_static['Name']
		self.mvl_name  = self.mv_loop['Name']

	def get_runname(self):
		return list(self.f['/data'].keys())

	def get_data(self, runname):
		dat_arr = self.f['/data/'+runname]
		if dat_arr.shape[0] == 1:
			return dat_arr[0]
		else:
			return dat_arr

	def get_datas(self, keys=None):
		if keys == None:
			keys = list(self.f['/data'].keys())

		names = []
		dats  = []
		for key in keys:
			names.append(key)
			dats.append(self.get_data(key))
		names = np.array(names)
		dats  = np.array(dats)

		return names, dats

	def get_MV_val(self, MVname=None, runname=None):
		start = 0
		if runname == None:
			runname = self.mv_static.dtype.names
			start = 1
		if MVname != None:
			MVname = np.where(self.mvs_name==MVname)[0][0]
		vals = self.mv_static[runname][MVname]
		try:
			return list(vals)
		except:
			return vals

	def get_fitparm(self, name):
		popt = self.f['/Fitting/'+name+"_popt"]
		try:
			pcov = self.f['/Fitting/'+name+"_pcov"]
		except:
			pcov = None
		return np.array(popt), np.array(pcov)

	def save_fitparm(self, name, popt, pcov=None, func=None):
		popt = np.array(popt)
		pcov = np.array(pcov) if pcov!=None else None
		# Check if fitting group exists
		if not 'Fitting' in list(self.f.keys()):
			fitgrp = self.f.create_group('Fitting')
		else:
			fitgrp = self.f['/Fitting']
		# Check if fitting result already exist. If so, will delete the old item
		# and create a new one. No warning will show
		if name+"_popt" in list(fitgrp.keys()):
			fitgrp.__delitem__(name+"_popt")
		if name+"_pcov" in list(fitgrp.keys()):
			fitgrp.__delitem__(name+"_pcov")
		fitpopt = fitgrp.create_dataset(name+"_popt", data=popt)
		if (pcov!=None):
			fitpcov = fitgrp.create_dataset(name+"_pcov", data=pcov)
		# Add function variable name to the dataset attribute
		if func != None:
			args = inspect.getargspec(func)[0]
			fitpopt.attrs['FitFunc'] = func.__name__
			for ii, arg in enumerate(args[1:]):
				fitpopt.attrs[str(arg)] = ii

	def get_info(self, info_name):
		return self.infogrp[info_name]
	
	def save_info(self, info_name, info_array):
		# Check if dataset
		if info_name in list(self.infogrp.keys()):
			self.infogrp.__delitem__(info_name)			
		info_array = np.array(info_array)
		self.infogrp.create_dataset(info_name, data=info_array)

	def get_loop(self, runname, repetition=1):
		mvname = self.mv_loop['Name']
		mvarr = self.mv_loop[runname]
		jmin, jmax = mvarr[:2]

		vals = []
		for j in range(jmin, jmax+1):
			pair = []
			for ii, var in enumerate(mvarr[2:]):
				eval('val='+var)
				pair.append(val)
			vals.append(pair)

		


