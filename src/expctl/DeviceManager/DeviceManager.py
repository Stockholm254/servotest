import socket
import pickle as pickle
import time
import zmq
from ..utilities import jGlobals
from ..utilities.util import *
import coloredlogs, logging

# Create ZeroMQ context
context = zmq.Context()

# Create a logger object.
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')

#Networking abstraction as zmq multipart messages
def _send_msg(sock, msg, payload=None):
    # Send a message (command) to the client with an optional payload
    if payload is None:
        #only send a string as a command
        sock.send_multipart([msg.encode(),])
    else:
        #send command and python object
        sock.send_multipart([msg.encode(), dumps(payload)])

def _recv_msg(sock):
    # Receive message, return string and (optional) payload (python object)
    multipart = sock.recv_multipart()
    msg = multipart[0].decode()
    if len(multipart)>1:
        payload = loads(multipart[1])
        return msg, payload
    else:
        return msg, None

class Device:

    def __init__(self, host, port, name = 'Seq', timeout=1.0):
        self.host = host
        self.port = port
        self.name = name
        self.timeout = timeout
        self.sock = None

    ######################################################################
    ###-------------------- Communication Commands --------------------###
    ######################################################################
    #Networking abstraction as zmq multipart messages
    def send_msg(self, msg, payload=None):
        _send_msg(self.sock, msg, payload)

    def recv_msg(self):
        return _recv_msg(self.sock)

    # Function try to connect to the server with timeout
    def Connect(self):
        #  Socket to talk to server
        sock = context.socket(zmq.REQ)
        sock.setsockopt(zmq.CONNECT_TIMEOUT, int(self.timeout*1e3))
        try:
            sock.connect(f"tcp://{self.host}:{self.port}")
        except:
            logger.error(f"Error connecting to {self.host}:{self.port}. Is the server listening?")
        else:
            self.sock = sock
    @property
    def connected(self):
        return False if self.sock is None else True

    # Send sequence data to the server
    def Send(self, seq): 
        #try: 
        #    jGlobals.RUN_FLAG
        #except NameError:
        #    return
        #if jGlobals.RUN_FLAG == 0: # if RUN_FLAG is 0, do not send the data
        #    return

        # Check if server connected
        if self.sock is None:
            logger.error("Server not connected!, Connect() before sending!")
            return

        # Try send the sequence data. Return 0 if connection is termintated by the server
        try:
            self.send_msg("SEQ", payload=seq)  # Send the sequence data, gets pickled
            response, _ = self.recv_msg() # Print server's reply if connection
            print(response)
        except Exception as e:
            logger.exception("Problem receiving ACK.")
            
    # Hold the device until being physically triggered
    def Queue(self): 
        # Check if server connected
        if self.sock is None:
            logger.error("Server not connected!, Connect() before sending!")
            return

          # Send QUEUE command
        self.send_msg("QUEUE")

    # Receive message from server after "QUEUE" command
    def PrepFinish(self): 
        try:
            response, _ = self.recv_msg()
            print(response)
            return 1
        except:
            return 0

    # Run the sequence
    def Run(self): 
        # Check if server connected
        if self.sock is None:
            logger.error("Server not connected!, Connect() before sending!")
            return

        self.send_msg("RUN")
        response, _ = self.recv_msg()
        print(response)

     # THIS ROUTINE WAITS FOR UP TO 1.1*STOP_TIME/1000000 seconds FOR THE SEQUENCE TO COMPLETE, AS EVIDENCE BY THE ASSOCIATED SERVER BEING ABLE TO REPLY TO A PING REQUEST! returns true if the server finished, false otherwise
    def WaitTilDone(self):
        return self.Ping()

    # Ping the servers
    def Ping(self):
        #TODO needs rework!
        # Check if server connected
        if self.sock is None:
            logger.error("Server not connected!, Connect() before sending!")
            return

        self.send_msg("PING")
        try:
            response, _ = self.recv_msg()
            print(response)
        except:
            logger.error("Ping from server timed out")
            return False
        else:
            return True

    # Get plot data from device servers
    def AcquirePlotData(self):
        # Check if server connected
        if self.sock is None:
            logger.error("Server not connected!, Connect() before sending!")
            return

          # Send QUEUE command
        self.send_msg("GETPLOTDATA")
        try:
            response, plt_data = self.recv_msg()
            print(response)
            return plt_data
        except:
            logger.error("Failed to get plot data")
            return None


