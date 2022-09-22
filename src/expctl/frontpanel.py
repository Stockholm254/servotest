#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import datetime
import os
import re
from shutil import copyfile
import math
import numpy as np
import gc
import copy
import pdb 
import pickle
import winsound
from pathlib import Path, WindowsPath
import shelve
from numpy.lib.npyio import save
import secrets

import wx
import wx.lib.agw.floatspin as FS
from wx.lib.buttons import *

# GUI helper functions
from .utilities import PlotSeq
from .utilities import BkpData
from .utilities.ReadMV import ReadMV as ReadMV, CompareMV
from .utilities.ReadMV import ChkScriptName
from .utilities.LoadSequence import seq_parser
from .utilities.LoadSequence import MetaVariable
from .utilities.SetSSV import GenSSVSeq
from .utilities.RemoteCtrl import RemoteServer, StopRemoteServer
from .utilities.Feedback import FBControlMV

#import .utilities.jGlobals as jGlobals
from .utilities import jGlobals
from .utilities.jGlobals import *
from .utilities.util import *
from .utilities.FilenameGenerator import *
from .servers.util.server import *

from .dat.all_channels import * #THIS IS WHERE WE DEFINE SEQUENCES AND CHANNELS WITHIN THEM!!
from .sequencer.sequence import *

from .DeviceManager.DeviceManager import DeviceManager
from .WorkerThread.WorkerThread import WorkerThread, EVT_RESULT, EVT_UPDATE, EVT_PLOT_TIMES

from .config.config import * # control suite preference
import coloredlogs, logging

#Experiment database connection
import expdatabase.conf as conf
from pymongo import MongoClient
from expdatabase.db import createRun, finalizeRun, updateRunMVs
from expdatabase.types import RunIdle, RunLooped
from bson import ObjectId
import zlib

# Create a logger object.
logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG')

######################
#     UTILITIES      #
######################
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

#########################################
###        The main GUI class         ###
#########################################
# Front Panel Mode
FPMODE_SSV = 0 # SSV mode
FPMODE_SEQ = 1 # regular mode
FPMODE_REM = 2 # remote control mode (TODO not developed yet!)
FPMODE_FB  = 3 # set feedback MV mode

SOUND_FOLDER = Path(__file__).parent/"dat/sounds/"
SOUND_LIST = ['1.wav']
ICON_FOLDER = Path(__file__).parent/"gui_icons/"

