"""
Simple image viewer for absorption and fluorescence images
Ariel Sommer 2016
version 1.1

New features
Has super absorption mode where first image is a pre-image
"""

import wx
import wx.lib.buttons as buttons
import os
import inspect
import math
import numpy as np
# from scipy.ndimage import imread
from matplotlib.image import imread
import _thread as thread
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

import matplotlib
matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
from matplotlib.figure import Figure

#from mpltools import style
#style.use('dark_background')

from .helperfunctions import *
from pathlib import Path
#http://www.wxpython.org/docs/api/wx-module.html
#http://wiki.wxpython.org/Non-Blocking%20Gui

# Camera resolution
cam_x = 1280.
cam_y = 960.
aspect_ratio = cam_x/cam_y
# Show resolution
show_x = 1080
show_y = 810

############################################################
###                    Utility Classes                   ###
############################################################
class ImagePanel(wx.Panel):
	'''
	Image panel for embeding matplotlib plot
	'''
	def __init__(self, parent, size):
		wx.Panel.__init__(self, parent, size=wx.Size(*size))
		self.figure = Figure()
		self.axes = self.figure.add_subplot(111)
		self.axes.get_xaxis().set_visible(False)
		self.axes.get_yaxis().set_visible(False)
		self.figure.subplots_adjust(left=.001, bottom=.001, right=.999, top=.999)
		self.canvas = FigureCanvas(self, -1, self.figure)
		self.toolbar = NavigationToolbar(self.canvas)
		self.toolbar.Hide()
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.canvas, 1, wx.LEFT|wx.TOP|wx.GROW)
		self.SetSizer(self.sizer)
		self.Fit()
	
class Entry(object):
	'''
	Represents one entry in the history list.
	Includes a collection of Images with names
	'''
	def __init__(self, img_array, name, mode, frameNames):
		self.images = img_array
		self.name = name
		self.mode = mode
		self.frameNames = frameNames

MODE_ABSORPTION   = "absorption"
MODE_FLUORESCENCE = "fluorescence"
MODE_OTHER        = "other"

MAX_HISTORY = 10

myEVT_LOAD = wx.NewEventType()
EVT_LOAD = wx.PyEventBinder(myEVT_LOAD, 1)
class LoadEvent(wx.PyCommandEvent):
	"""Event to signal that an image should be loaded"""
	def __init__(self, etype, eid, value=None):
		wx.PyCommandEvent.__init__(self, etype, eid)
		self._value = value
	def GetValue(self):
		return self._value

myEVT_CLOSE = wx.NewEventType()
EVT_MYCLOSE = wx.PyEventBinder(myEVT_CLOSE, 1)
class CloseEvent(wx.PyCommandEvent):
	"""Event to signal that the frame should close"""
	def __init__(self, etype, eid):
		wx.PyCommandEvent.__init__(self, etype, eid)

def Colorize(a, cmap="jet"):
  '''
  Convert the 2D array a to an rgb array using a colormap
  a: integers from 0 to 255
  returns: RGB array of integers from 0 to 255
  '''
  SM = ScalarMappable(norm=Normalize(0,255),cmap=cmap)
  rgb = SM.to_rgba(a, bytes=True)[:,:,0:3]
  return rgb

