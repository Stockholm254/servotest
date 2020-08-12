#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

import zmq
import numpy as np
from pickle import dumps, loads

context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")
flags=0
seq = np.array([1., 2., 3.])

#  Do 10 requests, waiting each time for a response
for request in range(10):
    print("Sending request %s …" % request)
    string = b"SEQ"
    #socket.send_string(string, flags | zmq.SNDMORE)
    #socket.send_pyobj(seq, flags)
    socket.send_multipart([string, dumps(seq)])
    #  Get the reply.
    message = socket.recv_string(flags)
    print("Received reply %s [ %s ]" % (request, message))
    payload = socket.recv_pyobj(flags)
    print("Payload: ", payload)