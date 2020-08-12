import re
import numpy as np
from datetime import datetime

############################################
###  File Naming Convention for Devices  ###
############################################
PHOTONCOUNTER = ("([\W+\w+]*) T ([\W+\w+]*)_(\d+)_CLK(\d+).txt", ("Date", "Time", "j", "CLK"))
PHOTONTIMER = ("([\W+\w+]*) T ([\W+\w+]*)_(\d+).bin", ("Date", "Time", "j"))

#########################
### File name parser  ###
#########################
def get_absruntime(fname, fname_fmt=PHOTONCOUNTER):
	fmt = fname_fmt[0]
	m = re.match(fmt, fname.strip())
	item = [m.group(ii+1) for ii in range(len(fname_fmt[1]))]
	time = datetime.strptime(item[-4][-10:]+' '+item[-3], "%Y-%m-%d %H-%M-%S-%f")
	return time

def get_reltime(time_arr):
	"""Get relative time with respect to the first run"""
	tt = []
	t0 = time_arr[0]
	for t in time_arr:
		tt.append((t-t0).total_seconds())
	return tt

def get_runtime(fnames, p=PHOTONCOUNTER):
	"""Get absolute run time"""
	t_abs = []
	for fname in fnames:
		t_abs.append(get_absruntime(fname, fname_fmt=p))
	t_rel = get_reltime(t_abs)
	return t_rel

def get_difftime(fnames, p=PHOTONCOUNTER):
	"""Get time difference between each run"""
	t_diff = []
	t0 = get_absruntime(fnames[0], fname_fmt=p)
	for ii, fname in enumerate(fnames[1:]):
		t1 = get_absruntime(fname, fname_fmt=p)
		t_diff.append((t1-t0).total_seconds())
		t0 = t1
	return t_diff

def get_missrun(fnames, p=PHOTONCOUNTER):
	fmt = p[0]
	mf = np.array([])
	for ii, fname in enumerate(fnames):
		m = re.match(fmt, fname.strip())
		j1 = int(m.group(3))
		if (ii>0):
			if (j1-j0>1):
				mf = np.append(mf, np.arange(j0+1, j1))
		j0 = j1
	return mf




