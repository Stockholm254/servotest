import os
import numpy as np
from os.path import isfile, join, basename
from glob import glob

def check_dir(home_dir):
	folders = []
	for dirs in os.listdir(home_dir):
		fdir = os.path.join(home_dir, dirs)
		if os.path.isdir(fdir):
			folders.append(dirs)
	return folders

def check_file(directory, fmt='txt'): # Get the names of certain type file from the directory
	files = glob(directory+"/*."+fmt)
	sfiles = sorted(files, key=lambda x: int(basename(x).partition('.')[0].split('_')[-1])) # Sort the filename with respect to j value
	print("Number of Files:", len(files))
	return np.array(sfiles)

def load_files(file_list):
	trace_len = len(np.loadtxt(file_list[0]))
	new_list = np.empty((0, trace_len))
	for files in file_list:
		trace_data = np.loadtxt(files)
		trace_data_resized = np.resize(trace_data, (1, trace_len))
		new_list = np.append(new_list, trace_data_resized, axis=0)
	print("Files loaded!")
	return new_list

def shot_noise(raw_data, avg_num):
	data_sigma = np.sqrt(raw_data)
	return data_sigma

# def avg_data(raw_data, avg_num, avg_axis=0):
# 	'''
# 	avg_axis: How the data is iterated. 0 for floor, and 1 for mod
# 	'''
# 	trace_len = raw_data.shape[1]
# 	if avg_axis == 0:
# 		split_data = np.reshape(raw_data, (raw_data.shape[0]/avg_num, avg_num, trace_len))
# 		avg_data = np.average(split_data, axis=1)
# 	elif avg_axis == 1:
# 		split_data = np.reshape(raw_data, (avg_num, raw_data.shape[0]/avg_num, trace_len))
# 		avg_data = np.average(split_data, axis=0)
# 	return avg_data

def load_avg_data(data_dir, filename, avg_num):
	raw_data = np.loadtxt(data_dir+filename)
	split_data = np.split(raw_data, raw_data.shape[0]/avg_num, 0)
	avg_data = [np.average(SubArray, axis=0) for SubArray in split_data]
	np_avg_data = np.array(avg_data)
	return np_avg_data

def avgdat(data_dir, avg_num, avg_axis=1):
	# Load the data and take average
	full_data = load_files(check_file(data_dir))
	avged_data = avg_data(full_data, avg_num, avg_axis)
	return full_data, avged_data

def avg_data_noscan(data_dir, avg_num, avg_axis=1):
	'''
	avg_axis: How the data is iterated. 0 for floor, and 1 for mod
	'''
	raw_data = load_files(check_file(data_dir))
	raw_data = np.array(raw_data)
	print(str(len(raw_data))+' files found.')
	avg_row = np.average(raw_data, axis=1)

	if avg_axis == 0:
		split_data = np.reshape(avg_row, (avg_row.shape[0]/avg_num, avg_num))
		avg_data = np.average(split_data, axis=1)
	elif avg_axis == 1:
		split_data = np.reshape(avg_row, (avg_num, avg_row.shape[0]/avg_num))
		avg_data = np.average(split_data, axis=0)

	avg_data = np.array(avg_data)

	return raw_data, avg_data

def save_data(data_dir, data_filename, avg_num, avg_axis=0):
	# Defing output filenames
	out_name = data_filename+'.dat'
	avg_out_name = data_filename+'_avg'+'.dat'
	# Load the data and take average
	full_data = load_files(check_file(data_dir))
	avged_data = avg_data(full_data, avg_num, avg_axis)
	# Save all data and averaged data to two files
	print("Saving files!")
	np.savetxt(data_dir+out_name, full_data)
	np.savetxt(data_dir+avg_out_name, avged_data)

def reshape_fnames(fnames, avg_num, axis=1):
	if axis == 0:
		fnames = np.reshape(fnames, (len(fnames)/avg_num, avg_num))
	elif axis == 1:
		fnames = np.reshape(fnames, (avg_num, len(fnames)/avg_num))
		fnames = np.transpose(fnames)
	return fnames

def avg_data(file_dir, avg_num, avg_axis=1):
	fnames = check_file(file_dir)
	fnames = np.array(fnames)
	trace_len = len(np.loadtxt(fnames[0]))
	
	if avg_axis == 0:
		fnames = np.reshape(fnames, (len(fnames)/avg_num, avg_num))
	elif avg_axis == 1:
		fnames = np.reshape(fnames, (avg_num, len(fnames)/avg_num))
		fnames = np.transpose(fnames)

	dat_all = []
	for ii in range(len(fnames)):
		dat_row = np.array([0]*trace_len)
		for jj in range(len(fnames[ii])):
			new_dat = np.loadtxt(fnames[ii, jj])
			if (len(new_dat)==len(dat_row)):
				dat_row = dat_row+new_dat
			elif (len(new_dat)>len(dat_row)):
				dat_row = dat_row+new_dat[:trace_len]
			elif (len(new_dat)<len(dat_row)):
				# print "WARNING: Bin number does not match!"
				dat_row = dat_row+np.append(new_dat, [0]*(len(dat_row)-len(new_dat)))
		dat_all.append(1.0*dat_row/avg_num)

	return np.array([]), dat_all

def avg_data_s(file_dir, avg_num, avg_axis=1):
	pdata = avg_data(file_dir, avg_num, avg_axis)
	return pdata[1:], ['avg']

def avg_data_all(file_dir):
	fnames = check_file(file_dir)
	fnames = np.array(fnames)
	trace_len = len(np.loadtxt(fnames[0]))
	avg_num = len(fnames)
	dat_all = []
	dat_row = np.array([0]*trace_len)
	for jj in range(len(fnames)):
		dat_row += np.loadtxt(fnames[jj])
	dat_all.append(1.0*dat_row/avg_num)

	return np.array([]), dat_all

def avg_data_only(file_dir, avg_num, avg_axis=1):
	fnames = check_file(file_dir)
	fnames = np.array(fnames)
	trace_len = len(np.loadtxt(fnames[0]))
	
	if avg_axis == 0:
		fnames = np.reshape(fnames, (len(fnames)/avg_num, avg_num))
	elif avg_axis == 1:
		fnames = np.reshape(fnames, (avg_num, len(fnames)/avg_num))
		fnames = np.transpose(fnames)

	dat_all = []
	for ii in range(len(fnames)):
		dat_row = np.array([0]*trace_len)
		for jj in range(len(fnames[ii])):
			dat_row += np.loadtxt(fnames[ii, jj])
		dat_all.append(1.0*dat_row/avg_num)

	return dat_all