import os
import zipfile
import datetime
import shutil
import glob
import win32wnet
import win32netcon
from pathlib import Path
from ..config.config import *
# Default home directory and date
#datadir = Path("../../TestOutput/Data/") #"E:/Data"
datadir = DIR_DATA
datenow = datetime.datetime.now()

class dataBackup:
  def __init__(self, HomeDir=datadir, bkpDate=datenow):
    self.home_dir = Path(HomeDir)    # Data home directory
    self.date_dir = bkpDate.strftime('/%Y/%m/%d')          # Data date directory
    self.file_dir = self.home_dir/self.date_dir               # Full data directory
    self.log_dir  = DIR_LOG #Path("../../TestOutput/Log/DataBkp")#"E:/Log/DataBkp"  # Backup log folder
    
    self.host     = DIR_DATA.parent/"backup" #Path("../../TestOutput/backup")#"//SIMONLABSERVER/backup"              # Bakkup server host name
    self.drive    = DIR_DATA.parent/"backup" #Path("../../TestOutput/backup")                                     # Net work drive
    self.bkpPath  = "/Rydberg Experiment Data"+self.date_dir # Backup folder on server
    
    self.folders = []
    self.fileNum = 0
    
    try:
      os.chdir(self.file_dir)
    except:
      print('Folder does not exist.')
    
  def listDir(self, complete=0):
    self.folders = []
    for dirs in os.listdir(os.getcwd()):
      if os.path.isdir(dirs):
        self.folders.append(dirs)
    return self.folders
        
  def zipData(self):
    for dirs in self.folders:
      if os.path.exists(dirs+".zip"):
        os.remove(dirs+".zip")
      dirsplit = os.path.split(dirs)
      if dirsplit[0] != '':
        fname = dirsplit[-1]
        subdirs = dirsplit[:-1]
        dirname = os.path.join(*subdirs)
        os.chdir(dirname)
      else:
        fname = dirs
      zf = zipfile.ZipFile(fname+".zip", "w", compression=zipfile.ZIP_DEFLATED)
      for root, dirs, files in os.walk(fname):
        for file in files:
          zf.write(os.path.join(root, file))
          self.fileNum += 1
      zf.close()
    return self.fileNum
      
  def netDriveMap(self):
    drive = self.drive
    networkPath = self.host
    if (os.path,exists(drive)):
      win32wnet.WNetCancelConnection2(drive, 1, 1)
      
    try:
      win32wnet.WNetAddConnection2(win32netcon.RESOURCETYPE_DISK, drive, networkPath, None)
    except:
      print("Failed to map the network disk!")
  
  def CopyFile(self):
    fullBKPPath = self.drive / self.bkpPath
    print(fullBKPPath)
    try:
      if not os.path.exists(fullBKPPath):
        os.makedirs(fullBKPPath)
      for cfile in glob.glob("*.zip"):
        shutil.copy2(cfile, fullBKPPath)
      return 1
    except:
      return 0

  def clearZip(self):
    for cfile in glob.glob("*.zip"):
      os.remove(cfile)

  def bkpLog(self):
    sep = "=========================================================\n"
    log = ""
    log += "Backup Date: " + self.date.strftime("%Y-%m-%d") + "\n"
    log += sep
    log += "Folders Backuped: \n"
    for dirs in self.folders:
      log += self.home_dir / dirs + "\n"
    log += sep
    log += "Number of Files Backuped: " + str(self.fileNum) + "\n"
    
    full_log_dir = self.log_dir / self.date.strftime("%Y-%m-%d")+".log"
    if not os.path.exists(self.log_dir):
      os.makedirs(self.log_dir)

    f = open(full_log_dir, "w")
    f.write(log)
    f.close()
    