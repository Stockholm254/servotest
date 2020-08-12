import matplotlib.pyplot as plt
import numpy as np
import scipy.misc
from matplotlib.colors import ColorConverter
from .jplot import *
from os import getcwd
from .jstyle import *
import colorsys

def lin(n, nu):
	return n*nu

xx = np.linspace(1, 10, 10)

fig = plt.figure(**fig_default)
ax = fig.add_subplot(111)

# print colorsys.hls_to_rgb(.3,.5,.5), '=================='
# print colorsys.rgb_to_hls(1,1,0), '=================='

for ii in range(24)[::4]:
	yy = lin(xx, ii)
	yerr = 2*xx

	fcolor = colorsys.hls_to_rgb(ii*10/350., .8, .9)
	ecolor = colorsys.hls_to_rgb(ii*10/350., .4, .9)

	ax.errorbar(xx, yy, yerr=yerr, fmt='o',
		mfc=fcolor, mew=2, ms=6, mec=ecolor,
		ecolor=ecolor, elinewidth=2, capsize=0)

# plt.savefig(getcwd()+'/sample/figure_1.png')
plt.show()
