import PyCapture2
import time
import datetime
import os
import matplotlib.pyplot as plt
import numpy as np
import inspect
import threading
from .ImViewer import createViewer, loadImage
from sys import exit
from ..ServerClass import Server, logger
from pathlib import Path

#DIR_DATA = "E:/Data/"
from ...config.config import DIR_DATA

fullpath = Path(__file__).parent

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
	def __init__(self):
		#self.get_c = flycapture2.Context()
		self.shutter_time = 0
		self.num_of_images = 0
		self.run_name = ""
		self.folder_name = ""
		self.setDate()      
	
	def setDate(self):
		self.run_time = datetime.datetime.now()
		self.date_dir = self.run_time.strftime("%Y\\%m\\%d\\")
		
	def InitCamera(self):
		#Connect to the camera
		#self.camera = self.get_c.get_camera_from_index(0)
		#self.get_c.connect(self.camera[0], self.camera[1], self.camera[2], self.camera[3])

		# Ensure sufficient cameras are found
		bus = PyCapture2.BusManager()
		num_cams = bus.getNumOfCameras()
		print('Number of cameras detected: ', num_cams)
		if not num_cams:
				logger.error('Insufficient number of cameras. Exiting...')
				exit()

		# Select camera on 0th index
		self.c = PyCapture2.Camera()
		uid = bus.getCameraFromIndex(0)
		self.c.connect(uid)
		print_camera_info(self.c)

		#Set Video mode
		if BIT12:
			self.c.setVideoModeAndFrameRate(PyCapture2.VIDEO_MODE.VM_1280x960Y16, PyCapture2.FRAMERATE.FR_7_5)
		else:
			self.c.setVideoModeAndFrameRate(PyCapture2.VIDEO_MODE.VM_1280x960Y8, PyCapture2.FRAMERATE.FR_15) # 17, 3 
		
		 
		logger.info(f"Video mode: {self.c.getVideoModeAndFrameRate()}")

		# #Set camera properties
		# self.get_c.set_property(type=1, on_off=True, abs_value=-0.061)   # AUTO_EXPOSURE 
		#self.c.setProperty(type=PyCapture2.PROPERTY_TYPE.AUTO_EXPOSURE, onOff=False, abs_value=-0.061) #autoManualMode=0,
		autoexp_prop = self.c.getProperty(PyCapture2.PROPERTY_TYPE.AUTO_EXPOSURE)
		autoexp_prop.absControl = True
		autoexp_prop.onOff = True
		autoexp_prop.autoManualMode = False
		autoexp_prop.absValue = -0.061
		self.c.setProperty(autoexp_prop)

		# self.get_c.set_property(type=13, abs_value=24)                   # GAIN
		# self.c.setProperty(type=PyCapture2.PROPERTY_TYPE.GAIN, abs_value=24)
		gain_prop = self.c.getProperty(PyCapture2.PROPERTY_TYPE.GAIN)
		gain_prop.absControl = True
		gain_prop.autoManualMode = 0
		gain_prop.absValue = 24
		self.c.setProperty(gain_prop)


		# Configure trigger mode
		trigger_mode = self.c.getTriggerMode()
		trigger_mode.onOff = True
		trigger_mode.mode = 1 # 1 for bulb trigger
		trigger_mode.parameter = 0
		trigger_mode.source = 0 #External trigger #7     # Using software trigger
		self.c.setTriggerMode(trigger_mode)

		self.c.setConfiguration(grabTimeout = 10000)
		self.c.startCapture()  
		
	def GrabImages(self, shutter=0, gain=24., number=0, runname="", foldername=""):
		self.shutter_time = shutter
		self.num_of_images = number
		self.run_name = runname
		self.folder_name = foldername
		
		#Generating image file names
		self.setDate()
		img_dir = DIR_DATA/self.date_dir/self.folder_name
		# img_dir += "IMG_"+self.run_name+"\\" # Add subfolder for each run
		self.img_dir = img_dir
		logger.debug("saving to {}".format(self.img_dir))
		
		img_name = []
		for pic in range(0, self.num_of_images):
			#
			if BIT12:
				img_name.append(img_dir/(self.run_name + "_IMG" + str(pic+1) + ".png"))
			else:
				img_name.append(img_dir/(self.run_name + "_IMG" + str(pic+1) + ".PGM"))
		if not os.path.exists(img_dir):
			os.makedirs(img_dir)
		
		#Set shutter time
		#self.get_c.set_property(type=12, abs_value=float(self.shutter_time)) #SHUTTER
		#self.c.setProperty(type=PyCapture2.PROPERTY_TYPE.SHUTTER , abs_value=float(self.shutter_time))
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
		prop_type = [1, 12, 13]
		prop_type_dic = {1: "Auto exposure", 12: "Shutter", 13: "Gain"}
		prop_type_units = {1: "EV", 12: "ms", 13: "dB"}
		prop_info = []
		for _type in prop_type:
			new_info = self.c.getProperty(_type) #self.get_c.get_property(type)
			prop_info.append(new_info)
		for prop in prop_info:
			logger.info(prop_type_dic[prop.type] + " = " + str(prop.absValue) + prop_type_units[prop.type])

		#Grab images
		#self.get_c.GrabImages(filename=img_name, numImages=self.num_of_images)
		images = {}
		err=False
		for i, img in enumerate(img_name):
			try:
					image = self.c.retrieveBuffer()
			except PyCapture2.Fc2error as fc2Err:
					logger.exception('Error retrieving buffer for image {} of {} : {}'.format(i, len(img_name), fc2Err))
					err=True
			else:
				images[img] = image
		if not err:
			for img in img_name:
				try:

					if BIT12:
						newimg = images[img].convert(PyCapture2.PIXEL_FORMAT.MONO16)
						newimg.save(str(img).encode('utf-8'), PyCapture2.IMAGE_FILE_FORMAT.PNG)
					else:
						newimg = images[img].convert(PyCapture2.PIXEL_FORMAT.MONO8)
						newimg.save(str(img).encode('utf-8'), PyCapture2.IMAGE_FILE_FORMAT.PGM)
				except:
					logger.exception("couldn't save image")
		return not err
							
			
	 
	def SaveCameraLog(self, runtime=""):
		#log_dir = "E:\\Logs\\LOG_Cam\\" + self.date_dir
		log_dir = Path("E:/Logs/LOG_Cam")/self.date_dir
		# log_dir = os.path.expanduser("~\\camera_test\\" + self.date_dir) #Testing image folder
		log_name = log_dir/(self.run_name + ".txt")
		
		if not os.path.exists(log_dir):
			os.makedirs(log_dir)
		
		text = ""
		text_info = ""
		
		#Read paras from the camera
		prop_type = [1, 12, 13]
		prop_type_dic = {1: "Auto exposure", 12: "Shutter", 13: "Gain"}
		prop_type_units = {1: "EV", 12: "ms", 13: "dB"}
		prop_info = []
		for _type in prop_type:
			new_info = self.c.getProperty(_type) #self.get_c.get_property(type)
			prop_info.append(new_info)
		for prop in prop_info:
			#text_info += prop_type_dic[prop["type"]] + " = " + str(prop["abs_value"]) + prop_type_units[prop["type"]] + "\n"
			text_info += prop_type_dic[prop.type] + " = " + str(prop.absValue) + prop_type_units[prop.type] + "\n"
			
		text += "###Log for Grey Point Chameleon camera (File generated on " + self.run_time.strftime('%b %d, %Y at %H:%M:%S') + ")###\n\n"
		text += "##Sequences dependent parameters##\n"
		text += "Shutter time = " + str(self.shutter_time) + "\n"
		text += "Number of images = " + str(self.num_of_images) + "\n"
		text += "\n"
		text += "##Parameters read from the camera##\n"
		text += text_info
		text += "\n"
		text += "##Parameters hard coded in pyflycapture2 module##\n"
		text += "Trigger mode = 0 (IMPORTANT: This is hard coded in pyflycapture2, and not read from the camera!)\n"
		text += "Video mode = 1280*960 12 bit\n"
		text += "Output file format = PNG"
		
		f = open(log_name, 'w')
		f.write(text)
		f.close()
		
	def Disconnect(self):
		self.c.disconnect()
		logger.info("Disconnected the camera.")
	