############################################################
###                  Image Viewer GUI                    ###
############################################################
class ImageViewer(wx.Frame):
	def __init__(self, app, closeable=True):
		# History inventory
		self.history = []        
		# Image properties
		self.x0 = 0
		self.x1 = 960
		self.y0 = 0
		self.y1 = 1280
		self.scale_factor = show_x/cam_x
		
		# GUI properties
		style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLIP_CHILDREN
		if closeable:
			style = style | wx.CLOSE_BOX
		
		# wx.Frame.__init__(self, None, title="Image Viewer", style=style)
		wx.Frame.__init__(self, None, title="Image Viewer")
		self.closeable = closeable
		# self.icon = wx.Icon("imageviewer.png", wx.BITMAP_TYPE_PNG)
		# self.SetIcon(self.icon)
		self.app = app
		
		# Main sizer
		self.sizer_main = wx.BoxSizer(wx.HORIZONTAL)
		
		#Control panel
		self.panell = wx.Panel(self, wx.ID_ANY)
		#Left side sizer
		self.sizer_left = wx.BoxSizer(wx.VERTICAL)
		#Objects
		#File and frame selection
		self.loadButton = wx.Button(self.panell,label="Load")
		self.frame_label = wx.StaticText(self.panell, label="\n\tImage sub-frames")
		self.frame_list = wx.ListBox(self.panell, size=(200,80))
		self.frame_list.Append("_ "*20)
		self.hist_label =wx.StaticText(self.panell, label="\n\tHistory stack")
		self.hist_list = wx.ListBox(self.panell, size=(200,300))
		#Fitting result
		# self.ln_fitresult = wx.StaticLine(self.panell, -1, style=wx.LI_HORIZONTAL)
		self.ln_fit        = wx.StaticLine(self.panell, -1, style=wx.LI_HORIZONTAL)
		self.ChkBox_fit    = wx.CheckBox(self.panell, label='Fit')
		self.txt_fitxtitle = wx.StaticText(self.panell, label="Fit X")
		self.txt_fitx      = wx.StaticText(self.panell, label="-"*30, size=(200,100))
		self.txt_fitytitle = wx.StaticText(self.panell, label="Fit Y")
		self.txt_fity      = wx.StaticText(self.panell, label="-"*30, size=(200,100))
		#Add to sizer
		# self.sizer_left.Add(self.ln_fitresult, 0, wx.ALL|wx.EXPAND, border=5)
		self.sizer_left.Add(self.loadButton, 0, wx.EXPAND, border=5)
		self.sizer_left.Add(self.frame_label, 0, wx.EXPAND, border=5)
		self.sizer_left.Add(self.frame_list, 0, wx.ALL|wx.EXPAND, border=5)
		self.sizer_left.Add(self.hist_label, 0, wx.EXPAND, border=5)
		self.sizer_left.Add(self.hist_list, 0, wx.ALL|wx.EXPAND, border=5)
		self.sizer_left.Add(self.ln_fit, 0, wx.ALL|wx.EXPAND, border=5)
		self.sizer_left.Add(self.ChkBox_fit, 0, wx.ALL|wx.EXPAND, border=5)
		self.sizer_left.Add(self.txt_fitxtitle, 0, wx.ALL|wx.EXPAND, border=5)
		self.sizer_left.Add(self.txt_fitx, 0, wx.ALL|wx.EXPAND, border=5)
		self.sizer_left.Add(self.txt_fitytitle, 0, wx.ALL|wx.EXPAND, border=5)
		self.sizer_left.Add(self.txt_fity, 0, wx.ALL|wx.EXPAND, border=5)
		#Bind functions
		self.loadButton.Bind(wx.EVT_BUTTON, self.onLoadButton)
		self.frame_list.Bind(wx.EVT_LISTBOX, self.onFrameList)
		self.hist_list.Bind(wx.EVT_LISTBOX, self.onHistList)
		#Set left sizer
		self.panell.SetSizerAndFit(self.sizer_left)
		self.sizer_left.Fit(self.panell)
		
		#Image side panel
		self.panelr = wx.Panel(self, wx.ID_ANY)
		#Image side sizer
		self.sizer_right = wx.GridBagSizer(hgap=1, vgap=1)
		self.sizer_img   = wx.BoxSizer(wx.VERTICAL)
		self.sizer_fitx  = wx.BoxSizer(wx.VERTICAL)
		self.sizer_fity  = wx.BoxSizer(wx.VERTICAL)
		self.sizer_home  = wx.BoxSizer(wx.VERTICAL)
		#Image Object
		self.imgCtrl = ImagePanel(self.panelr, size=(show_x, show_y))
		self.fit_x = ImagePanel(self.panelr, size=(show_x, 100))
		self.fit_y = ImagePanel(self.panelr, size=(100, show_y))
		#Initial image
		self.image = self.imgCtrl.axes.imshow(np.random.rand(show_y, show_x), interpolation='none')
		#Home button
		home_ico_path = Path(__file__).parent/"home.png"
		bmp = wx.Bitmap(str(home_ico_path), wx.BITMAP_TYPE_ANY)
		# self.btn_home = buttons.GenBitmapButton(self.panelr, wx.ID_ANY, bitmap=bmp, size=(100,100))
		self.btn_home = wx.BitmapButton(self.panelr, wx.ID_ANY, bitmap=bmp, size=(100,100))
		#Add obj to right sizer
		self.sizer_img.Add(self.imgCtrl, 0, wx.EXPAND)
		self.sizer_fitx.Add(self.fit_x, 0, wx.EXPAND)
		self.sizer_fity.Add(self.fit_y, 0, wx.EXPAND)
		self.sizer_home.Add(self.btn_home, 1, wx.EXPAND)
		#Add to right sizer
		self.sizer_right.Add(self.sizer_img, pos=(0,0), flag=wx.EXPAND)
		self.sizer_right.Add(self.sizer_fitx, pos=(1,0), flag=wx.EXPAND)
		self.sizer_right.Add(self.sizer_fity, pos=(0,1), flag=wx.EXPAND)
		self.sizer_right.Add(self.sizer_home, pos=(1,1), flag=wx.EXPAND)
		#Bind mouse event for zoom
		self.imgCtrl.axes.figure.canvas.mpl_connect('button_press_event', self.OnZoom)
		self.btn_home.Bind(wx.EVT_BUTTON, self.onResetZoom)
		#Set right side panel sizer
		self.panelr.SetSizerAndFit(self.sizer_right)
		self.sizer_right.Fit(self.panelr)
		
		#Panel sizers
		self.sizer_panelr = wx.BoxSizer(wx.VERTICAL)
		self.sizer_panell = wx.BoxSizer(wx.VERTICAL)
		self.sizer_panelr.Add(self.panelr, 1, wx.ALL|wx.EXPAND)
		self.sizer_panell.Add(self.panell, 1, wx.ALL|wx.EXPAND)
		
		#Add right sizer to main sizer
		self.sizer_main.Add(self.sizer_panell, 0, flag=wx.EXPAND)
		self.sizer_main.Add(self.sizer_panelr, 0, flag=wx.EXPAND)
		
		#Set main sizer
		self.SetSizerAndFit(self.sizer_main)
		self.sizer_main.Fit(self)
		
		#Bind buttons
		self.Bind(EVT_LOAD, self.onLoadEvent)
		self.Bind(EVT_MYCLOSE, self.onCloseSignal)
		self.Bind(wx.EVT_CLOSE, self.onGUIClose)
		self.imgCtrl.Bind(wx.EVT_MOUSE_EVENTS, self.OnZoom)
		
		self.Show(True)

	def GUI_loop(self):
		self.app.MainLoop()
		
	def onGUIClose(self, event):
		if event.CanVeto() and not self.closeable:
			dlg = wx.MessageDialog(self,
				"Closing " + self.GetTitle() +" from the GUI is disabled",
				"Note", wx.OK|wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()
		else:
			self.Destroy()

	def onCloseSignal(self, event):
		self.Close(force=True)

	def onFrameList(self, event):
		self.drawSelectedFrame()

	def onHistList(self,event):
		self.showSelectedEntry()
		self.drawSelectedFrame()
		self.fitSelectedFrame()

	def onLoadEvent(self, event):
		self.loadImages(*event.GetValue())

	def onLoadButton(self, event):
		wildcard = "PGM files (*.PGM)|*.pgm;*.PGM"
		# dialog = wx.FileDialog(None, "Select the image files",
		#                        wildcard=wildcard,
		#                        style=wx.OPEN|wx.FD_MULTIPLE)
		dialog = wx.FileDialog(None, "Select the image files",
							   wildcard=wildcard)
		do_load=False
		if dialog.ShowModal() == wx.ID_OK:
			fnames = dialog.GetPaths()
			nimages = len(fnames)
			if nimages == 3:
				mode = MODE_ABSORPTION
				name = os.path.split(fnames[0])[1][:-9]
			elif nimages == 2:
				mode = MODE_FLUORESCENCE
				name = os.path.split(fnames[0])[1][:-9]
			else:
				mode = MODE_OTHER
				name = os.path.split(fnames[0])[1]
			do_load = True

		dialog.Destroy()
		if do_load:
			self.loadImages(fnames, name, mode)
			
	def onPan(self, event):
		self.imgCtrl.toolbar.pan()
			
	def onZoom(self, event):
		self.imgCtrl.toolbar.zoom()
		
	def onResetZoom(self, event):
		self.imgCtrl.toolbar.home()
		self.x0, self.x1 = 0, cam_y
		self.y0, self.y1 = 0, cam_x
		self.scale_factor = show_x/cam_x
		
		self.drawSelectedFrame()
		self.fitSelectedFrame()
	
	def loadImages(self, filenames, name, mode):
		if len(filenames) == 0:
		  print("no files to load")
		  return
		  
		# Load ndarrays from files
		imgArrays = []
		for fname in filenames:
			# imgArrays.append(np.flipud(imread(fname, mode="RGB")))
			if str(fname)[-3:]=="png":
				print("loaded png")
				im=imread(fname)
				imgArrays.append(np.flipud(im)) #/1.0*2**16
			else:
				imgArrays.append(np.flipud(imread(fname)/255.))
		
		# Define additional arrays
		if mode == MODE_ABSORPTION:
			absArray = (imgArrays[0]-imgArrays[2])/(imgArrays[1]-imgArrays[2]+1e-6)
			imgArrays.insert(0, absArray)
			self.image.set_cmap('gray')
		elif mode == MODE_FLUORESCENCE:
			fore = np.array(imgArrays[0])
			back = np.array(imgArrays[1])
			fore[fore < back] = back[fore < back]
			diff = fore - back
			self.image.set_cmap('jet')
			imgArrays.insert(0, diff)
			
		# Define frame names
		if mode == MODE_ABSORPTION:
			frameNames = ["Absorption image","Probe with atoms","Probe without atoms","Dark field"]
		elif mode == MODE_FLUORESCENCE:
			frameNames = ["Fluorescence image", "Probe with atoms", "Probe without atoms"]
		else:
			frameNames = [str(i) for i in range(len(imgArrays))]
		
		# Update history
		entry = Entry(imgArrays, name, mode, frameNames)
		self.history.insert(0, entry)
		# Update history list UI
		self.hist_list.Insert(name,0)
		self.hist_list.Select(0)
		if len(self.history) > MAX_HISTORY:
		  x = self.history.pop()
		  del x
		  self.hist_list.Delete(self.hist_list.GetCount()-1)
		self.Refresh()
				
		# Update drawing
		self.showSelectedEntry()
		self.drawSelectedFrame()
		self.fitSelectedFrame()

	def showSelectedEntry(self):
		ind = self.hist_list.GetSelection()
		entry = self.history[ind]

		# Populate the frame list
		self.frame_list.Clear()
		for frameName in entry.frameNames:
			self.frame_list.Append(frameName)
		self.frame_list.Select(0)
		self.Refresh()

	def drawSelectedFrame(self):
		try:
			entry = self.history[self.hist_list.GetSelection()]
		except IndexError:
			return

		frame_ind = self.frame_list.GetSelection()
		img = entry.images[frame_ind]
		img = img[self.x0:self.x1, self.y0:self.y1]
		self.image.set_data(img)
		
		self.imgCtrl.axes.figure.canvas.draw()
	  
	def fitSelectedFrame(self):
		# Get image array
		try:
			entry = self.history[self.hist_list.GetSelection()]
		except IndexError:
			return
		frame_ind = self.frame_list.GetSelection()
		arr = entry.images[0]
		arr = arr[self.x0:self.x1, self.y0:self.y1]
		# Compute cross-sections
		self.sumsX=np.sum(arr, axis=0)
		self.sumsY=np.sum(arr, axis=1)
		# Index list
		indsX=np.arange(self.x0, self.x0+len(self.sumsX))
		indsY=np.arange(self.y0, self.y0+len(self.sumsY))[::-1] # Y plot is vertical and top down
		
		# Fittings (from Jon's GaussianFitter.py)
		# Set default empty list for fit in case of error
		pltxx = np.linspace(indsX[0], indsX[-1], 500)
		pltyy = np.linspace(indsY[0], indsY[-1], 500)
		pltxxFit = np.zeros(500)
		pltyyFit = np.zeros(500)
		ParmStrX = ''
		ParmStrY = ''
		# GENERATE INITIAL GUESSES FOR FITTING GAUSSIANS
		Xguesses=fitfunc_guess(indsX,self.sumsX)
		Yguesses=fitfunc_guess(indsY,self.sumsY)
		# Fit the curve
		try:
			if self.ChkBox_fit.GetValue():
				poptX, pcovX = curve_fit(fitfunc, indsX, self.sumsX, p0=Xguesses)
				poptY, pcovY = curve_fit(fitfunc, indsY, self.sumsY, p0=Yguesses)
				# Fitting result
				pltxxFit = fitfunc(pltxx, *poptX)
				pltyyFit = fitfunc(pltyy, *poptY)
				# Update fit result
				ParmStrX = ParmToStr(fitfunc, poptX, pcovX)
				ParmStrY = ParmToStr(fitfunc, poptY, pcovY)
		except Exception as e:
		  	print("Caught runtime error during fitting: \n" + str(e))
		
		# Update fit resultself.txt_fitx.SetLabel(str(poptX))
		self.txt_fitx.SetLabel(ParmStrX)
		self.txt_fity.SetLabel(ParmStrY)
		# self.sizer_left.Layout()
		# Update plot
		self.fit_x.axes.cla()
		self.fit_y.axes.cla()
		# Plot data
		self.fit_x.axes.plot(indsX, self.sumsX, 'c.')
		self.fit_y.axes.plot(self.sumsY, indsY, 'c.')
		# Plot fit
		if self.ChkBox_fit.GetValue():
			self.fit_x.axes.plot(pltxx, pltxxFit, 'w', linewidth=2)
			self.fit_y.axes.plot(pltyyFit, pltyy, 'w', linewidth=2)
		# Set plot range
		self.fit_x.axes.set_xlim(indsX[0], indsX[-1])
		self.fit_y.axes.set_ylim(indsY[-1], indsY[0])
		# Redraw the canvas
		self.fit_x.axes.figure.canvas.draw()
		self.fit_y.axes.figure.canvas.draw()
		
	def OnZoom(self, event):
		zoom = 0
		if event.dblclick:
			if event.button == 1:
				zoom = 1
			elif event.button == 3:
				zoom = -1
		if zoom != 0:
			# Locate the new center
			yy, xx = event.xdata, event.ydata # New center relative to current image
			yy, xx = yy/self.scale_factor, xx/self.scale_factor # Index of new center relative to current image
			newxc, newyc = self.x0+xx, self.y0+yy # Absolute index of new center
			# Scale factor
			rsf = 1.5**zoom # Relative zoom factor
			self.scale_factor = self.scale_factor*rsf
			# Calculate new image boundary
			self.x0 = int(max(int(newxc)-int(960./2./self.scale_factor), 0))
			self.x1 = int(min(int(newxc)+int(960./2./self.scale_factor), cam_y))
			self.y0 = int(max(int(newyc)-int(1280./2./self.scale_factor), 0))
			self.y1 = int(min(int(newyc)+int(1280./2./self.scale_factor), cam_x))
			# Update UI
			self.drawSelectedFrame()
			self.fitSelectedFrame()

# helper function
def ParmToStr(func, popt, pcov):
	parm_str = ''
	parm_name = inspect.getargspec(func)[0][1:]
	for ii in range(len(parm_name)):
		name = parm_name[ii]
		val  = sd(popt[ii], 5)
		err  = sd(pcov[ii, ii]**0.5, 3)
		parm_str += name+'='+val+' +/- '+err+'\n'
	return parm_str
def sd(num, digit):
	return eval('\'%.'+str(digit)+'g\' %'+str(num))

# signal functions
def loadImage(viewer, filenames, name):
	N=len(filenames)
	if N==3:
		mode = MODE_ABSORPTION
	elif N==2:
		mode = MODE_FLUORESCENCE
	else:
		mode = MODE_OTHER
		
	evt = LoadEvent(myEVT_LOAD, -1, (filenames, name, mode))
	wx.PostEvent(viewer, evt)

def closeViewer(viewer):
	wx.PostEvent(viewer,CloseEvent(myEVT_CLOSE, -1))

# launcher functions
def createViewer(closeable=True):
	app=wx.App(False)
	viewer=ImageViewer(app, closeable=closeable)
	return viewer
	
def launchViewer():
	app=wx.App(False)
	viewer=ImageViewer(closeable=False)
	thread.start_new_thread(app.MainLoop,())
	return viewer
	
def standaloneViewer():
	app = wx.App(False)
	ImageViewer(app, closeable=True)
	app.MainLoop()

# Tests
def __testLoadSignal():
	#simulate what the camera server would do
	viewer = launchViewer()
	fnames = ["2016-04-01 T 19-23-37-061_6_IMG1.PGM"]
	fnames.append("2016-04-01 T 19-23-37-061_6_IMG2.PGM")
	fnames.append("2016-04-01 T 19-23-37-061_6_IMG3.PGM")
	import time
	time.sleep(1)
	for i in range(4):
		loadImage(viewer, fnames, "img"+str(i), MODE_ABSORPTION)
		time.sleep(1)
	time.sleep(5)
	closeViewer(viewer)
	time.sleep(1)
def __testServerThread():
	app = wx.App(False)
	viewer = ImageViewer(closeable=True)
	thread.start_new_thread(__serverThread, (viewer,))
	app.MainLoop()
def __serverThread(viewer):
	fnames = ["2016-04-01 T 19-23-37-061_6_IMG1.PGM"]
	fnames.append("2016-04-01 T 19-23-37-061_6_IMG2.PGM")
	fnames.append("2016-04-01 T 19-23-37-061_6_IMG3.PGM")
	import time
	time.sleep(1)
	for i in range(4):
		loadImage(viewer, fnames, "img"+str(i), MODE_ABSORPTION)
		time.sleep(1)
	time.sleep(5)
	# closeViewer(viewer)
	time.sleep(1)
	
if __name__=="__main__":
	standaloneViewer()
