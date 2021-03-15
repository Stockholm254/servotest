# -*- coding: utf-8 -*-
"""
V0.1 of Camera server with Qt and pyqtgraph
"""
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import numpy as np
import os
import time
from .gpcamera import MockCamera, GP_camera
from ..ServerClass import logger, Server
from copy import deepcopy
# Interpret image data as row-major instead of col-major
#pg.setConfigOptions(imageAxisOrder='row-major')
pg.mkQApp()

## Define main window class from template
path = os.path.dirname(os.path.abspath(__file__))
uiFile = os.path.join(path, 'viewer.ui')
WindowTemplate, TemplateBaseClass = pg.Qt.loadUiType(uiFile)

class CameraServer(Server):

	def __init__(self, name, port, message):
		super().__init__(name, port, message)
		self.device = GP_camera(BIT12 = False)
		self.imgbuffer=[]
		try:
			self.device.InitCamera()
			logger.info("Camera initiated.")
		except:
			logger.exception("Failed to connect the camera!")

	def RunServer(self, seq, autostart=1):
		TIME_START = time.time()
		
		chan = seq.getChannelByName("Camera")
		thehardwarevalues = chan.GetHardwareValues()
		run_name = 'IMG'+seq.runname
		folder_name = seq.foldername
		self.NumOfImage = 0
		ShutterTime = 0
		
		if folder_name == "":
			folder_name = "camera"
		
		chan_gain = seq.getChannelByName("Camera gain")
		save_switch_chan = seq.getChannelByName("Camera save")
		save_switch_values = save_switch_chan.GetHardwareValues()
		#gain_hwvalues = chan_gain.GetHardwareValues()
		save_switch = save_switch_values[0][1]
		gain_mv = chan_gain._TransValues[0][1] # find the first value
		logger.info("Gain from FP: {} dB".format(gain_mv))

		shutter_end = 0
		shutter_beg = 0
		gap_beg = -100000 #In case the down edge is at the beginning of the sequence, then the first elements in shutter_gap will be 0, and result in an frame rate error.
		gap_end = 0
		shutter_gap = []
		
		newval = 1
		oldval = 1 #Steady state value of camera channel. Since the camera is triggered by falling edge, so the SSV is high. 
		
		if autostart == 0:
			for interval in thehardwarevalues:
				# Detect trigger edge and calculate shutter time
				if interval[1] == 0 and interval[3] == 0:
					newval = 0
					if newval != oldval:
						self.NumOfImage += 1
						shutter_beg = interval[0]
						gap_end = interval[0]
						shutter_gap.append((gap_end - gap_beg)/1000)
				else:
					newval = 1
					if newval != oldval:
						shutter_end = interval[0]
						gap_beg = interval[0]
						ShutterTime = (shutter_end - shutter_beg)/1000
				oldval = newval
					
			if self.NumOfImage > 0:
				min_gap_time = min(shutter_gap)
				if min_gap_time < 80:
					logger.error("Frame rate exceeds the maximum value (14fps)!")
				else:
					logger.info("Number of images will be captured: " + str(self.NumOfImage))
					logger.info("Shutter time: " + str(ShutterTime)+ "ms")
					self.imgbuffer = []
					try:
						success, imgbuffer = self.device.GrabImages(shutter=ShutterTime, gain=gain_mv, save=save_switch, number=self.NumOfImage, runname=run_name, foldername=folder_name)
						self.device.CopyImages(foldername=folder_name) # New
						logger.debug("Success {}".format(success))
					except:
						logger.exception("Failed to grab images!")
					else:
						self.imgbuffer = np.stack(imgbuffer, axis=0)
						logger.debug("Grabbed {} images".format(len(self.imgbuffer)))
					# try:
					# 	self.device.SaveCameraLog()
					# except:
					# 	logger.exception("Failed to save the log file!")
					
					# loadImagefromBuffer(self.viewer, deepcopy(self.imgbuffer), self.device.run_name)
					
					# Thread safe way. This queues a call to the slot with  "Qt.QueuedConnection", but also doesn't block the current thread.
					# QMetaObject.invokeMethod(self.viewer, 'setData', Qt.QueuedConnection,Q_ARG(np.ndarray,self.imgbuffer[0]))
		elif autostart == 1:
			TIME_STOP = time.time()
			return TIME_STOP-TIME_START

	def cmd_queue(self):
		if self.seq is None:
			logger.error('QUEUE failed. Sequence has not been imported!')
			self.send_msg(self.ReplyHeader() + 'QUEUE failed. Sequence has not been imported!')
		else:
			self.send_msg(self.ReplyHeader() + 'Sequence has been queued... Trigger it whenever!')
			try:
				self.RunServer(self.seq, autostart=0)
			except:
				logger.exception("Failed in taking or saving images!")

	def run(self):
		return self.RunServer(self.seq, autostart=1)

	def plotdata(self):
		return [0,], [0,]


