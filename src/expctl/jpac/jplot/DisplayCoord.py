import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

def ShowDisplayCoord(figure):
	coordax = figure.add_axes([0,0,1,1])
	loc_major = MultipleLocator(1e-1)
	loc_minor = MultipleLocator(2e-2)
	coordax.xaxis.set_major_locator(loc_major)
	coordax.yaxis.set_major_locator(loc_major)
	coordax.xaxis.set_minor_locator(loc_minor)
	coordax.yaxis.set_minor_locator(loc_minor)
	coordax.grid(b=True, which='major', color='0.6', linestyle='-')
	coordax.grid(b=True, which='minor', color='0.9', linestyle='-')
