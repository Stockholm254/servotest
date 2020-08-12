def CN2CR(dat, prb_time):
	'''
	Convert event number per bin to count rate in kHz

	Input: data array, probe time in ms
	Output: data array in kHz
	'''
	bin_num = len(dat)
	return dat/(prb_time/bin_num)
