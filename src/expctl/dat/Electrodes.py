#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import socket
from pathlib import Path
from scipy.optimize import lsq_linear

with np.load(Path(__file__).parent/"lluna_matrix8.npz") as data:
	transfer_mat = data['mat_field2el']
with np.load(Path(__file__).parent/"lluna_matrix9_msj.npz") as data:
	matrix9_ln = data['mat_field2el']

	
def Field2Voltage(_FVec):
	FVec = np.array(_FVec)
	VVec = np.dot(transfer_mat, FVec)
	return VVec


def Field2Voltage_ln(_FVec):
	FVec = np.array(_FVec)#[[0,1,2,3,6,7,9,10]]
	VVec = np.dot(matrix9_ln, FVec)
	return VVec













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
def Field2Voltage_lsq(_FVec):
	FVec = np.array(_FVec)
	res1 = lsq_linear(matrix9, FVec, bounds=(-10, 10), lsmr_tol='auto', verbose=1)
	VVec = res1.x
	return VVec

# transfer_mat = np.loadtxt("C:/Users/Simonlab/Programming/Control Suite/utilities/Fop8x9.csv") # Based on Ariel's simulation of Nathan's cavity
# transfer_mat = 10.0*np.loadtxt("./dat/B1.dat") # Based on Logan's simulation of Nathan's cavity
# transfer_mat = 10.0*np.loadtxt(Path(__file__).parent/"B1.dat") # Based on Logan's simulation of Nathan's cavity

# with np.load(Path(__file__).parent/"lluna_matrix8.npz") as data:
# 	transfer_mat = data['mat_field2el'] # Based on Lukas's simulation of LLuna # where is this histroical factor of ten coming from?

# # with np.load(Path(__file__).parent/"lluna_matrix9.npz") as data:
# with np.load(Path(__file__).parent/"matrix8_glass_no_box.npz") as data:
# 	matrix9 = data['mat_el2field'] # Based on Lukas's simulation of LLuna # where is this histroical factor of ten coming from?

# # with np.load(Path(__file__).parent/"lluna_matrix9_msj.npz") as data:
# with np.load(Path(__file__).parent/"matrix9_glass_no_box.npz") as data:
# 	matrix9_ln = data['mat_field2el'] # least norm solution based off Lukas' simulation of Lluna in Ansys
