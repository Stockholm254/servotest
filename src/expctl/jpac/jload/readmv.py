import os
import re
import numpy as np

def readMV(fname):
	f = open(fname, 'r')
	lines = f.readlines()

	seqname = ''
	jrange = [0, 0]
	# smv = {}
	# lmv = {}
	smv = []
	lmv = []

	smvnum = 0
	lmvnum = 0

	sep = '='*40

	for line in lines:
		# Check script name
		m = re.match('# Script name: ([\w\.\+]*)', line.strip())
		if m != None:
			seqname = m.group(1)

		# Check iteration range
		m = re.match('#\s*j_min:\s*(\w+)', line.strip())
		if m != None:
			jrange[0] = int(m.group(1))
			lmv.insert(0, ('j_min', int(m.group(1))))
		m = re.match('#\s*j_max:\s*(\w+)', line.strip())
		if m != None:
			jrange[1] = int(m.group(1))
			lmv.insert(1, ('j_max', int(m.group(1))))

		# Check if line is of form: variable = value
		# m = re.match('(\w+)\s*=\s*([-]?[-+\w+\.]*)', line.strip())
		m = re.match('(\w+)\s*=\s*(.+)*', line.strip())
		if m != None:
			try:
				val = float(m.group(2))
				# smv.append([m.group(1), val])
				smv.append((m.group(1), val))
				# smv[m.group(1)] = val
				smvnum += 1
			except ValueError:
				lmv.append((m.group(1), m.group(2)))
				# lmv[m.group(1)] = m.group(2)
				lmvnum += 1

	# Covert data to numpy array
	smv = np.array(smv, dtype=[('Name', 'S50'), ('Value', float)])  # Static MVs
	lmv = np.array(lmv, dtype=[('Name', 'S50'), ('Value', 'S100')]) # Loop MVs

	reporttxt = sep+'\n'
	reporttxt += "Sequence name: "+seqname+'\n'+sep+'\n'
	reporttxt += "j_min: "+str(jrange[0])+'\n'
	reporttxt += "j_max: "+str(jrange[1])+"\n"+sep+'\n'
	reporttxt += "Number of static variables: "+str(smvnum)+'\n'
	reporttxt += "Number of loop variables: "+str(lmvnum)+"\n"+sep+'\n'
	reporttxt += "Loop variables:"+'\n'
	for item in lmv:
		reporttxt += item[0]+' = '+item[1]+'\n'
	print(reporttxt)

	return seqname, jrange, smv, lmv

def GetRunInfo(mv_fname):
	info = []
	f = open(mv_fname, 'r')
	for line in f.readlines():
		# Check script name
		m = re.match('# Script name: ([\w\.\+]*)', line.strip())
		if m != None:
			info.append(["Seq Name", m.group(1)])
		# Check iteration range
		m0 = re.match('#\s*j_min:\s*(\w+)', line.strip())
		m1 = re.match('#\s*j_max:\s*(\w+)', line.strip())
		if (m0!=None) & (m1!=None):
			info.append(["j range", [m0.group(1), m1.group(1)]])
		# Check if line is of form: variable = value
		m = re.match('(\w+)\s*=\s*(.+)*', line.strip())
		if m != None:
			info.append([m.group(1), m.group(2)])
	f.close()
	return info

def info2nparr(info_arr, runnames=None):
	seqnames, jranges, smvss, lmvss = [], [], [], []

	smvss = [info_arr[0][2]['Name']]
	lmvss = [info_arr[0][3]['Name']]

	for ii, info in enumerate(info_arr):
		seqname, jrange, smvs, lmvs = info
		seqnames.append(seqname)
		smvss.append(smvs['Value'])
		lmvss.append(lmvs['Value'])

	if runnames == None:
		runnames = ['Run'+str(ii) for ii in range(len(info_arr))]

	# smvsdtype = [('Name', 'S50')]+[('run'+str(ii+1), float) for ii in range(len(info_arr))]
	smvsdtype = [('Name', 'S50')]+[(rname, float) for rname in runnames]
	smvss = np.array(smvss)
	smvss = [tuple(smvss[:, ii]) for ii in range(len(smvss[0]))]
	smvss = np.array(smvss, dtype=smvsdtype)

	# lmvsdtype = [('Name', 'S50')]+[('run'+str(ii+1), 'S100') for ii in range(len(info_arr))]
	lmvsdtype = [('Name', 'S50')]+[(rname, 'S100') for rname in runnames]
	lmvss = np.array(lmvss)
	lmvss = [tuple(lmvss[:, ii]) for ii in range(len(lmvss[0]))]
	lmvss = np.array(lmvss, dtype=lmvsdtype)

	return seqnames, smvss, lmvss

def get_infos(datadir):
	subdirs = [subdir for subdir in os.listdir(datadir)]
	infos = []
	runnames = []
	for subdir in subdirs:
		if os.path.isdir(datadir+'/'+subdir):
			runnames.append(subdir)
			loopcodedir = datadir+'/'+subdir+'/MVs'
			for f in os.listdir(loopcodedir):
				if f.endswith('.txt'):
					MVfname = loopcodedir+'/'+f
			[seqname, jrange, smvs, lmvs] = readMV(MVfname)
			infos.append([seqname, jrange, smvs, lmvs])
	seqnames, smvss, lmvss = info2nparr(infos, runnames)
	return seqnames, smvss, lmvss




