import multiprocessing as mp
import flycapture2
import time
import datetime
import os
import matplotlib.pyplot as plt
import numpy as np
import inspect
import threading
from multiprocessing import Pool

from servers.server import *
from utilities.util import *
import ImViewer as iv
import thread
# from utilities.ShowIMG import ShowIMG

DIR_DATA = "E:\\Data\\"

fullpath = os.path.abspath(inspect.getfile(inspect.currentframe()))

server = Server("COut1", 60614)
server.message = fullpath + '\n'
server.message += '===========================================\n'
server.message += '==             Camera Server 1           ==\n'
server.message += '==        for Point Grey Chameleon       ==\n'
server.message += '===========================================\n'

server.message += 'Resolution: 1280*960\n'
server.message += 'Bit Depth: 8\n'
server.message += 'Maximum Trigger Rate: 14fps\n'
server.message += 'WARNING: The maximum frame rate is 14fps!\n'

# class ShowThread(threading.Thread):
    # def __init__(self):
        # threading.Thread.__init__(self)
        # self.show_obj = ShowIMG()
        # plt.show(block=False)
    # def run(self):
        # self.show_obj.tprint()

# class ShowIMG:
  # def __init__(self):
    # self.fig = plt.figure()
    # self.ax  = self.fig.add_subplot(111)
    # self.init_img = [[0,1],[2,3]]
    
    # self.ax.imshow(self.init_img, cmap='Greys_r')
    
    # self.timer = self.fig.canvas.new_timer(interval=100)
    # self.timer.add_callback(self.updatetest)
    # self.timer.start()
    
  # def tprint(self):
    # for ii in range(100):
      # print "I'm running: "+str(ii)
      # time.sleep(1)
    
  # def updatetest(self):
    # plt.cla()
    # rand_img = np.random.rand(200, 200)
    # self.ax.imshow(rand_img)
    # self.fig.canvas.draw()
    
  # def update(self, img_dir, img_runname, img_num=3):
    # try:
      # if img_num == 3:
        # foregnd  = plt.imread(img_dir+img_runname+"_IMG1"+".PGM")
        # beamonly = plt.imread(img_dir+img_runname+"_IMG2"+".PGM")
        # backgnd  = plt.imread(img_dir+img_runname+"_IMG3"+".PGM")
        
        # diff = 1.0*(foregnd-backgnd)/(beamonly-backgnd+1e-5)
        # diff = diff[420:590, 620:790] # Chop the image
        
        # plt.cla()
        # self.ax.imshow(diff, cmap='Greys_r', vmin=0.0, vmax=1.0)
        # self.fig.canvas.draw()
        # plt.pause(1e-4)
        # return 1
    # except Exception as e:
      # print e
      # return 0

class GP_camera:
  def __init__(self):
    self.get_c = flycapture2.Context()
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
    self.camera = self.get_c.get_camera_from_index(0)
    self.get_c.connect(self.camera[0], self.camera[1], self.camera[2], self.camera[3])
    
    #Set camera properties
    self.get_c.set_video_mode_and_frame_rate(17, 3)                  # VEDIO_MODE_AND_FRAME_RATE
    # self.get_c.set_video_mode_and_frame_rate(23, 6)                  # VEDIO_MODE_AND_FRAME_RATE
    self.get_c.set_property(type=1, on_off=True, abs_value=-0.061)   # AUTO_EXPOSURE 
    self.get_c.set_property(type=13, abs_value=24)                   # GAIN
    self.get_c.set_property(type=14, on_off=True, abs_control=False) # TRIGGER_MODE
    self.get_c.settriggeredEXT()                                     # EXTERNAL_TRIGGER
    #Start capture
    self.get_c.start_capture()
  
  # def GrabImages(self, shutter=0, number=0, runname=""):
    # self.shutter_time = shutter
    # self.num_of_images = number
    # self.run_name = runname
    
    # #Generating image file names
    # self.setDate()
    # img_dir = "J:\\Data\\" + self.date_dir
    # # img_dir = os.path.expanduser("~\\camera_test\\" + self.date_dir) #Testing image folder
    # img_name = []
    # for pic in range(0, self.num_of_images):
      # img_name.append(img_dir + self.run_name + "_IMG" + str(pic+1) + ".PGM")
    # if not os.path.exists(img_dir):
      # os.makedirs(img_dir)
    
    # #Set shutter time
    # self.get_c.set_property(type=12, abs_value=float(self.shutter_time)) #SHUTTER
    
    # #Grab images
    # # self.get_c.AllocMemory(numImages=self.num_of_images)
    # self.get_c.GrabImages(filename=img_name, numImages=self.num_of_images)
    
  def GrabImages(self, shutter=0, number=0, runname="", foldername=""):
    self.shutter_time = shutter
    self.num_of_images = number
    self.run_name = runname
    self.folder_name = foldername
    
    #Generating image file names
    self.setDate()
    img_dir = DIR_DATA+self.date_dir+self.folder_name+"\\"
    # img_dir += "IMG_"+self.run_name+"\\" # Add subfolder for each run
    self.img_dir = img_dir
    
    img_name = []
    for pic in range(0, self.num_of_images):
      img_name.append(img_dir + self.run_name + "_IMG" + str(pic+1) + ".PGM")
    if not os.path.exists(img_dir):
      os.makedirs(img_dir)
    
    #Set shutter time
    self.get_c.set_property(type=12, abs_value=float(self.shutter_time)) #SHUTTER
    
    #Grab images
    # self.get_c.AllocMemory(numImages=self.num_of_images)
    self.get_c.GrabImages(filename=img_name, numImages=self.num_of_images)
   
  def SaveCameraLog(self, runtime=""):
    log_dir = "E:\\Logs\\LOG_Cam\\" + self.date_dir
    # log_dir = os.path.expanduser("~\\camera_test\\" + self.date_dir) #Testing image folder
    log_name = log_dir + self.run_name + ".txt"
    
    if not os.path.exists(log_dir):
      os.makedirs(log_dir)
    
    text = ""
    text_info = ""
    
    #Read paras from the camera
    prop_type = [1, 12, 13]
    prop_type_dic = {1: "Auto exposure", 12: "Shutter", 13: "Gain"}
    prop_type_units = {1: "EV", 12: "ms", 13: "dB"}
    prop_info = []
    for type in prop_type:
      new_info = self.get_c.get_property(type)
      prop_info.append(new_info)
    for prop in prop_info:
      text_info += prop_type_dic[prop["type"]] + " = " + str(prop["abs_value"]) + prop_type_units[prop["type"]] + "\n"
      
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
    text += "Video mode = 1280*960 8 bit\n"
    text += "Output file format = PGM"
    
    f = open(log_name, 'w')
    f.write(text)
    f.close()
    
  def Disconnect(self):
    self.get_c.disconnect()
    printGreen("Disconnected the camera.")
  
