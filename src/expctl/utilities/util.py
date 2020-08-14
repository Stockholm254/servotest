#!/usr/bin/python

import pickle as pickle
import ctypes
import os
import re
import struct
import sys
import argparse
import zmq
from pickle import dumps, loads

def is_int(s):
  try:
      int(s)
      return True
  except ValueError:
      return False
        
def is_number(s):
  try:
    float(s)
    return True
  except ValueError:
    return False

# UNITS #
s = 1000000
ms = 1000
us = 1
ns = .01
   
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
COLOR_BLACK       = 0x00
COLOR_DARK_RED    = 0x04
COLOR_GRAY        = 0x08
COLOR_GREEN       = 0x0A
COLOR_CYAN        = 0x0B
COLOR_RED         = 0x0C
COLOR_PINK        = 0x0D
COLOR_YELLOW      = 0x0E
COLOR_WHITE       = 0x0F

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
  
#=============================== Print Help Menu =================================#
# Print the help menu!  
def createParser():
  parser = argparse.ArgumentParser()
  parser.add_argument('-p', '--plot', dest='PlotGraphs', action='store_const', const=True, default=False, help='plot sequences and store the graphs')
  args = parser.parse_args()
  return args

def printHelp(args):
  print(('\n' * 100))
  print("###############################################################################")
  print("#                        SimonDOUT v.0.1 (Graham Greve)                       #")
  print("#       Create tasks for the NI PCIe-6537 50MHz Digital Output card.          #")
  print("#                                                                             #")
  print("# COMMANDS:                                                                   #")
  print("#                                                                             #")
  print("#  ", end=' ')
  setColor(COLOR_PINK); print("help", end=' '); resetColor()
  print("        Print this help information.                                 #")
  print("#  ", end=' ')
  setColor(COLOR_PINK); print("start", end=' '); setColor(COLOR_YELLOW); print("[id]", end=' '); resetColor()
  print("  Create a new task on a line between 0-31                     #")
  print("#  ", end=' ')
  setColor(COLOR_PINK); print("status", end=' '); resetColor()
  print("      Print line status: 1 is busy, 0 is free                      #")
  print("#  ", end=' ')
  setColor(COLOR_PINK); print("stop", end=' '); setColor(COLOR_YELLOW); print("[id]", end=' '); resetColor()
  print("   Stop a task                                                  #")
  print("#  ", end=' ')
  setColor(COLOR_PINK); print("quit", end=' '); resetColor()
  print("        Exit the program                                             #")
  print("#                                                                             #")
  print("###############################################################################")
  print("")

  
#============================== Print Line Status ================================#
# Print line status: 1 is busy, 0 is free.
def printStatus(args):
    print("\n  port0: ", end=' ')
    for y in range(0, 8):
      sys.stdout.write(str(lineStatus[y])) # print without space
    print("  port1: ", end=' ')
    for y in range(8, 16):
      sys.stdout.write(str(lineStatus[y]))
    print("\n  port2: ", end=' ')
    for y in range(16, 24):
      sys.stdout.write(str(lineStatus[y]))
    print("  port3: ", end=' ')
    for y in range(24, 32):
      sys.stdout.write(str(lineStatus[y]))
    print("\n")
    
# MATH #
def formatTimeUnits(us):
  if (us >= 1000000):
    return str(us/s) + "s"
  if (us >= 1000):
    return str(us/ms) + "ms"
  if (us >= 1):
    return str(us) + "us"
  else:
    return str(us) + "ns"

# takes microseconds and returns a scaled version
def fakeDuration(us):
  if (us >= 1000000):
    return 100
  if (us >= 10000):
    return 70
  if (us >= 100):
    return 50
  if (us >= 1):
    return 35
  else:
    return 20
