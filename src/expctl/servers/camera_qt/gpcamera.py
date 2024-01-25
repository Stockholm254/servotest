try:
	import PyCapture2
except:
	pass
import time
import datetime
import os
import shutil
import numpy as np
from ..ServerClass import logger
from pathlib import Path
from copy import deepcopy
from ...config.config import DIR_DATA

BIT12 = False

def print_camera_info(cam):
		cam_info = cam.getCameraInfo()
		print('\n*** CAMERA INFORMATION ***\n')
		print('Serial number - %d' % cam_info.serialNumber)
		print('Camera model - %s' % cam_info.modelName)
		print('Camera vendor - %s' % cam_info.vendorName)
		print('Sensor - %s' % cam_info.sensorInfo)
		print('Resolution - %s' % cam_info.sensorResolution)
		print('Firmware version - %s' % cam_info.firmwareVersion)
		print('Firmware build time - %s' % cam_info.firmwareBuildTime)
		print()

class GP_camera:
	def __init__(self, BIT12=False, camera_id=0, video_mode=0, trigger_port=0, trigger_mode=0):
		#self.get_c = flycapture2.Context()
		self.shutter_time = 0
		self.num_of_images = 0
		self.run_name = ""
		self.folder_name = ""
		self.setDate()     
		self.BIT12 = BIT12
		self.camera_id = camera_id
		self.video_mode = video_mode
		self.trigger_port = trigger_port
		self.trigger_mode = trigger_mode
		logger.debug("Trigger on GPIO {:d}".format(self.trigger_port))
		
	def setDate(self):
		self.run_time = datetime.datetime.now()
		self.date_dir = self.run_time.strftime("%Y\\%m\\%d\\")
	
	@staticmethod
	def ListCameras():
		# Get list of connected cameras for GUI
		bus = PyCapture2.BusManager()
		num_cams = bus.getNumOfCameras()
		logger.debug('Number of cameras detected: {:d}'.format(num_cams))
		res = {}
		for n in range(num_cams):
			cam = PyCapture2.Camera()
			uid = bus.getCameraFromIndex(n)
			cam.connect(uid)
			cam_info = cam.getCameraInfo()
			res[n] = {'i': n,'name': cam_info.modelName, 'serial': cam_info.serialNumber, 'res': cam_info.sensorResolution}
			cam.disconnect()
		return res

	def InitCamera(self):
		#Connect to the camera

		# Ensure sufficient cameras are found
		bus = PyCapture2.BusManager()
		num_cams = bus.getNumOfCameras()
		logger.info('Number of cameras detected: {:d}'.format(num_cams))
		if not num_cams or self.camera_id>num_cams:
				logger.error('Insufficient number of cameras. Exiting...')
				exit()

		# Select camera on 0th index
		self.c = PyCapture2.Camera()
		uid = bus.getCameraFromIndex(self.camera_id)
		self.c.connect(uid)
		print_camera_info(self.c)

		# conf = self.c.getConfiguration()
		# logger.debug(f"Camera configuration {conf}")
		# # conf.registerTimeout = 1500
		# self.c.setConfiguration(registerTimeout = 1500, grabTimeout = 1500)
		# conf = self.c.getConfiguration()
		# logger.debug(f"Camera configuration after {conf}")

		logger.info(f"Video mode: {self.c.getVideoModeAndFrameRate()}")

		#Set Video mode
		if self.BIT12:
			self.c.setVideoModeAndFrameRate(PyCapture2.VIDEO_MODE.VM_1280x960Y16, PyCapture2.FRAMERATE.FR_7_5)
		else:
			#self.c.setVideoModeAndFrameRate(PyCapture2.VIDEO_MODE.VM_1280x960Y8, PyCapture2.FRAMERATE.FR_15) # 17, 3 
			pass
		
		 
		logger.info(f"Video mode: {self.c.getVideoModeAndFrameRate()}")

		# #Set camera properties
		autoexp_prop = self.c.getProperty(PyCapture2.PROPERTY_TYPE.AUTO_EXPOSURE)
		autoexp_prop.absControl = True
		autoexp_prop.onOff = True
		autoexp_prop.autoManualMode = False
		autoexp_prop.absValue = -0.061
		self.c.setProperty(autoexp_prop)

		gain_prop = self.c.getProperty(PyCapture2.PROPERTY_TYPE.GAIN)
		gain_prop.absControl = True
		gain_prop.autoManualMode = 0
		gain_prop.absValue = 24
		self.c.setProperty(gain_prop)

		# Configure trigger mode
		trigger_mode = self.c.getTriggerMode()
		trigger_mode.onOff = True
		trigger_mode.mode = self.trigger_mode # 0 for programmed shutter time, 1 for bulb trigger
		trigger_mode.parameter = 0
		trigger_mode.source = int(self.trigger_port) #0 #External trigger #7     # Using software trigger
		trigger_mode.polarity = 0 # Polarity trigger low
		self.c.setTriggerMode(trigger_mode)
		self.c.setConfiguration(grabTimeout = 3000)
		self.c.startCapture()  
		
	def GrabImages(self, shutter=0, gain=24., save=0, number=0, runname="", foldername=""):
		self.shutter_time = shutter
		self.num_of_images = number
		self.run_name = runname
		self.folder_name = foldername
		
		#Generating image file names
		self.setDate()
		img_dir = DIR_DATA/self.date_dir/self.folder_name
		self.img_dir = img_dir
		logger.debug("saving to {}".format(self.img_dir))
		
		img_name = []
		for pic in range(0, self.num_of_images):
			#
			if self.BIT12:
				img_name.append(img_dir/(self.run_name + "_IMG" + str(pic+1) + ".png"))
			else:
				img_name.append(img_dir/(self.run_name + "_IMG" + str(pic+1) + ".PGM"))
		if not os.path.exists(img_dir):
			os.makedirs(img_dir)
		
		#Set shutter time
		shutter_prop = self.c.getProperty(PyCapture2.PROPERTY_TYPE.SHUTTER)
		shutter_prop.absControl = True
		shutter_prop.autoManualMode = 0
		shutter_prop.absValue = float(self.shutter_time)
		self.c.setProperty(shutter_prop)

		#Gain
		gain_prop = self.c.getProperty(PyCapture2.PROPERTY_TYPE.GAIN)
		gain_prop.absControl = True
		gain_prop.autoManualMode = 0
		gain_prop.absValue = gain
		self.c.setProperty(gain_prop)

		
		#DEBUG Read paras from the camera
		# prop_type = [1, 12, 13]
		# prop_type_dic = {1: "Auto exposure", 12: "Shutter", 13: "Gain"}
		# prop_type_units = {1: "EV", 12: "ms", 13: "dB"}
		# prop_info = []
		# for _type in prop_type:
		# 	new_info = self.c.getProperty(_type)
		# 	prop_info.append(new_info)
		# for prop in prop_info:
		# 	logger.info(prop_type_dic[prop.type] + " = " + str(prop.absValue) + prop_type_units[prop.type])

		#Grab images
		images_file = {}
		imgbuffer = []
		err=False
		for i, img in enumerate(img_name):
			try:
				image = self.c.retrieveBuffer()
			except PyCapture2.Fc2error as fc2Err:
					logger.exception('Error retrieving buffer for image {} of {} : {}'.format(i, len(img_name), fc2Err))
					err=True
			else:
				#Convert to a numpy array with the right shape
				cv_image = np.transpose(np.array(image.getData(), dtype="uint8").reshape( (image.getRows(), image.getCols()) ) )
				imgbuffer.append(cv_image)
				images_file[img] = image

		return (not err), imgbuffer, images_file
							
	def CopyImages(self, foldername=""):
		COPYPath = DIR_DATA/self.date_dir/foldername
		BKPPath = Path("S:/Rydberg Experiment Data")/self.date_dir/foldername
		files = [file for file in os.listdir(COPYPath) if os.path.isfile(os.path.join(COPYPath, file))]
		try:
			if not os.path.exists(BKPPath):
				os.makedirs(BKPPath)
			for file in files:
				if not os.path.exists(os.path.join(BKPPath, file)):
					shutil.copy(os.path.join(COPYPath, file), BKPPath)
			return 1
		except:
			return 0
	
	 
	def SaveCameraLog(self, runtime=""):
		#log_dir = "E:\\Logs\\LOG_Cam\\" + self.date_dir
		log_dir = Path("C:/Logs")/self.date_dir
		# log_dir = os.path.expanduser("~\\camera_test\\" + self.date_dir) #Testing image folder
		log_name = log_dir/(self.run_name + ".txt")
		
		if not os.path.exists(log_dir):
			os.makedirs(log_dir)
		
	def Disconnect(self):
		self.c.disconnect()
		logger.info("Disconnected the camera.")


