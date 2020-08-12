import os
import numpy as np
import h5py
from jload import *

#############################
###    Helper Function    ###
#############################
def GetH5Files(path):
	dirs = os.listdir(path)
	h5f = []
	for f in dirs:
		if f.endswith('.hdf5'):
			h5f.append(path+'/'+f)
	return h5f

def GetMVFileName(data_dir, fmt='txt'):
	MVfname = glob(os.path.join(data_dir, 'MVs', '*.txt'))[0]
	print("MV file name: \'"+MVfname+"\'")
	return MVfname

#############################
###    HDF5 file class    ###
#############################
class H5Data:
	def __init__(self, fname, read_only=False):
		if os.path.exists(fname+'.hdf5') and read_only: 
			self.f = h5py.File(fname+'.hdf5', 'r')
		elif os.path.exists(fname+'.hdf5') and not read_only:
			self.f = h5py.File(fname+'.hdf5', 'r+')
		elif not os.path.exists(fname+'.hdf5'):
			print("Crating a new file!")
			self.f = h5py.File(fname+'.hdf5', 'w')

	def _GetGrp(self, grp):
		if not grp in list(self.f.keys()): 
			self.f.create_group(grp)
		return self.f['/'+grp]

	def _AddDataSet(self, grp, dname, arr=[], attr=[]):
		host_grp = self._GetGrp(grp)
		if dname in host_grp:
			host_grp.__delitem__(dname)
		dset = self._GetGrp(grp).create_dataset(dname, data=arr)
		for _attr in attr:
			dset.attrs[str(_attr[0])] = _attr[1]
		return 1

	def AddDataSet(self, grp, dname, arr=[], attr=[]):
		self._AddDataSet(grp, dname, arr, attr)
		return 1

	def VLenDSet(self, grp, dname, d_shape, d_type=np.dtype('int32')):
		host_grp = self._GetGrp(grp)
		if dname in host_grp:
			host_grp.__delitem__(dname)
		dt = h5py.special_dtype(vlen=d_type)
		dset = host_grp.create_dataset(dname, d_shape, dtype=dt)
		return dset

	def AddRun(self, data_dir, pmethod, arg,
			   grp='data', runname='auto'): 
		
		"""Add a new data set to the file

		Parameters
		----------
		data_dir: str
			Directory of data that contains both actual data file and MV file
		
		pmethod: func
			Function for parsing the data files. The output of the function 
			must have data array and data array structure

		arg: dict
			Arguments for the parsing function.

		grp: str
			Name of the data group.

		runname: str
			Runname of the folder.

		Reture
		------
		None

		"""

		# Get runname
		runname = os.path.split(data_dir)[-1] if runname=='auto' else runname
		# Get processed data and data set info
		datas, datas_struct = pmethod(**arg)
		mvs = GetRunInfo(GetMVFileName(data_dir))
		# Write into HDF5 file
		for ii, data in enumerate(datas):
			dataset_name = runname+'_'+datas_struct[ii]
			dat_grp = self._GetGrp(grp)
			if dataset_name in dat_grp:
				dat_grp.__delitem__(dataset_name)
			self._AddDataSet(grp, dataset_name, data, mvs)

	def get_runnames(self, grp='data'): # Get all runnames in the file
		return list(self._GetGrp(grp).keys())

	def get_datnames(self, grp='data'): # Get data rame from group
		return list(self._GetGrp(grp).keys())

	def get_data(self, runname, grp='/data'):
		dat_arr = self.f[grp+'/'+runname]
		if dat_arr.shape[0] == 1:
			return np.array(dat_arr[0])
		else:
			return np.array(dat_arr)

	def get_datas(self, keys='all'):
		if keys == 'all':
			keys = list(self.f['/data'].keys())

		names = []
		dats  = []
		for key in keys:
			names.append(key)
			dats.append(self.get_data(key))
		names = np.array(names)
		dats  = np.array(dats)

		return names, dats

	def get_mv(self, runname, mvname):
		return self._GetGrp("data")[runname].attrs[mvname]

	def get_mvname(self, runname):
		return list(self._GetGrp("data")[runname].attrs.keys())

	def get_mvs(self, mvname, runnames='all'):
		runnames = list(self.f["/data"].keys()) if runnames=='all' else runnames
		mv = []
		for key in runnames:
			try:
				mv.append([key, self.f["/data/"+key].attrs[mvname]])
			except:
				continue
		return mv

	def get_lmvs(self, runname):
		lmvs = []
		dset_attr = self._GetGrp('data')[runname].attrs
		for key in list(dset_attr.keys())[3:]:
			try:
				mv_val = float(dset_attr[key])
			except:
				lmvs.append([str(key), dset_attr[key]])
		return lmvs

	def get_smvs(self, runname):
		smvs = []
		dset_attr = self._GetGrp('data')[runname].attrs
		for key in list(dset_attr.keys())[3:]:
			try:
				mv_val = float(dset_attr[key])
				smvs.append([str(key), mv_val])
			except:
				continue
		return smvs

	def del_datas(self, runname, grp='data'):
		self._GetGrp(grp).__delitem__(runname)
		return 1

	
		



