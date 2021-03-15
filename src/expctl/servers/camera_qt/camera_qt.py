# -*- coding: utf-8 -*-
"""
V0.5 of Camera server with Qt and pyqtgraph
"""
from dataclasses import dataclass
from datetime import datetime
from numpy.lib.npyio import save
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import numpy as np
import os
import time
from scipy.optimize import curve_fit
try:
    import PyCapture2
except:
    from .gpcamera import Mock_GP_camera as Camera
else:
    from .gpcamera import GP_camera as Camera

from ..ServerClass import logger, Server
from copy import deepcopy

import expdatabase.conf as conf
from expdatabase.db import insertImage
from expdatabase.types import ShotImage
from pymongo import MongoClient
from bson import ObjectId

IMG_ABS= {0: 'fg', 1: 'bg', 2: 'ref'}
IMG_FL = {0: 'fg', 1: 'bg'}

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


class DbWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        #super(self.__class__, self).__init__(parent)
        super(DbWorker, self).__init__(parent)
        try:
            self.client = MongoClient(host=conf.DB_HOST, port=conf.DB_PORT, username=conf.USER_RAW_WRITER , password=conf.PASSWORD_RAW_WRITER, authSource=conf.DB_RAW)
        except:
            logger.exception("Database connection could not be established!")
        else:
            logger.info("Database connected.")

    def storeImage(self, item):
        insertImage(self.client, item.run_id, item.shot, item.save)
        logger.debug("stored image from thread")
    
    @pyqtSlot(object)
    def store(self, item):
        self.storeImage(item)

class CameraServer(Server):
    
    def __init__(self, name, port, message, parent, camera_id):
        super().__init__(name, port, message)
        #self.device = GP_camera(BIT12 = False)
        self.parent=parent
        self.device = Camera(camera_id=camera_id)
        self.ROI = ()
        self.imgbuffer=[]
        try:
            self.device.InitCamera()
            logger.info("Camera initiated.")
        except:
            logger.exception("Failed to connect the camera!")

        #create saving thread for db
        # self.queue = queue.Queue()
        # self.DbThread = DbWriter(q = self.queue, name='dbwriter')
        # self.DbThread.start()

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
                        success, imgbuffer = self.device.GrabImages(shutter=ShutterTime, gain=gain_mv, number=self.NumOfImage, runname=run_name, foldername=folder_name)
                        logger.debug("Success {}".format(success))
                    except:
                        logger.exception("Failed to grab images!")
                    else:
                        self.imgbuffer = np.stack(imgbuffer, axis=0)
                        logger.debug("Grabbed {} images".format(len(self.imgbuffer)))
                        buf = deepcopy(self.imgbuffer)
                        # send images to GUI
                        self.parent.result.emit(buf)
                        logger.debug("Emitted to GUI")

                        # apply ROI for saving
                        if len(self.ROI)>0:
                            x0, x1, y0, y1 = self.ROI
                            imgbuffer = self.imgbuffer[:,x0:x1,y0:y1]

                        #save image into db
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
                                        roi=self.ROI,
                                        data=ims)
                        save = True if seq.saveswitch==2 else False
                        item = ImageQueueItem(run_id=ObjectId(seq.run_id), save=save, shot=shot)
                        #self.queue.put(item)
                        self.parent.storeSignal.emit(item)
                        logger.debug("Emitted to Thread")

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
    storeSignal = pyqtSignal(object)

    def __init__(self, parent=None, camera_id=0):
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
        self.serv = CameraServer("COut1", 60614, message=message, parent=self, camera_id=camera_id)
        self.worker = DbWorker()  # no parent!
        self.thread = QThread()  # no parent!

        self.storeSignal.connect(self.worker.store)
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.thread.quit)
        self.thread.start()

    def acquire(self, roi):
        self.serv.set_ROI(roi)
        self.serv.main_loop(cond_fn=(lambda : not QThread.currentThread().isInterruptionRequested()) )

        self.thread.quit()
        self.thread.wait()
        print("Exiting...")
    
    @pyqtSlot(tuple)
    def start(self, roi):
        self.acquire(roi)

