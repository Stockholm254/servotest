import numpy as np

def bin_data(data, bin_num):
	'''Bin data array

	Parameters
	----------
	data: ndarray
		Input array for binning. (Must be 1D)
	
	bin_num: Bin size
		Number of data points per bin

	Returns
	-------
	new_data: ndarray
		Binnded array
	'''
	data_length = len(data)
	new_length = int(np.floor(data_length)/bin_num)
	rnd_ind = int(bin_num)*new_length
	new_data = np.sum(np.reshape(data[:rnd_ind], (new_length, bin_num)), axis=1)/bin_num
	if data_length>rnd_ind:
		new_data = np.append(new_data, np.sum(data[rnd_ind:])/(data_length-rnd_ind))
	return new_data

def fold_data(data, prd):
	data_folded = np.zeros(int(np.floor(prd)+1))
	for ii in range(len(data)):
		rnd_ind = int(np.floor(ii%prd))
		data_folded[rnd_ind] += data[ii]
	return data_folded

def stitch(arr, cyl, drange):
	prd = 1.*len(arr)/cyl
	sub_range = drange[1]-drange[0]
	new_len = (drange[1]-drange[0])*cyl
	new_arr = np.zeros(new_len)
	for ii, ele in enumerate(arr):
		new_ind = np.floor(ii%prd)
		if (new_ind<drange[0]) or (new_ind>drange[1]):
			continue
		else:
			new_ind -= drange[0]
			new_ind += np.floor(ii/prd)*sub_range-1
		new_arr[int(new_ind)] = ele
	return new_arr

def nparr(arrs):
	new_arrs = []
	for arr in arrs:
		new_arrs.append(np.array(arr))
	return new_arrs

def spike_ind(arr, w, t):
	rm_ind = []
	for ii in range(len(arr)):
		ind0 = max(ii-w, 0); ind1 = min(ii+w, len(arr)-1)
		mean = np.mean(arr[ind0:ind1])
		if not (mean-t)<arr[ii]<(mean+t):
			rm_ind.append(ii)
	return rm_ind

def spike_filter(arr, w, t):
	s_ind = spike_ind(arr, w, t)
	return np.delete(arr, s_ind)

def fold_lr(arr):
	arr = np.array(arr)
	_len = len(arr)

	if _len%2==0:
		arrl = arr[:_len/2]
		arrr = arr[_len/2:]
		arr_new = (arrl[::-1]+arrr)/2.
	elif _len%2 == 1 :
		mind = int(np.floor(_len/2.))
		arrl = arr[:mind]
		arrr = arr[mind:]
		arr_new = arrr
		arr_new[1:] = (arr_new[1:]+arrl[::-1])/2.
	
	return arr_new
