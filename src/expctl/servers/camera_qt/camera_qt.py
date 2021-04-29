# -*- coding: utf-8 -*-
"""
V0.5 of Camera server with Qt and pyqtgraph
"""
from dataclasses import dataclass
from datetime import datetime
from numpy.lib.npyio import save
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
#from pyqtgraph import Qt
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import numpy as np
import os
import time
from scipy.optimize import curve_fit
# try:
#     import PyCapture2
# except:
#     from .gpcamera import Mock_GP_camera as Camera
# else:
#     from .gpcamera import GP_camera as Camera

try:
    import PySpin
except:
    from .spincamera import Mock_GP_camera as Camera
else:
    from .spincamera import GP_camera as Camera

from ..ServerClass import logger, Server
from copy import deepcopy
from collections import deque
import expdatabase.conf as conf
from expdatabase.db import insertImage
from expdatabase.types import ShotImage
from pymongo import MongoClient
from bson import ObjectId

IMG_ABS= {0: 'fg', 1: 'bg', 2: 'ref'}
IMG_FL = {0: 'fg', 1: 'bg'}

STORE_FILES = False

CAMERA_SERIALS = {13442499: 'Cam Absorption', 15331899: 'Cam Fluorescence', 17497066: 'Cam Absorption 3',}
DEFAULT_ROI = {13442499: (500, 1100, 350, 950), 15331899: (550, 850, 250, 950), 17497066: (500, 1100, 350, 950), 17497066: (500, 1100, 800, 1300)}
DEFAULT_FIT_ROI = {13442499: (500, 1100, 350, 950), 15331899: (550, 850, 250, 950), 17497066: (500, 1100, 350, 950), 17497066: (600, 1000, 900, 1200)}
CAMERA_KWARGS = {17497066: {'trigger_port': 2, 'trigger_mode': 1, 'video_mode': (23, 8)}} #CM3 full resolution (2048x1536) (23, 8) 
# Interpret image data as row-major instead of col-major
#pg.setConfigOptions(imageAxisOrder='row-major')
pg.mkQApp()

## Define main window class from template
path = os.path.dirname(os.path.abspath(__file__))
uiFile = os.path.join(path, 'viewer_fit.ui')
WindowTemplate, TemplateBaseClass = pg.Qt.loadUiType(uiFile)

@dataclass
class ImageQueueItem:
    run_id: ObjectId
    save: bool
    shot: ShotImage
    images_file: dict

@dataclass
class ImageBufferItem:
    buffer: np.ndarray
    gain: float
    shutter: float
    power: float

class DbWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super(DbWorker, self).__init__(parent)
        try:
            self.client = MongoClient(host=conf.DB_HOST, port=conf.DB_PORT, username=conf.USER_RAW_WRITER , password=conf.PASSWORD_RAW_WRITER, authSource=conf.DB_AUTH)
        except:
            logger.exception("Database connection could not be established!")
            self.client = None
        else:
            logger.info("Database connected.")

    def storeImage(self, item):
        # Save to the DB
        try:
            insertImage(self.client, item.run_id, item.shot, item.save)
        except:
            logger.exception("Problem storing image to DB")
        else:
            logger.debug("stored image in DB from thread")
        # Save as files for legacy reasons  
        if STORE_FILES:  
            for name, img in item.images_file.items():
                try:
                    newimg = img.convert(PyCapture2.PIXEL_FORMAT.MONO8)
                    if not name.parent.exists():
                        name.parent.mkdir(parents=True)
                    p = str(name).encode('utf-8').replace(b'\\',b'/')
                    newimg.save(p, PyCapture2.IMAGE_FILE_FORMAT.PGM)
                except:
                    logger.exception("couldn't save image")

    @pyqtSlot(object)
    def store(self, item):
        self.storeImage(item)

