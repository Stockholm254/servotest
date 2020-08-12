import numpy as np
from .bin2dat import *
from jload import *

##################################################
###    Functions for building the histogram    ###
##################################################

def H1(data, tmax):
	""" Build one photon histogram

	Parameters
	----------
	data: list
		Event time of all channels.
	tmax: int
		Maximum probe time in FPGA clock cycle

	Returns
	-------
	list
		Single photon event vs time. 

	"""
	hist_all = []
	for dd in data:
		hist = np.zeros(tmax)
		if len(dd)>0:
			hist[dd] = 1
		hist_all.append(hist)
	return hist_all

def H2(data, max_dt):
	""" Build two photons histogram
	
	Parameters
	----------
	data : list
		Folded list of event time.
	max_dt : int
		Length maximum time in FPGA clock cycle. 

	Regurns
	-------
	list
		Number of two photon events vs time in FPGA clock cycle. 
	
	"""
	evt_a, evt_b = data
	hab = np.zeros(2*(max_dt-1)+1)

	for ii in range(len(evt_a)):
		ea = evt_a[ii]
		eb = evt_b[ii]
		la, lb = len(ea), len(eb)

		if la>0 and lb>0:
			for jj in range(la+lb-1):
				ind11, ind12 = max(la-1-jj, 0),  min(la+lb-1-jj, la)
				ind21, ind22 = max(-la+1+jj, 0), min(jj+1, lb)

				dcs = ea[ind11:ind12]-eb[ind21:ind22]
				for dc in dcs:
					hab[dc+int(max_dt)-1] += 1

	return hab

def fold_event(evt_arr, prd, cyl_num=10, drange=[0, -1]):
	"""Fold the event array according to probe cycles

	Parameters
	----------
	evt_arr : list
		Array of event time of all channels. 
	prd : int
		Period of probe in FPGA clock cycles
	cyl_num : int, list
		Number of cycles that will be used. Start from the first one if given, 
		as a int, and specified cycles if given as a list
	drange : list
		Index of starting and stopping of the probe

	Returns
	-------
	list
		Array with splitted probe cycles for each channels.

	"""
	arr = []

	if type(cyl_num) == int:
		cyl_num = [0, cyl_num]

	for chan in evt_arr:
		chan = np.array(chan)
		chan_arr = []
		for ii in range(cyl_num[0], cyl_num[1]):
			chan_arr.append(chan[np.logical_and(ii*prd+drange[0]<=chan, \
												chan<=ii*prd+drange[1])])
		arr.append(chan_arr)
	return arr

#####################
###   Utilities   ###
#####################

def fold_hist(hist, prd=None, drange=[0,-1]):
	if prd == None:
		prd = len(hist)

	hist_fold = []
	for ii in range(int(np.floor(len(hist)/prd)+1)):
		ind0, ind1= int(np.floor(ii*prd)), min(np.floor((ii+1)*prd), len(hist))
		sub_int = hist[ind0+drange[0]:ind0+drange[1]]
		hist_fold.append(sub_int)

	return hist_fold

def get_evt_num(evt_arr):
	evts = []
	for chan in evt_arr:
		chan = np.array(chan)
		cc = 0
		for ee in chan:
			cc += len(ee)
		evts.append(cc)
	return evts

def InitHistArr(t_max, t_prd, t0, t1,
				res_num,
				clk_cyl):
	dt = t1-t0
	Na, Nb = 0, 0                             # Number of total single photon events
	f_num = 0                                 # Number of runs (including re-slicing cycle)
	SPCM1_N, SPCM2_N = np.array([]), np.array([])  # Events number histogram
	Ha, Hb = np.zeros(t_max), np.zeros(t_max) # Single photon histogram
	Hab = np.zeros(2*(dt-1)+1)                # Two photon histogram
	return Na, Nb, Ha, Hb, Hab, f_num, SPCM1_N, SPCM2_N

def eval_g2_parm(t_max, t_prd, t0, t1,
				 res_num, clk_cyl):
	return t_max, t_prd, t0, t1, res_num, clk_cyl

def get_g2_norm(t0, t1, **kwarg):
	dt = t1-t0
	norm = np.array([1.0*dt/(dt-tau) for tau in range(dt)])
	norm = np.append(norm[1:][::-1], norm)
	return norm

##########################################
###    Build histogram for data set    ###
##########################################
DATASTRUCT_HIST = ["Na", "Nb", "Ha", "Hb", "Hab", \
				   "f_num", "SPCM1_N", "SPCM2_N"]
				   