class CameraServer:
  def __init__(self):
    self.device = GP_camera()
  
  def StartServer(self):
    try:
      self.device.InitCamera()
      print "Camera initiated."
    except:
      printError("Failed to connect the camera!")
    
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
          printError("Frame rate exceeds the maximum value (14fps)!")
        else:
          print("Number of images will be captured: " + str(self.NumOfImage))
          print("Shutter time: " + str(ShutterTime)) + "ms"
            
          try:
            error   = self.device.GrabImages(shutter=ShutterTime, number=self.NumOfImage, runname=run_name, foldername=folder_name)
            # error = self.device.GrabImages(shutter=ShutterTime, number=self.NumOfImage, runname=run_name)
          except:
            printError("Failed to grab images!")
          try:
            error = self.device.SaveCameraLog()
          except:
            printError("Failed to save the log file!")
          # device.Disconnect()
          
    elif autostart == 1:
      TIME_STOP = time.time()
      return TIME_STOP-TIME_START

def serverLoop(viewer):
  # ImgWindow = ShowIMG()
  # plt.show(block=False)
  # plt.draw()
  
  # p = Pool(4)
  # p.map(plt.show(), [])
  # p.map(ImgWindow.updatetest, [])
  # print "continuing"
  
  sev = CameraServer()
  sev.StartServer()
  
  server.Listen()
  
  while True:
    clientSocket, addr = server.sock.accept()
    
    while True:

      print "listening!!!"
      data = recv_msg(clientSocket) # Receive a command
      print data
      data = printGrayDate(data)    # Print the full command  as received
      if data != None:
        tokens = data.strip().split(' ', 2)  # Isolate the command in case it contains extra info
        command = tokens[0]

      if command == "RUN":  # Run the sequence (if we've already received it)
        if server.seq == None:
          printError('Run() failed. Sequence has not been imported!')
          send_msg(clientSocket, server.ReplyHeader() + 'Run() failed. Sequence has not been imported!')
          break
        else:
          time_taken = sev.RunServer(server.seq)
          success = time_taken
    
        time_taken = '%.2f' % success
        send_msg(clientSocket, server.ReplyHeader() + 'Successfully ran sequence (' + str(time_taken) + ' seconds).')
        break
        
      if command == "QUEUE":  # Run the sequence (if we've already received it)
        if server.seq == None:
          printError('Queue() failed. Sequence has not been imported!')
          send_msg(clientSocket, server.ReplyHeader() + 'Queue() failed. Sequence has not been imported!')
          break
        else:
          try:
            send_msg(clientSocket, server.ReplyHeader() + 'Sequence has been queued... Trigger it whenever!')
            sev.RunServer(server.seq, 0)
            # ImgWindow.update(sev.device.img_dir, sev.device.run_name, img_num=3)
            fnames = [sev.device.img_dir+sev.device.run_name+"_IMG"+str(ii+1)+".PGM" for ii in range(sev.NumOfImage)]
            iv.loadImage(viewer, fnames, sev.device.run_name)
          except Exception as e:
            printError("Failed to taking or saving images!")
            printError(str(e))
          break
        
      # Load in a sequence
      elif command == "SEQ":
        seq_data = recv_msg(clientSocket)
        server.seq = pickle.loads(seq_data)  # Unpack the sequence
        numChannels = 0
        for chan in server.seq.allChannels:
          if chan != None: numChannels += 1
        printGreen("Received sequence ("+str(numChannels)+" channels): "+str(server.seq.name)+".")
        reply = "Received '"+str(server.seq.name)+"'; " + str(numChannels) + " channels defined."
        send_msg(clientSocket, server.ReplyHeader() + reply)
        break
        
      else:
        reply = 'Unexpected command'
        send_msg(clientSocket, server.ReplyHeader() + reply)
        break
    
    clientSocket.close()
  
if __name__ == '__main__':
  viewer = iv.createViewer()
  thread.start_new_thread(serverLoop, (viewer,))
  viewer.GUI_loop()
  