class CameraServer(Server):
    
    def __init__(self, name, port, message, parent, camera_id, camera_kwargs):
        super().__init__(name, port, message)
        #self.device = GP_camera(BIT12 = False)
        self.parent=parent
        self.device = Camera(camera_id=camera_id, **camera_kwargs)
        self.ROI = ()
        self.imgbuffer=[]
        try:
            self.device.InitCamera()
            logger.info("Camera initiated.")
        except:
            logger.exception("Failed to connect the camera!")

    def set_ROI(self, roi):
        if len(roi)==4:
            self.ROI = tuple(roi)
        else:
            self.ROI = ()

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

        chan_pwr = seq.getChannelByName("Camera Img_horz_pwr")
        Img_horz_pwr_vals = chan_pwr._TransValues
        #logger.info("Img_horz_pwr values from FP: {}".format(Img_horz_pwr_vals))
        Img_horz_pwr = Img_horz_pwr_vals[-1][1]
        logger.info("Img_horz_pwr from FP: {}".format(Img_horz_pwr))

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
                        success, imgbuffer, images_file = self.device.GrabImages(shutter=ShutterTime, gain=gain_mv, number=self.NumOfImage, runname=run_name, foldername=folder_name)
                        logger.debug("Success {}".format(success))
                        if not success:
                            raise RuntimeError("Grab Images failed, this shot will not be saved!")
                    except:
                        logger.exception("Failed to grab images!")
                    else:
                        #self.imgbuffer = np.stack(imgbuffer, axis=0)
                        self.imgbuffer = ImageBufferItem(buffer=np.stack(imgbuffer, axis=0),
                                                        gain=gain_mv, 
                                                        shutter=ShutterTime, 
                                                        power=Img_horz_pwr)

                        logger.debug("Grabbed {} images".format(len(self.imgbuffer.buffer)))
                        logger.debug("Image shape: {}".format(self.imgbuffer.buffer.shape))
                        buf = deepcopy(self.imgbuffer)
                        # send images to GUI
                        self.parent.result.emit(buf)
                        logger.debug("Emitted to GUI")

                        #save image into db
                        if seq.saveswitch>0:
                            # apply ROI for saving
                            if len(self.ROI)==4:
                                x0, y0, x1, y1 = self.ROI
                                imgbuffer = self.imgbuffer.buffer[:,x0:x1,y0:y1]
                                _roi = self.ROI
                            else:
                                #_roi = (0, 0, self.imgbuffer.shape[1], self.imgbuffer.shape[2])
                                _roi = (0, 0, self.imgbuffer.buffer.shape[1], self.imgbuffer.buffer.shape[2])
                                imgbuffer = self.imgbuffer.buffer
                            
                            if self.NumOfImage==3:
                                im_type = 'abs' 
                                ims = {IMG_ABS[i]: imgbuffer[i] for i in range(self.NumOfImage)}
                            elif self.NumOfImage==2:  
                                im_type = 'fl'
                                ims = {IMG_FL[i]: imgbuffer[i] for i in range(self.NumOfImage)}
                            else:
                                im_type = 'unkwn'
                                ims = {'u_i'.format(i): imgbuffer[i] for i in range(self.NumOfImage)}
                            

                            shot = ShotImage(date=datetime.now(), 
                                            j=int(seq.counter), 
                                            img_type=im_type, 
                                            roi=_roi,
                                            data=ims)
                            save = True if seq.saveswitch==2 else False
                            
                            item = ImageQueueItem(run_id=ObjectId(seq.run_id), save=save, shot=shot, images_file=images_file)
                            #self.queue.put(item)
                            self.parent.storeSignal.emit(item)
                            logger.info("Emitted to Save Thread")

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
    result = pyqtSignal(object)
    storeSignal = pyqtSignal(object)

    def __init__(self, parent=None, port=60614, camera_id=0, camera_kwargs={}):
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
        self.serv = CameraServer("COut1", port, message=message, parent=self, camera_id=camera_id, camera_kwargs=camera_kwargs)
        self.worker = DbWorker()  # no parent!
        self.thread = QThread()  # no parent!

        self.storeSignal.connect(self.worker.store)
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.thread.quit)
        self.thread.start()

    def acquire(self, roi):
        self.serv.set_ROI(roi)
        self.serv.main_loop(cond_fn=(lambda : not QThread.currentThread().isInterruptionRequested()) )
        self.serv.device.Disconnect()
        self.thread.quit()
        self.thread.wait()
        print("Exiting...")
    
    @pyqtSlot(tuple)
    def start(self, roi):
        self.acquire(roi)

@dataclass
class ImageEntryItem:
    imgarray: np.ndarray
    names: dict
    label: str