class Mock_GP_camera:
	def __init__(self, BIT12=False, camera_id=0):
		#self.get_c = flycapture2.Context()
		self.shutter_time = 0
		self.num_of_images = 0
		self.run_name = ""
		self.folder_name = ""
		self.setDate()     
		self.BIT12 = BIT12
		self.camera_id=camera_id


	def setDate(self):
		self.run_time = datetime.datetime.now()
		self.date_dir = self.run_time.strftime("%Y\\%m\\%d\\")
	
	@staticmethod
	def ListCameras():
		# Get list of connected cameras for GUI
		return {0: {'name': "Mock Cam FL", 'serial': 1234, 'res': (1280, 960)}, 1: {'name': "Mock Cam ABS", 'serial': 5678, 'res': (1280, 960)}}
		
	def InitCamera(self):
		#Connect to the camera
		self.c = MockCamera()
		
	def GrabImages(self, shutter=0, gain=24., number=0, runname="", foldername=""):
		self.shutter_time = shutter
		self.num_of_images = number
		self.run_name = runname
		self.folder_name = foldername
		
		#Grab images
		imgbuffer = []
		err=False
		if self.camera_id == 1: #ABS
			_beam = self.c.get(sigma=(200, 200), poisition_noise=3, amplitude_noise=0.05)
			_atoms = self.c.get(sigma=(30, 30), poisition_noise=7, amplitude_noise=0.05)
			imgbuffer.append((_beam*np.exp(-_atoms*0.8)*180).astype(np.uint8)) #foreground
			imgbuffer.append((_beam*180).astype(np.uint8)) #background
			imgbuffer.append((np.random.random(_beam.shape)*0.1*180).astype(np.uint8)) #ref
		else: #FL
			_im = self.c.get(sigma=(20, 50), poisition_noise=5, amplitude_noise=0.1)
			imgbuffer.append((_im*180).astype(np.uint8)) #foreground
			imgbuffer.append((np.random.random(_im.shape)*0.1*180).astype(np.uint8)) #background

		return (not err), imgbuffer
							
	def Disconnect(self):
		logger.info("Disconnected the camera.")

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