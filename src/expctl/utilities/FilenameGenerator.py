#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import os
from pathlib import Path

FNAMEFMT_DATETIME = "_D %Y-%m-%d T %H-%M-%S-%f"
DIRFMT_DATETIME   = "%Y/%m/%d"

########################
## Filename Generator ##
########################
#def __init__():
#	return

# Generate datetime directory
def GenDTDir(home_dir, dt, sub_dir=''):
	#return os.path.join(home_dir, dt.strftime(DIRFMT_DATETIME), sub_dir)
	return Path(home_dir)/dt.strftime(DIRFMT_DATETIME)/sub_dir

# Generate a standard format file name
def GenFname(header, dt, post='', postfix='.txt'):
	return header+dt.strftime(FNAMEFMT_DATETIME)[:-3]+'_'+post+postfix
	
# Generate a 
def GenFullFname(home_dir, sub_dir='', fname_header='NA', date_time=datetime.datetime.now(), fname_post='', fmt='.txt'):
	return GenDTDir(home_dir, dt=date_time, sub_dir=sub_dir) / GenFname(fname_header, dt=date_time, post=fname_post, postfix=fmt)

def ChkDirExist(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)

# if __name__ == '__main__':
	# print GenFullFname(home_dir="Expt_Log", fname_header='PC', fname_post='0')
	# print GenDTDir("C:/Users/Simonlab/Documents/Log", dt=datetime.now())
	# print GenFname(header='LOGFP', dt=datetime.now(), post=str(5))