class ServerWorker(QObject):
	finished = pyqtSignal()
	result = pyqtSignal(np.ndarray)

	def __init__(self, parent=None):
		#super(self.__class__, self).__init__(parent)
		super(ServerWorker, self).__init__(parent)
		message = """===========================================
		==             Camera Server 1           ==
		==        for Point Grey Chameleon       ==
		===========================================

		Resolution: 1280*960
		Bit Depth: 8
		Maximum Trigger Rate: 14fps
		WARNING: The maximum frame rate is 14fps!"""
		self.serv = CameraServer("COut1", 60614, message=message)

	def acquire(self, delay):
		# this replaces the Server class main loop for now
		while not QThread.currentThread().isInterruptionRequested():
			ev = self.serv.sock.poll(10)
			if ev != 0:
				try:
					command, data = self.serv.recv_msg() # Receive a command
					print(command)
				except KeyboardInterrupt:
					logger.info("W: interrupt received, stopping…")
					break
				else:
					if command == "RUN":  # Run the sequence (if we've already received it)
						self.serv.cmd_run()
					
					elif command == "SEQ": # Load in a sequence
						self.serv.cmd_seq(data)

					elif command == "QUEUE": # Queue/arm for trigger
						self.serv.cmd_queue()
						print("Acquired {} frames".format(len(self.serv.imgbuffer)))
						#now the images should be in self.serv.imgbuffer, get them and send a signal
						if len(self.serv.imgbuffer)>0:
							buf = deepcopy(self.serv.imgbuffer)
							self.result.emit(buf)
							print("Emitted")

					elif command == 'GETPLOTDATA': # Get plot data from server
						self.serv.cmd_plotdata()
					
					elif command == 'PING':
						self.serv.cmd_ping()
						
					else:
						self.serv.cmd_unknown(command)

		# clean up
		self.serv.sock.close()
		#context.term()
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
		
		self.data = np.zeros((1280, 960))

		# Create the main window
		self.ui = WindowTemplate()
		self.ui.setupUi(self)
		self.ui.fpsInput.setMinimum(1)
		self.ui.fpsInput.setMaximum(10)
		self.ui.stopButton.clicked.connect(self.button_stop)
		self.ui.startButton.clicked.connect(self.button_start)
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
	def button_start(self):
		self.create_thread()
		self.start_acquire.emit(float(self.ui.fpsInput.value()))
		self.ui.startButton.setEnabled(False)
		self.ui.stopButton.setEnabled(True)
		self.ui.fpsInput.setEnabled(False)

	def create_thread(self):
		# 1 - create Worker and Thread inside the Form
		self.worker = ServerWorker()  # no parent!
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
		self.hist = pg.HistogramLUTItem()
		self.hist.setImageItem(self.img)
		gv.addItem(self.hist,row=0, col=2)

		# Another plot area for displaying ROI data
		self.plot_x = gv.addPlot(row=1, col=0)
		self.plot_x.setMaximumHeight(150)
		#self.plot_x.setXLink(self.plot_main)
		self.plot_y = gv.addPlot(row=0, col=1)
		self.plot_y.setMaximumWidth(150)
		#self.plot_y.setYLink(self.plot_main)

		gv.resize(800, 600)
		gv.show()

		# set position and scale of image
		self.img.scale(1.0, 1.0)
		#self.img.translate(-50, 0)
		#self.update_plot()
		# zoom to fit imageo
		self._init_plot()
		self.roi.sigRegionChanged.connect(self.update_roi)
		self.update_roi()

	
	def _update_plot(self, imgArrays):
		#
		mode = None
		if imgArrays.shape[0]==3:
			absArray = (imgArrays[0]-imgArrays[2])/(imgArrays[1]-imgArrays[2]) #+1e-6
			data = 1-absArray
			logger.debug("absorption")
			mode = "ABS"
		elif imgArrays.shape[0]==2:
			fore = np.array(imgArrays[0])
			back = np.array(imgArrays[1])
			fore[fore < back] = back[fore < back]
			diff = fore - back
			data = diff
			logger.debug("fluorescence")
			mode = "FL"
		else:
			data = imgArrays
			logger.debug("1 image")

		# if data.shape != self.data.shape:
		# 	self.plot_main.autoRange() 
		self.data = data.T
		self.img.setImage(self.data)
		
		if mode=="ABS":
			self.hist.setLevels(0., 1.)
			self.hist.setLevels(min=0,max=1.0)
		else:
			self.hist.setLevels(min=0,max=100)
			# self.hist.setLevels(np.nanmin(self.data), np.nanmax(self.data))
		self.update_roi()

	def _init_plot(self):
		data = np.zeros((1280, 960))
		self._update_plot(data)

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

win = MainWindow()

class MockWorker(QObject):
	finished = pyqtSignal()
	result = pyqtSignal(object)

	def __init__(self, parent=None):
		#super(self.__class__, self).__init__(parent)
		super(MockWorker, self).__init__(parent)
		self.cam = MockCamera()

	def acquire(self, delay):
		print("Is interrtup requested: {}".format(QThread.currentThread().isInterruptionRequested())) 
		while not QThread.currentThread().isInterruptionRequested():
			image = self.cam.get()
			self.result.emit(image)
			print("Acquired")
			QThread.msleep(int(1000*delay))
		print("Exiting...")

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
	import sys
	win = MainWindow()
	if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()
