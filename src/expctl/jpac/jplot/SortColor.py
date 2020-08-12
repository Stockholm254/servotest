import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
import numpy as np
from .jstyle import jcc

# for key in jcc:
# 	c = jcc[key][-1]
# 	print mcolors.rgb_to_hsv(mcolors.hex2color(c))

keys = list(jcc.keys())
keys_sorted = sorted(keys, key=lambda x: -mcolors.rgb_to_hsv(mcolors.hex2color(jcc[x][-1]))[0])

# print keys_sorted

xx = np.array([0, 1])
yy = np.array([0, 1])

for ii, key in enumerate(keys_sorted):
	# print "\""+key+"\""+":"+" "+str(jcc[key])+", "
	plt.plot(xx, yy+0.1*ii, jcc[key][-1], lw=2)

plt.show()