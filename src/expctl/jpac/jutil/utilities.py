import numpy as np
import matplotlib.pyplot as plt
import os
import inspect

def get_arg_ind(func, arg_name):
	args = inspect.getargspec(func)[0][1:]
	return args.index(arg_name)

def print_list(l):
	for ii, item in enumerate(l):
		print(ii, item)

def chk_finite(xx, yy):
	finite_ele = np.where(np.isfinite(yy))
	return xx[finite_ele], yy[finite_ele]

def sn(data, avg_num=1):
	data = np.array(data)
	return np.sqrt((data+1./avg_num)/avg_num)

def count2rate(arr, prb_time, bin_num):
	'''Convert counts per bin to count rate'''
	return np.array(arr)*bin_num/prb_time

def mergedict(dicts):
	"""Merge multiple dictionaries"""
	new_dict = {}
	for dd in dicts:
		new_dict.update(dd)
	return new_dict

def checkdir(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)
	return directory






