import ctypes
import msvcrt
import struct
import sys
import socket
import time
import os
import re
import zmq
from pickle import dumps, loads

uInt8   = ctypes.c_ubyte
int16   = ctypes.c_short
uInt16  = ctypes.c_ushort
int32   = ctypes.c_long
uInt32  = ctypes.c_ulong
uInt64  = ctypes.c_ulonglong
float64 = ctypes.c_double
task_handle_type = uInt32

context = zmq.Context()

#=============================== Server Class ==================================#
class Server:
  # def __init__(self, name, port):
  def __init__(self, name, port):
    self.message = ''
    self.name = name
    self.port = port
    self.task_id = 0
    self.seq = None
    self.sock = None
    

  def Listen(self):
    ClearTerminal()
    if self.message:
      print((self.message))
    self.sock = context.socket(zmq.REP)
    port = self.port
    try:
      #self.sock.bind((host, port))
      self.sock.bind(f"tcp://*:{port}")
      printYellow(self.name + ' started listening on ' + str(port) + ".") #TODO fix print address
    except socket.error as msg:
      printError('Bind failed. Error code: ' + str(msg[0]) + '. Error message: ' + msg[1])
      sys.exit()
    #self.sock.listen(5)
    
  def ReplyHeader(self):
    return time.strftime('['+self.name+': %b %d %H:%M:%S]') + " "
    

#=============================== Networking ==================================#
def send_msg(sock, msg, payload=None):
    # Send a message (command) to the client with an optional payload
    if payload is None:
      #only send a string as a command
      sock.send_multipart([msg.encode(),])
    else:
      #send command and python object
      sock.send_multipart([msg.encode(), dumps(payload)])

def recv_msg(sock):
    # Receive message, return string and (optional) payload (python object)
    multipart = sock.recv_multipart()
    msg = multipart[0].decode()
    if len(multipart)>1:
      payload = loads(multipart[1])
      return msg, payload
    else:
      return msg, None
   
#========================== Display / Color  ==================================#
def ClearTerminal():
  os.system('cls' if os.name=='nt' else 'clear')  

# Required for colored text 
def get_csbi_attributes(handle):
  import struct
  csbi = ctypes.create_string_buffer(22)
  res = ctypes.windll.kernel32.GetConsoleScreenBufferInfo(handle, csbi)
  # assert res
  if res:
    (bufx, bufy, curx, cury, wattr, left, top, right, bottom, maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
    return wattr

# Constants from the Windows API
STD_OUTPUT_HANDLE = -11
COLOR_BLACK        = 0x00
COLOR_DARK_RED     = 0x04
COLOR_GRAY         = 0x08
COLOR_GREEN        = 0x0A
COLOR_CYAN         = 0x0B
COLOR_RED          = 0x0C
COLOR_PINK         = 0x0D
COLOR_YELLOW       = 0x0E
COLOR_WHITE        = 0x0F

if (os.name != "posix"):
  color_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
  color_reset = get_csbi_attributes(color_handle)


# Set background and foreground color  
def setColor(foreground=0xF, background=0x0):
  if (os.name != "posix"):
    ctypes.windll.kernel32.SetConsoleTextAttribute(color_handle, foreground | (background << 4))

  
# Set colors back to normal
def resetColor():
  if (os.name != "posix"):
    ctypes.windll.kernel32.SetConsoleTextAttribute(color_handle, color_reset)

def printError(msg):
  if (os.name == "posix"):
    print("\033[91m"+str(msg)+"\033[0m")
  else:
    setColor(COLOR_RED); print(msg); resetColor()
    
def printComment(msg):
  if (os.name == "posix"):
    print("\033[94m"+str(msg)+"\033[0m")
  else:
    setColor(COLOR_CYAN); print(msg); resetColor()
    
def printGreen(msg):
  if (os.name == "posix"):
    print("\033[92m"+str(msg)+"\033[0m")
  else:
    setColor(COLOR_GREEN); print(msg); resetColor()
    
def printYellow(msg):
  if (os.name == "posix"):
    print("\033[93m"+str(msg)+"\033[0m")
  else:
    setColor(COLOR_YELLOW); print(msg); resetColor()

def printGrayDate(msg):
  try:
    matchObj = None
    matchObj = re.match(r'(\[.*\])(.*)', msg)
  except TypeError as te:
    print("Type Error. Got msg = ",msg)
    
  if not matchObj:
    print("Error in printGrayDate. Expected message of format: [xxx] Message.")
    print(msg)
    return msg
  if matchObj.group(2) == " PING":
    return str(matchObj.group(2))
  if (os.name == "posix"):
    print("\x1b[37;2m"+str(matchObj.group(1))+"\033[0m" + str(matchObj.group(2)))
  else:
    setColor(COLOR_GRAY); sys.stdout.write(str(matchObj.group(1))); resetColor(); print(str(matchObj.group(2)))
  return str(matchObj.group(2))
