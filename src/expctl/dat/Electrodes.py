#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import socket
from pathlib import Path

# transfer_mat = np.loadtxt("C:/Users/Simonlab/Programming/Control Suite/utilities/Fop8x9.csv") # Based on Ariel's simulation of Nathan's cavity
# transfer_mat = 10.0*np.loadtxt("./dat/B1.dat") # Based on Logan's simulation of Nathan's cavity
transfer_mat = 10.0*np.loadtxt(Path(__file__).parent/"B1.dat") # Based on Logan's simulation of Nathan's cavity
#transfer_mat = 10.0*np.loadtxt("C:/users/lukas/box/lukas/04_software/python/py3lab/control_suite_package/expctl/src/expctl/dat/B1.dat") # Based on Logan's simulation of Nathan's cavity

# Arduino logger server
host = '192.168.1.105'
port = 60637

VDevRatio = 200.0
a_x = 0.00015788
Ex0 = -0.026813

# def GetPiezoVoltage():
	# s = socket.socket()
	# s.connect((host, port))
	# v = float(s.recv(3))
	# # v = VDevRatio*v*5.0/256
	# s.close()
	# # print "Piezo voltage: "+str(v)
	# return v
	
def GetPiezoVoltage():
	return 60.0

def FieldOffset(PiezoVoltage):
	if PiezoVoltage >= 100:
		Ex_offset = a_x*PiezoVoltage+Ex0
		Ey_offset = -0.073
		Ez_offset = -0.175
	else:
		Ex_offset = a_x*100.0+Ex0
		Ey_offset = -0.073
		Ez_offset = -0.175
	arr_Eoff = [Ex_offset, Ey_offset, Ez_offset, 0.0, 0.0, 0.0, 0.0, 0.0]
	return np.array(arr_Eoff)

def Field2Voltage_PiezoCompensated(FVec):
	PiezoVoltage = GetPiezoVoltage()
	FVec = FVec+FieldOffset(PiezoVoltage)
	VVec = np.dot(transfer_mat, FVec)
	return VVec
	
def Field2Voltage(FVec):
	VVec = np.dot(transfer_mat, FVec)
	return VVec



