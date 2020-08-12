import numpy as np
import matplotlib.pyplot as plt
from .jplot import *

fig = plt.figure()
row, col = 3, 1
# row, col = 1, 3

ax_ind = 0
for ii in range(row):
	for jj in range(col):
		ax_ind += 1
		ax = fig.add_subplot(row, col, ax_ind)
		setticks(ax, [[.2, .4, .6, .8], [.2, .4, .6, .8]])

# for ax in fig.get_children():
# 	print ax.get_position()

print(fig.get_children())

def sort_axes(fig):
	axes = fig.get_axes()

def setpanellabel(fig, label, axis=1, gap=True):
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


setpanellabel(fig, ['x label', 'y label'], axis=1, gap=0)
plt.show()