def build_hist(data_dir, 
				t_max, t_prd, t0, t1,
				res_num,
				clk_cyl):
	"""
	Build histogram for single and two photons event
	"""
	
	# Initialize array
	dt = t1-t0
	Na, Nb = 0, 0                             # Number of total single photon events
	f_num = 0                                 # Number of runs (including re-slicing cycle)
	SPCM1_N, SPCM2_N = [], []                 # Events number histogram
	Ha, Hb = np.zeros(t_max), np.zeros(t_max) # Single photon histogram
	Hab = np.zeros(2*(dt-1)+1)                # Two photon histogram

	fnames = check_file(data_dir, fmt='bin')
	for ii, fname in enumerate(fnames):
		# Convert binary data to event list
		evt_arr = bin2dat_lr(fname)
		evt_arr_f = fold_event(evt_arr, prd=t_prd, cyl_num=res_num, drange=[t0, t1])
		# Build single photon event list
		na, nb = get_evt_num(evt_arr_f)
		Na += na
		Nb += nb
		SPCM1_N.append(na)
		SPCM2_N.append(nb)
		f_num += res_num if type(res_num)==int else res_num[1]-res_num[0]
		# Calculate single and two photons histogram
		hist_1 = H1(evt_arr, t_max)
		hist_2 = H2(evt_arr_f, dt)
		# Build histogram
		ha, hb = hist_1
		Ha += ha; Hb += hb
		Hab += hist_2

	return [[Na], [Nb], Ha, Hb, Hab, [f_num], SPCM1_N, SPCM2_N], DATASTRUCT_HIST

DATASTRUCT_HIST4 = ["N1", "N2", "N3", "N4", 
                    "H1", "H2", "H3", "H4",
                    "Hff", "Hbb", "Hfb", 
                   "f_num", 
                   "SPCM1_N", "SPCM2_N", "SPCM3_N", "SPCM4_N"]

def build_hist_fb(fnames, 
                t_max, t_prd, t0, t1,
                res_num,
                clk_cyl):
    """Build histogram for single and two photons event. Multi channel version

    Parameters
    ----------
    fnames : list
    	List of file names to analyze. 
	t_max : int
		Maximum probe time in FPGA clock cycle.
	t_prd : int
		Slice-probe period in FPGA clock cycle.
	t0 : int
		Probe starting time. 
	t1 : int
		Probe stop time.
	res_num: int, list
		Number of slice-probe cycles. Start from the first cycle if using 
		integer, and specified cycle range if using list.
	clk_cyl: float
		FPGA clock time in ns. 

	Returns
	-------
	list
		Output data. 
	list
		List of data structures. 

    """

    # Initialize array
    dt = t1-t0
    N1, N2, N3, N4 = 0, 0, 0, 0         # Number of total single photon events
    f_num = 0                           # Number of runs (including re-slicing cycle)
    Nc1, Nc2, Nc3, Nc4 = [], [], [], [] # Events number list

    # Event histogram
    # Single photon events
    Hist1, Hist2 = np.zeros(t_max), np.zeros(t_max) # Forward mode
    Hist3, Hist4 = np.zeros(t_max), np.zeros(t_max) # Backward mode
    # Two photon events
    Hff = np.zeros(2*(dt-1)+1) # forward-foward correlation
    Hbb = np.zeros(2*(dt-1)+1) # backward-backward correlation
    Hfb = np.zeros(2*(dt-1)+1) # forward-backward correlation

    # Loop over all files
    for ii, fname in enumerate(fnames):
        # Convert binary data to event list
        evt_arr   = bin2dat_4c(fname)
        # Fold slicing cycles
        evt_arr_f = fold_event(evt_arr, prd=t_prd, cyl_num=res_num, drange=[t0, t1])
        # Build single photon event list
        n1, n2, n3, n4 = get_evt_num(evt_arr_f)
        N1 += n1; N2 += n2; N3 += n3; N4 += n4;
        Nc1.append(n1); Nc2.append(n2); Nc3.append(n3); Nc4.append(n4); 
        f_num += res_num if type(res_num)==int else res_num[1]-res_num[0]
        # Calculate single and two photons histogram
        # Single photon histogram
        hist_1 = H1(evt_arr, t_max)
        # Two photons histogram
        evt_f1, evt_f2, evt_b1, evt_b2 = evt_arr_f
        
        evt_f = evt_f1+evt_f2
        evt_b = evt_b1+evt_b2
        
        hist_2_ff = H2([evt_f1, evt_f2], dt)
        hist_2_bb = H2([evt_b1, evt_b2], dt)
        hist_2_fb = H2([evt_f, evt_b], dt)
        # Build histogram
        h1, h2, h3, h4 = hist_1
        Hist1 += h1; Hist2 += h2; Hist3 += h3; Hist4 += h4;
        Hff += hist_2_ff; Hbb += hist_2_bb; Hfb += hist_2_fb;

    return [[N1], [N2], [N3], [N4],
            Hist1, Hist2, Hist3, Hist4, 
            Hff, Hbb, Hfb, 
            [f_num],
            Nc1, Nc2, Nc3, Nc4
            ], DATASTRUCT_HIST4

