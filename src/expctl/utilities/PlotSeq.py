#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx
import numpy as np
import math
import datetime
import time
import pyqtgraph
import colorsys
from .util import *

############################
###  Plot Device Values  ###
############################
def PlotSeq_DeviceValue(dm):
  # Configurate qtgraph
  plotTitle = "Hardware Timing"
  pyqtgraph.setConfigOption('background', '#ffffff')
  pyqtgraph.setConfigOption('foreground', '#333333')
  plotWidget = pyqtgraph.plot(title=plotTitle)
  p1 = plotWidget.plotItem
  plotWidget.resize(1300, 650)
  
  seqs = dm.seq_plot

  # Load plot data from the server
  ytick_locations = []
  t = 0;
  x = [0]
  chancounter = 0  # for y-offset
  ymax=0
  for _seq in seqs:
    # ALL RETURNED TIME SHOULD BE IN us SCALE
    try: # Try to get device data from servers
      resp = dm.devices[_seq.name].AcquirePlotData() 
      time_list, pltDatas = resp
    except:
      printError('Failed to acquire device data from the '+_seq.name+' server.')
      return
    
    for _chan in _seq.channelsToGraph:
      rgb = colorsys.hls_to_rgb(1.0 * (chancounter % 32) / 32, .4, .8)
      rgba = (256 * rgb[0], 256 * rgb[1], 256 * rgb[2], 30) # 30 is opacity (0-255)
      #rgb = '%02x%02x%02x' % (256 * rgb[0], 256 * rgb[1], 256 * rgb[2])  # generate rgb based on position
      #rgb = (256 * rgb[0], 256 * rgb[1], 256 * rgb[2])

      # time_axis = np.array(time_list[_chan.chanid])
      time_axis = np.array(time_list)
      chan_data = np.array(pltDatas[_chan.chanid])
      chan_data = .7*chan_data/_chan.max_v + chancounter
      ymax = max(max(chan_data), ymax)
      
      y = [chan_data[0]]
      x = [time_axis[0]]
      for ii in range(len(chan_data[1:])):
        y.append(chan_data[ii])
        y.append(chan_data[ii+1])
        x.append(time_axis[ii+1])
        x.append(time_axis[ii+1])
      x = 1e-6*np.array(x) # Convert us to sec
      
      ytick_locations.append((chancounter, _chan.name))
      
      newline = plotWidget.plot(x, y, pen={'color': (0.5, 0.5, 0.5)}, fillLevel=chancounter, brush=rgba)  ## setting pen=(i,3) automaticaly creates three different-colored pens
      #newline.setData()
      
      chancounter += 1
      
  now = datetime.datetime.now()
  datestr = now.strftime("%b %d, %Y at %I:%M %p")

  plotWidget.setTitle("<span style='font-weight: bold'>" + plotTitle + "</span> <span style='color: #999'>("+datestr+")</span>")
  plotWidget.setLabel('bottom', '<span style="font-size: 14px; font-weight: bold;">Time</span>', 's') # Time axis label
  p1.setLabels(left='<span style="font-size: 14px; font-weight: bold">Channels</span>') # Left axis labels (channel names)
  p1.showGrid(x=True, y=True, alpha=.12)

  p1.getAxis('left').setTicks([ytick_locations])
  plotWidget.getAxis('left').textWidth = 150
  p1.getAxis('left').setWidth(100)
  
  p1.setMouseEnabled(x=True, y=False) # The mouse scroll only zoom in on x axis.
  
  # Create a movable time reference line
  refLinel = pyqtgraph.InfiniteLine(pos=0, angle=90, pen={'color': 'r'}, movable=True, bounds=None)
  refLiner = pyqtgraph.InfiniteLine(pos=x[-1], angle=90, pen={'color': 'b'}, movable=True, bounds=None)
  p1.addItem(refLinel)
  p1.addItem(refLiner)
  
  '''TODO: TIME LABELS'''
  # timeBars=[]
  # labelTimes=True
  # try: # Get time interval value
  #   for interval in timeObj:
  #     timeBars.append(interval.end_t()/1.0e6)
  # except NameError:
  #   labelTime=False
  
  # for t in timeBars: # Add reference line for each time interval
  #   refLine = pyqtgraph.InfiniteLine(pos=t, angle=90, pen={'color': 1}, movable=False, bounds=None)
  #   p1.addItem(refLine)
  
  # if labelTimes:
  #   for t in timeObj:
  #     if t.getName():
  #       if t.start_t() != t.end_t():
  #         text  = pyqtgraph.TextItem(t.getName(), color=0.7, angle=0)
  #         text.setPos(t.start_t()/1.0e6, chancounter+1)
  #         p1.addItem(text)
  
  p1.setYRange(0, chancounter)
  plotWidget.show()

