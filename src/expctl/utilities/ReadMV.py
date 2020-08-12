#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
from pathlib import Path
# from utilities.util import is_number as is_number
# from utilities.util import printError, printYellow

from .util import is_number as is_number
from .util import printError, printYellow

def __init__():
	return

def ChkScriptName(fname_mv, fname_seq):
	''' 
	Check if the sequence name in the MV file is the same with the 
	currently loaded sequence.
	'''
	with open(fname_mv, 'r') as f:
		# Check that the script name matches the current file
		firstline  = f.readline().split(": ")
		fileScript = firstline[1].replace(".py","").replace("\n", "")
		if fileScript != fname_seq:
			#printYellow("MV file script \""+fileScript+"\", does not match the current script name \""+fname_seq+"\"")
			printYellow(f"MV file script \"{fileScript}\", does not match the current script name \"{fname_seq}\"")
			return -1
		else:
			return 1

def ReadMV(fname):
	mv_dict = {}
	mv_loop = ''
	j_range = ['NA', 'NA']
	prerun  = '0'
	runname = ''
	
	with open(fname, 'r') as f:
		for line in f: # Read line by line and record the variables

			# Check if line define loop variable
			m = re.match('(\w+)\s*=\s*([-]?[\w\.\W]*)', line.strip())
			if m != None:
				var_name = m.group(1)
				var_val  = m.group(2)
				if not is_number(var_val):
					mv_loop += var_name+' = '+var_val+'\n'
					mv_dict[var_name] = 'LOOP'
				else:
					mv_dict[var_name] = var_val

			# Check if line gives the loop run range
			m = re.match('\s*j_min:\s*([\w\W]*)', line[1:].strip())
			if m != None:
				j_range[0] = str(m.group(1))
			m = re.match('\s*j_max:\s*([\w\W]*)', line[1:].strip())
			if m != None:
				j_range[1] = str(m.group(1))

			# Check for prerun
			m = re.match('\s*pre:\s*([\w\W]*)', line[1:].strip())
			if m != None:
				prerun = str(m.group(1))

			# Check for data runname
			m = re.match('\s*Runname:\s*([\w\W]*)', line[1:].strip())
			if m != None:
				runname = m.group(1)
	
	return mv_dict, mv_loop, j_range, prerun, runname

def CompareMV(fname, fp_mv):
	# Get MV values from the file
	mv_dict, mv_loop, j_range, prerun, runname = ReadMV(fname)
	# Compare with the front panel value
	mv_none = [] # MVs not defined in the file as a steady state value

	rtxt  = '='*50+'\n'
	rtxt += 'MV Name'.ljust(25)+'Panel'.ljust(10)+'File'.ljust(10)+'\n'
	rtxt += '-'*50+'\n'

	for _mv in fp_mv: # update MV values
		if not _mv.name in mv_dict: # Check if the MV is defined in the file
			mv_none.append(_mv.name)
		else:
			if float(_mv.value) != float(mv_dict[_mv.name]): # compare with the current front panel value
				rtxt += _mv.name.ljust(25)+str(_mv.value).ljust(10)+str(mv_dict[_mv.name]).ljust(10)+'\n'
		
	rtxt += '='*50
	print(rtxt)
	if len(mv_none) > 0:
		print(str(mv_none)+' are not defined as static MV in the file!')

	return 1

# if __name__ == '__main__':
# 	fname = r'C:\Users\Simonlab\Programming\dev\Control_Suite_X\Control_Suite_X_v0.3\usr\remote\MV.txt'
# 	ReadMV(fname)