def build_hist1(data_dir, 
				t_max, t_prd, t0, t1,
				res_num,
				clk_cyl):
	"""
	Build histogram for single photon event
	"""
	# Initialize array
	dt = t1-t0
	Na, Nb = 0, 0
	f_num = 0
	SPCM1_N, SPCM2_N = [], []
	Ha, Hb = np.zeros(t_max), np.zeros(t_max)
	Hab = np.zeros(2*(dt-1)+1)

	fnames = check_file(data_dir, fmt='bin')
	for ii, fname in enumerate(fnames):
		# Convert binary data to event list
		evt_arr = bin2dat_lr(fname)
		evt_arr_f = fold_event(evt_arr, prd=t_prd, cyl_num=res_num, drange=[t0, t1])
		# Build single photon event list
		na, nb = get_evt_num(evt_arr_f)
		Na += na
		Nb += nb
		SPCM1_N.append(na)
		SPCM2_N.append(nb)
		f_num += res_num if type(res_num)==int else res_num[1]-res_num[0]
		# Calculate single and two photons histogram
		hist_1 = H1(evt_arr, t_max)
		# hist_2 = H2(evt_arr_f, dt)
		# Build histogram
		ha, hb = hist_1
		Ha += ha; Hb += hb
		# Hab += hist_2

	return [[Na], [Nb], Ha, Hb, Hab, [f_num], SPCM1_N, SPCM2_N], DATASTRUCT_HIST

def build_hist_fnames(fnames, \
					  t_max, t_prd, t0, t1, \
					  res_num, \
					  clk_cyl):
	"""
	Build histogram for single photon event
	"""
	# Initialize array
	dt = t1-t0
	Na, Nb = 0, 0
	f_num = 0
	SPCM1_N, SPCM2_N = [], []
	Ha, Hb = np.zeros(t_max), np.zeros(t_max)
	Hab = np.zeros(2*(dt-1)+1)

	for ii, fname in enumerate(fnames):
		# Convert binary data to event list
		evt_arr = bin2dat_lr(fname)
		evt_arr_f = fold_event(evt_arr, prd=t_prd, cyl_num=res_num, drange=[t0, t1])
		# Build single photon event list
		na, nb = get_evt_num(evt_arr_f)
		Na += na
		Nb += nb
		SPCM1_N.append(na)
		SPCM2_N.append(nb)
		f_num += res_num if type(res_num)==int else res_num[1]-res_num[0]
		# Calculate single and two photons histogram
		hist_1 = H1(evt_arr, t_max)
		hist_2 = H2(evt_arr_f, dt)
		# Build histogram
		ha, hb = hist_1
		Ha += ha; Hb += hb
		Hab += hist_2

	return [[Na], [Nb], Ha, Hb, Hab, [f_num], SPCM1_N, SPCM2_N], DATASTRUCT_HIST

def build_hist1_hr(data_dir, 
				t_max, t_prd, t0, t1,
				res_num,
				clk_cyl):
	"""
	Build histogram for single photon event with super time resolution
	"""
	# Initialize array
	t0 = 4*t0; t1 = 4*t1; t_max = 4*t_max;
	dt = t1-t0
	Na, Nb = 0, 0
	f_num = 0
	SPCM1_N, SPCM2_N = [], []
	Ha, Hb = np.zeros(t_max), np.zeros(t_max)
	Hab = np.zeros(2*(dt-1)+1)

	fnames = check_file(data_dir, fmt='bin')
	for ii, fname in enumerate(fnames):
		# Convert binary data to event list
		evt_arr = bin2dat_hr(fname)
		evt_arr_f = fold_event(evt_arr, prd=t_prd, cyl_num=res_num, drange=[t0, t1])
		# Build single photon event list
		na, nb = get_evt_num(evt_arr_f)
		Na += na
		Nb += nb
		SPCM1_N.append(na)
		SPCM2_N.append(nb)
		f_num += res_num if type(res_num)==int else res_num[1]-res_num[0]
		# Calculate single and two photons histogram
		hist_1 = H1(evt_arr, t_max)
		# Build histogram
		ha, hb = hist_1
		Ha += ha; Hb += hb

	return [[Na], [Nb], Ha, Hb, Hab, [f_num], SPCM1_N, SPCM2_N], DATASTRUCT_HIST



