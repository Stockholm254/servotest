import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np

fcolor = '#A6A0D8'
ecolor = '#353D91'

##################################################
###                 Line Style                 ###
##################################################
jls = {
	"ebar": {'fmt':'o', 'mfc':fcolor, 'mew':1, 'ms':6, 'mec':ecolor, 'ecolor':ecolor, 'elinewidth':1, 'capsize':0}	
}

##################################################
###                Figure Setup                ###
##################################################
FIG_LOGBOOK   = {'tight_layout': True,  'facecolor': 'white', 'figsize': (5.6, 4.2)}
FIG_LARGE     = {'tight_layout': True,  'facecolor': 'white', 'figsize': (16., 9.)}
FIG_IPYTHON   = {'tight_layout': True,  'facecolor': 'white', 'figsize': (10., 7.5)}
FIG_PRLSINGLE = {'tight_layout': False, 'facecolor': 'white', 'figsize': (3.5, 2.)}
FIG_NORMAL    = {'tight_layout': True,  'facecolor': 'white', 'figsize': (4.0, 3.0)}

##################################################
###                Color Scheme                ###
##################################################
jcc = {
	"reds": ['#fee5d9', '#fcae91', '#fb6a4a', '#de2d26', '#a50f15'], 
	"yelloworangereds": ['#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#bd0026'], 
	"purplereds": ['#f1eef6', '#d7b5d8', '#df65b0', '#dd1c77', '#980043'], 
	"bluepurples": ['#edf8fb', '#b3cde3', '#8c96c6', '#8856a7', '#810f7c'], 
	"redpurples": ['#feebe2', '#fbb4b9', '#f768a1', '#c51b8a', '#7a0177'], 
	"purples": ['#f2f0f7', '#cbc9e2', '#9e9ac8', '#756bb1', '#54278f'], 
	"yellowgreenblues": ['#ffffcc', '#a1dab4', '#41b6c4', '#2c7fb8', '#253494'], 
	"blues": ['#eff3ff', '#bdd7e7', '#6baed6', '#3182bd', '#08519c'], 
	"greenblues": ['#f0f9e8', '#bae4bc', '#7bccc4', '#43a2ca', '#0868ac'], 
	"purpleblues": ['#f1eef6', '#bdc9e1', '#74a9cf', '#2b8cbe', '#045a8d'], 
	"purplebluegreens": ['#f6eff7', '#bdc9e1', '#67a9cf', '#1c9099', '#016c59'], 
	"bluegreens": ['#ffffcc', '#c2e699', '#78c679', '#31a354', '#006837'], 
	"yellowgreens": ['#ffffcc', '#c2e699', '#78c679', '#31a354', '#006837'], 
	"greens": ['#edf8e9', '#bae4b3', '#74c476', '#31a354', '#006d2c'], 
	"yelloworangebrowns": ['#ffffd4', '#fed98e', '#fe9929', '#d95f0e', '#993404'], 
	"oranges": ['#feedde', '#fdbe85', '#fd8d3c', '#e6550d', '#a63603'], 
	"orangereds": ['#fef0d9', '#fdcc8a', '#fc8d59', '#e34a33', '#b30000'], 
	"greys": ['#f7f7f7', '#cccccc', '#969696', '#636363', '#252525'], 
}

# Sorted color scheme according to hue
jcc_keys = ['reds', 
		   'yelloworangereds', 
		   'purplereds', 
		   'bluepurples', 
		   'redpurples', 
		   'purples', 
		   'yellowgreenblues', 
		   'blues', 
		   'greenblues', 
		   'purpleblues', 
		   'purplebluegreens', 
		   'yellowgreens', 
		   'bluegreens', 
		   'greens', 
		   'yelloworangebrowns', 
		   'oranges', 
		   'orangereds', 
		   'greys']

##################################################
###               Usefule labels               ###
##################################################
lb_deltaMHz = "$\delta$ (MHz)"
lb_cratekHz = "Count Rate (kHz)"
lb_tauus = "$\\tau$ ($\mu$s)"
lb_transpercent = "Relative Transmission (%)"
	
##################################################
###              Utility Functions             ###
##################################################
def markerstyle(linestyle, colorstyle):
	ms = jls[linestyle]
	ms['mfc'] = colorstyle[0]
	ms['mec'] = colorstyle[1]
	ms['ecolor'] = colorstyle[1]
	return ms

##################################################
###                 Plot Style                 ###
##################################################

### Nature ###
LINEWIDTH_NAT     = 0.75
LABELFONTSIZE_NAT = 8.5
TICKFONTSIZE_NAT  = 7.0
LABELFONTDIC      = {'family': 'sans-serif', 
					 'color':  'k', 
					 'weight': 'bold', 
				     'size': 10}
def SetRCParms_nat(): # Set global plotting properties for Nature figures
	mpl.rcParams['axes.linewidth']    = 0.75
	mpl.rcParams['xtick.major.size']  = 2.4
	mpl.rcParams['xtick.major.width'] = 0.3
	mpl.rcParams['xtick.minor.size']  = 1.2
	mpl.rcParams['xtick.minor.width'] = 0.3
	mpl.rcParams['xtick.labelsize']   = 7.0
	mpl.rcParams['ytick.major.size']  = 2.4
	mpl.rcParams['ytick.major.width'] = 0.3
	mpl.rcParams['ytick.minor.size']  = 1.2
	mpl.rcParams['ytick.minor.width'] = 0.3
	mpl.rcParams['ytick.labelsize']   = 7.0
	mpl.rcParams['xtick.direction']   = 'in'
	mpl.rcParams['ytick.direction']   = 'in'
	mpl.rcParams['axes.labelsize']    = 8.5
	mpl.rcParams['lines.linewidth']   = 0.75













