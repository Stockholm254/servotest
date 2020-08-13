import socket
import pickle as pickle
import time
import zmq

from ..utilities import jGlobals
from ..utilities.util import *

context = zmq.Context()

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

    ######################################################################
    ###-------------------- Communication Commands --------------------###
    ######################################################################
    # Function try to connect to the server with timeout
    def TryConnect(self, host, port, to=1.0):
        #  Socket to talk to server
        sock = context.socket(zmq.REQ)
        #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        #sock.settimeout(to)
        try:
            #sock.connect((host, port))
            sock.connect(f"tcp://{host}:{port}")
            return sock
        except IOError:
            printError(f"Send(): Error connecting to {host}:{port}. Is the server listening?")
            return 0

    # Send sequence data to the server
    def Send(self, seq): 
        try: 
            jGlobals.RUN_FLAG
        except NameError:
            return
        if jGlobals.RUN_FLAG == 0: # if RUN_FLAG is 0, do not send the data
            return

        # Connect to the server
        host, port = seq.IP, seq.port
        sock = self.TryConnect(host, port)
        if sock == 0: return 0

        # Pack and send data
        #seqdata = pickle.dumps(seq, 1) # pack sequence data
        
        # Try send the sequence data. Return 0 if connection is termintated by the server
        try:
            #send_msg(sock, "["+host+"] SEQ (Incoming sequence)") # Alert server that a sequence is coming
            #send_msg(sock, seqdata) # Send the pickled sequence data
            send_msg(sock, "SEQ", payload=seq)
            #printGrayDate(recv_msg(sock)) # Print server's reply if connection
            response, _ = recv_msg(sock)
            print(response)
        except:
            return 0
        sock.close()

        return 1

    # Hold the device until being physically triggered
    def Queue(self, seq): 
        # Connect to the server
        host, port = seq.IP, seq.port
        sock = self.TryConnect(host, port)
        if sock == 0: return -1

          # Send QUEUE command
        send_msg(sock, "QUEUE")
        return sock

    # Receive message from server after "QUEUE" command
    def PrepFinish(self, sock): 
        try:
            #printGrayDate(recv_msg(sock))
            response, _ = recv_msg(sock)
            print(response)
            sock.close()
            return 1
        except:
            return 0

    # Run the sequence
    def Run(self, seq): 
        # Connect to the server
        host, port = seq.IP, seq.port
        sock = self.TryConnect(host, port)
        if sock == 0: return 0

        send_msg(sock, "RUN")
        #printGrayDate(recv_msg(sock))
        response, _ = recv_msg(sock)
        print(response)
        sock.close()

     # THIS ROUTINE WAITS FOR UP TO 1.1*STOP_TIME/1000000 seconds FOR THE SEQUENCE TO COMPLETE, AS EVIDENCE BY THE ASSOCIATED SERVER BEING ABLE TO REPLY TO A PING REQUEST! returns true if the server finished, false otherwise
    def WaitTilDone(self, seq):
        sock = context.socket(zmq.REQ)
        #sock = socket.socket()
        #sock.settimeout(1.1*self.TIME_STOP/1e6) #GIVE IT TWICE THE MAX SEQUENCE TIME TO FINISH, BUT REALLY WE SHOULD NEED NO TIME FLAT!
        serverfinished=True
        try:
           #sock.connect((seq.IP, seq.port))
           sock.connect(f"tcp://{seq.IP}:{seq.port}")
        except IOError:
            print(self.name + " Stalled or not listening!")
            serverfinished=False
        else:
            send_msg(sock, "PING")
            response, _ = recv_msg(sock)
            print(response)
        sock.close()
        return serverfinished

    # Ping the servers
    def Ping(self, seq):
        host, port = seq.IP, seq.port
        sock = self.TryConnect(host, port, to=0.1)
        if sock == 0: 
            return 0
        else:
            send_msg(sock, "PING")
            response, _ = recv_msg(sock)
            print(response)
            sock.close()
            return 1

    # Get plot data from device servers
    def AcquirePlotData(self, seq):
        # Connect to the server
        host, port = seq.IP, seq.port
        sock = self.TryConnect(host, port)
        if sock == 0: 
            return 0

          # Send QUEUE command
        send_msg(sock, "GETPLOTDATA")
        response, plt_data = recv_msg(sock)
        print(response)
        sock.close()
        return plt_data
        #try:
        #    plt_data = pickle.loads(rtn_msg)
        #    return plt_data
        #except:
        #    return -1
        