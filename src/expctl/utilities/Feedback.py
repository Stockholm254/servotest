from . import LoadSequence
import wx
import numpy as np
import time
import pdb
import glob
import os
import csv

# from ..jpac.jload import *
# from ..jpac.jutil import *
# from ..jpac.jfit import jfit
# from ..jpac.jfunc import jfunc


# Most of this is intended for handling feedback conrol MVs, whose values change based on the results of experimental measuremnets.
# However, on 03/27/19 we are adding additional functionality to allow us to feedFORWARD, modifying MVs based on an
# external measurement and a lookup table of measurement-MVvalue pairs. 
# TODO:
# Create an eval function that is intended for FF; this function should be directly associated with a particular folder
# where it goes to look for the latest measured voltage, as well as a place to look for a lookup table for the feedforward pairs
# 
BlueComp_FF_Voltage_Folder = 'Z:/RydbergExperimentLogs/AMtemp/' # should take the most recent voltage from this file
BlueComp_Voltage_Column = 30 # indexed from 0!
# BlueComp_FF_LUT_Base = ***

# Feedback Measurement Processing Functions  # USE THIS ONCE YOU HAVE IT SAVING FEEDBACK MV SOMEWHERE
# def get_smv(data_dir, mv_name):
# 	mv_dir = data_dir+'/MVs'
# 	mv_file = [f for f in glob(mv_dir+'/*.txt')][0]
# 	seqname, jrange, smv, lmv = readMV(mv_file)
# 	mv_ind = np.where(smv['Name']==mv_name)
# 	mv_val = smv['Value'][mv_ind][0]
# 	return mv_val


from dataclasses import dataclass

@dataclass
class Update:
    observable: str
    j: int
    data: np.array

def BlueComp_ExTrim_FF(data_dir, MVs=None, latest=0):
	# which column of the LUT corresponds to each electric field value?
	# read in the latest voltage
	attempt = 0
	while attempt < 10:
		try:
			list_of_files = glob.glob(BlueComp_FF_Voltage_Folder+"*.csv")
			latest_file = max(list_of_files, key=os.path.getctime) # this is a 1 line CSV
			f = open(latest_file, "rb")
			csvreader = csv.reader(f, delimiter = ',')
			row = next(csvreader)
			voltage = (float(row[BlueComp_Voltage_Column])+0.155)*108
			print(voltage)
			return 0.000121*voltage+9.559*10**(-7)*voltage**2-0.0084
		except:
			print('A file was deleted while we searched!')
			attempt = attempt + 1
	print('WARNING: Blue voltage feedforward cannot find appropriate voltage file!')
	return 0
		

def BlueComp_EyTrim_FF(data_dir, MVs=None, latest=0):
	# which column of the LUT corresponds to each electric field value?
	# read in the latest voltage
	# list_of_files = glob.glob(EField_BlueComp_FF_Voltage_Folder)
	# latest_file = max(list_of_files, key=os.path.getctime) # should we assume this is a csv? probably.. and take the last value
	# **** should also REMOVE ALL BUT THE LATEST FILE, so that this folder doesn't get too full ****
	return 0.0

def BlueComp_EzTrim_FF(data_dir, MVs=None, latest=0):
	# which column of the LUT corresponds to each electric field value?
	# read in the latest voltage
	# list_of_files = glob.glob(EField_BlueComp_FF_Voltage_Folder)
	# latest_file = max(list_of_files, key=os.path.getctime) # should we assume this is a csv? probably.. and take the last value
	# **** should also REMOVE ALL BUT THE LATEST FILE, so that this folder doesn't get too full ****
	return 0.0


def VRS_balance(data_dir, MVs=None, latest=0): # ASSUMES DIRECTORY CONTAINS ONLY LATEST MEASUREMENT
	# print(data_dir)
	# time.sleep(5)
	raw, dat = avg_data(data_dir, 1) # Average data
	# import pdb; pdb.set_trace()
	middle = np.round(len(dat[0])/2)
	return (np.sum(dat[0][middle+1:])+1)/(np.sum(dat[0][0:middle])+1)


def VRS_g(data_dir, MVs=None, latest=0): # ASSUMES VERY GOOD SNR (so it doesn't even bother subtracting bkg)
	print('VRS g')
	raw, dat = avg_data(data_dir, 1) # Average data
	# scan_df = get_smv(data_dir, 'PRB_df_MHz')
	# xx = np.linspace(-scan_df, scan_df, len(dat))
	xx = np.linspace(-1, 1, len(dat[0]))
	return np.sum(np.abs(xx)*dat[0])/np.sum(dat)