class FrontPanel(wx.Frame):
  def __init__(self):
    jGlobals.init() # Initialize global variables

    # Front panel GUI
    wx.Frame.__init__(self, None, wx.ID_ANY, title='SimonLab Control Suite 3', size=(1300, 750)) 
    self.panel = wx.Panel(self, wx.ID_ANY)
    # self.window_size = self.GetSize()
    
    ###################################
    ### IMPORTANT PROGRAM VARIABLES ###
    ###################################
    # Solfware info
    self.VERSION = "X_v1.0" # in the about menu
    # Device manager
    self.dm = DeviceManager(all_seqs=all_sequences, act_seqs=[]) #all_sequences
    # Sequence code and modifiable variables
    self.preamble       = '' # stores code which will be appended before modified variables
    self.metavariables  = [] # stores modifiable variables in the sequence file
    self.metavariables_fb = [] # stores modifiable variables for the FEEDBACK sequence
    self.metavariables_controlled = [] # stores a list of variables are accessible to feedback CONTROL
    self.loop_code      = '' # Loop code
    self.staticcode     = '' # stores code which will be appended after the modified variables
    # Run control thread
    self.worker       = None # thread for running the sequence
    self.RemoteServer = None # Remote control server
    # GUI properties
    self.MVCOLS = 8          # number of modifiable variable columns
    self.mode   = FPMODE_SEQ # Front panel running mode (only Set SSV or sequence for now)
    # File directories and names
    self.dir_seq   = DIR_SEQ       # default sequence file dir
    self.dir_mv    = DIR_MV        # default MV file dir
    self.dir_data  = ""            # default data dir
    self.fname_seq = ""            # default sequence file name
    self.fname_mv  = ""            # default MV file name
    self.temp_dir  = DIR_TEMP      # Temp file directory
    self.temp_MV   = FNAME_TEMP_MV # Temp MV file from the last run before set SSV
    self.script_name = "sequence"  # sequence name used by "Load" button
    # Configuration files
    self.fp_cfg = "FrontPanel.cfg"  # GUI property file to persist for each run

    self.run_id = None
    #Initialize experiment database connection
    try:
      self.client = MongoClient(host=conf.DB_HOST, port=conf.DB_PORT, username=conf.USER_RAW_WRITER , password=conf.PASSWORD_RAW_WRITER, authSource=conf.DB_AUTH)
    except:
      logger.exception("Database connection could not be established!")
      self.client = None
    else:
      logger.info("Database connection established.")

    FONT_MONO = wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL, False, 'Consolas')
    
    ########################################
    ###               MENU               ###
    ########################################
    self.menuBar = wx.MenuBar()
    menu = wx.Menu() ### File ###
    mi_load = wx.MenuItem(menu, wx.ID_OPEN, "&Load Sequence\tCtrl+O", "Load Sequence.")
    mi_load.SetBitmap(wx.Bitmap(str((ICON_FOLDER/'load.png'))))
    menu.Append(mi_load)
    self.Bind(wx.EVT_MENU, self.OnOpen, mi_load)
    mi_load_mv = wx.MenuItem(menu, wx.ID_ANY,"&Load MVs\tCtrl+L","Load metavariables from file.")
    menu.Append(mi_load_mv)
    self.Bind(wx.EVT_MENU, self.OnLoadMV, mi_load_mv)
    mi_export_mv = wx.MenuItem(menu, wx.ID_ANY, "&Export MVs\tCtrl+S", "Save current metavariable values.")
    mi_export_mv.SetBitmap(wx.Bitmap(str((ICON_FOLDER/'save2.png'))))
    menu.Append(mi_export_mv)
    self.Bind(wx.EVT_MENU, self.ExportMV, mi_export_mv)
    mi_export_lc = wx.MenuItem(menu, wx.ID_ANY, "&Export Loop Code\tCtrl+E", "Save current loop code.")
    mi_export_lc.SetBitmap(wx.Bitmap(str((ICON_FOLDER/'save.png'))))
    menu.Append(mi_export_lc)
    self.Bind(wx.EVT_MENU, self.ExportLoopedCode, mi_export_lc)
    menu.AppendSeparator()
    mi_exit = wx.MenuItem(menu, wx.ID_EXIT, "E&xit\tCtrl+W", "Close window and exit program.")
    mi_exit.SetBitmap(wx.Bitmap(str((ICON_FOLDER/'exit.png'))))
    menu.Append(mi_exit)
    self.Bind(wx.EVT_MENU, self.OnClose, mi_exit)
    self.menuBar.Append(menu, "&File")
    menu = wx.Menu()   ### Servers ###
    m_ping = wx.MenuItem(menu, wx.ID_ANY, "&Ping Servers\tAlt-P", "Ping all servers.")
    m_ping.SetBitmap(wx.Bitmap(str((ICON_FOLDER/'ping.png'))))
    menu.Append(m_ping)
    self.Bind(wx.EVT_MENU, self.OnPingServers, m_ping)
    menu.AppendSeparator()
    self.m_seq = [] # servers menu item
    for ii in range(len(self.dm.seq_all)):
      seq = self.dm.seq_all[ii]
      self.m_seq.append(wx.MenuItem(menu, wx.ID_ANY, seq.name, kind=wx.ITEM_CHECK))
      menu.Append(self.m_seq[-1])
      menu.Check(self.m_seq[-1].GetId(), False)
    for ii in range(len(self.dm.seq_all)):
      self.Bind(wx.EVT_MENU, self.OnCheckServers, self.m_seq[ii])
    self.menuBar.Append(menu, "&Servers")
    menu = wx.Menu()  ### Sequence ###
    m_plot = wx.MenuItem(menu, wx.ID_ANY, "&Plot Sequences\tAlt-G", "Generate interactive plot of sequence with PyQtGraph.")
    m_plot.SetBitmap(wx.Bitmap(str((ICON_FOLDER/'graph.png'))))
    menu.Append(m_plot)
    self.Bind(wx.EVT_MENU, self.OnPlotSeq, m_plot)
    m_selplot = wx.MenuItem(menu, wx.ID_ANY, "&Select Channels to Plot\tAlt-S", "Select channels for the plotting.")
    menu.Append(m_selplot)
    self.Bind(wx.EVT_MENU, self.OnSelectPlot, m_selplot)
    menu.AppendSeparator()
    self.m_run = wx.MenuItem(menu, wx.ID_ANY, "&Run\tAlt-R", "Run single time.")
    self.m_run.SetBitmap(wx.Bitmap(str((ICON_FOLDER/'run.png'))))
    menu.Append(self.m_run) 
    self.Bind(wx.EVT_MENU, self.OnRunSingle, self.m_run)   
    self.m_run_looped = wx.MenuItem(menu, wx.ID_ANY, "&Looped Run\tAlt-L", "Run with loop parameters defined in the loop panel.")
    self.m_run_looped.SetBitmap(wx.Bitmap(str((ICON_FOLDER/'run-looped.png'))))
    menu.Append(self.m_run_looped)
    self.Bind(wx.EVT_MENU, self.OnRunLooped, self.m_run_looped)  
    self.m_run_repeatedly = wx.MenuItem(menu, wx.ID_ANY, "&Run Repeatedly\tAlt-Y", "Run repeatedly.")
    self.m_run_repeatedly.SetBitmap(wx.Bitmap(str((ICON_FOLDER/'run-repeated.png'))))
    menu.Append(self.m_run_repeatedly)
    self.Bind(wx.EVT_MENU, self.OnRunRepeated, self.m_run_repeatedly)
    self.m_run_idle = wx.MenuItem(menu, wx.ID_ANY, "&Idle Run\tAlt-I", "Idle run. No log file will be saved.")
    menu.Append(self.m_run_idle)
    self.Bind(wx.EVT_MENU, self.OnRunIdle, self.m_run_idle)
    self.menuBar.Append(menu, "Se&quence")
    menu = wx.Menu() ### Utilities ###
    m_compareMV = wx.MenuItem(menu, wx.ID_ANY, "&Compare MVs\tAlt-C", "Compare MVs")
    menu.Append(m_compareMV)
    self.Bind(wx.EVT_MENU, self.OnCompareMV, m_compareMV)
    self.menuBar.Append(menu, "Utilities")
    menu = wx.Menu()  ### Help ###
    m_about = wx.MenuItem(menu, wx.ID_ABOUT, "&About\tF1", "Information about this program")
    m_about.SetBitmap(wx.Bitmap(str((ICON_FOLDER/'about.png'))))
    menu.Append(m_about)
    self.Bind(wx.EVT_MENU, self.OnAbout, m_about)
    m_help = wx.MenuItem(menu, wx.ID_HELP, "&Help\tF2", "Open the help documentation PDF")
    m_help.SetBitmap(wx.Bitmap(str((ICON_FOLDER/'help.png'))))
    menu.Append(m_help)
    self.Bind(wx.EVT_MENU, self.OnHelp, m_help)
    self.menuBar.Append(menu, "&Help")
    self.SetMenuBar(self.menuBar)
    
    ########################################
    ###            STATUS BAR            ###
    ########################################
    self.statusbar = MyStatusBar(self)
    self.SetStatusBar(self.statusbar)
    self.statusbar.SetStatusText("Load a sequence to begin.") # Default message

    ########################################
    ###            MAIN PANEL            ###
    ########################################
    ### TOP SIZER FOR THE WHOLE FRONT PANEL ###
    self.sizer_top = wx.FlexGridSizer(8, 1, 3, 10) # Top sizer for the whole front panel

    ###############################
    ### Construct Main MV Panel ###
    ###############################
    ## Sizer ##
    # Main body sizer
    self.sizer_MainPanel = wx.FlexGridSizer(1, 2, 3, 10) # Body sizer
    # Sub-Sizers
    self.sizer_MV      = wx.GridBagSizer(hgap=2, vgap=2)
    self.sizer_MVTab   = wx.BoxSizer(wx.VERTICAL)   # sizer for MV tabs
    self.sizer_reserve = wx.BoxSizer(wx.HORIZONTAL) # sizer for reserved space
    self.sizer_RunCtrl = wx.BoxSizer(wx.VERTICAL)   # sizer for run control
    self.sizer_runbtns = wx.BoxSizer(wx.HORIZONTAL) # sizer for run buttons
    self.sizer_runpref = wx.GridBagSizer(hgap=10, vgap=2) # sizer for running preference
    self.sizer_server  = wx.BoxSizer(wx.VERTICAL) # sizer for status of the server
    ## Buttons and MV Tabs ##
    # Run Buttons
    self.btn_run          = wx.Button(self.panel,     wx.ID_ANY, 'Run Single')
    #self.btn_run_repeated = wx.Button(self.panel,     wx.ID_ANY, 'Run Repeatedly')
    self.btn_run_idle     = wx.Button(self.panel,     wx.ID_ANY, 'Run Idle')
    #self.chkbox_savedata   = wx.CheckBox(self.panel,   wx.ID_ANY, 'Save Data')
    self.txt_rungap       = wx.StaticText(self.panel, wx.ID_ANY, 'Run Gap (ms):')
    self.txtctrl_rungap   = wx.TextCtrl(self.panel,   wx.ID_ANY, size=(55, -1), value=str(5))
    self.ln_runsetting    = wx.StaticLine(self.panel, wx.ID_ANY)
    # Reserved Space 1
    self.reserved1p = wx.Panel(self.panel, style=wx.BORDER_NONE)
    self.reserved1  = wx.StaticText(self.reserved1p, wx.ID_ANY, 'Reserved Space #1')
    self.reserved1.SetForegroundColour((200, 200, 200))
    # Reserved Space 2
    self.reserved2p = wx.Panel(self.panel, style=wx.BORDER_NONE)
    self.reserved2  = wx.StaticText(self.reserved2p, wx.ID_ANY, 'Reserved Space #2')
    self.reserved2.SetForegroundColour((200, 200, 200))
    ## Add to sizer ##
    self.sizer_reserve.Add(self.reserved1p, 1, flag=wx.ALL|wx.EXPAND,                border=5)
    self.sizer_reserve.Add(self.reserved2p, 1, flag=wx.ALL|wx.ALIGN_RIGHT|wx.EXPAND, border=5)
    self.sizer_MV.Add(self.sizer_MVTab,     pos=(0,0), flag=wx.ALL|wx.ALIGN_TOP, border=5)
    self.sizer_MV.Add(self.sizer_reserve,   pos=(1,0), flag=wx.ALL|wx.ALIGN_TOP, border=5)
    self.sizer_MV.AddGrowableRow(0, 0)
    self.sizer_MV.AddGrowableCol(0, 0)
    

    # self.sizer_runbtns.Add(self.btn_run,          0, flag=wx.ALL|wx.ALIGN_TOP|wx.ALIGN_RIGHT, border=5)
    # self.sizer_runbtns.Add(self.btn_run_repeated, 0, flag=wx.ALL|wx.ALIGN_TOP|wx.ALIGN_RIGHT, border=5)
    # self.sizer_runbtns.Add(self.btn_run_idle,     0, flag=wx.ALL|wx.ALIGN_TOP|wx.ALIGN_RIGHT, border=5)
    self.sizer_runbtns.Add(self.btn_run,          0, flag=wx.ALL|wx.ALIGN_TOP|wx.LEFT, border=5)
    #self.sizer_runbtns.Add(self.btn_run_repeated, 0, flag=wx.ALL|wx.ALIGN_TOP|wx.LEFT, border=5)
    self.sizer_runbtns.Add(self.btn_run_idle,     0, flag=wx.ALL|wx.ALIGN_TOP|wx.LEFT, border=5)
    #self.sizer_runbtns.Add(self.chkbox_savedata,        0, flag=wx.ALL|wx.EXPAND, border=5)
    self.sizer_runpref.Add(self.txt_rungap,     pos=(0,0), flag=wx.ALL|wx.ALIGN_TOP|wx.ALIGN_LEFT, border=5)
    self.sizer_runpref.Add(self.txtctrl_rungap, pos=(0,1), flag=wx.ALL|wx.ALIGN_TOP|wx.ALIGN_LEFT, border=5)
    self.sizer_RunCtrl.Add(self.sizer_runbtns,   0, flag=wx.LEFT|wx.ALIGN_TOP,               border=5)
    self.sizer_RunCtrl.Add(self.sizer_runpref,   0, flag=wx.ALL|wx.ALIGN_TOP|wx.ALIGN_LEFT,  border=5)
    self.sizer_RunCtrl.Add(self.ln_runsetting,   0, flag=wx.ALL|wx.EXPAND,                   border=5)
    self.sizer_RunCtrl.Add(self.sizer_server,    0, flag=wx.ALL|wx.ALIGN_TOP|wx.ALIGN_LEFT,  border=5)
    self.sizer_MainPanel.Add(self.sizer_MV,      0, flag=wx.ALL|wx.ALIGN_TOP|wx.EXPAND,      border=5)
    self.sizer_MainPanel.Add(self.sizer_RunCtrl, 0, flag=wx.ALL|wx.ALIGN_TOP|wx.EXPAND,      border=5)
    self.sizer_MainPanel.AddGrowableCol(0)
    
    ###########################
    ### Construct Title Bar ###
    ###########################
    ## Sizer ##
    self.sizer_Title = wx.FlexGridSizer(1, 11, 8, 5) # Title sizer
    ## Buttons and Icons ##
    # Title and icon
    bmp = wx.Bitmap(wx.Image(str(ICON_FOLDER/"38740-200.png"), wx.BITMAP_TYPE_ANY).Scale(30, 30, wx.IMAGE_QUALITY_HIGH))
    titleIco1 = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp, size=(30, 30))
    titleIco2 = wx.StaticBitmap(self.panel, wx.ID_ANY, bmp, size=(30, 30))
    title = wx.StaticText(self.panel, wx.ID_ANY, 'Simon Lab Software Suite Front Panel 3')
    title.SetFont(wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL, False, 'Calibri'))
    # Buttons
    self.btn_remote      = wx.Button(self.panel,     wx.ID_ANY, 'Remote')
    self.ping_server     = wx.Button(self.panel,     wx.ID_ANY, 'Ping Servers')
    self.btn_plot_seq    = wx.Button(self.panel,     wx.ID_ANY, 'Plot Sequences')
    self.btn_set_ssv     = wx.Button(self.panel,     wx.ID_ANY, 'Set Steady State Values')
    self.btn_load_file   = wx.Button(self.panel,     wx.ID_ANY, 'Load')
    self.btn_reload_file = wx.Button(self.panel,     wx.ID_ANY, 'Reload')
    self.btn_load_MV     = wx.Button(self.panel,     wx.ID_ANY, 'Load MVs')    
    self.lbl_fname_seq   = wx.StaticText(self.panel, wx.ID_ANY, 'Load sequence file')
    self.lbl_fname_seq.SetForegroundColour((255, 0, 0)) # set red text color
    ## Add object to the title sizer ##
    # self.sizer_Title.Add(titleIco1,            flag=wx.TOP|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, border=5)
    self.sizer_Title.Add(self.btn_remote,      flag=wx.TOP|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,  border=5)
    self.sizer_Title.Add(self.ping_server,     flag=wx.TOP|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,  border=5)
    self.sizer_Title.Add(self.btn_plot_seq,    flag=wx.TOP|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL,  border=5)
    self.sizer_Title.Add(titleIco1,            flag=wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, border=5)
    self.sizer_Title.Add(title,                flag=wx.TOP|wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL,  border=8)
    self.sizer_Title.Add(titleIco2,            flag=wx.TOP|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,  border=5)
    self.sizer_Title.Add(self.btn_set_ssv,     flag=wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL,  border=5)
    self.sizer_Title.Add(self.btn_reload_file, flag=wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL,  border=5)
    self.sizer_Title.Add(self.btn_load_MV,     flag=wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL,  border=5)
    self.sizer_Title.Add(self.btn_load_file,   flag=wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, border=5)
    self.sizer_Title.Add(self.lbl_fname_seq,   flag=wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, border=10)
    self.sizer_Title.AddGrowableCol(2, 0)
    self.sizer_Title.AddGrowableCol(5, 0)



    ##############################
    ### Construct Feedback Box ###
    ##############################
    self.sizer_FeedMain  = wx.FlexGridSizer(1, 5, 3, 10)
    self.sizer_FeedCol   = wx.BoxSizer(wx.VERTICAL) # the main column for feedback MEASUREMENT settings
    self.sizer_NumBetRow = wx.BoxSizer(wx.HORIZONTAL) # the row with both static and control text
    ### Feedback Measurement Settings:
    # Static label text
    self.txt_FeedLabel   = wx.StaticText(self.panel, wx.ID_ANY, 'Feedback Measurement Settings:')
    # Checkbox
    self.chkbox_FeedOn         = wx.CheckBox(self.panel, wx.ID_ANY, 'Enable Feedback Shots')
    # Buttons
    self.btn_FeedLoadMV        = wx.Button(self.panel, wx.ID_ANY, 'Load FB Measure MVs', size=(150,27))
    self.btn_FeedSaveMV        = wx.Button(self.panel, wx.ID_ANY, 'Save FB Measure MVs', size=(150,27))
    self.btn_CtrlLoadMV        = wx.Button(self.panel, wx.ID_ANY, 'Load FB Ctrl MVs', size=(150,27))
    self.btn_CtrlSaveMV        = wx.Button(self.panel, wx.ID_ANY, 'Save FB Ctrl MVs', size=(150,27))
    # Numerical Input
    self.txt_FeedShotsBetLabel = wx.StaticText(self.panel, wx.ID_ANY, 'Shots between feedback: ')
    self.txtctrl_FeedShotsBet  = wx.TextCtrl(self.panel, wx.ID_ANY, size=(55, -1), value=str(9))
    # add txt to row
    self.sizer_NumBetRow.Add(self.txt_FeedShotsBetLabel)
    self.sizer_NumBetRow.Add(self.txtctrl_FeedShotsBet)
    # add to main feedback column
    self.sizer_FeedCol.Add(self.txt_FeedLabel, flag=wx.ALL, border=5)
    self.sizer_FeedCol.Add(self.chkbox_FeedOn, flag=wx.ALL, border=5)
    self.sizer_FeedCol.Add(self.btn_FeedLoadMV, flag=wx.ALL, border=5)
    self.sizer_FeedCol.Add(self.btn_FeedSaveMV, flag=wx.ALL, border=5)
    self.sizer_FeedCol.Add(self.btn_CtrlLoadMV, flag=wx.ALL, border=5)
    self.sizer_FeedCol.Add(self.btn_CtrlSaveMV, flag=wx.ALL, border=5)
    self.sizer_FeedCol.Add(self.sizer_NumBetRow, flag=wx.ALL, border=5)
    ## add to FeedMain
    # self.sizer_FeedMain.Insert(5, self.sizer_FeedCol, border=5)
    self.sizer_FeedMain.Add(self.sizer_FeedCol, border=5)
    self.sizer_FeedMain.Add(wx.StaticLine(self.panel, wx.ID_ANY, style=wx.LI_VERTICAL), flag=wx.ALL|wx.EXPAND, border=0)
    ### Feedback Control Settings:
    self.sizer_FeedControl = None
    self.UpdateFeedbackControlPanel()




    ##########################
    ### Construct Loop Box ###
    ##########################
    ## Loop Box sub-sizers ##
    self.sizer_LoopMain = wx.FlexGridSizer(1, 9, 3, 10) # sizer for whole loop box
    self.sizer_LoopCtrl = wx.BoxSizer(wx.VERTICAL) # sizer for loop setting
    self.sizer_LoopCode = wx.BoxSizer(wx.VERTICAL) # sizer for loop code
    self.sizer_LoopInfo = wx.BoxSizer(wx.VERTICAL) # sizer for other informations
    self.sizer_LoopBtns = wx.BoxSizer(wx.VERTICAL) # sizer for buttons
    # Sub-Sizers
    self.sizer_LoopCtrlSub1 = wx.GridBagSizer(hgap=1, vgap=3) # sub-sizer for loop start and end point
    ## Loop Setting ##
    # Settings
    self.txt_loop         = wx.StaticText(self.panel, wx.ID_ANY, 'Loop Settings:')
    self.lbl_j0           = wx.StaticText(self.panel, wx.ID_ANY, 'j0:')
    self.txtctrl_j0       = wx.TextCtrl(self.panel,   wx.ID_ANY, '1',  size=(60, -1))
    self.lbl_j1           = wx.StaticText(self.panel, wx.ID_ANY, 'j1:')
    self.txtctrl_j1       = wx.TextCtrl(self.panel,   wx.ID_ANY, '10', size=(60, -1))
    self.txt_prerun       = wx.StaticText(self.panel, wx.ID_ANY, 'Pre runs:')
    self.txtctrl_prerun   = wx.TextCtrl(self.panel,   wx.ID_ANY, '0',  size=(40, -1))
    self.txt_dirname      = wx.StaticText(self.panel, wx.ID_ANY, 'Folder name:')
    self.txtctrl_dirname  = wx.TextCtrl(self.panel,   wx.ID_ANY, '',   size=(150, -1))
    self.chkbox_rand      = wx.CheckBox(self.panel,   wx.ID_ANY, 'Randomize Order')
    self.chkbox_autobkp   = wx.CheckBox(self.panel,   wx.ID_ANY, 'Auto Backup')
    self.chkbox_autoidle  = wx.CheckBox(self.panel,   wx.ID_ANY, 'Auto Idle When Done')
    self.chkbox_autoidle.SetValue(True)
    self.chkbox_autobkp.SetValue(True)
    self.ln_loopsetting   = wx.StaticLine(self.panel, wx.ID_ANY, style=wx.LI_VERTICAL)
    # Loop code
    self.txt_loopcode     = wx.StaticText(self.panel, wx.ID_ANY, 'Loop Code:')
    self.txtctrl_loopcode = wx.TextCtrl(self.panel,   wx.ID_ANY, '', size=(200, 250), style=wx.TE_MULTILINE|wx.EXPAND)
    self.ln_loopcode      = wx.StaticLine(self.panel, wx.ID_ANY, style=wx.LI_VERTICAL)
    # Other info
    self.txt_expinfo      = wx.StaticText(self.panel, wx.ID_ANY, 'Other Informations:')
    self.txtctrl_expinfo  = wx.TextCtrl(self.panel,   wx.ID_ANY, '', size=(200, 250), style=wx.TE_MULTILINE|wx.EXPAND)
    self.ln_expinfo       = wx.StaticLine(self.panel, wx.ID_ANY, style=wx.LI_VERTICAL)
    # Buttons
    self.btn_run_looped    = wx.Button(self.panel, wx.ID_ANY, 'Looped Run',       size=(150,27))
    self.btn_update_loopMV = wx.Button(self.panel, wx.ID_ANY, 'Loop Variables',   size=(150,27))
    self.btn_bkp_data      = wx.Button(self.panel, wx.ID_ANY, 'Backup Data',      size=(150,27))
    self.btn_save_loopcode = wx.Button(self.panel, wx.ID_ANY, 'Save Loop Code',   size=(150,27))
    ## Add Sizers ##
    self.sizer_LoopCtrl.Add(self.txt_loop, 0, flag=wx.ALL|wx.EXPAND, border=7)
    self.sizer_LoopCtrlSub1.Add(self.lbl_j0,          pos=(0,0), flag=wx.ALL, border=1)
    self.sizer_LoopCtrlSub1.Add(self.txtctrl_j0,      pos=(0,1), flag=wx.ALL, border=1)
    self.sizer_LoopCtrlSub1.Add(self.lbl_j1,          pos=(1,0), flag=wx.ALL, border=1)
    self.sizer_LoopCtrlSub1.Add(self.txtctrl_j1,      pos=(1,1), flag=wx.ALL, border=1)
    self.sizer_LoopCtrlSub1.Add(self.txt_prerun,      pos=(2,0), flag=wx.ALL, border=1)
    self.sizer_LoopCtrlSub1.Add(self.txtctrl_prerun,  pos=(2,1), flag=wx.ALL, border=1)
    self.sizer_LoopCtrlSub1.Add(self.txt_dirname,     pos=(3,0), flag=wx.ALL|wx.EXPAND, border=1)
    self.sizer_LoopCtrlSub1.Add(self.txtctrl_dirname, pos=(3,1), flag=wx.ALL|wx.EXPAND, border=1)
    self.sizer_LoopCtrl.Add(self.sizer_LoopCtrlSub1, 0, flag=wx.ALL|wx.EXPAND, border=5)
    self.sizer_LoopCtrl.Add(self.chkbox_rand,        0, flag=wx.ALL|wx.EXPAND, border=5)
    self.sizer_LoopCtrl.Add(self.chkbox_autobkp,     0, flag=wx.ALL|wx.EXPAND, border=5)
    self.sizer_LoopCtrl.Add(self.chkbox_autoidle,    0, flag=wx.ALL|wx.EXPAND, border=5)
    self.sizer_LoopCode.Add(self.txt_loopcode,       0, flag=wx.ALL|wx.EXPAND, border=5)
    self.sizer_LoopCode.Add(self.txtctrl_loopcode,   0, flag=wx.ALL|wx.EXPAND, border=5)
    self.sizer_LoopInfo.Add(self.txt_expinfo,        0, flag=wx.ALL|wx.EXPAND, border=5)
    self.sizer_LoopInfo.Add(self.txtctrl_expinfo,    0, flag=wx.ALL|wx.EXPAND, border=5)
    self.sizer_LoopBtns.Add(self.btn_run_looped,     0, flag=wx.ALL|wx.EXPAND, border=5)
    self.sizer_LoopBtns.Add(self.btn_update_loopMV,  0, flag=wx.ALL|wx.EXPAND, border=5)
    self.sizer_LoopBtns.Add(self.btn_bkp_data,       0, flag=wx.ALL|wx.EXPAND, border=5)
    self.sizer_LoopBtns.Add(self.btn_save_loopcode,  0, flag=wx.ALL|wx.EXPAND, border=5)
    # Add to loop main
    self.sizer_LoopMain.Add(self.sizer_LoopCtrl, 0, flag=wx.ALL|wx.EXPAND, border=5)
    self.sizer_LoopMain.Add(self.ln_loopsetting, 0, flag=wx.ALL|wx.EXPAND, border=0)
    self.sizer_LoopMain.Add(self.sizer_LoopCode, 0, flag=wx.ALL|wx.EXPAND, border=5)
    self.sizer_LoopMain.Add(self.ln_loopcode,    0, flag=wx.ALL|wx.EXPAND, border=0)
    self.sizer_LoopMain.Add(self.sizer_LoopInfo, 0, flag=wx.ALL|wx.EXPAND, border=5)
    self.sizer_LoopMain.Add(self.ln_expinfo,     0, flag=wx.ALL|wx.EXPAND, border=1)
    self.sizer_LoopMain.Add(self.sizer_LoopBtns, 0, flag=wx.ALL|wx.EXPAND, border=5)
    self.sizer_LoopMain.AddGrowableCol(2)
    self.sizer_LoopMain.AddGrowableCol(4)

    # Elements that don't exist yet but will exist later
    self.notebook = None
    self.FBtab = None






    ########################################
    ### Add sub-sizers to self.sizer_top ###
    ########################################
    self.sizer_top.Add(self.sizer_Title,          0, flag=wx.CENTER|wx.EXPAND, border=5)
    self.sizer_top.Add(wx.StaticLine(self.panel), 0, flag=wx.ALL|wx.EXPAND,    border=5)
    self.sizer_top.Add(self.sizer_MainPanel,      0, flag=wx.ALL|wx.EXPAND,    border=5)
    self.sizer_top.Add(wx.StaticLine(self.panel), 0, flag=wx.ALL|wx.EXPAND,    border=5)
    self.sizer_top.Add(self.sizer_FeedMain,       0, flag=wx.ALL|wx.EXPAND,    border=5)
    self.sizer_top.Add(wx.StaticLine(self.panel), 0, flag=wx.ALL|wx.EXPAND,    border=5)
    self.sizer_top.Add(self.sizer_LoopMain,       0, flag=wx.ALL|wx.EXPAND,    border=5)
    self.sizer_top.AddGrowableRow(2, 0)
    self.sizer_top.AddGrowableCol(0, 0)
    # set sizers
    self.panel.SetSizer(self.sizer_top) # set all sizers
    # self.SetSizeHints(900, 620, 1920, 1200) # minW, minH, maxW, maxH
    # self.sizer_top.Fit(self) # Resize window/sizers to fit content
    # layout
    self.Center()
    # self.Maximize()
    self.Show()
    
    #############################
    ### DO ALL BUTTON BINDING ###
    #############################
    self.Bind(wx.EVT_CLOSE,  self.OnClose) # Bind close button to OnClose function
    self.Bind(wx.EVT_BUTTON, self.SetSSV,            self.btn_set_ssv)
    self.Bind(wx.EVT_BUTTON, self.OnOpen,            self.btn_load_file)
    self.Bind(wx.EVT_BUTTON, self.LoadSeq,           self.btn_reload_file)
    self.Bind(wx.EVT_BUTTON, self.OnLoadMV,          self.btn_load_MV)
    self.Bind(wx.EVT_BUTTON, self.OnRunSingle,       self.btn_run)
    #self.Bind(wx.EVT_BUTTON, self.OnRunRepeated,     self.btn_run_repeated)
    self.Bind(wx.EVT_BUTTON, self.OnRunIdle,         self.btn_run_idle)
    self.Bind(wx.EVT_BUTTON, self.OnRunLooped,       self.btn_run_looped)
    self.Bind(wx.EVT_BUTTON, self.OnChooseLoopedVar, self.btn_update_loopMV)
    self.Bind(wx.EVT_BUTTON, self.OnBkpData,         self.btn_bkp_data)
    self.Bind(wx.EVT_BUTTON, self.OnPingServers,     self.ping_server)
    self.Bind(wx.EVT_BUTTON, self.OnPlotSeq,         self.btn_plot_seq)
    self.Bind(wx.EVT_BUTTON, self.OnLoadFBMV,        self.btn_FeedLoadMV)
    self.Bind(wx.EVT_BUTTON, self.ExportFBMV,        self.btn_FeedSaveMV)
    self.Bind(wx.EVT_BUTTON, self.OnLoadCtrlMV,      self.btn_CtrlLoadMV)
    self.Bind(wx.EVT_BUTTON, self.OnSaveCtrlMV,      self.btn_CtrlSaveMV)
    # self.Bind(wx.EVT_BUTTON, self.OnRemote,          self.btn_remote) # Remote control
    self.Bind(wx.EVT_SIZE,   self.OnResize)
    self.Bind(wx.EVT_CLOSE,  self.OnClose)

    # All buttons will be disabled during the run (This is created for convenience)
    '''TODO: AUTO DETECT GUI OBJECTS'''
    self.all_btn = [
                    self.btn_run, 
                    #self.btn_run_repeated, 
                    self.btn_run_idle,
                    self.btn_run_looped,  
                    self.btn_load_file, 
                    self.btn_reload_file, 
                    self.btn_load_MV, 
                    self.btn_set_ssv, 
                    self.btn_update_loopMV, 
                    self.btn_bkp_data, 
                    self.btn_remote, 
                    self.ping_server, 
                    self.btn_plot_seq,
                    self.btn_save_loopcode,
                    self.btn_FeedLoadMV,
                    self.btn_FeedSaveMV,
                    self.btn_CtrlLoadMV,
                    self.btn_CtrlSaveMV
                   ]
    self.all_man = [
                    self.m_run, 
                    self.m_run_looped, 
                    self.m_run_repeatedly, 
                    self.m_run_idle, 
                   ]

    ### Call this function when the thread returns. ###
    EVT_RESULT(self, self.OnReturnFromRun) # Run result
    EVT_UPDATE(self, self.OnUpdateRunInfo) # Run info real time update
    EVT_PLOT_TIMES(self, self.OnReturnFromDebug) # Event for return Interlaver timing object from worker

    ### Reload the Front Panel ###
    self.InitFP()

  #############################################################################
  #=============================== GUI Methods ===============================#
  #############################################################################
  def InitFP(self): # Reload settings from the memory
    path = self.temp_dir / self.fp_cfg
    new_path = path.parent / (path.name + '.dat')
    if os.path.exists(new_path):

        #ActSeqNames = [] #catch empty ActSeqNames
        print('Loading Front Panel Configurations!')
        # f = open(persist_fname, 'r')
        # for line in f.readlines():
        #   #exec(str(line))
        #   line = line.strip('\n')
        #   print(line)
        #   exec(line)
        # f.close()

        d = shelve.open(str(self.temp_dir/self.fp_cfg))
        self.dir_seq = d['dir_seq']
        self.fname_seq = d['fname_seq']
        self.script_name = d['script_name']
        ActSeqNames = d['ActSeqNames']
        d.close()
        # print(ActSeqNames)
        try:
            self.LoadSeq() # Load last sequence
            self.LoadMV(mv_dir=self.temp_dir, mv_fname=self.temp_MV) # Load MVs
        except:
            pass
        seq_new = []
        # print(ActSeqNames)
        # Select active sequence in the manu bar and update the device manager using OnCheckServers()
        for ii, seq in enumerate(self.dm.seq_all): # Loop over all available sequence in the device manager
            if seq.name in ActSeqNames:
                self.menuBar.Check(self.m_seq[ii].GetId(), True)
                seq_new.append(seq)
            else:
                self.menuBar.Check(self.m_seq[ii].GetId(), False)
        # print(seq_new) 
        self.dm.SetActiveSeq(seq_new)
        self.OnCheckServers(None)

  # George W Bush was a very bad president (Graham said so)
  #####################################################
  ###          Sequence and MV File Loading         ###
  #####################################################
  def OnOpen(self, event):
    '''Create the Load File Dialog and load the file'''
    # dlg = wx.FileDialog(self, message="Open a sequence...", defaultDir=self.dir_seq, defaultFile="", style=wx.FD_OPEN)

    dlg = wx.FileDialog(self, message="Open a sequence...")
    
    if dlg.ShowModal() == wx.ID_OK: # Call the dialog as a model-dialog so user is required to choose Ok or Cancel
      self.fname_seq = dlg.GetFilename()
      self.dir_seq   = Path(dlg.GetDirectory())
      self.script_name = self.fname_seq.replace(".py", "")
      self.LoadSeq()
    dlg.Destroy()
    
    if self.mode != FPMODE_SSV: # To enable load a sequence in the SSV mode
      self.mode = FPMODE_SEQ
      self.btn_set_ssv.SetLabel("Set Steady State Value")
    
  def LoadSeq(self, event=None): 
    '''Load a sequence file's modifiable variable information onto the screen/loop code box'''
    # if in FB mode, switch back to regular before loading
    if self.mode == FPMODE_FB:
        self.SetFB()

    # Load contents from the sequence file
    if self.fname_seq == None:
      return -1
    #if not os.path.isfile(str(self.dir_seq)+"/"+str(self.fname_seq)):
    path_seq = self.dir_seq / self.fname_seq
    if not path_seq.exists():
      self.statusbar.Error("Error: file not found ("+str(self.dir_seq / self.fname_seq)+").")
      return -1
    self.SetTitle("Simon Lab Software Suite: "+self.fname_seq)
    
    wx.BeginBusyCursor()
    # Load sequence file contents and parse it
    f = open(path_seq, 'r')  # traverse the file directory and find filename in the OS
    contents = f.readlines() # load all lines in the sequence file
    f.close()
    self.preamble, self.metavariables, self.staticcode = seq_parser(contents) # Parse the sequence file

    self.lbl_fname_seq.SetLabel(self.fname_seq) # Set sequence label
    self.SetupMetavars() # Setup the UI for MVs
    wx.EndBusyCursor()

    # GUI layout
    self.SetSizeHints(-1, -1, -1, -1) # minW, minH, maxW, maxH
    self.panel.Layout()
    # self.Maximize()

  
  def SetupMetavars(self):
    '''Given a list of modifiable variables and their values, create little labels and text boxes, fill them in, put them on the screen'''
    FONT_MONO = wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL, False, 'Consolas')
    
    relevant_MV = self.metavariables
    print("Setup Metavars")
        
        

    notebook = wx.Notebook(self.panel) # MV notebook
    notebooksizer = wx.BoxSizer(wx.VERTICAL) # Notebook sizer
    tablist = [] # Tab sizer list
    newvars = [] # MV sizer list
    
    tabname = 'None'

    for x in range(0, len(relevant_MV)+1): # Loop over all metavariables
        if x < len(relevant_MV):
            MV = relevant_MV[x]

        if (MV.tabname!=tabname) or (x==len(relevant_MV)): # Create new variable tab
            if tabname != 'None':
                # Add sizers to the previous tab sizer list
                for ii in range(int(math.ceil(1.*len(var_lbl)/self.MVCOLS))):
                    for jj in range(self.MVCOLS): # Add MV labels
                        var_ind = ii*self.MVCOLS+jj
                        if var_ind >= len(var_lbl):
                            newvars[-1].Add(wx.StaticText(tab, label=""))
                        else:
                            newvars[-1].Add(var_lbl[var_ind], 0, wx.ALIGN_BOTTOM)
                    for jj in range(self.MVCOLS): # Add MV values
                        var_ind = ii*self.MVCOLS+jj
                        if var_ind >= len(var_lbl):
                            break
                        newvars[-1].Add(var_val[var_ind], 0, wx.BOTTOM)
            if x < len(relevant_MV):
                # Initialize tab variables
                # Create a new MV tab
                tabname = MV.tabname # Name of the new tab
                tablist.append(wx.Panel(notebook)) # Add the notebook to the list of all tabs
                notebook.AddPage(tablist[-1], tabname) # Add new notebook
                tab = tablist[-1]
                # Clear MV sizer list
                newvars.append(wx.FlexGridSizer(4*self.MVCOLS, self.MVCOLS, 5, 10)) # Create a new sizer list for the tab
                var_lbl = [] # Clear MV labels list
                var_val = [] # Clear MV values list
        
        if x < len(relevant_MV):
            # Add MV GUI object to a list
            MV.label = wx.CheckBox(tab, wx.ID_ANY, label=str(MV.name), style=wx.CHK_3STATE|wx.CHK_ALLOW_3RD_STATE_FOR_USER)
            # check if the checkbox should start checked (because MV with same name is in feedback lists)
            for compareMV in self.metavariables_fb:
                if MV.name == compareMV.name:
                    MV.label.Set3StateValue(1) # default is 0
                    break
            for compareMV in self.metavariables_controlled:
                if MV.name == compareMV.name:
                    MV.label.Set3StateValue(2) # default is 0
                    break
            MV.label.SetFont(FONT_MONO)
            if MV.type != 2: # Type 1 MV
                MV.textCtrl = MVTextCtrl(tab, value=str(MV.value), mv=MV)
                MV.textCtrl.SetFont(FONT_MONO)
            else: # Type 2 MV
                MV.textCtrl = FS.FloatSpin(tab, -1, min_val=MV.min, max_val=MV.max, increment=MV.inc, value=MV.value, agwStyle=FS.FS_LEFT)
                MV.textCtrl.SetFont(FONT_MONO)
                MV.textCtrl.SetFormat("%f")
                MV.textCtrl.SetDigits(MV.digits)
            var_lbl.append(MV.label)
            var_val.append(MV.textCtrl)

    # Set MV notebook sizers
    notebooksizer.Add(notebook, 1, flag=wx.ALL|wx.EXPAND, border=5)
    for ii in range(len(newvars)):
        tablist[ii].SetSizer(newvars[ii])

    # Update sizer_MainPanel
    self.sizer_MV.Hide(self.sizer_MVTab)
    self.sizer_MVTab.Clear(delete_windows=True) # 02/14/19 Logan: this is a crucial line
                                            # which fixes a bug; namely, Remove() deletes
                                            # SIZER children but does not delete
                                            # WINDOW children, only sizers; thus the notebooks 
                                            # were all persisting forever, eventually
                                            # causing a deterministic crash
    self.sizer_MV.Remove(self.sizer_MVTab)
    self.sizer_MV.Add(notebooksizer, pos=(0,0), flag=wx.ALL|wx.EXPAND, border=5)
    # Update GUI
    self.sizer_MV.Layout()
    self.sizer_MVTab = notebooksizer
    self.SetStatusText("Loaded sequence from '"+self.fname_seq+"' (found "+str(len(relevant_MV))+" modifiable variables).", 0)

    # Update modifiable variables
    for x in range(0, len(relevant_MV)):
        # bind checkbox clicks
        self.Bind(wx.EVT_CHECKBOX, lambda event, x=x: self.OnMVChangeState(event, relevant_MV[x]), relevant_MV[x].label)
        # bind text updates
        if relevant_MV[x].type != 2: # Type 2 MV
            self.Bind(wx.EVT_TEXT, lambda event, x=x: self.OnMetavarUpdate(event, relevant_MV[x]), relevant_MV[x].textCtrl)
        else: # Type 1 MV
            self.Bind(wx.EVT_SPINCTRL, lambda event, x=x: self.OnMetavarUpdate(event, relevant_MV[x]), relevant_MV[x].textCtrl)

    self.notebook = notebook
    self.SetupFBMVs()
    #self.CorrectPCSaveSwitch()

    
  def CorrectPCSaveSwitch(self):
    # look for an MV named PC_save_switch; if it exists, ensure that it is a FB measurement MV, that its 
    # value in the main sequence is 0, and its value in FeedbackMeasure is 1
    for x, MV in enumerate(self.metavariables):
        if MV.name == 'PC_save_switch':
            # pdb.set_trace()
            MV.label.Set3StateValue(1) # Feedback Measure MV
            self.OnMVChangeState(None, MV)
            MV.value = 0.0
            MV.textCtrl.SetValue(str(MV.value))
            for y, FBMV in enumerate(self.metavariables_fb):
                if FBMV.name == 'PC_save_switch':
                    FBMV.value = 1.0
                    FBMV.textCtrl.SetValue(str(FBMV.value))
                    break
        if MV.name == 'DetMode': # make sure it is 1 in FeedbackMeasure
            # pdb.set_trace()
            MV.label.Set3StateValue(1) # Feedback Measure MV
            self.OnMVChangeState(None, MV)
            for y, FBMV in enumerate(self.metavariables_fb):
                if FBMV.name == 'DetMode':
                    FBMV.value = 1.0
                    FBMV.textCtrl.SetValue(str(FBMV.value))
                    break


  def SetupFBMVs(self):
    FONT_MONO = wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL, False, 'Consolas')
    notebook=self.notebook
    relevant_MV = self.metavariables_fb
    tabname = '*FeedbackMeasure*' # Name of the new tab

    # if a feedback tab already exists, remove it
    for index in range(notebook.GetPageCount()):
        if self.notebook.GetPageText(index) == tabname:
            self.notebook.DeletePage(index)
            self.notebook.SendSizeEvent()
            break

    
    # create a single new tab
    tab = wx.Panel(notebook) # Make a new tab
    # Clear MV sizer list
    tabsizer = wx.FlexGridSizer(4*self.MVCOLS, self.MVCOLS, 5, 10) # Create a new sizer list for the tab
    var_lbl = [] # Clear MV labels list
    var_val = [] # Clear MV values list

    # add MVs to that tab
    for x, MV in enumerate(relevant_MV): # Loop over all metavariables_fb
        # Add MV GUI object to a list
        MV.label = wx.StaticText(tab, wx.ID_ANY, label=str(MV.name)) # should JUST BE A LABEL for the FB MVs
        MV.label.SetFont(FONT_MONO)
        if MV.type != 2: # Type 1 MV
            MV.textCtrl = MVTextCtrl(tab, value=str(MV.value), mv=MV)
            MV.textCtrl.SetFont(FONT_MONO)
        else: # Type 2 MV
            MV.textCtrl = FS.FloatSpin(tab, -1, min_val=MV.min, max_val=MV.max, increment=MV.inc, value=MV.value, agwStyle=FS.FS_LEFT)
            MV.textCtrl.SetFont(FONT_MONO)
            MV.textCtrl.SetFormat("%f")
            MV.textCtrl.SetDigits(MV.digits)
        var_lbl.append(MV.label)
        var_val.append(MV.textCtrl)

    # put elements in tab
    for ii in range(int(math.ceil(1.*len(var_lbl)/self.MVCOLS))):
        for jj in range(self.MVCOLS): # Add MV labels
            var_ind = ii*self.MVCOLS+jj
            if var_ind >= len(var_lbl):
                tabsizer.Add(wx.StaticText(tab, label=""))
            else:
                tabsizer.Add(var_lbl[var_ind], 0, wx.ALIGN_BOTTOM)
        for jj in range(self.MVCOLS): # Add MV values
            var_ind = ii*self.MVCOLS+jj
            if var_ind >= len(var_lbl):
                break
            tabsizer.Add(var_val[var_ind], 0, wx.BOTTOM)

    tab.SetSizer(tabsizer)
    self.FBtab = tab
    notebook.AddPage(tab, tabname) # Add tab to notebook

    # EVENT BINDINGS
    for x in range(0, len(relevant_MV)):
        # bind checkbox clicks
        self.Bind(wx.EVT_CHECKBOX, lambda event, x=x: self.OnMVChangeState(event, relevant_MV[x]), relevant_MV[x].label)
        # bind text updates
        if relevant_MV[x].type != 2: # Type 2 MV
            self.Bind(wx.EVT_TEXT, lambda event, x=x: self.OnMetavarUpdate(event, relevant_MV[x]), relevant_MV[x].textCtrl)
        else: # Type 1 MV
            self.Bind(wx.EVT_SPINCTRL, lambda event, x=x: self.OnMetavarUpdate(event, relevant_MV[x]), relevant_MV[x].textCtrl)




  def OnLoadMV(self, event):
    # Create a dialog for selecting MV file to load    
    dlg = wx.FileDialog(self, message="Open a MV file...", defaultDir=str(self.dir_mv), defaultFile="", style=wx.FD_OPEN)
    if dlg.ShowModal() == wx.ID_OK: # Call the dialog as a model-dialog so user is required to choose Ok or Cancel
        self.dir_mv   = Path(dlg.GetDirectory())
        self.fname_mv = dlg.GetFilename()
    dlg.Destroy()

    e = self.LoadMV()

  def OnLoadFBMV(self, event):
    # Create a dialog for selecting MV file to load    
    dlg = wx.FileDialog(self, message="Open a MV file...", defaultDir=str(self.dir_mv), defaultFile="", style=wx.FD_OPEN)
    if dlg.ShowModal() == wx.ID_OK: # Call the dialog as a model-dialog so user is required to choose Ok or Cancel
        e = self.LoadFBMVs(mv_dir=dlg.GetDirectory(),mv_fname=dlg.GetFilename())
    dlg.Destroy()

  def OnLoadCtrlMV(self, event):
    # Create a dialog for selecting MV file to load    
    dlg = wx.FileDialog(self, message="Open a MV file...", defaultDir=str(self.dir_mv), defaultFile="", style=wx.FD_OPEN)
    if dlg.ShowModal() == wx.ID_OK: # Call the dialog as a model-dialog so user is required to choose Ok or Cancel
        e = self.LoadCtrlMVs(fdir=dlg.GetDirectory(),fname=dlg.GetFilename())
    dlg.Destroy()

  def OnSaveCtrlMV(self, event):
    datenow = datetime.datetime.now()
    filestr = "CtrlMVs-"+self.script_name+datenow.strftime("-%m-%d-%Y")+".txt"
    dlg = wx.FileDialog(self, message="Save current metavariable values to a file...", defaultDir=str(DIR_MV), defaultFile=filestr, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
    if dlg.ShowModal() == wx.ID_OK: # Call the dialog as a model-dialog so user is required to choose Ok or Cancel
      save_fname_seq = dlg.GetFilename()
      save_dir_seq = dlg.GetDirectory()
      self.SaveCtrlMVs(save_dir_seq, save_fname_seq)
      self.SetStatusText("Saved metavariable values to '"+filestr+"'.", 0)
    dlg.Destroy()

  def OnCompareMV(self, event):
    dlg = wx.FileDialog(self, message="Open a MV file...", defaultDir=str(self.dir_mv), defaultFile="", style=wx.FD_OPEN)
    if dlg.ShowModal() == wx.ID_OK: # Call the dialog as a model-dialog so user is required to choose Ok or Cancel
        f_dir  = dlg.GetDirectory()
        f_name = dlg.GetFilename()
    dlg.Destroy()

    ClearTerminal()
    CompareMV(os.path.join(f_dir, f_name), self.metavariables)

  def LoadFBMVs(self, event=None, mv_dir='', mv_fname=''):
    mv_dir   = self.dir_mv   if mv_dir=='' else mv_dir
    mv_fname = 'FB'+self.fname_mv if mv_fname=='' else mv_fname
    fname = Path(mv_dir)/mv_fname
    if not ChkScriptName(fname, self.script_name): # Get MV is the file exist
        print('FB MVs not found.')
        return -1
    else:
        # Need to ensure that the "state" of the regular MVs is correct after loading
        # Store a list of regular MVs that change state, so you can update them at the end
        MV_changed = []
        # First, for every FBMV in the previous set, return to state 0
        for FBMV in self.metavariables_fb:
            for MV in self.metavariables:
                if FBMV.name == MV.name:
                    MV.label.Set3StateValue(0)
                    MV_changed.append(MV)
                break
        # Then load the MVs and create new FBMVs
        self.metavariables_fb = []
        print("Loading FBMV file: "+mv_fname)
        mv_dict, mv_loop, jrange, pre, runname = ReadMV(fname) # Parse the file and load MVs into static and loop arries
        for mv_name in mv_dict:
            mv_val = mv_dict[mv_name]
            newMV = MetaVariable(mv_name, value=mv_val)
            self.metavariables_fb.append(newMV)

        # Set states for regular MVs and  take additional attributes (min, max, type, inc, etc) from the corresponding regular MV
        for FBMV in self.metavariables_fb:
            for MV in self.metavariables:
                if FBMV.name == MV.name:
                    # take additional attributes (min, max, type, inc, etc) from the corresponding regular MV
                    FBMV.min = MV.min
                    FBMV.max = MV.max
                    FBMV.inc = MV.inc
                    FBMV.type = MV.type
                    FBMV.digits = MV.digits
                    # set appropriate checkbox state
                    MV.label.Set3StateValue(1)
                    MV_changed.append(MV)
                    break
            for MV in self.metavariables_controlled:
                if FBMV.name == MV.name:
                    # delete the controlled MV
                    self.metavariables_controlled.remove(MV)
                    break
        # Note that it didn't seem necessary to do anything to the changed MVs, but still tracking them for future convenience
        # in case I do need to add something
        # Update the GUI
        self.SetupFBMVs()
        self.UpdateFeedbackControlPanel()

  def SaveCtrlMVs(self, fdir, fname):
    # If we first clear out all of the GUI information, then we can pickle the Ctrl MVs, save them, and rebuild the GUI
    fpath = Path(fdir) / fname
    f = open(fpath, 'w')

    for CtrlMV in self.metavariables_controlled:
        CtrlMV.updateFromGUI() # make sure MV values reflect GUI
        CtrlMV.clearGUI()

    if len(self.metavariables_controlled)>0:
      pickle.dump(self.metavariables_controlled, f)
    self.UpdateFeedbackControlPanel() # rebuilds GUI objects
    f.close()

  
  def LoadCtrlMVs(self, mv_dir='', mv_fname=''):
    mv_path = Path(mv_dir) / mv_fname
    if mv_path.exists():
        print("Loading CtrlMV file: "+ mv_fname) 
        f = open(mv_path, 'rb')
        try:
          self.metavariables_controlled = pickle.load(f)
        except EOFError:
          print("CtrlMVs empty, this is probably fine")
        finally:
          f.close()
        # go through regular MVs; if they now correspond to a FB MV, set checkbox appropriately AND remove measurement MV if necessary

        self.UpdatedCtrlMVs() # ensures that regular and FBMVs are consistent with the new control MVs
        self.UpdateFeedbackControlPanel() # build feedback control GUI
    else:
        print('Ctrl MVs not found.')

  def UpdatedCtrlMVs(self): # ensures that regular and FBMVs are consistent with the new control MVs
    for MV in self.metavariables:
        foundCtrl = False
        for CtrlMV in self.metavariables_controlled:
            if CtrlMV.name == MV.name:
                foundCtrl= True
                MV.label.Set3StateValue(2)
                break
        if MV.label.Get3StateValue() == 2 and not foundCtrl: # used to be Ctrl, now it isn't
            MV.label.Set3StateValue(0)
    updatedFBMV = False
    for CtrlMV in self.metavariables_controlled: 
        for FBMV in self.metavariables_fb: # if there's a match FBMV, remove it
            if CtrlMV.name == FBMV.name:
                self.metavariables_fb.remove(FBMV)
                updatedFBMV = True
                break
    if updatedFBMV:
        self.SetupFBMVs()



  def LoadMV(self, event=None, mv_dir='', mv_fname=''):
    relevant_MV = self.metavariables

    mv_dir   = self.dir_mv   if mv_dir=='' else mv_dir
    mv_fname = self.fname_mv if mv_fname=='' else mv_fname
    # Check if someone chose an FB or Ctrl MV; if so, remove the beginning and continue loading
    if mv_fname[0:4]=='Ctrl':
        mv_fname = mv_fname[4:]
    elif mv_fname[0:2]=='FB':
        mv_fname = mv_fname[2:]

    fname = Path(mv_dir)/mv_fname
    print("Loading MV file: "+mv_fname)
    if not ChkScriptName(fname, self.script_name): # Get MV is the file exist
        return -1
    else:
        mv_dict, mv_loop, jrange, pre, runname = ReadMV(fname) # Parse the file and load MVs into static and loop arries

        # Update the values of the metavariables
        for mv in relevant_MV: # Update MV values
          try:
            if mv_dict[mv.name] != 'LOOP': # Don't update if it's a loop variable
                mv.value = mv_dict[mv.name]
          except KeyError as kerr:
            print("No variable named "+mv.name+" in the file")

        # Update values on the front panel
        self.SetupMetavars() # Setup the static MVs
        self.txtctrl_loopcode.SetValue(mv_loop) # Update loop code

        # Update j range and pre run and runname
        if not jrange[0] == 'NA':
            print('Load loop settings!')
            self.txtctrl_j0.SetValue(jrange[0])
            self.txtctrl_j1.SetValue(jrange[1])
            self.txtctrl_prerun.SetValue(pre)
            self.txtctrl_dirname.SetValue(runname[1:-1])

        # Load corresponding feedback measurement MVs and feedback control MVs (each function checks existence)
        self.LoadFBMVs(mv_dir=mv_dir, mv_fname='FB'+mv_fname)
        self.LoadCtrlMVs(mv_dir=mv_dir, mv_fname='Ctrl'+mv_fname)

        return 1



  ####################################
  ###       Device Managment       ###
  ####################################
  # Ping the device server to see if they are online
  def OnPingServers(self, event):
    self.sizer_server.Clear(True) # Clear server status sizers
    fails = 0 # Number of servers failed to respond

    #for seq in self.dm.seq_act: # Check all selected servers
    #    e = self.dm.Ping(seq)
    for name, dev in self.dm.devices.items():
        e = dev.Ping() #ping all devices
        if e == 0:
            fails += 1
            statusText1 = wx.StaticText(self.panel, wx.ID_ANY, name+": Not Listening")
            statusText1.SetForegroundColour((255, 0, 0))
            self.sizer_server.Add(statusText1, 0, wx.TOP, border=5)
        elif e == 1:
            statusText1 = wx.StaticText(self.panel, wx.ID_ANY, name+": Listening")
            statusText1.SetForegroundColour((170, 170, 170))
            self.sizer_server.Add(statusText1, 0, wx.TOP, border=5)

    if fails > 0:
        self.statusbar.Error(str(fails)+" servers did not respond.")
    else:
        self.statusbar.SetStatusText("All servers listening.")

    # Update UI
    self.panel.Layout()
    self.Refresh()
  
  # Choose the active sequence
  def OnCheckServers(self, event):
    self.sizer_server.Clear(True) # Clear server status sizers

    #self.dm.seq_act = [] # Clear the active sequence list
    seq_new = []
    for ii, seq in enumerate(self.dm.seq_all): # Loop over all available sequence in the device manager
        if self.m_seq[ii].IsChecked():
            #self.dm.seq_act.append(seq)
            seq_new.append(seq)
    self.dm.SetActiveSeq(seq_new)

    # Refresh the GUI
    self.panel.Layout()
    self.Refresh()
    self.OnPingServers(None) # check if server is listening
    
  # Select which variable to iterate during the loop run and put it into the loop code text box
  def OnChooseLoopedVar(self, event):
    '''TODO: NEW FUNCTION TO GENERATE LOOP CODE AUTOMATICALLY'''
    metavariablenames = []
    metavariablevalue = []

    for metavariable in self.metavariables:
      metavariablenames.append(metavariable.name)
      metavariablevalue.append(metavariable.value)
      
    existLoopLines = self.txtctrl_loopcode.GetValue().splitlines()
    existVars = {}
    for line in existLoopLines:
      existName, existVal = line.replace(" ", "").split("=")
      existVars[existName] = existVal
      
    ind = []
    for var in existVars:
      ind.append(metavariablenames.index(var))
    
    # Create a new window for selection
    dlg = wx.MultiChoiceDialog(self, "Choose the variables for the loop code", "All MVs", metavariablenames)
    dlg.SetSelections(ind)
    
    loopvars = []
    if (dlg.ShowModal() == wx.ID_OK):
      selections = dlg.GetSelections()
      loopvars = [metavariablenames[x] for x in selections]
      loopvarvals = [metavariablevalue[x] for x in selections]
    dlg.Destroy()
    
    # Generate loop code text
    text = ''
    for x in range(0, len(loopvars)):
      if loopvars[x] in existVars:
        text += loopvars[x]+" = "+str(existVars[loopvars[x]])+"\n"
      else:
        text += loopvars[x]+" = "+str(loopvarvals[x])+"\n"
    self.txtctrl_loopcode.SetValue(text)

    return 1
    
  # Save metavariables at their current values to a file
  def ExportMV(self, event):
    datenow = datetime.datetime.now()
    filestr = "MVs-"+self.script_name+datenow.strftime("-%m-%d-%Y")+".txt"
    dlg = wx.FileDialog(self, message="Save current metavariable values to a file...", defaultDir=str(DIR_MV), defaultFile=filestr, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) #TODO FD_save
    if dlg.ShowModal() == wx.ID_OK: # Call the dialog as a model-dialog so user is required to choose Ok or Cancel
      save_fname_seq = dlg.GetFilename()
      save_dir_seq = dlg.GetDirectory()
      self.SaveMV(save_dir_seq, save_fname_seq)
      self.SaveMV(save_dir_seq, 'FB'+save_fname_seq, FB_flag=True)
      self.SaveCtrlMVs(save_dir_seq, 'Ctrl'+save_fname_seq) 
      self.SetStatusText("Saved metavariable values to '"+filestr+"', along with feedback settings to corresponding files.", 0)
    dlg.Destroy()

# Save metavariables at their current values to a file
  def ExportFBMV(self, event):
    datenow = datetime.datetime.now()
    filestr = "FBMVs-"+self.script_name+datenow.strftime("-%m-%d-%Y")+".txt"
    dlg = wx.FileDialog(self, message="Save current metavariable values to a file...", defaultDir=str(DIR_MV), defaultFile=filestr, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
    if dlg.ShowModal() == wx.ID_OK: # Call the dialog as a model-dialog so user is required to choose Ok or Cancel
      save_fname_seq = dlg.GetFilename()
      save_dir_seq = dlg.GetDirectory()
      self.SaveMV(save_dir_seq, save_fname_seq, FB_flag=True)
      self.SetStatusText("Saved metavariable values to '"+filestr+"'.", 0)
    dlg.Destroy()
  
  # Save current MV settings to a text file. No loop information will be included.
  def SaveMV(self, dir_seq, fname, FB_flag=False):
    datenow = datetime.datetime.now()
    path_seq = Path(dir_seq) / fname
    f = open(path_seq, 'w')
    # Write MV file
    f.write( "# Script name: "+str(self.script_name)+"\n" ) # Sequence name
    f.write( "#   Generated: "+datenow.strftime("%b %d, %Y %H:%M:%S.%f")+"\n\n" ) # Date created
    if not FB_flag: # save regular MVs
        for _MV in self.metavariables:
          f.write(_MV.name+" = "+str(_MV.value)+'\n') # MV values
    else: # save FB MVs
        for _MV in self.metavariables_fb:
          f.write(_MV.name+" = "+str(_MV.value)+'\n') # MV values
    f.close()
    return 1

  def GenerateMVCode(self, date_time):
    code  = "# Script name: "+str(self.fname_seq)+"\n"
    code += "#   Generated: "+date_time.strftime("%b %d, %Y %H:%M:%S.%f")[:-3]+"\n\n"
    for _MV in self.metavariables:
      code += _MV.name+" = "+str(_MV.value)+'\n' # MV values
    return code
      
  # Generate a loop code using MVs in the variable area and looping variable in the loop run text box
  def GenerateLoopCode(self):
    looped_vars = self.txtctrl_loopcode.GetValue().splitlines()
    loop_vars = {}
    for line in looped_vars:
      if re.match(r'^\s*$', line): continue# Check for empty lines
      var_name, var_val = line.replace(" ", "").split("=")
      loop_vars[var_name] = var_val
    
    text = ""
    for x in range(0, len(self.metavariables)):
      metavarname = self.metavariables[x].name
      metavarval  = str(self.metavariables[x].value)
      if not self.metavariables[x].name in loop_vars:
        text += metavarname+" = "+metavarval+"\n"
      else:
        text += metavarname+" = "+loop_vars[metavarname]+"\n"
    return text

  # Generate a MV dict using MVs in the variable area and looping variable in the loop run text box
  def GenerateMVDict(self):
    looped_vars = self.txtctrl_loopcode.GetValue().splitlines()
    loop_vars = {}
    for line in looped_vars:
      if re.match(r'^\s*$', line): continue# Check for empty lines
      var_name, var_val = line.replace(" ", "").split("=")
      loop_vars[var_name] = var_val
    
    sMVs = {} #static MVs
    lMVs = {} #loop MVs
    for x in range(0, len(self.metavariables)):
      metavarname = self.metavariables[x].name
      metavarval  = self.metavariables[x].value
      if not self.metavariables[x].name in loop_vars:
        #text += metavarname+" = "+metavarval+"\n"
        sMVs[metavarname] = float(metavarval)
      else:
        #text += metavarname+" = "+loop_vars[metavarname]+"\n"
        lMVs[metavarname] = loop_vars[metavarname]
    return sMVs, lMVs
    
  # Save loop code at their current values to a text file
  def ExportLoopedCode(self, event, flag=1):
    folder_name = self.txtctrl_dirname.GetValue()
    if folder_name.strip() == '':
      folder_name = 'SPCM'
    datenow = datetime.datetime.now()
    filestr = "LC-"+self.script_name+datenow.strftime("-%m-%d-%Y")+".txt"
    data_dir = DIR_DATA/datetime.datetime.now().strftime("%Y/%m/%d/")/folder_name/"MVs/"
    if not data_dir.exists():
      os.makedirs(data_dir)
    if flag == 1:
      dlg = wx.FileDialog(self, message="Save current looped code...", defaultDir=data_dir, defaultFile=filestr, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
      if dlg.ShowModal() == wx.ID_OK: # Call the dialog as a model-dialog so user is required to choose Ok or Cancel
        save_fname_seq = dlg.GetFilename()
        save_dir_seq = Path(dlg.GetDirectory())
        dlg.Destroy()
    elif flag == 0:
      save_fname_seq = filestr
      save_dir_seq = data_dir
    
    save_path = Path(save_dir_seq) / save_fname_seq
    f = open(save_path, 'w')
    self.loop_code = self.GenerateLoopCode()
    loop_start = self.txtctrl_j0.GetValue()
    loop_stop = self.txtctrl_j1.GetValue()
    f.write( "# Script name: "+str(self.fname_seq)+"\n" )
    f.write( "#   Generated: "+datenow.strftime("%b %d, %Y")+"\n" )
    f.write( "#       j_min: "+str(loop_start)+"\n" )
    f.write( "#       j_max: "+str(loop_stop)+"\n\n" )
    f.write(self.loop_code)
    f.close()
    # self.SetStatusText("Saved looped code to '"+filestr+"'.", 0)
    copyfile(self.dir_seq/self.fname_seq, save_dir_seq/self.fname_seq) # Copy the sequence file into the destination directory
    # self.SetStatusText("Copied sequence file to '"+filestr+"'.", 0)
    # also save FB MVs
    self.SaveCtrlMVs(save_dir_seq, "Ctrl"+save_fname_seq)
    self.SaveMV(save_dir_seq, "FB"+save_fname_seq, FB_flag=True)

  # Save exeriment info
  def ExportInfo(self):
    f_subdir = self.txtctrl_dirname.GetValue()
    if f_subdir.strip() == '':
      f_subdir = 'SPCM'
    f_name = GenFname(header='INFO', dt=datetime.datetime.now(), post='', postfix='.info')
    f_dir  = GenDTDir(DIR_DATA, dt=datetime.datetime.now(), sub_dir=f_subdir+'/MVs')
    ChkDirExist(f_dir)
    
    text_info = self.txtctrl_expinfo.GetValue()
    f = open(f_dir/f_name, 'w')
    f.write(text_info)
    f.close()

    return 1
  
  ##########################################
  ###         Execute Experiment         ###
  ##########################################
  # Helper function to disable UI objects
  def __DisableBtn__(self, btn_use, label='None'):
    for btn in self.all_btn:
        if btn == btn_use:
            if label != 'None':
                btn.SetLabel(label)
        else:
            btn.Disable()
    for man in self.all_man:
        man.Enable(False)
    return 1
  
  def __EnableBtn__(self):
    # Restore button label
    self.btn_run.SetLabel("Run")
    self.btn_run_looped.SetLabel("Looped Run")
    #self.btn_run_repeated.SetLabel("Run Repeatedly")
    self.btn_run_idle.SetLabel("Idle")
    
    # Enable all buttons
    for btn in self.all_btn:
        btn.Enable()

    # Enable all manual objects
    for man in self.all_man:
        man.Enable(True)
    
    return 1
  
  # Update the worker once number of MVs changes on the screen
  def OnMetavarUpdate(self, event, mv):
    text = event.GetString()
    if is_number(text):
      mv.value = float(text)
      if self.worker != None:
        self.worker._need_update = 1

  # Run a sequence one time. We keep things as close to the looping runs as possible.
  def OnRunSingle(self, event):
    # Trigger the worker thread unless it's already busy
    if not self.worker:
      self.statusbar.SetStatusText('Running sequence a single time.')
      wx.BeginBusyCursor()
      self.__DisableBtn__(self.btn_run, label='Abort')
      self.worker = WorkerThread(self, loop=0, runflag=1)
    else:
      self.statusbar.SetStatusText("Aborted single run (I don't think you can do that...)")
      self.worker.abort()

  # Run a sequence repeatedly (no j values)
  def OnRunRepeated(self, event):
    if self.worker:
      self.statusbar.SetStatusText('Aborted repeated run.')
      self.worker.abort()
      return 1
    
    time_delay = self.txtctrl_rungap.GetValue()
    if not is_number(time_delay):
      self.statusbar.Error("'Time between runs' must be an integer or float.")
      return -1
    time_delay = float(time_delay)
    if time_delay < 0:
      self.statusbar.Error("'Time between runs' must be positive.")
      return -1
  
    self.statusbar.SetStatusText('Running repeatedly.')
    wx.BeginBusyCursor()
    #self.__DisableBtn__(self.btn_run_repeated, label='Abort')
    self.worker = WorkerThread(self, loop=1, delay=time_delay, runflag=1)
  
  # Run a sequence repeatedly without saving log
  def OnRunIdle(self, event=None):
    if self.worker:
      self.statusbar.SetStatusText('Aborted repeated run.')
      self.worker.abort()
      return 1
    
    time_delay = self.txtctrl_rungap.GetValue()
    if not is_number(time_delay):
      self.statusbar.Error("'Time between runs' must be an integer or float.")
      return -1
    time_delay = float(time_delay)
    if time_delay < 0:
      self.statusbar.Error("'Time between runs' must be positive.")
      return -1
  
    # Here the actual looped run is entered, create run in DB
    sMVs, lMVs = self.GenerateMVDict()
    # Read and compress sequence and info
    path_seq = self.dir_seq / self.fname_seq
    with open(path_seq, 'r') as fs:
      seq_bin = zlib.compress(fs.read().encode())
    loop_fname  = self.txtctrl_dirname.GetValue()
    run_time = datetime.datetime.now()

    text_info = self.txtctrl_expinfo.GetValue()
    _loop_name = loop_fname
    if _loop_name =='':
      _loop_name = secrets.token_hex(8)
    idle_name = "IDLE_{}".format(_loop_name)
    run_doc = RunIdle(name=idle_name, date=run_time, initMVs=sMVs, updateMVs=[], sequence=seq_bin, info=text_info)
    #self.savedata_switch = bool(self.chkbox_savedata.GetValue())
    self.savedata_switch = 0
    _run_id = createRun(self.client, run=run_doc, save=False)
    self.run_id = str(_run_id) #cast BSON Object ID into string

    self.statusbar.SetStatusText('Running repeatedly.')
    wx.BeginBusyCursor()
    self.__DisableBtn__(self.btn_run_idle, label='Abort')
    # pdb.set_trace()
    
    self.worker = WorkerThread(self, loop=4, delay=time_delay, runflag=1, saveswitch=1)

  # Run a sequence using the loop code and parameters    
  def OnRunLooped(self, event=None):
    if self.worker:
      self.statusbar.SetStatusText('Aborted looped run.')
      self.worker.abort()
      return 1
        
    time_delay = self.txtctrl_rungap.GetValue()
    if not is_number(time_delay):
      self.statusbar.Error("'Time between runs' must be an integer or float.")
      return -1
    time_delay = float(time_delay)
    if time_delay < 0:
      self.statusbar.Error("'Time between runs' must be positive.")
      return -1

    # Gather loop run info
    # Pre run, loop start and loop stop index
    loop_prerun = self.txtctrl_prerun.GetValue()
    loop_start  = self.txtctrl_j0.GetValue()
    loop_stop   = self.txtctrl_j1.GetValue()
    if (not (is_int(loop_start) and is_int(loop_stop)) and is_int(loop_prerun)):
      self.statusbar.Error("Error: Loop indices must be integers.")
      return
    loop_prerun = int(loop_prerun)
    loop_start  = int(loop_start)
    loop_stop   = int(loop_stop)
    if (loop_stop<loop_start):
      self.statusbar.Error("Error: Loop stop must be greater than or equal to loop start.")
      return

    # Get data folder name and check if that folder already exist
    loop_fname  = self.txtctrl_dirname.GetValue()
    self.dir_data = loop_fname
    run_time = datetime.datetime.now()
    trace_dir = run_time.strftime("%Y/%m/%d/")
    trace_full_dir = DIR_DATA/trace_dir/loop_fname
    # If the folder already exist, ask if want to append
    if (loop_fname!="") & (trace_full_dir.exists()):
      dlg = wx.MessageDialog(self, "Folder already exists. Press \"Yes\" to append to it?", "Warning!", wx.YES_NO|wx.ICON_QUESTION)
      result = dlg.ShowModal()
      dlg.Destroy()
    else:
      result = wx.ID_YES
    if result == wx.ID_NO:
      return
    
    # Create loop code
    self.loop_code = self.GenerateLoopCode()

    # Here the actual looped run is entered, create run in DB
    sMVs, lMVs = self.GenerateMVDict()
    Nshots = int(loop_stop-loop_start+1)
    sMVs.update({'j_min': loop_start, 'j_max': loop_stop})
    # Read and compress sequence and info
    path_seq = self.dir_seq / self.fname_seq
    with open(path_seq, 'r') as fs:
      seq_bin = zlib.compress(fs.read().encode())

    text_info = self.txtctrl_expinfo.GetValue()
    run_doc = RunLooped(name=loop_fname, date=run_time, Nshots=Nshots,
                        staticMVs=sMVs, loopMVs=lMVs, sequence=seq_bin, info=text_info)
    self.savedata_switch = True #bool(self.chkbox_savedata.GetValue())
    logger.debug("Loopen run with save_switch {}".format(self.savedata_switch))
    _run_id = createRun(self.client, run=run_doc, save=self.savedata_switch)
    self.run_id = str(_run_id) #cast BSON Object ID into string

    # Trigger the worker thread unless it's already busy
    self.statusbar.Error("Loop from "+str(loop_start)+" to "+str(loop_stop))
    self.statusbar.SetStatusText('Running loop.')
    self.ExportLoopedCode(None, flag=0)
    self.__DisableBtn__(self.btn_run_looped, label='Abort') # disable UI
    wx.BeginBusyCursor()
    
    self.worker = WorkerThread(self, loop=2, delay=time_delay, startval=loop_start, stopval=loop_stop, 
                              prerun=loop_prerun, runflag=1, saveswitch=(2 if self.savedata_switch else 1))
    
  # Called when we return from a run thread: update status bar, re-enable UI  
  def OnReturnFromRun(self, event):
    # Show Result Status
    if event.data == 1:
      seagulls = ["I just ran. womp", "I ran so far away", "I just ran", "I ran all night and day", "...I couldn't get away", "*Guitar Solo*"]
      self.statusbar.SetStatusText(seagulls[int(1e2*np.random.rand())%len(seagulls)])
    else:
      self.statusbar.SetStatusText("Ran sequence "+str(event.data)+" times.")
    
    # Clear worker thread
    self.worker = None
    '''TODO: GARBAGE COLLECTION'''
    # TODO set run in DB as done
    if self.run_id is not None:
      finalizeRun(self.client, run_id=ObjectId(self.run_id), save=self.savedata_switch)
    # Re-enable UI
    wx.EndBusyCursor()
    if not self.RemoteServer:
        self.__EnableBtn__()

    # Save info and backup data for looped run
    if event.loop:
        self.ExportInfo()
        time.sleep(.5) # Extra time for device to save the data.
        if self.chkbox_autobkp.GetValue():
            self.OnBkpData(None)
        if self.chkbox_autoidle.GetValue():
            # # # # play a sound to indicate that the run is finished, then start idling
            frequency = 2500  # Set Frequency To 2500 Hertz
            duration = 1000  # Set Duration To 1000 ms == 1 second
            winsound.Beep(frequency, duration)
            # winsound.PlaySound('sound.wav', winsound.SND_FILENAME)
            self.OnRunIdle()
  
  def OnUpdateRunInfo(self, event):
    if event.abort:
        self.worker.abort()
        self.ShowMessage(event.data)
    else:
        self.statusbar.SetStatusText(event.data)

  def OnReturnFromDebug(self, event):
    if event.abort:
        self.worker.abort()
        self.ShowMessage(event.data)
    else:
        self.statusbar.SetStatusText(event.data)
  
  
  #######################################
  ###         Utility Methods         ###
  #######################################
  def debug(self, event=None):
    print("#"*50)
  
  # Remote control mode
  def OnRemote(self, event): 
    if self.mode == FPMODE_REM:
      self.RemoteServer.abort() # Terminate remote server
      self.RemoteServer = None # Clear remote server thread
      StopRemoteServer() # Last call to close server client loop
      self.__EnableBtn__() # Enable all buttons
      self.mode = FPMODE_SEQ # Switch to regular mode
    elif self.mode == FPMODE_SEQ:
      self.__DisableBtn__(self.btn_remote) # Disable all buttons

      '''TODO: DISABLE ALL TEXTCTRL'''
      # children = self.sizer_LoopCode.GetChildren()
      # for child in children:
      #   widget = child.GetWindow()
      #   print widget
      #   if isinstance(widget, wx.TextCtrl):
      #     widget.Enable(False)

      self.mode = FPMODE_REM # Switch to remote mode
      self.RemoteServer = RemoteServer(self) # Create remote server thread

    return 1

  # Change the front panel to stead state mode
  def SetSSV(self, event):
    if self.mode == FPMODE_FB:
      # if in feedback mode, DO NOTHING except warn the user why it failed
      self.statusbar.SetStatusText("Cannot switch to SSVs while modifying feedback MVs!")
    elif self.mode == FPMODE_SEQ: # Go to set SSV mode
      # Save current sequence and MV
      self.SaveMV(self.temp_dir, self.temp_MV) # Save the MV for current sequence
      self.temp_dir_seq   = self.dir_seq   # save current sequence dir
      self.temp_fname_seq = self.fname_seq # save current sequence filename
      # Switch sequnce to the temp directory
      self.dir_seq   = self.temp_dir # change dir to temp directory
      self.fname_seq = 'SetSSV.py'   # change filename to SetSSV
      self.script_name = self.fname_seq.replace(".py", "")
      # Preserve the settings
      self.temp_LoopTxt = self.txtctrl_loopcode.GetValue()
      self.temp_j0 = self.txtctrl_j0.GetValue()
      self.temp_j1 = self.txtctrl_j1.GetValue()

      # Write SSV sequence
      text_ssv = GenSSVSeq(all_sequences) # generate set ssv sequence
      f = open(self.dir_seq/self.fname_seq, 'w')
      f.write(text_ssv)
      f.close()
      
      
      self.btn_set_ssv.SetLabel("Back to the Sequence") # Change ui label
      self.mode = FPMODE_SSV # change front panel mode to SetSSV
      self.LoadSeq() # load set ssv sequence
      
    elif self.mode == FPMODE_SSV: # Go back to regular sequence mode
      self.dir_seq   = self.temp_dir_seq # restore sequence directory
      self.fname_seq = self.temp_fname_seq # restore sequence filename
      self.script_name = self.fname_seq.replace(".py", "")
      self.LoadSeq() # Reload sequence
      # Load static mvs
      self.LoadMV(mv_dir=self.temp_dir, mv_fname=self.temp_MV) # Reload MVs
      # Load loop settings. This is required since the temp MV file only record the static mv, so the loop settings are lost
      # Not using the loop code since sometimes we define constant variable in the loop code, 
      # but those variables won't be recognized as loop code
      self.txtctrl_loopcode.SetValue(self.temp_LoopTxt)
      self.txtctrl_j0.SetValue(self.temp_j0)
      self.txtctrl_j1.SetValue(self.temp_j1)

      self.btn_set_ssv.SetLabel("Set Steady State Value") # Change button label
      self.mode = FPMODE_SEQ # Switch mode to regular sequence mode


    return 1



  def OnMVChangeState(self, event, MV):
    # print(MV.label.Get3StateValue()) # 0 is unchecked, 1 is checked, 2 is filled
    # find and remove any corresponding FB MV UNLESS it's actually supposed to exist
    for FBMV in self.metavariables_fb:
        if FBMV.name == MV.name:
            self.metavariables_fb.remove(FBMV)
    # find and remove any corresponding controlled MV UNLESS it's actually supposed to exist
    for FBMV in self.metavariables_controlled:
        if FBMV.name == MV.name:
            self.metavariables_controlled.remove(FBMV)            

    if MV.label.Get3StateValue() == 2: # if it just became a control MV
        newMV = FBControlMV(MV.name, P=0, I=0, value=MV.value, typeval=MV.type, minval=MV.min, maxval=MV.max, maxinc=MV.inc)
        self.metavariables_controlled.append(newMV)
        print('FB Control MV')
    elif MV.label.Get3StateValue() == 1: # if it just became a feedback measurement MV, make sure it is removed from FB measurement and control    
        newMV = MetaVariable(MV.name, tabname='*FeedbackMeasure*', value=MV.value, type=MV.type, min=MV.min, max=MV.max, inc=MV.inc, digits=MV.digits)
        self.metavariables_fb.append(newMV)
        print('FB Measurement MV')
    elif MV.label.Get3StateValue() == 0: # if it just became an ordinary MV, make sure it is removed from FB measurement and control
        print('Ordinary MV')

    self.UpdateFeedbackControlPanel()
    self.SetupFBMVs()



  def UpdateFeedbackControlPanel(self):
    for MV in self.metavariables_controlled:
        print(MV.name)

    newFBPanel = wx.FlexGridSizer(len(self.metavariables_controlled)+1, 13, 3, 10) # for the feedback CONTROL settings
    
    # Add title bar
    newFBPanel.Add(wx.StaticText(self.panel, wx.ID_ANY, 'Enable'))
    newFBPanel.Add(wx.StaticText(self.panel, wx.ID_ANY, 'Feed Forward'))
    newFBPanel.Add(wx.StaticText(self.panel, wx.ID_ANY, 'MV Name'))
    newFBPanel.Add(wx.StaticText(self.panel, wx.ID_ANY, 'Current Value'))
    newFBPanel.Add(wx.StaticText(self.panel, wx.ID_ANY, 'Default Value'))
    newFBPanel.Add(wx.StaticText(self.panel, wx.ID_ANY, 'Max Value'))
    newFBPanel.Add(wx.StaticText(self.panel, wx.ID_ANY, 'Min Value'))
    newFBPanel.Add(wx.StaticText(self.panel, wx.ID_ANY, 'Max Step Size'))
    newFBPanel.Add(wx.StaticText(self.panel, wx.ID_ANY, 'P'))
    newFBPanel.Add(wx.StaticText(self.panel, wx.ID_ANY, 'I'))
    newFBPanel.Add(wx.StaticText(self.panel, wx.ID_ANY, 'Eval Function'))
    newFBPanel.Add(wx.StaticText(self.panel, wx.ID_ANY, 'Set Point'))
    newFBPanel.Add(wx.StaticText(self.panel, wx.ID_ANY, 'Latest Eval'))

    # Add FB control MVs 
    for FBMV in self.metavariables_controlled:
        FBMV.makeFBRow(newFBPanel, self.panel, self)


    if self.sizer_FeedControl != None:
        self.sizer_FeedMain.Hide(self.sizer_FeedControl)
        self.sizer_FeedMain.Remove(self.sizer_FeedControl)

    self.sizer_FeedMain.Add(newFBPanel, border=5)
    self.sizer_FeedMain.Layout() # IMPORTANT after removing and adding sizer children!
    # store for later
    self.sizer_FeedControl = newFBPanel


  # Backup the data folder in the folder box to the lab server
  def OnBkpData(self, event):
    cwd = os.getcwd() # The dataBackup class will change the workinng directory. This will change the directory back to the front panel
    bkp = BkpData.dataBackup(bkpDate=datetime.datetime.now())
    FolderToBkp = self.txtctrl_dirname.GetValue()
    if FolderToBkp.strip() == '':
      FolderToBkp = 'SPCM'
      '''TODO: MAKE IT THE SAME AS THE DEVICE SAVING DIRECTORY'''
    FolderToBkpFull = bkp.file_dir/FolderToBkp
    if FolderToBkpFull.exists():
      bkp.folders = [FolderToBkp]
      FileNum = bkp.zipData()
      e = bkp.CopyFile()
      if e == 1:
        self.statusbar.SetStatusText(str(FileNum)+" files have been copied to the server!")
      elif e == 0:
        self.statusbar.SetStatusText("Failed to copy the file to the server!")
        print(FolderToBkpFull)
      bkp.clearZip()
    else:
      self.statusbar.SetStatusText("Folder ("+str(FolderToBkp)+") does not exist!")
    os.chdir(cwd) # change working directory
    gc.collect()
  
  # Open a GUI for plot channel selection
  def OnSelectPlot(self, event):
    dlg = PlotSeq.ChanSelect(SEQUENCES_TO_GRAPH) # Selection window
    if dlg.ShowModal() == wx.ID_OK:
      rtn_seq = dlg.GetSeq()
    dlg.Destroy()
    for ii in range(len(rtn_seq)): # Overwrite channelsToGraph property of each sequence
      if rtn_seq[ii].name == SEQUENCES_TO_GRAPH[ii].name:
        SEQUENCES_TO_GRAPH[ii].channelsToGraph = rtn_seq[ii].channelsToGraph
  
  # Plot the sequence of selected channels. 
  def OnPlotSeq(self, event):
    # RUN_FLAG = 0 # Do not run the sequence
    self.debug_done = 0

    wx.BeginBusyCursor()
    IntervalTime = {'times': None}
    self.worker = WorkerThread(self, loop=5, IntervalerObj=IntervalTime) # Execute the sequence file
    self.worker.join()
    try:
      _IntervalTime = IntervalTime['Intervaler']
    except KeyError:
      _IntervalTime = None
    logger.debug("IntervalTime {}".format(_IntervalTime))

    PlotSeq.PlotSeq_DeviceValue(self.dm, IntervalTime=_IntervalTime) # Plot the actual device value
    '''TODO: PLOT SEQUENCE VALUES. FUNCTION IS DONE, ONLY NEED GUI OBJECT'''
    #time.sleep(.5) # wait the code to be executed by the WorkerThread
    #PlotSeq.PlotSeq_SeqValue(self.dm, IntervalTime) # Plot the sequence data

  # Save current settings before close the program
  def OnClose(self, event):
    # Terminate all thread
    if self.worker:
        self.worker.abort()
        self.worker = None
    if self.RemoteServer:
        self.RemoteServer.abort() # Terminate remote server
        self.RemoteServer = None
        StopRemoteServer()

    # Get all the sequences being used
    ActSeqNames = []
    for _seq in self.dm.seq_act:
        ActSeqNames.append(_seq.name)
    
    # Save front panel parameters
    # savetxt  = ''
    # savetxt += 'self.dir_seq   = {!r}\n'.format(WindowsPath(self.dir_seq))
    # savetxt += 'self.fname_seq = \''+self.fname_seq+'\'\n'
    # savetxt += 'self.script_name = \''+self.script_name+'\'\n'
    # savetxt += 'ActSeqNames = '+str(ActSeqNames)+'\n'
    # f = open(self.temp_dir/self.fp_cfg, 'w')
    # f.write(savetxt)
    # f.close()
    d = shelve.open(str(self.temp_dir/self.fp_cfg))
    d['dir_seq'] = WindowsPath(self.dir_seq)
    d['fname_seq'] = self.fname_seq
    d['script_name'] = self.script_name
    d['ActSeqNames'] = ActSeqNames
    d.close()

    # Save current MVs
    self.SaveMV(self.temp_dir, self.temp_MV)
    self.SaveMV(self.temp_dir, 'FB'+self.temp_MV, FB_flag=True)
    #self.SaveCtrlMVs(self.temp_dir, 'Ctrl'+self.temp_MV) #TODO: fix
      
    self.Destroy() # Close the GUI
  
  def OnResize(self, event):
    self.reserved1.SetLabel("Reserved space #1: "+str(self.reserved1p.GetSize()))
    self.reserved2.SetLabel("Reserved space #2: "+str(self.reserved2p.GetSize()))
    nw, nh = self.reserved1p.GetSize()
    
    if nw > nh:
      nh = nw * nh /nw
    else:
      nw = nh * nw / nh

    event.Skip()

  # Show a popup box with title and msg
  def ShowMessage(self, msg, title='So, uh...', icon=wx.ICON_INFORMATION):
    wx.MessageBox(msg, title, icon)
  
  # Show the 'About' popup box
  def OnAbout(self, event):
    wx.MessageBox("Simon Lab Software Suite\n\nVersion " + self.VERSION + "\nAuthor: Graham Greve\n\nI was written using wxPython for GUI and PyQtGraph for plotting. I'm free software, provided as is, with no guarantees. A helpful PDF full of documentation was provided at one point.\n\nThanks to all who helped me come alive.\n\n\"Turn your can'ts into cans and your dreams into plans.\"", "About This Program", wx.ICON_INFORMATION)
  
  # Open the 'Help' PDF
  def OnHelp(self, event):
    # If this file ever moves... I'm sorry.
    os.startfile("documentation\Software Suite User Manual.pdf")

##################################
###     Text Contral Class     ###
##################################
class MVTextCtrl(wx.TextCtrl):
  def __init__(self, parent, value="0.0", mv=None):
    wx.TextCtrl.__init__(self, parent, value=value)
    self.mv = mv

##################################
###     Custom Status Bar!     ###
##################################
class MyStatusBar(wx.StatusBar):
  def __init__(self, parent):
    super(MyStatusBar, self).__init__(parent)
    self.error = 0
    self.SetFieldsCount(2)
    self.SetStatusText('        ', 1)
    self.SetStatusWidths([-1,700])
    self.icon = wx.StaticBitmap(self, bitmap=wx.Bitmap(str((ICON_FOLDER/'error.png'))))
    self.Bind(wx.EVT_SIZE, self.OnSize)

  def OnPaint(self, e):
    if self.error == 1:
      PlaceIcon()
    else:
      self.icon.SetPosition((100, 100))

  # This (along with OnPaint and Error) was supposed to update a little icon in the bottom right corner to indicate an error. Can YOU figure it out?
  def PlaceIcon(self):
    rect = self.GetFieldRect(1)
    self.icon.SetPosition((rect.x+5, rect.y+3))
#    self.icon = wx.StaticBitmap(self, bitmap=wx.Bitmap(str(('utilities/gui_icons/exit.png'))))

  def OnSize(self, e):
    e.Skip()
    self.PlaceIcon()
      
  def Error(self, msg):
   #self.PlaceIcon()
   error = 1
   self.SetStatusText('        '+msg, 1)

###########################
### Run the Front Panel ###
###########################
if __name__ == '__main__':

  app = wx.App(redirect=False)
  FrontPanel()
  app.MainLoop()
  