class ItemModel(QtCore.QAbstractListModel):
    def __init__(self, *args, items=None, **kwargs):
        super(ItemModel, self).__init__(*args, **kwargs)
        #self.items = deque(items or [], maxlen=16) 
        self.items = deque(maxlen=16) 

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            entry = self.items[index.row()]
            text = "Image {} {:d}".format(entry.label, index.row())
            return text

    def rowCount(self, index):
        return len(self.items)

    def get(self, idx):
        return self.items[idx]

class MainWindow(TemplateBaseClass):  
    start_acquire = pyqtSignal(tuple)
    stop_acquire = pyqtSignal()

    def __init__(self, port=60614):
        TemplateBaseClass.__init__(self)
        self.setWindowTitle('Qt Camera Server')
        self.port = port
        self.data = np.zeros((1280, 960))

        # Create the main window
        self.ui = WindowTemplate()
        self.ui.setupUi(self)
        #get cameras
        self.cams = Camera.ListCameras()
        # Name known cameras
        for n, c in self.cams.items():
            if c['serial'] in CAMERA_SERIALS.keys():
                c['name'] = CAMERA_SERIALS[c['serial'] ]

        camstrs = ["{}: {}".format(c['name'], c['serial']) for c in self.cams.values()]
        self.ui.comboBox.addItems(camstrs)
        self.ui.stopButton.clicked.connect(self.button_stop)
        self.ui.startButton.clicked.connect(self.button_start)
        self.ui.stopButton.setEnabled(False)
        for el in [self.ui.x0SpinBox, self.ui.x1SpinBox, self.ui.y0SpinBox, self.ui.y1SpinBox]:
            el.setRange(0,2000)
            el.valueChanged.connect(self.update_roi_save_from_spinbox)
        self.ui.checkBox_lockroi.stateChanged.connect(self.update_roi_lock)
        self.ui.comboBox.currentIndexChanged.connect(self.set_default_save_roi)

        self.history = deque(maxlen=16)

        self.frame_model = QtGui.QStandardItemModel()
        self.ui.listView.setModel(self.frame_model)

        self.entry_model = ItemModel()
        self.ui.imgList.setModel(self.entry_model)
        
        #self.frame_model.itemChanged.connect(self._show_selected_frame)
        self.ui.listView.selectionModel().selectionChanged.connect(self._show_selected_frame)
        self.ui.imgList.selectionModel().selectionChanged.connect(self._show_selected_entry)

        self.setup_plot()
        self.set_default_save_roi()
        self.ui.checkBox_saveroi.setChecked(True)
        self.show()

    @pyqtSlot()
    def set_default_save_roi(self):
        camera_id = self.ui.comboBox.currentIndex()
        ser = self.cams[camera_id]['serial'] #serial of current camera
        if ser in DEFAULT_ROI.keys():
            res = self.cams[camera_id]['res'].split('x') #.decode('utf-8')
            xmax, ymax = int(res[0]), int(res[1])
            self.ui.x1SpinBox.setMaximum(xmax)
            self.ui.y1SpinBox.setMaximum(ymax)

            # save ROI
            x0, x1, y0, y1 = DEFAULT_ROI[ser]
            self.ui.x0SpinBox.setValue(x0)
            self.ui.x1SpinBox.setValue(x1)
            self.ui.y0SpinBox.setValue(y0)
            self.ui.y1SpinBox.setValue(y1)
            self.update_roi_save_from_spinbox()

            # fit ROI
            x0, x1, y0, y1 = DEFAULT_FIT_ROI[ser]
            self.roi.setPos(x0, y0, update=True)
            self.roi.setSize((abs(x1-x0), abs(y1-y0)), update=True)
        # Set default ROI for this camera

    @pyqtSlot()
    def button_stop(self):
        self.stop_thread()
        self.ui.startButton.setEnabled(True)
        self.ui.stopButton.setEnabled(False)
        self.ui.checkBox_saveroi.setEnabled(True)
        self.ui.x0SpinBox.setEnabled(True)
        self.ui.x1SpinBox.setEnabled(True)
        self.ui.y0SpinBox.setEnabled(True)
        self.ui.y1SpinBox.setEnabled(True)
        #self.roi_save.setEnabled(True)

    @pyqtSlot()
    def button_start(self):
        
        if self.ui.checkBox_saveroi.isChecked():
            x0 = self.ui.x0SpinBox.value()
            x1 = self.ui.x1SpinBox.value()
            y0 = self.ui.y0SpinBox.value()
            y1 = self.ui.y1SpinBox.value()
            roi = (x0, y0, x1, y1)
        else:
            roi = ()

        self.create_thread()
        self.start_acquire.emit(roi)
        self.ui.startButton.setEnabled(False)
        self.ui.stopButton.setEnabled(True)
        self.ui.x0SpinBox.setEnabled(False)
        self.ui.x1SpinBox.setEnabled(False)
        self.ui.y0SpinBox.setEnabled(False)
        self.ui.y1SpinBox.setEnabled(False)


    def create_thread(self):
        # 1 - create Worker and Thread inside the Form
        camera_id = self.ui.comboBox.currentIndex()
        logger.info(f"Opening camera {camera_id}")
        ser = self.cams[camera_id]['serial'] #serial of current camera
        if ser in CAMERA_KWARGS.keys():
            kwargs = CAMERA_KWARGS[ser]
        else:
            kwargs = {}

        self.worker = ServerWorker(port=self.port, camera_id=camera_id, camera_kwargs=kwargs)  # no parent!
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

        # Custom ROI for save region
        self.roi_save = pg.ROI([1280/2, 300], [500, 500], movable=False, resizable=False, rotatable=False, pen=pg.mkPen('b', width=2, style=QtCore.Qt.DashLine))
        #self.roi_save.addScaleHandle([0.5, 1], [0.5, 0.5])
        #self.roi_save.addScaleHandle([0, 0.5], [0.5, 0.5])
        self.plot_main.addItem(self.roi_save)
        self.roi_save.setZValue(5)  # make sure ROI is drawn above image

        # Custom ROI for selecting an image region
        self.roi = pg.ROI([1280/2, 300], [250, 600], pen=pg.mkPen('w', width=2, style=QtCore.Qt.SolidLine))
        self.roi.addScaleHandle([0.5, 1], [0.5, 0.5])
        self.roi.addScaleHandle([0, 0.5], [0.5, 0.5])
        self.plot_main.addItem(self.roi)
        self.roi.setZValue(10)  # make sure ROI is drawn above image
        # Contrast/color control
        self.hist = pg.HistogramLUTItem()
        self.hist.setImageItem(self.img)
        self.hist.gradient.loadPreset('inferno')

        self.hist.setHistogramRange(0., 255.)
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
        self.roi_save.sigRegionChanged.connect(self.update_roi_save_from_plot)
        self.update_roi()
        self.update_roi_save_from_plot()

  
    def _update_plot(self, buffer_item: ImageBufferItem):
        #
        mode = "UNKWN"
        imgArrays = buffer_item.buffer
        if imgArrays.shape[0]==3:
            data = self._process_absorption(buffer_item)
            #data = buffer_item.buffer[1]
            mode = "ABS"
            frameNames = {0: "Absorption image", 1: "Probe with atoms", 2: "Probe without atoms", 3: "Dark field"}
            logger.debug("ABS")
        elif imgArrays.shape[0]==2:
            data = self._process_fluorescence(buffer_item)
            mode = "FL"
            frameNames = {0: "Fluorescence image", 1: "Probe with atoms", 2: "Probe without atoms"}
            logger.debug("FL")
        else:
            data = imgArrays[0]
            frameNames = {i: str(i) for i in range(len(imgArrays))}
            logger.debug("unknown number of images")

        
        entry = ImageEntryItem(imgarray=np.concatenate([data[None,:,:], buffer_item.buffer],axis=0) , names=frameNames, label=mode)
        #self.history.appendleft(entry)
        self.entry_model.items.appendleft(entry)
        self.entry_model.layoutChanged.emit()  
        self.data = data
        self.img.setImage(self.data, autoLevels=self.ui.checkBox_autoscale.isChecked())
        
        if mode=="ABS":
            #self.hist.setLevels(0., 1.)
            #self.hist.setLevels(0., 3.)
            #self.hist.setHistogramRange(0., 1.)
            pass
        else:
            if self.ui.checkBox_autoscale.isChecked():
                self.hist.setLevels(np.nanmin(self.data), np.nanmax(self.data))
        self.update_roi()

    def _show_selected_entry(self):
        print("Data Changed")
        self.frame_model.clear()
        index = self.ui.imgList.selectionModel().selectedIndexes()[0].row()
        print(index)
        for n in self.entry_model.get(index).names:
            print(n)
            item = QtGui.QStandardItem("Frame {}".format(n))
            self.frame_model.appendRow(item)
        self.frame_model.layoutChanged.emit()

    def _show_selected_frame(self):
        print("Frame changed")
        index_entry = self.ui.imgList.selectionModel().selectedIndexes()[0].row()
        entry = self.entry_model.get(index_entry)
        index_frame = self.ui.listView.selectionModel().selectedIndexes()[0].row()
        print(index_frame)
        self.data = entry.imgarray[int(index_frame)]
        self.img.setImage(self.data)

    def _process_fluorescence(self, buffer_item):
        imgArrays = buffer_item.buffer
        fore = np.array(imgArrays[0])
        back = np.array(imgArrays[1])
        fore[fore < back] = back[fore < back]
        diff = fore - back

        def _img_time(t):
            return 2.16e1*t 

        def _img_gain(g):
            return 4.87e3*np.exp(g*1.17e-1)

        def _img_pwr(p):
            return np.polyval([ -13560.43361486,  179062.01299561, -753441.71015276, 1025454.73261022], p)

        scale_time = _img_time(0.4)/_img_time(buffer_item.shutter) # Img_time used for calibration was 400us = 0.4 ms
        scale_gain = _img_gain(14.0)/_img_gain(buffer_item.gain)
        scale_power = _img_pwr(5.0)/_img_pwr(buffer_item.power)

        return 61.43*scale_time*scale_gain*scale_power*diff

    def _process_absorption(self, buffer_item):
        logger.debug("processing absorption")
        imgArrays = buffer_item.buffer
        
        if self.ui.checkBox_absScale.isChecked():
            bounds_roi, _ = self.roi.getArraySlice(self.data, self.img, returnSlice=True)
            bounds_roi_save, _ = self.roi_save.getArraySlice(self.data, self.img, returnSlice=True)
            logger.debug(f"ROI {bounds_roi}")
            logger.debug(f"ROI save{bounds_roi_save}")
            msk = np.zeros(imgArrays[0].shape, dtype=np.int8)
            msk[bounds_roi_save] = 1
            msk[bounds_roi] = 0

            fg_scale = np.nansum(imgArrays[0]*msk)
            bg_scale = np.nansum(imgArrays[1]*msk)

            absArray = (imgArrays[1]*fg_scale/bg_scale)/(imgArrays[0])
            absArray = np.nan_to_num(absArray, nan=1e-1, posinf=1e-1, neginf=1e-1)
            data = np.log(absArray)
            data = np.nan_to_num(data, nan=0, posinf=0, neginf=0)

        else:
            absArray = (imgArrays[1]-imgArrays[2])/(imgArrays[0]-imgArrays[2])
            absArray = np.nan_to_num(absArray, nan=1e-1, posinf=1e-1, neginf=1e-1)
            data = np.log(absArray)
            data = np.nan_to_num(data, nan=0, posinf=0, neginf=0)

        # scale factor for absolute atom number
        res_Xsec = 1.356 * 1e-9 # cm^2 (resonant cross section from Steck)
        px_to_um = 3.75 # um
        data = data / res_Xsec *(px_to_um**2*1e-8) # um to cm 

        return data

    def _init_plot(self):
        data = np.concatenate([np.ones((1, 1280, 960)), np.zeros((1, 1280, 960)), 2*np.ones((1, 1280, 960)), 3*np.ones((1, 1280, 960))], axis=0)
        buf = ImageBufferItem(buffer=data, gain=0.0, shutter=1.0, power=5.0)
        self._update_plot(buf)

    @pyqtSlot(np.ndarray)
    def setData(self,data):
        self._update_plot(data)

    # Callbacks for handling user interaction
    def update_roi(self):
        #selected = self.roi.getArraycRegion()
        # profiling revealed that getArraycRegion took a significant amount of time as it interpolates when the ROI handles don't align to an integer!
        # this method should only slice the numpy array by ineintegersgers and be much faster!
        slc, _ = self.roi.getArraySlice(self.data, self.img, returnSlice=True)
        selected = self.data[slc]

        ysum = selected.sum(axis=0)
        y_x =  np.arange(len(ysum))
        
        xsum = selected.sum(axis=1)
        x_x = np.arange(len(xsum))

        self.plot_x.plot(x_x, xsum, clear=True)
        self.plot_y.plot(ysum, y_x, clear=True)

        if self.ui.fitCheckBox.isChecked():
            popt_x, pcov_x = fit1Dgauss((x_x,xsum))
            popt_y, pcov_y = fit1Dgauss((y_x,ysum))

            #fix negative sigmas
            popt_x[2] = abs(popt_x[2])
            popt_y[2] = abs(popt_y[2])

            self.plot_x.plot(x_x, gauss1D(x_x,*popt_x))
            self.plot_y.plot(gauss1D(y_x,*popt_y),y_x)

            self.ui.fitSpinBox_fluorX.setText("{:.3e}".format(popt_x[0]*popt_x[2]*np.sqrt(2*np.pi)))
            self.ui.fitSpinBox_fluorY.setText("{:.3e}".format(popt_y[0]*popt_y[2]*np.sqrt(2*np.pi)))
            self.ui.fitSpinBox_sigmaX.setText("{:.3e}".format(popt_x[2]))
            self.ui.fitSpinBox_sigmaY.setText("{:.3e}".format(popt_y[2]))
            self.ui.fitSpinBox_atoms.setText("{:.3e}".format( np.sqrt(popt_x[0]*popt_y[0]*popt_x[2]*popt_y[2]*(2*np.pi))    ) ) ### add scale factor here ###  


    def update_roi_save_from_plot(self):
        xl, yl = self.roi_save.pos() # lower left corner
        w, h = self.roi_save.size() # width and height
        self.ui.x0SpinBox.blockSignals(True)
        self.ui.x1SpinBox.blockSignals(True)
        self.ui.y0SpinBox.blockSignals(True)
        self.ui.y1SpinBox.blockSignals(True)
        self.ui.x0SpinBox.setValue(xl)
        self.ui.x1SpinBox.setValue(xl+w)
        self.ui.y0SpinBox.setValue(yl)
        self.ui.y1SpinBox.setValue(yl+h)
        self.ui.x0SpinBox.blockSignals(False)
        self.ui.x1SpinBox.blockSignals(False)
        self.ui.y0SpinBox.blockSignals(False)
        self.ui.y1SpinBox.blockSignals(False)
        print("updated roi from plot")	

    def update_roi_save_from_spinbox(self):
        #xl, yl = self.roi_save.pos() # lower left corner
        #w, h = self.roi_save.size() # width and height
        #print("before:", xl, yl, w, h)
        x0 = self.ui.x0SpinBox.value()
        x1 = self.ui.x1SpinBox.value()
        y0 = self.ui.y0SpinBox.value()
        y1 = self.ui.y1SpinBox.value()
        #print("after:", x0, y0, x1-x0, y1-y0)
        self.roi_save.setPos(x0, y0, update=False)
        self.roi_save.setSize((x1-x0, y1-y0), update=False)
        print("updated roi from spin")	

    def update_roi_lock(self):
        lock = self.ui.checkBox_lockroi.isChecked()
        if lock:
            self.ui.x0SpinBox.setEnabled(False)
            self.ui.x1SpinBox.setEnabled(False)
            self.ui.y0SpinBox.setEnabled(False)
            self.ui.y1SpinBox.setEnabled(False)
            self.roi_save.setEnabled(False)
        else:
            self.ui.x0SpinBox.setEnabled(True)
            self.ui.x1SpinBox.setEnabled(True)
            self.ui.y0SpinBox.setEnabled(True)
            self.ui.y1SpinBox.setEnabled(True)
            self.roi_save.setEnabled(True)


def createViewer():
    win = MainWindow()
    # QtGui.QApplication.instance().exec_()
    win.show()
    return win

def startapp():
    QtGui.QApplication.instance().exec_()

def gauss1D(x,a,x0,sigma,c):
    return a*np.exp(-(x-x0)**2/(2*sigma**2))+c

def fit1Dgauss(data):
    (x,y) = data
    #inital guesses
    mean = sum(x * y) / sum(y)
    sigma = np.sqrt(sum(abs(y) * (x - mean)**2) / sum(abs(y)))
    p0 = [max(y)-min(y),mean,sigma,min(y)]
    popt, pcov = curve_fit(gauss1D, *data, p0)
    
    return popt,pcov



#win = MainWindow()

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    win = MainWindow(port=60614)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
