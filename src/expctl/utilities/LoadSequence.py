#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

#######################
#      UTILITIES      #
#######################
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

#######################
#    MetaVariables    #
#######################
class MetaVariable: 
  def __init__(self, name, tabname=None, value=0, type=1, min=0, max=1, inc=.1, digits=2):
    self.name = name
    self.tabname = tabname
    
    if is_number(value):
      self.value = float(value)
    else:
      self.value = 0.0
    
    self.label    = None # GUI object for name
    self.textCtrl = None # GUI object for value
    
    self.type     = type # MV type
    if type == 2:
      if is_number(min):
        self.min = float(min)
      else:
        self.min = 0.0
      if is_number(max):
        self.max = float(max)
      else:
        self.max = 1.0
      if is_number(inc):
        self.inc = float(inc)
      else:
        self.inc = 0.1
      if is_int(digits):
        self.digits = int(digits)
      else:
        self.digits = 2
    else:
      self.min=None
      self.max=None
      self.inc=None
      self.digits=None







def seq_parser(contents):
    newTabs = "Others"

    preamble   = ""
    staticcode = ""
    mv = []
    
    # Begin parse the sequence line by line
    state = 0
    for line in contents: # First line of comments is for free
      if state == 0:
        if (len(line)>2) and (line[0]=='#') and (line[1]=='#'):  # Second line of comments indicates we're inputting with modifiable variables
          state = 1
          continue
        preamble += line
       
      if state == 1: # Load MVs
        if (len(line)>2) and (line[0]=='#') and (line[1]=='#'):  # Second line of comments indicates we're inputting with modifiable variables
          state = 2
          continue
          
        # Check if line is of form: Tab:[Tab_Name]
        m = re.search("Tab:"+"(\w+)\s*", line.strip())
        if m != None:
          newTabs = m.group(1).strip()
          
        # Check if line is of form: variable = value
        m = re.match('(\w+)\s*=\s*([-]?[\w\.]*)', line.strip())
        if m != None:
          if m.group(1) != 'j': # j is not a permitted variable name!!!
            mv.append(MetaVariable(m.group(1).strip(), newTabs, m.group(2).strip()))
        
        # Check if line is of type=2, a float spin thingy
        m = re.match('MV\(\s*(.+)\s*,\s*min=(.*)\s*,\s*max=(.*)\s*,\s*init=(.*)\s*,\s*inc=(.*)\s*,\s*digits=(.*)\s*\)', line.strip())
        if m != None:
          if m.group(1) != 'j': # j is not a permitted variable name!!!
            mv.append(MetaVariable(m.group(1).strip(), newTabs, m.group(4).strip(), type=2, min=m.group(2), max=m.group(3), inc=m.group(5), digits=m.group(6)))
          
      if state == 2: # Load non-MV sequence code
        staticcode += line
        continue
    
    return preamble, mv, staticcode
