#!/usr/bin/python 
# -*- coding: utf-8 -*- 

import wx
import socket
import pickle as pickle
from threading import Thread
from .util import *
from ..config.config import * # control suite preference

HOST = IP_RYDBURGER
PORT = PORT_REMOTECTRL

def WriteFile(fdir, fname, txt):
	f = open(fdir+fname, 'w')
	for l in txt:
		f.write(l)
	f.close()
	return 1

def StopRemoteServer():
	# This will send a command to finish the last while loop
	sock = socket.socket()
	sock.connect((HOST, PORT))
	send_msg(sock, "["+HOST+"] CLOSESERVER")
	sock.close()
	return 1

EVT_ID_LOADSEQ = wx.NewId()
EVT_ID_LOADMVS = wx.NewId()
EVT_ID_LOOPRUN = wx.NewId()

def EVT_LOADSEQ(win, func):
	win.Connect(-1, -1, EVT_ID_LOADSEQ, func)
def EVT_LOADMVS(win, func):
	win.Connect(-1, -1, EVT_ID_LOADMVS, func)
def EVT_LOOPRUN(win, func):
	win.Connect(-1, -1, EVT_ID_LOOPRUN, func)

class RemoteEvent(wx.PyEvent):
	"""Simple event to carry arbitrary result data back to GUI."""
	def __init__(self, EVT_ID):
		wx.PyEvent.__init__(self)
		self.SetEventType(EVT_ID)

class RemoteServer(Thread):
	def __init__(self, FrontPanel):
		Thread.__init__(self)

		self.FrontPanel = FrontPanel # notify window

		self._dir = DIR_REM
		self.seq_name = ""
		self.mv_name  = ""

		# Create remote server
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((HOST, PORT))
		self.sock.listen(1)

		self._abort = 0 # Abort indicator

		# Bind FrontPanel functions
		EVT_LOADSEQ(self.FrontPanel, self.FrontPanel.LoadSeq)
		EVT_LOADMVS(self.FrontPanel, self.FrontPanel.LoadMV)
		EVT_LOOPRUN(self.FrontPanel, self.FrontPanel.OnRunLooped)

		self.start() # This starts the thread running on creation

	def run(self):
		printGreen("Remote server started!")

		while not self._abort:
			ClientSocket, addr = self.sock.accept()
			printYellow('Receiving from'+str(addr[0]))

			while True:
				data = printGrayDate(recv_msg(ClientSocket))
				command = data.strip().split(' ', 2)[0]

				if command == 'SEQUENCE':
					self.seq_name = pickle.loads(recv_msg(ClientSocket))
					printGreen("Getting sequence '"+self.seq_name[1:]+"'")
					seq_data = pickle.loads(recv_msg(ClientSocket))
					WriteFile(self._dir, self.seq_name, seq_data)
					reply = "Received sequence file: '"+str(self.seq_name)+"'; "
					send_msg(ClientSocket, reply)
					break

				elif command == 'MV':
					self.mv_name = pickle.loads(recv_msg(ClientSocket))
					printGreen("Getting MV file '"+self.mv_name[1:]+"'")
					mv_data = pickle.loads(recv_msg(ClientSocket))
					WriteFile(self._dir, self.mv_name, mv_data)
					reply = "Received MV file: '"+str(self.mv_name)+"'; "
					send_msg(ClientSocket, reply)
					break

				elif command == 'LOADSEQ':
					if self.seq_name == "":
						printError('No sequence file received!')
						break
					self.FrontPanel.dir_seq   = self._dir
					self.FrontPanel.fname_seq = self.seq_name[1:]
					self.script_name          = self.seq_name[1:].replace(".py", "")
					wx.PostEvent(self.FrontPanel, RemoteEvent(EVT_ID_LOADSEQ))
					reply = 'Sequence file \''+self.seq_name+'\' has been loaded.'
					send_msg(ClientSocket, reply)
					break

				elif command == 'LOADMV':
					if self.mv_name == "":
						printError('No MV file received!')
						break
					self.FrontPanel.dir_mv   = self._dir
					self.FrontPanel.fname_mv = self.mv_name[1:]
					wx.PostEvent(self.FrontPanel, RemoteEvent(EVT_ID_LOADMVS))
					reply = 'MV file \''+self.mv_name+'\' has been loaded.'
					send_msg(ClientSocket, reply)
					break

				elif command == 'RUNLOOP':
					wx.PostEvent(self.FrontPanel, RemoteEvent(EVT_ID_LOOPRUN))
					reply = 'Running loop.'
					send_msg(ClientSocket, reply)
					break

				elif command == 'DEBUG':
					self.FrontPanel.OnPingServers(None)
					break

				elif command == 'CLOSESERVER':
					break

				else:
					reply = 'Unexpected command!'
					send_msg(clientSocket, server.ReplyHeader() + reply)
					break

			ClientSocket.close()
		
		self.sock.close()
		printGreen('Remote server closed!')

	def abort(self):
		self._abort = 1