class DeviceManager:
    '''Module for talking to all hardware servers
    This module will have the information about status of all sequences and servers. It 
    is also responsible for all the communication between the front panel and servers
    through a TCP/IP port. 
    '''

    def __init__(self, all_seqs, act_seqs):
        self.seq_all = all_seqs # all available sequences defined in all_channels.py
        self.seq_act = act_seqs # sequences being used

        # Get sequence to graph
        self.seq_plot = []
        for _seq in self.seq_all:
            if _seq.graph == 1:
                self.seq_plot.append(_seq)

        self.devices = {s.name: Device(host=s.IP, port=s.port, name=s.name) for s in self.seq_act}

    def connect(self):
        
        # Initialize poll set
        self.poller = zmq.Poller()

        socks = {}
        for dev in self.devices.values():
            dev.Connect()
            sock = dev.sock
            self.poller.register(sock, zmq.POLLIN)
            socks[dev.name] = sock
            logger.debug(f"Connected to device {dev.name}")

        self.socks = socks

    def AwaitResposes(self, devices=None, timeout=1.0):
        if devices is None:
            devices = self.devices

        devices_recv = list(devices.keys()) #copy device names to keep track what was received
        devices_resp = {} #collect answers from devices
        # Process messages from device sockets
        t0 = time.time()
        while True:
            try:
                evsocks = dict(self.poller.poll(10)) #poll every 50ms for answers
            except KeyboardInterrupt:
                return None
                
            for d in devices_recv:
                dev = devices[d] #get device by name
                if dev.sock in evsocks:
                    resp, _ = dev.recv_msg()
                    devices_resp[d] = resp
                    devices_recv.remove(d)
            t1 = time.time()
            if len(devices_recv) == 0:
                logger.info("All devices prepared")
                return devices_resp

            if (t1-t0)>timeout:
                logger.error("AwaitResposes timed out, following servers left: " + str(devices_recv))
                return None

    def SendAndQueueSequences(self, master_sequence, timeout=1.):
        SlaveDevices = {}
        tqueuestart = time.time()
        for seq in self.seq_act:
            print(seq.name+" (Length: "+str(seq.TIME_STOP/1e6)+"s):")
            print('\tSending...')
            #for now, find device through name, TODO: make more robust way
            dev = self.devices[seq.name]
            dev.Send(seq)

            if seq != master_sequence: # Queue the sequence unless is master sequence
                SlaveDevices[seq.name] = dev
                dev.Queue()
                logger.debug(seq.name + " queued")
            else:
                logger.debug('\tMaster sequence, will run after all sequences have been queued...')
        tqueueend = time.time()

        responses = self.AwaitResposes(devices=SlaveDevices, timeout=timeout)
        for k, v in responses.items():
            logger.debug(f"Device {k} finished preparation: {v}")
        tcheckprepend = time.time()

        return tqueueend-tqueuestart , tcheckprepend-tqueueend

    def Run(self, master_sequence):
        dev = self.devices[master_sequence.name]
        dev.Run()

    def WaitForAllToFinish(self, timeout=1.0):
        for dev in self.devices.values():
            dev.send_msg("PING") #ping all devices

        responses = self.AwaitResposes(timeout=timeout)
        if responses is None:
            return False
        else:
            for k, v in responses.items():
                logger.debug(f"Device {k} finished running: {v}")
            return True