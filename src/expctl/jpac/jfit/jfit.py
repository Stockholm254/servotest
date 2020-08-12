from scipy.optimize import curve_fit
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import inspect
from ..jplot import setticks

def fit(xdata, ydata, fitform, ysigma=[], guesses=None):
	if len(ysigma) != len(ydata):
		asigma = False
		ysigma = None
	else:
		asigma = True

	if guesses != None:
		try:
			guesses = list(guesses)
		except:
			guesses = guesses(xdata, ydata)
	
	args = inspect.getargspec(fitform)[0][1:]
	arg_num = len(args)

	# Fit the curve
	try:
		popt, pcov = curve_fit(fitform, xdata, ydata, \
			p0=guesses, sigma=ysigma, absolute_sigma=asigma)
	except Exception as e:
		print(e)
		popt = np.nan*np.ones(arg_num)
		pcov = np.inf*np.ones((arg_num, arg_num))

	return popt, pcov

def fit_all(xdatas, ydatas, fitform, ysigma=None, guesses=None):
	data_num = len(ydatas)

	if len(xdatas.shape) == 1:
		xdatas = np.repeat([xdatas], data_num, axis=0)

	if ysigma == None:
		asigma = False
		ysigma = [None]*data_num
	else:
		asigma = True

	run_guesses = 0
	if guesses != None:
		try:
			guessed_parm = list(guesses)
		except:
			run_guesses = 1

	# Fit datas
	args = inspect.getargspec(fitform)[0][1:]
	arg_num = len(args)

	popts = []
	pcovs = []
	for ii in range(data_num):
		try:
			if run_guesses == 1: # Get guesses from function
				guessed_parm = guesses(xdatas[ii], ydatas[ii])
			popt, pcov = curve_fit(fitform, xdatas[ii], ydatas[ii], \
				p0=guessed_parm, sigma=ysigma[ii], absolute_sigma=asigma)
		except Exception as e:
			print(e)
			popt = np.nan*np.ones(arg_num)
			pcov = np.inf*np.ones((arg_num, arg_num))
		popts.append(popt)
		pcovs.append(pcov)

	return np.array(popts), np.array(pcovs)

###########################
###  Utility Functions  ###
###########################
# def print_parm(func, popt, pcov=None):
# 	parmText = ""
# 	args = inspect.getargspec(func)[0][1:]
# 	max_arg_len = max(len(arg) for arg in args)
# 	if pcov.any() != None:
# 		perr = np.sqrt(np.diag(pcov))
# 	else:
# 		perr = "NA"
		
# 	for ii, arg in enumerate(args):
# 		parmName = str(arg)
# 		parmVal  = '%.3f'%popt[ii]
# 		if pcov == None:
# 			parmText += parmName.ljust(max_arg_len+2)+'='.ljust(2)+parmVal+'\n'
# 		else:
# 			perrVal  = '%.3f'%perr[ii]
# 			parmText += parmName.ljust(max_arg_len+2)+'='.ljust(2)+parmVal+" +/- "+perrVal+'\n'
# 	print parmText
# 	return parmText

def print_parm(func, popt, pcov=None):
	parmText = ""
	args = inspect.getargspec(func)[0][1:]
	max_arg_len = max(len(arg) for arg in args)
	perr = np.sqrt(np.diag(pcov))
		
	for ii, arg in enumerate(args):
		parmName = str(arg)
		parmVal  = '%.3f'%popt[ii]
		perrVal  = '%.3f'%perr[ii]
		parmText += parmName.ljust(max_arg_len+2)+'='.ljust(2)+parmVal+" +/- "+perrVal+'\n'
	print(parmText)
	return parmText

def plot_fit(xdata, ydata, func, parm, points=None, fmt='b-'):
	gs = gridspec.GridSpec(20, 1)
	fig = plt.figure(facecolor='white')
	ax_fit = fig.add_subplot(gs[5:, 0])
	ax_res = fig.add_subplot(gs[:4, 0])

	xfit = np.linspace(min(xdata), max(xdata), 1000)
	yfit = func(xfit, *parm)
	yres = ydata-func(xdata, *parm)

	ax_fit.plot(xdata, ydata, fmt, label="Data")
	ax_fit.plot(xfit, yfit, 'r', lw=1.5)
	ax_res.plot(xdata, yres, fmt)
	ax_res.plot([xdata[0], xdata[-1]], [0, 0], '0.8', lw=1.5)
	if points != None: 
		ax_fit.plot(xdata[points], ydata[points], 'ro')

	setticks(ax_res, [[], 'auto'])

	plt.show()

def make_fit_data(func, popt, range, pts=1000):
	xfit = np.linspace(range[0], range[1], 1000)
	yfit = func(xfit, *popt)
	return np.array([xfit, yfit])

def show_fit(xdata, ydata, func, popt, pcov=None, points=None):
	print_parm(func, popt, pcov)
	plot_fit(xdata, ydata, func, popt, points)

def save_fit_txt(xdata, ydata, func, popt, pcov, save_dir, name=""):
	xfit = np.linspace(min(xdata), max(xdata), 1000)
	yfit = func(xfit, *popt)

	np.savetxt(save_dir+'/'+name+"_popt.txt", popt)
	np.savetxt(save_dir+'/'+name+"_pcov.txt", pcov)
	np.savetxt(save_dir+'/'+name+"_data.txt", np.array([xdata, ydata]))
	np.savetxt(save_dir+'/'+name+"_fit.txt", np.array([xfit, yfit]))

	file = open(save_dir+'/'+name+"_func.py", 'w')
	for line in inspect.getsourcelines(func)[0]:
		file.write(line)
	file.close()
	return 1