class CameraServer(Server):

	def __init__(self, name, port, message, viewer):
		super().__init__(name, port, message)
		self.viewer = viewer
		self.device = GP_camera()
		try:
			self.device.InitCamera()
			logger.info("Camera initiated.")
		except:
			logger.error("Failed to connect the camera!")

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
		#gain_hwvalues = chan_gain.GetHardwareValues()
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
						
					try:
						self.device.GrabImages(shutter=ShutterTime, gain=gain_mv, number=self.NumOfImage, runname=run_name, foldername=folder_name)
						# error = self.device.GrabImages(shutter=ShutterTime, number=self.NumOfImage, runname=run_name)
					except:
						logger.error("Failed to grab images!")
					try:
						self.device.SaveCameraLog()
					except:
						logger.exception("Failed to save the log file!")
					
		elif autostart == 1:
			TIME_STOP = time.time()
			return TIME_STOP-TIME_START

	def cmd_queue(self):
		if self.seq is None:
			logger.error('QUEUE failed. Sequence has not been imported!')
			self.send_msg(self.ReplyHeader() + 'QUEUE failed. Sequence has not been imported!')
		else:
			try:
				self.send_msg(self.ReplyHeader() + 'Sequence has been queued... Trigger it whenever!')
				self.RunServer(self.seq, 0)
				# ImgWindow.update(sev.device.img_dir, sev.device.run_name, img_num=3)
				if BIT12:
					fnames = [self.device.img_dir/(self.device.run_name+"_IMG"+str(ii+1)+".png") for ii in range(self.NumOfImage)]
				else:
					fnames = [self.device.img_dir/(self.device.run_name+"_IMG"+str(ii+1)+".PGM") for ii in range(self.NumOfImage)]
				loadImage(self.viewer, fnames, self.device.run_name)
			except Exception as e:
				logger.exception("Failed in taking or saving images!")

	def run(self):
		return self.RunServer(self.seq)

	def plotdata(self):
		return [0,], [0,]

	
if __name__ == '__main__':
	message = """===========================================
	==             Camera Server 1           ==
	==        for Point Grey Chameleon       ==
	===========================================

	Resolution: 1280*960
	Bit Depth: 8
	Maximum Trigger Rate: 14fps
	WARNING: The maximum frame rate is 14fps!"""

	viewer = createViewer()
	server = CameraServer("COut1", 60614, message=message, viewer=viewer)
	t = threading.Thread(name='camera server', target=server.main_loop)
	t.start()
	#thread.start_new_thread(server.main_loop)
	viewer.GUI_loop()
	t.join()