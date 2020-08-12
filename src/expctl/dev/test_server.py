
#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#
from signal import signal, SIGINT
from sys import exit
import time
import zmq
import numpy as np
from pickle import dumps, loads

def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    exit(0)

signal(SIGINT, handler)
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
flags = 0

while True:
    #  Wait for next request from client
    #command = socket.recv_string(flags)
    #print("Received request: %s" % command)
    #payload = socket.recv_pyobj(flags)
    #print("Payload: ", payload)
    multipart = socket.recv_multipart(flags)
    print(multipart)
    if len(multipart)>1:
        payload = loads(multipart[1])
        print("Payload: ", payload)
        #  Do some 'work'
        time.sleep(0.1)
        response = payload + 2.
        #  Send reply back to client
        socket.send_multipart([b"SUCCESS", dumps(response)])
    else:
        socket.send_multipart([b"SUCCESS",])