def PlotSeq_SeqValue(dm):
  # Configurate qtgraph
  plotTitle = "Sequence Timing"
  pyqtgraph.setConfigOption('background', '#ffffff')
  pyqtgraph.setConfigOption('foreground', '#333333')
  plotWidget = pyqtgraph.plot(title=plotTitle)
  p1 = plotWidget.plotItem
  plotWidget.resize(1300, 650)
  
  seqs = dm.seq_plot # Get all sequence to graph

  # Load plot data from the server
  ytick_locations = [] # channel name location
  t = 0 # start time
  x = [0] # event value
  chancounter = 0  # for y-offset
  ymax = 0 # channel maximum

  for _seq in seqs:
    for _chan in _seq.channelsToGraph: # loop over plot channels

      if _chan == None or len(_chan._UserValues) == 0: # check for empty channels
        continue

      # Setup colors for edge and filling
      rgb  = colorsys.hls_to_rgb(1.0*(chancounter%32)/32, .4, .8)
      rgba = (256*rgb[0], 256*rgb[1], 256*rgb[2], 30) # 30 is opacity (0-255)
      #rgb  = '%02x%02x%02x' % (256*rgb[0], 256*rgb[1], 256*rgb[2])  # generate rgb based on position
      rgb = (256 * rgb[0], 256 * rgb[1], 256 * rgb[2])

      # Get channel values:
      y = []; x = [];
      for ii in range(0, len(_chan._UserValues)):
        pair = _chan._UserValues[ii] # get time-value tuple
        x.append(pair[0]/1e6); y.append(chancounter+.7*pair[1]/_chan.max_v); # start value
        x.append(pair[2]/1e6); y.append(chancounter+.7*pair[3]/_chan.max_v); # final value
        if ii < len(_chan._UserValues)-1: # fill in the gaps between each time intervals
          x.append(_chan._UserValues[ii+1][0]/1e6); y.append(chancounter+.7*pair[3]/_chan.max_v);
      ytick_locations.append((chancounter, _chan.name)) # add new channel tick location
      
      newline = plotWidget.plot(x, y, pen={'color': rgb}, fillLevel=chancounter, brush=rgba)  ## setting pen=(i,3) automaticaly creates three different-colored pens
      newline.setData()
      
      chancounter += 1
      
  now = datetime.datetime.now()
  datestr = now.strftime("%b %d, %Y at %I:%M %p")

  plotWidget.setTitle("<span style='font-weight: bold'>" + plotTitle + "</span> <span style='color: #999'>("+datestr+")</span>")
  plotWidget.setLabel('bottom', '<span style="font-size: 14px; font-weight: bold;">Time</span>', 's') # Time axis label
  p1.setLabels(left='<span style="font-size: 14px; font-weight: bold">Channels</span>') # Left axis labels (channel names)
  p1.showGrid(x=True, y=True, alpha=.12)

  p1.getAxis('left').setTicks([ytick_locations])
  plotWidget.getAxis('left').textWidth = 150
  p1.getAxis('left').setWidth(100)
  
  p1.setMouseEnabled(x=True, y=False) # The mouse scroll only zoom in on x axis.
  
  # Create a movable time reference line
  refLinel = pyqtgraph.InfiniteLine(pos=0,     angle=90, pen={'color': 'r'}, movable=True, bounds=None)
  refLiner = pyqtgraph.InfiniteLine(pos=x[-1], angle=90, pen={'color': 'b'}, movable=True, bounds=None)
  p1.addItem(refLinel)
  p1.addItem(refLiner)
  
  '''TODO: TIME LABELS'''
  # timeBars=[]
  # labelTimes=True
  # try: # Get time interval value
  #   for interval in timeObj:
  #     timeBars.append(interval.end_t()/1.0e6)
  # except NameError:
  #   labelTime=False
  
  # for t in timeBars: # Add reference line for each time interval
  #   refLine = pyqtgraph.InfiniteLine(pos=t, angle=90, pen={'color': 1}, movable=False, bounds=None)
  #   p1.addItem(refLine)
  
  # if labelTimes:
  #   for t in timeObj:
  #     if t.getName():
  #       if t.start_t() != t.end_t():
  #         text  = pyqtgraph.TextItem(t.getName(), color=0.7, angle=0)
  #         text.setPos(t.start_t()/1.0e6, chancounter+1)
  #         p1.addItem(text)
  
  p1.setYRange(0, chancounter)
  plotWidget.show()
  
