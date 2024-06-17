try:
	import PySpin
	
except:
	pass
import time
import datetime
import os
import numpy as np
from ..ServerClass import logger
from pathlib import Path
from copy import deepcopy
from ...config.config import DIR_DATA
from .simple_pyspin import Camera

class CameraError(Exception):
	pass

_SYSTEM = None

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
		logger.debug("Trigger on GPIO {}".format(self.trigger_port))
		
	def setDate(self):
		self.run_time = datetime.datetime.now()
		self.date_dir = self.run_time.strftime("%Y\\%m\\%d\\")
	
	@staticmethod
	def ListCameras():
		# Get list of connected cameras for GUI
		global _SYSTEM

		if _SYSTEM is None:
			_SYSTEM = PySpin.System.GetInstance()

		cam_list = _SYSTEM.GetCameras()
		num_cams = cam_list.GetSize()
		logger.debug('Number of cameras detected: {:d}'.format(num_cams))
		res = {}
		for i, cam in enumerate(cam_list):
			device_model_name = cam.TLDevice.DeviceModelName.GetValue()
			device_serial = cam.TLDevice.DeviceSerialNumber.ToString()
			res[i] = {'i': i,'name': device_model_name, 'serial': int(device_serial), 'res': '3000x2000'}
		
		del cam
		cam_list.Clear()
		print(res)
		return res

	def InitCamera(self):
		#Connect to the camera
		# Get list of connected cameras for GUI
		global _SYSTEM
			
		try:
			self.c = Camera(index=self.camera_id) # Acquire Camera
		except:
			_SYSTEM = PySpin.System.GetInstance()
			self.c = Camera(index=self.camera_id) # Acquire Camera

		self.c.init() # Initialize camera

		# #Set camera properties
		# self.c.OffsetX = 0
		# self.c.OffsetY = 0

		# self.c.Width = self.c.SensorWidth
		# self.c.Height = self.c.SensorHeight

		_width = self.c.get_info('Width')
		_height = self.c.get_info('Height')
		self.c.OffsetX = 0
		self.c.OffsetY = 0
		self.c.Width = _width['max']
		self.c.Height = _height['max']
		logger.debug(f"Camera width: {self.c.Width}, height: {self.c.Height}")
		logger.debug(f'Camera width: {self.c.Width}, height: {self.c.Height}, offset x:{self.c.OffsetX }, ofset y:{self.c.OffsetY }')

		# To control the exposure settings, we need to turn off auto
		self.c.GainAuto = 'Off'
		# Set the gain to 20 dB or the maximum of the camera.
		gain = min(20, self.c.get_info('Gain')['max'])
		print("Setting gain to %.1f dB" % gain)
		self.c.Gain = gain
		self.c.ExposureAuto = 'Off'
		print(self.c.get_info('ExposureTime'))

		self.c.ExposureTime = 1000 # microseconds

		self.c.TriggerMode ='Off'
		self.c.TriggerSelector = 'FrameStart'
		self.c.TriggerSource = f'Line{self.trigger_port:d}'
		self.c.TriggerMode = 'On'


		self.c.start()

		# for i in range(2):
		# 	try:
		# 		self.c.get_image(wait=False)
		# 	except:
		# 		logger.exception("trying to empty out image buffer of camera...")

		#self.c.stop()

		
	def GrabImages(self, shutter=0, gain=24., number=0, runname="", foldername=""):
		self.shutter_time = shutter
		self.num_of_images = number
		self.run_name = runname
		self.folder_name = foldername
		
		#Generating image file names
		self.setDate()
		img_dir = DIR_DATA/self.date_dir/self.folder_name
		self.img_dir = img_dir
		
		img_name = []
		for pic in range(0, self.num_of_images):
			#
			if self.BIT12:
				img_name.append(img_dir/(self.run_name + "_IMG" + str(pic+1) + ".png"))
			else:
				img_name.append(img_dir/(self.run_name + "_IMG" + str(pic+1) + ".PGM"))
		# if not os.path.exists(img_dir):
		# 	os.makedirs(img_dir)
		
		#Set shutter time
		self.c.ExposureTime = float(1e3*self.shutter_time) # microseconds

		#Gain
		self.c.Gain = max(0, min(gain, 44.0))

		#self.c.start()
		#Grab images
		images_file = {}
		imgbuffer = []
		err=False
		for i, img in enumerate(img_name):
			logger.debug(f"Grabbing image {i} of {self.num_of_images}")
			try:
				image = self.c.get_array(wait=7000)
			except:
				logger.exception('Error retrieving buffer for image {} of {}'.format(i, len(img_name)))
				err=True
			else:
				#Convert to a numpy array with the right shape
				cv_image = np.transpose(image) #np.transpose(np.array(image.getData(), dtype="uint8").reshape( (image.getRows(), image.getCols()) ) )
				imgbuffer.append(cv_image)
				#images_file[img] = image

		#self.c.stop()

		return (not err), imgbuffer, images_file
							
	def Disconnect(self):
		try:
			self.c.close()
			global _SYSTEM
			#_SYSTEM.ReleaseInstance()
			logger.info("Disconnected the camera.")
		except AttributeError:
			logger.info("Camera already disconnected...")

	def __del__(self):
		try:
			self.c.close()
			global _SYSTEM
			#_SYSTEM.ReleaseInstance()
			logger.info("Delete the camera.")
		except AttributeError:
			logger.info("Camera already deleted...")
	def __exit__(self, type, value, traceback):
		try:
			self.c.close()
			global _SYSTEM
			#_SYSTEM.ReleaseInstance()
			logger.info("Exit the camera.")
		except AttributeError:
			logger.info("Camera already exited...")

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