def VRS_g_improved(data_dir, MVs=None, latest=0): # ASSUMES VERY GOOD SNR (so it doesn't even bother subtracting bkg)
	print('VRS g')
	raw, dat = avg_data(data_dir, 1) # Average data
	# scan_df = get_smv(data_dir, 'PRB_df_MHz')
	# xx = np.linspace(-scan_df, scan_df, len(dat))
	xx = np.linspace(-1, 1, len(dat[0]))
	middle = np.round(len(dat[0])/2)
	leftpk = np.sum(xx[0:middle]*dat[0][0:middle])/np.sum(dat[0][0:middle])
	rightpk = np.sum(xx[middle:]*dat[0][middle:])/np.sum(dat[0][middle:])

	found_flag = False
	if MVs != None:
		for MV in MVs:
			if MV.name == 'PRB_df_MHz':
				fscale = MV.value
				found_flag = True
				break
	if not found_flag:
		fscale = 1
	return fscale*(rightpk-leftpk)/2.0


def VRS_g_fit(data_dir, MVs=None, pguess=None, latest=0): # NEED TO TEST HOW SLOW THIS IS, BUT SHOULD BE MOST ROBUST WAY TO IDENTIFY G
	print('VRS g')
	raw, dat = avg_data(data_dir, 1) # Average data
	# scan_df = get_smv(data_dir, 'PRB_df_MHz')
	# xx = np.linspace(-scan_df, scan_df, len(dat)
	
	fitstart = time.clock()

	found_flag = False
	if MVs != None:
		for MV in MVs:
			if MV.name == 'PRB_df_MHz':
				fscale = MV.value
				found_flag = True
				break
	if not found_flag:
		fscale = 1

	yy = dat[0]
	xx = np.linspace(-fscale, fscale, len(yy))

	# if >100 datapoints, bin them
	if len(xx)>100:
		xx=bin_data(xx, np.round(len(yy)/100))
		yy=bin_data(yy, np.round(len(yy)/100))


	# fit params: [d0, dc, g, amp, offset]
	guess = []
	# if pguess == None or len(pguess) != 5: # if no/invalid previous parameters, make a decent first guess
	maxind = np.argmax(yy)
	guess = [0, 0, abs(xx[maxind]), yy[maxind]*30, np.min(yy)]
	# else:
	# 	guess = pguess


	pout = jfit.fit(xx, yy, jfunc.VRS, guesses=guess)
	print(('Fitting took ' + str(1000.0*(time.clock()-fitstart)) + ' ms'))
	# pdb.set_trace()

	if pguess != None:
		pguess = pout # update guess parameters for next time

	if np.isnan(pout[0][2]):
		return latest
	else:
		return pout[0][2]

# __FBfunctions__ = {
# 				'VRS_balance': VRS_balance,
# 				'VRS_g': VRS_g,
# 				'VRS_g_improved': VRS_g_improved,
# 				'VRS_g_fit': VRS_g_fit,
# 				'BlueComp_ExTrim_FF': BlueComp_ExTrim_FF,
# 				'BlueComp_EyTrim_FF': BlueComp_EyTrim_FF,
# 				'BlueComp_EzTrim_FF': BlueComp_EzTrim_FF
# 				}
__FBfunctions__ = {'Cavf0': None, 'EITpkf0': None} # TODO implement logic to get Observables from Controller/Cache

def is_float(s):
  try:
      float(s)
      return True
  except ValueError:
      return False