class MainWindow(TemplateBaseClass):  
    start_acquire = pyqtSignal(tuple)
    stop_acquire = pyqtSignal()

    def __init__(self):
        TemplateBaseClass.__init__(self)
        self.setWindowTitle('Qt Camera Server')
        
        self.data = np.zeros((1280, 960))

        # Create the main window
        self.ui = WindowTemplate()
        self.ui.setupUi(self)
        #get cameras
        cams = Camera.ListCameras()
        camstrs = ["{}: {}".format(c['name'], c['serial']) for c in cams.values()]
        self.ui.comboBox.addItems(camstrs)
        self.ui.stopButton.clicked.connect(self.button_stop)
        self.ui.startButton.clicked.connect(self.button_start)
        self.ui.stopButton.setEnabled(False)
        for el in [self.ui.x0SpinBox, self.ui.x1SpinBox, self.ui.y0SpinBox, self.ui.y1SpinBox]:
            el.setRange(0,2000)
            el.valueChanged.connect(self.update_roi_save_from_spinbox)
        self.ui.checkBox_lockroi.stateChanged.connect(self.update_roi_lock)
        self.setup_plot()

        self.show()

    @pyqtSlot()
    def button_stop(self):
        self.stop_thread()
        self.ui.startButton.setEnabled(True)
        self.ui.stopButton.setEnabled(False)
        self.ui.checkBox_saveroi.setEnabled(False)
        self.ui.x0SpinBox.setEnabled(True)
        self.ui.x1SpinBox.setEnabled(True)
        self.ui.y0SpinBox.setEnabled(True)
        self.ui.y1SpinBox.setEnabled(True)
        self.roi_save.setEnabled(True)

    @pyqtSlot()
    def button_start(self):
        
        if self.ui.checkBox_saveroi.isChecked():
            x0 = self.ui.x0SpinBox.value()
            x1 = self.ui.x1SpinBox.value()
            y0 = self.ui.y0SpinBox.value()
            y1 = self.ui.y1SpinBox.value()
            roi = (x0, x1, y0, y1)
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
        self.worker = ServerWorker(camera_id=camera_id)  # no parent!
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

  
    def _update_plot(self, imgArrays):
        #
        mode = None
        if imgArrays.shape[0]==3:
            absArray = (imgArrays[0]-imgArrays[2])/(imgArrays[1]-imgArrays[2]) #+1e-6
            data = 1-absArray
            mode = "ABS"
            logger.debug("ABS")
        elif imgArrays.shape[0]==2:
            fore = np.array(imgArrays[0])
            back = np.array(imgArrays[1])
            fore[fore < back] = back[fore < back]
            diff = fore - back
            data = diff
            mode = "FL"
            logger.debug("FL")
        else:
            data = imgArrays
            logger.debug("1 image")

        # if data.shape != self.data.shape:
        # 	self.plot_main.autoRange() 
        self.data = data
        self.img.setImage(self.data)
        
        if mode=="ABS":
            self.hist.setLevels(0., 1.)
            #self.hist.setHistogramRange(0., 1.)
        else:
            if self.ui.checkBox_autoscale.isChecked():
                self.hist.setLevels(np.nanmin(self.data), np.nanmax(self.data))
                #self.hist.setHistogramRange(np.nanmin(self.data), np.nanmax(self.data))
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

        ysum = selected.sum(axis=0)
        y_x =  np.arange(len(ysum))
        
        xsum = selected.sum(axis=1)
        x_x = np.arange(len(xsum))

        self.plot_x.plot(x_x, xsum, clear=True)
        self.plot_y.plot(ysum, y_x, clear=True)

        if self.ui.fitCheckBox.isChecked():
            popt_x, pcov_x = fit1Dgauss((x_x,xsum))
            popt_y, pcov_y = fit1Dgauss((y_x,ysum))

            self.plot_x.plot(x_x, gauss1D(x_x,*popt_x))
            self.plot_y.plot(gauss1D(y_x,*popt_y),y_x)

            # self.ui.fluorX.setText("Fluorescence X :"+ f'{(popt_x[0]*popt_x[2]*np.sqrt(2*math.pi)):.2f}')
            # self.ui.fluorY.setText("Fluorescence Y :"+ f'{(popt_y[0]*popt_y[2]*np.sqrt(2*math.pi)):.2f}')
            # self.ui.sigmaX.setText("Sigma X :"+ f'{popt_x[2]:.2f}')
            # self.ui.sigmaY.setText("Sigma Y :"+ f'{popt_y[2]:.2f}')
            #logger.debug(popt_x)
            #logger.debug(popt_y)
            self.ui.fitSpinBox_fluorX.setText("{:.3e}".format(popt_x[0]*popt_x[2]*np.sqrt(2*np.pi)))
            self.ui.fitSpinBox_fluorY.setText("{:.3e}".format(popt_y[0]*popt_y[2]*np.sqrt(2*np.pi)))
            self.ui.fitSpinBox_sigmaX.setText("{:.3e}".format(popt_x[2]))
            self.ui.fitSpinBox_sigmaY.setText("{:.3e}".format(popt_y[2]))
            self.ui.fitSpinBox_atoms.setText("{:.3e}".format(popt_x[0]*popt_x[2]*popt_y[0]*popt_y[2]*(2*np.pi)))


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
        xl, yl = self.roi_save.pos() # lower left corner
        w, h = self.roi_save.size() # width and height
        print("before:", xl, yl, w, h)
        x0 = self.ui.x0SpinBox.value()
        x1 = self.ui.x1SpinBox.value()
        y0 = self.ui.y0SpinBox.value()
        y1 = self.ui.y1SpinBox.value()
        print("after:", x0, y0, x1-x0, y1-y0)
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



win = MainWindow()

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    win = MainWindow()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
