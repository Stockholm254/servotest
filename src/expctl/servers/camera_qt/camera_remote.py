from .camera_qt import *
import zmq

#win = MainWindow()

context = zmq.Context()
URL = "simonlab-rydfries.stanford.edu:55555"

class ZMQWorker(QObject):
    finished = pyqtSignal()
    result = pyqtSignal(object)
    storeSignal = pyqtSignal(object)

    def __init__(self, parent=None, url='localhost:55555'):
        #super(self.__class__, self).__init__(parent)
        super(ZMQWorker, self).__init__(parent)
        
        try:
            self.zmq_socket = context.socket(zmq.SUB)
            self.zmq_socket.connect(f"tcp://{url}")
            self.zmq_socket.subscribe("")
        except:
            logger.exception("Couldn't connect to the remote camera viewer!")
        else:
            logger.exception("Connected to the remote camera viewer!")

    def acquire(self, roi):

        poller = zmq.Poller()
        poller.register(self.zmq_socket, zmq.POLLIN)
        while True:
            socks = dict(poller.poll())
            if self.zmq_socket in socks:
                data = self.zmq_socket.recv_pyobj()
                # new data received, emit to main thread
                self.result.emit(data)

        print("Exiting...")
    
    @pyqtSlot(tuple)
    def start(self, roi):
        self.acquire(roi)

class RemoteMainWindow(MainWindow):
    def __init__(self, title='Qt Camera Server USB 3.0', port=60614):
        super().__init__(title, port)

    def _get_cams(self):
        return {0: {'i': 0,'name': 'remote', 'serial': 1234, 'res': '1234x1234'}}

    def _setup_roi_signals(self):
        pass

    def _init_zmq(self):
        pass

    def create_thread(self):

        # 1 - create Worker and Thread inside the Form
        camera_id = self.ui.comboBox.currentIndex()
        logger.info(f"Opening camera {camera_id}")
        # ser = self.cams[camera_id]['serial'] #serial of current camera
        # if ser in CAMERA_KWARGS.keys():
        #     kwargs = CAMERA_KWARGS[ser]
        # else:
        #     kwargs = {}

        #self.worker = ServerWorker(port=self.port, camera_id=camera_id, camera_kwargs=kwargs)  # no parent!
        self.worker = ZMQWorker(url=URL)
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
    win = RemoteMainWindow(title='Remote Camera Viewer', port=60613)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