class FBControlMV(LoadSequence.MetaVariable):
	def __init__(self, name, P=0, I=0, value=0, typeval=1, minval=0, maxval=1, maxinc=1.0):
		LoadSequence.MetaVariable.__init__(self, name, tabname=None, value=value, type=typeval, min=minval, max=maxval, inc=maxinc)

		self.P = P
		self.I = I

		self.error_tot = 0 
		self.latest_eval = 0

		self.default_value = value # a record of a "default" value, which is not necessarily the current value
				
		self.enabled = False
		self.FF = False

		self.eval_function = 'Cavf0' # default
		self.set_point = 0

		if self.min == None:
			self.min = value
			self.max = value
			self.inc = 0

		self.prev_fit_params = []
		self.old_values = []

		self.clearGUI()

	def clearGUI(self): # remove/initialize GUI elements
		self.P_ctrl = None
		self.I_ctrl = None
		self.set_point_ctrl = None
		self.min_ctrl = None
		self.max_ctrl = None
		self.default_ctrl = None
		self.inc_ctrl = None
		self.enabled_ctrl = None
		self.FF_ctrl = None
		self.eval_function_control = None
		self.default_value_ctrl = None
		self.value_disp = None
		self.latest_eval_disp = None

	def makeFBRow(self, newFBPanel, window, frame):
		self.enabled_ctrl = wx.CheckBox(window, wx.ID_ANY)
		self.FF_ctrl = wx.CheckBox(window, wx.ID_ANY)
		self.value_disp = wx.StaticText(window, wx.ID_ANY, str(self.value))
		self.default_value_ctrl = wx.TextCtrl(window, wx.ID_ANY, str(self.default_value), size=(55, -1))
		self.max_ctrl = wx.TextCtrl(window, wx.ID_ANY, str(self.max), size=(55, -1))
		self.min_ctrl = wx.TextCtrl(window, wx.ID_ANY, str(self.min), size=(55, -1))
		self.inc_ctrl = wx.TextCtrl(window, wx.ID_ANY, str(self.inc), size=(55, -1))
		self.P_ctrl = wx.TextCtrl(window, wx.ID_ANY, str(self.P), size=(55, -1))
		self.I_ctrl = wx.TextCtrl(window, wx.ID_ANY, str(self.I), size=(55, -1))
		self.eval_function_control = wx.Choice(window, wx.ID_ANY, choices=list(__FBfunctions__.keys()), size=(100, -1))
		self.eval_function_control.SetSelection(list(__FBfunctions__.keys()).index(self.eval_function))
		# self.eval_function_control.SetSelection(list(__FBfunctions__).index(self.eval_function))
		self.set_point_ctrl = wx.TextCtrl(window, wx.ID_ANY, str(self.set_point), size=(55, -1))
		self.latest_eval_disp = wx.StaticText(window, wx.ID_ANY, str(self.latest_eval))

		newFBPanel.Add(self.enabled_ctrl)
		newFBPanel.Add(self.FF_ctrl)
		newFBPanel.Add(wx.StaticText(window, wx.ID_ANY, self.name))
		newFBPanel.Add(self.value_disp)
		newFBPanel.Add(self.default_value_ctrl)
		newFBPanel.Add(self.max_ctrl)
		newFBPanel.Add(self.min_ctrl)
		newFBPanel.Add(self.inc_ctrl)
		newFBPanel.Add(self.P_ctrl)
		newFBPanel.Add(self.I_ctrl)
		newFBPanel.Add(self.eval_function_control)
		newFBPanel.Add(self.set_point_ctrl)
		newFBPanel.Add(self.latest_eval_disp)

		self.enabled_ctrl.SetValue(self.enabled)
		self.FF_ctrl.SetValue(self.FF)
		# if self.FF:
			# self.disableNonFF()


		# need to bind the TextCtrls to updateFromGUI
		# frame.Bind(wx.EVT_TEXT, self.updateFromGUI, self.enabled_ctrl)
		frame.Bind(wx.EVT_CHECKBOX, self.disableNonFF, self.FF_ctrl)
		# frame.Bind(wx.EVT_TEXT, self.updateFromGUI self.default_value_ctrl)
		# frame.Bind(wx.EVT_TEXT, self.updateFromGUI self.max_ctrl)
		# frame.Bind(wx.EVT_TEXT, self.updateFromGUI self.min_ctrl)
		# frame.Bind(wx.EVT_TEXT, self.updateFromGUI self.inc_ctrl)
		# frame.Bind(wx.EVT_TEXT, self.updateFromGUI self.P_ctrl)
		# frame.Bind(wx.EVT_TEXT, self.updateFromGUI, self.enabled_ctrl)
		# frame.Bind(wx.EVT_TEXT, self.updateFromGUI, self.I_ctrl)
		# frame.Bind(wx.EVT_TEXT, self.updateFromGUI, self.set_point_ctrl)

		
	#feedbackIteration(socket=self.socket, MVs=self._notify_window.metavariables_fb)
	def feedbackIteration(self, socket=None, counter=0, MVs=None):
		if socket is None:
			print("not connected to FB server!")
			return

		if self.default_value_ctrl != None: # check that GUI objects have been created
			# First, needs to get the latest values from the GUI objects (if they are valid)
			self.updateFromGUI()

			print("Getting feedback for observable {}".format(self.eval_function))

			#try to get the last feedback value
			obs_name = self.eval_function #'Cavf0'
			trials = 30
			for i in range(trials):
				time.sleep(0.02)
				socket.send_pyobj(str(obs_name)) # TODO replace with eval function
				answer = socket.recv_pyobj()
				if answer == 'NOPE':
					print("Found no data for Observable {}".format(obs_name))
					continue
				
				#print("counter {}, j {}".format(counter, answer['j']))
				#sync logic
				if answer['j'] > counter: #the last j we got was higher than our current j, that must be old data!
					print("the last j we got was higher than our current j, that must be old data")
					continue 
				elif answer['j']< counter:
					# we don't have the newest result yet
					continue
				else:
					# we got the right data! update
					break
			
			if i == trials-1:
				print("timed out! not updating...")
				return
			print("Got feedback value {}".format(answer['data']))	
			fb_value = float(answer['data'])

			if np.isfinite(fb_value): # got a value, do the feedback
				self.latest_eval = fb_value #__FBfunctions__.get(self.eval_function)(data_dir, MVs=MVs, latest=self.latest_eval)
				#self.error_signal = self.latest_eval - self.value
				#self.error_tot = self.error_tot + self.error_signal
				self.error_signal = self.latest_eval - self.set_point
				

				# Update current value	
				if self.enabled_ctrl.GetValue():
					if not self.FF_ctrl.GetValue():
						# for now abuse P as FF gain so we do sign and scaling!
						if (self.I > 1) and (answer['j']>int(self.I)) and (abs(self.P*self.error_signal)<self.inc): #wait for the first couple shots to bring value there
							new_value = self.value + self.P*self.error_signal # what we would do in the current step
							#self.value = self.value + (new_value-self.value)/self.I # exponential smoothing didn't work great
							self.old_values.append(new_value)
							vals = self.old_values[-min(int(self.I), len(self.old_values)):]
							self.value = np.mean(vals)
							#TODO add small step logic here for self.inc
						else:
							#self.value += min(self.P*self.latest_eval, self.inc)
							if abs(self.P*self.error_signal)>self.inc: #we would change the variable by too much! could become unlocked
								self.value += np.sign(self.P*self.error_signal)*self.inc
							else:
								self.value += self.P*self.error_signal
						
					else: # FeedForward
						self.value=self.latest_eval

					# CHECK FOR INVALID CURRENT VALUES; 
					if self.value > self.max:
						self.value=self.max
						print("Warning: FB MV clipped!")
					elif self.value < self.min:
						self.value=self.min
						print("Warning: FB MV clipped!")
			else:
				print("Dind't update!")
			# Update StaticText Displays
			self.updateStaticText()

	def updateFromGUI(self):
		print('UFG')
		if self.default_value_ctrl != None: # check that GUI objects have been created
			if is_float(self.default_value_ctrl.GetValue()):
				self.default_value = float(self.default_value_ctrl.GetValue())
			if is_float(self.max_ctrl.GetValue()):
				self.max =float( self.max_ctrl.GetValue())
			if is_float(self.min_ctrl.GetValue()):
				self.min = float(self.min_ctrl.GetValue())
			if is_float(self.inc_ctrl.GetValue()):
				self.inc = float(self.inc_ctrl.GetValue())
			if is_float(self.P_ctrl.GetValue()):
				self.P = float(self.P_ctrl.GetValue())
			if is_float(self.I_ctrl.GetValue()):
				self.I = float(self.I_ctrl.GetValue())
			if is_float(self.set_point_ctrl.GetValue()):
				self.set_point = float(self.set_point_ctrl.GetValue())
			self.enabled = self.enabled_ctrl.GetValue()
			self.FF = self.FF_ctrl.GetValue()
			self.eval_function = self.eval_function_control.GetString(self.eval_function_control.GetCurrentSelection())


	def disableNonFF(self, event):
		print('MEEP')
		if self.FF_ctrl.GetValue():
			self.default_value_ctrl.Disable()
			self.max_ctrl.Disable()
			self.min_ctrl.Disable()
			self.inc_ctrl.Disable()
			self.P_ctrl.Disable()
			self.I_ctrl.Disable()
			self.set_point_ctrl.Disable()
		else:
			self.default_value_ctrl.Enable()
			self.max_ctrl.Enable()
			self.min_ctrl.Enable()
			self.inc_ctrl.Enable()
			self.P_ctrl.Enable()
			self.I_ctrl.Enable()
			self.set_point_ctrl.Enable()



	def updateStaticText(self):
		if self.default_value_ctrl != None: # check that GUI objects have been created
			self.value_disp.SetLabel("{:.3f}".format(self.value))
			self.latest_eval_disp.SetLabel("{:.3f}".format(self.latest_eval))

	def reset(self):
		if self.default_value_ctrl != None: # check that GUI objects have been created
			self.enabled_ctrl.SetValue(False) # disable feedback
			self.FF_ctrl.SetValue(False) # disable feedback
			self.value = self.default_value # return to default value
			self.error_signal = 0
			self.error_tot = 0