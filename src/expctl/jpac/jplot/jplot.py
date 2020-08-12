import numpy as np
import matplotlib.pyplot as plt
from os.path import exists
from .jstyle import *
from ..jutil import *

def jplot(ax, xdata, ydata, **kwargs):
	try: # try bin the data if bin number is specified in kwargs
		bin_num = kwargs['bin_num']
		xdata = bin_data(xdata, bin_num)
		ydata = bin_data(ydata, bin_num)
		del kwargs['bin_num']
	except:
		pass

	ax.plot(xdata, ydata, **kwargs)

def jerrbar(ax, xdat, ydat, xerr=[], yerr=[], color=jcc[jcc_keys[0]], label=''):
	if len(xerr) == 0:
		xerr = np.zeros(len(xdat))
	if len(yerr) == 0:
		yerr = np.zeros(len(ydat))

	ax.errorbar(xdat, ydat, label=label, xerr=xerr, yerr=yerr, 
				linestyle='none', 
				marker='o', ms=5, mew=.9, elinewidth=.9, mfc=color[-4], mec=color[-1], ecolor=color[-1], capsize=None)

def jplot2d(ax, data, extent=[0., 1., 0, 1.], aspect=1., label=None):
	# Calculate mesh grid
	data_y, data_x = data.shape
	x0 = extent[0]
	x1 = extent[1]+(extent[1]-extent[0])/(data_x-1)
	y0 = extent[2]
	y1 = extent[3]+(extent[3]-extent[2])/(data_y-1)
	xlist = np.linspace(x0, x1, data_x+1)
	ylist = np.linspace(y0, y1, data_y+1)
	xv, yv = np.meshgrid(xlist, ylist)
	# Plot and set aspect ratio
	im = ax.pcolor(xv, yv, data)
	ax.set_xlim(x0, x1)
	ax.set_ylim(y0, y1)
	ax.set_aspect(aspect*(x1-x0)/(y1-y0))
	# Set labels
	setlabels(ax, label)

	return im

######################################
###        Helper Functions        ###
######################################

def setlims(ax, xlim=None, ylim=None):
	if xlim != None:
		ax.set_xlim(xlim[0], xlim[1])
	if ylim != None:
		ax.set_ylim(ylim[0], ylim[1])

def setticks(ax, ticks=['auto', 'auto']):
	if ticks[0] != 'auto':
		ax.xaxis.set_ticks(ticks[0])
	if ticks[1] != 'auto':
		ax.yaxis.set_ticks(ticks[1])

def setlabels(ax, label):
	if label != None:
		ax.set_title(label[2]) if (len(label)==3) else None
		ax.set_xlabel(label[0])
		ax.set_ylabel(label[1])

def setpanellabels(fig, label, axis=0, gap=True):
	if label == None:
		return

	axes = fig.get_axes()

	if axis == 0:
		for ii, ax in enumerate(axes):
			ax.set_xlabel(label[0])
			if ii != 0:
				ax.yaxis.set_ticklabels([])
			else:
				ax.set_ylabel(label[1])
	elif axis == 1:
		for ii, ax in enumerate(axes):
			ax.set_ylabel(label[1])
			if ii != len(axes)-1:
				ax.xaxis.set_ticklabels([])
			else:
				ax.set_xlabel(label[0])

	if gap == False:
		plt.subplots_adjust(hspace=0, wspace=0)





