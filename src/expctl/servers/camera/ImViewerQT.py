# -*- coding: utf-8 -*-
"""
V0 of Camera server with Qt and pyqtgraph
"""

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, QMetaObject, Qt, Q_ARG
import numpy as np
import os
import time

# Interpret image data as row-major instead of col-major
#pg.setConfigOptions(imageAxisOrder='row-major')
pg.mkQApp()

## Define main window class from template
path = os.path.dirname(os.path.abspath(__file__))
uiFile = os.path.join(path, 'viewer.ui')
WindowTemplate, TemplateBaseClass = pg.Qt.loadUiType(uiFile)

class MockCamera:

	def __init__(self, Nx=1280, Ny=960):
		self.Nx = Nx
		self.Ny = Ny
		x = np.arange(Nx)
		y = np.arange(Ny)
		self.xx, self.yy = np.meshgrid(x, y, indexing='ij')

	@staticmethod
	def gauss2d(x, y, mu=(0, 0), sig=(1., 1.)):
		mux, muy = mu
		sigx, sigy = sig
		return np.exp(-0.5*( ((x-mux)/sigx)**2 + ((y-muy)/sigy)**2 )) #/(2*np.pi*sigx*sigy)

	def get(self, sigma=(30, 80), poisition_noise=20, amplitude_noise=0.1):
		if poisition_noise>0:
			mu = (np.random.normal(self.Nx/2, poisition_noise), np.random.normal(self.Ny/2, poisition_noise))
		else:
			mu = (self.Nx/2 ,self.Ny/2)

		z = MockCamera.gauss2d(self.xx, self.yy, mu=mu, sig=sigma)
		return z*(1 + amplitude_noise*np.random.rand())+ np.random.random(z.shape)*amplitude_noise

class Worker(QObject):
	finished = pyqtSignal()
	result = pyqtSignal(object)

	def __init__(self, parent=None):
		#super(self.__class__, self).__init__(parent)
		super(Worker, self).__init__(parent)
		self.cam = MockCamera()

	def acquire(self, delay):
		print("Is interrtup requested: {}".format(QThread.currentThread().isInterruptionRequested())) 
		while not QThread.currentThread().isInterruptionRequested():
			image = self.cam.get()
			self.result.emit(image)
			print("Acquired")
			QThread.msleep(int(1000*delay))
		print("Exiting...")

	
	@pyqtSlot(float)
	def start(self, fps):
		print("starting with fps: {}".format(fps))
		delay = 1.0/fps
		self.acquire(delay)

class MainWindow(TemplateBaseClass):  
	start_acquire = pyqtSignal(float)
	stop_acquire = pyqtSignal()

	def __init__(self):
		TemplateBaseClass.__init__(self)
		self.setWindowTitle('pyqtgraph example: Qt Designer')
		
		# Create the main window
		self.ui = WindowTemplate()
		self.ui.setupUi(self)
		self.ui.fpsInput.setMinimum(1)
		self.ui.fpsInput.setMaximum(10)
		self.ui.stopButton.clicked.connect(self.button_stop)
		self.ui.startButton.clicked.connect(self.button_call)
		self.ui.stopButton.setEnabled(False)
		self.setup_plot()

		self.show()

	@pyqtSlot()
	def button_stop(self):
		self.stop_thread()
		self.ui.startButton.setEnabled(True)
		self.ui.stopButton.setEnabled(False)
		self.ui.fpsInput.setEnabled(True)

	@pyqtSlot()
	def button_call(self):
		self.create_thread()
		self.start_acquire.emit(float(self.ui.fpsInput.value()))
		self.ui.startButton.setEnabled(False)
		self.ui.stopButton.setEnabled(True)
		self.ui.fpsInput.setEnabled(False)

	def create_thread(self):
		# 1 - create Worker and Thread inside the Form
		self.worker = Worker()  # no parent!
		self.thread = QThread()  # no parent!

		# 2 - Connect Worker`s Signals to Form method slots to post data.
		self.worker.result.connect(self._update_plot)
		self.start_acquire.connect(self.worker.start) #connect start_acquire signal to Worker thread .start method

		# 3 - Move the Worker object to the Thread object
		self.worker.moveToThread(self.thread)

		# 4 - Connect Worker Signals to the Thread slots
		self.worker.finished.connect(self.thread.quit)

		# 5 - Connect Thread started signal to Worker operational slot method
		#self.thread.started.connect(self.obj.acquireImgs) #do this manually through a signal instead to pass args into acquire
		# 6 - Start the thread
		self.thread.start()

	def stop_thread(self):
		self.thread.requestInterruption()
		self.thread.quit()
		self.thread.wait()
		print("Thread destroyed")
	
	def setup_plot(self):
		gv = self.ui.graphicsView
		# A plot area (ViewBox + axes) for displaying the image
		self.plot_main = gv.addPlot(row=0, col=0)

		# Item for displaying image data
		self.img = pg.ImageItem()
		self.plot_main.addItem(self.img)

		# Custom ROI for selecting an image region
		self.roi = pg.ROI([1280/2, 300], [250, 600])
		self.roi.addScaleHandle([0.5, 1], [0.5, 0.5])
		self.roi.addScaleHandle([0, 0.5], [0.5, 0.5])
		self.plot_main.addItem(self.roi)
		self.roi.setZValue(10)  # make sure ROI is drawn above image
		# Contrast/color control
		# hist = pg.HistogramLUTItem()
		# hist.setImageItem(img)
		# win.addItem(hist)

		# Another plot area for displaying ROI data
		self.plot_x = gv.addPlot(row=1, col=0)
		self.plot_x.setMaximumHeight(150)
		self.plot_y = gv.addPlot(row=0, col=1)
		self.plot_y.setMaximumWidth(150)

		gv.resize(800, 600)
		gv.show()

		# hist.setLevels(data.min(), data.max())
		# set position and scale of image
		self.img.scale(1.0, 1.0)
		#self.img.translate(-50, 0)
		#self.update_plot()
		# zoom to fit imageo
		self._init_plot()
		self.roi.sigRegionChanged.connect(self.update_roi)
		self.update_roi()

	
	def _update_plot(self, data):
		self.data = data
		self.img.setImage(self.data)
		self.plot_main.autoRange() 
		self.update_roi()

	def _init_plot(self):
		data = np.zeros((1280, 960))
		self._update_plot(data)

	def update_plot_test(self):
		# Generate image data
		data = np.random.normal(size=(200, 100))
		data[20:80, 20:80] += 2.+np.random.rand()
		data = pg.gaussianFilter(data, (3, 3))
		data += np.random.normal(size=(200, 100)) * 0.1
		self.data = data
		self.img.setImage(self.data)
		self.plot_main.autoRange()  

	@pyqtSlot(np.ndarray)
	def setData(self,data):
		self._update_plot(data)

	# Callbacks for handling user interaction
	def update_roi(self):
		selected = self.roi.getArrayRegion(self.data, self.img)
		ymean = selected.mean(axis=0)
		xmean = selected.mean(axis=1)
		self.plot_x.plot(np.arange(len(xmean)), xmean, clear=True)
		self.plot_y.plot(ymean, np.arange(len(ymean)), clear=True)
		

def createViewer():
	win = MainWindow()
	# QtGui.QApplication.instance().exec_()
	win.show()
	return win
def startapp():
	
	QtGui.QApplication.instance().exec_()


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
	import sys
	win = MainWindow()
	if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()