########################################################################
#                     Plot Channel Dialog GUI                          #
########################################################################
# GUI class for creating a dialog for selecting channels to plot
class ChanSelect(wx.Dialog):
  def __init__(self, seqs):
    wx.Dialog.__init__(self, None, title="Channels to Graph", size=(500,575))
    self.panel = wx.Panel(self)

    self.seqs = seqs
    
    self.seqchans = {}
    for seq in self.seqs:
      #self.seqchans[seq.name] = {}
      #self.seqchans[seq.name]["allChannels"] = [chan.name for chan in seq.allChannels if chan != None]
      #self.seqchans[seq.name]["graphChannels"] = [chan.name for chan in seq.channelsToGraph if chan != None]
      self.seqchans[seq.name] = {"allChannels": [chan.name for chan in seq.allChannels if chan != None],\
                                "graphChannels": [chan.name for chan in seq.channelsToGraph if chan != None]}
    self.seqsname = [seq.name for seq in self.seqs]
    self.onseqname = None
    
    self.onseq = self.seqs[0]
    self.allchans = self.onseq.allChannels
    self.graphchansname = []
    self.graphchansind = {}
    self.seqind = None
    
    # Add items
    self.seqBox = wx.ListBox(self.panel, wx.ID_ANY, choices=self.seqsname, size=(200,300))
    self.chanBox = wx.CheckListBox(self.panel, wx.ID_ANY, choices=[], style=wx.LB_MULTIPLE, size=(200,500))
    self.btn_selectall = wx.Button(self.panel, wx.ID_ANY, 'Select All')
    self.btn_selectnone = wx.Button(self.panel, wx.ID_ANY, 'Clear All')
    self.btn_ok = wx.Button(self.panel, wx.ID_OK, 'OK')
    # Create sizers
    self.bagSizer = wx.GridBagSizer(hgap=5, vgap=5)
    self.lbox = wx.GridBagSizer(hgap=1, vgap=5)
    self.rbox = wx.GridBagSizer(hgap=2, vgap=2)
    self.seqBoxSizer = wx.BoxSizer(wx.VERTICAL)
    self.chanBoxSizer = wx.BoxSizer(wx.VERTICAL)
    
    # Add sizers
    self.seqBoxSizer.Add(self.seqBox, flag=wx.ALL|wx.EXPAND|wx.ALIGN_TOP, border=5)
    self.chanBoxSizer.Add(self.chanBox, flag=wx.ALL|wx.EXPAND|wx.ALIGN_TOP, border=5)
    self.lbox.Add(self.seqBoxSizer, pos=(0,0), flag=wx.ALL|wx.EXPAND|wx.ALIGN_TOP, border=5)
    self.lbox.Add(self.btn_selectall, pos=(2,0), flag=wx.ALL|wx.EXPAND|wx.ALIGN_TOP, border=5)
    self.lbox.Add(self.btn_selectnone, pos=(3,0), flag=wx.ALL|wx.EXPAND|wx.ALIGN_TOP, border=5)
    self.lbox.Add(self.btn_ok, pos=(4,0), flag=wx.ALL|wx.EXPAND|wx.ALIGN_TOP, border=5)
    self.rbox.Add(self.chanBoxSizer, pos=(0,0), flag=wx.ALL|wx.EXPAND|wx.ALIGN_TOP, border=5)
    # Add sizers to the top sizer
    self.bagSizer.Add(self.lbox, pos=(0,0), flag=wx.ALL|wx.EXPAND|wx.ALIGN_TOP, border=5)
    self.bagSizer.Add(self.rbox, pos=(0,1), flag=wx.ALL|wx.EXPAND|wx.ALIGN_TOP, border=5)
    # Set sizer
    self.panel.SetSizer(self.bagSizer)
    
    # Bind events and functions
    self.Bind(wx.EVT_BUTTON, self.OnClose, id=wx.ID_CLOSE)
    self.Bind(wx.EVT_LISTBOX, self.OnSelectSeq, self.seqBox)
    self.Bind(wx.EVT_BUTTON, self.OnSelectAll, self.btn_selectall)
    self.Bind(wx.EVT_BUTTON, self.OnSelectNone, self.btn_selectnone)
    
  def OnClose(self, event):
    self.Close()
    
  def OnSelectSeq(self, event):
    self.update()
    
    ind = event.GetSelection()
    self.onseqname = self.seqsname[ind]
    self.chanBox.Set(self.seqchans[self.onseqname]['allChannels'])
    try:
      self.chanBox.SetCheckedStrings(self.seqchans[self.onseqname]['graphChannels'])
    except:
      return
    
  def update(self):
    if self.onseqname != None:
      self.seqchans[self.onseqname]["graphChannels"] = self.chanBox.GetCheckedStrings()
      
  def OnSelectAll(self, event):
    self.chanBox.SetCheckedStrings(self.seqchans[self.onseqname]['allChannels'])
      
  def OnSelectNone(self, event):
    self.chanBox.Set(self.seqchans[self.onseqname]["allChannels"])
      
  def GetSeq(self):
    self.update()
    
    for _seq in self.seqs:
      seqname = _seq.name
      _seq.channelsToGraph = []
      for gchanname in self.seqchans[seqname]["graphChannels"]:
        gchan = _seq.getChannelByName(gchanname)
        _seq.channelsToGraph.append(gchan)
    
    return self.seqs
    
    