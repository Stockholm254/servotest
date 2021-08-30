# Intervaler class
# Helps automate the definition of time intervals in sequences

class TimeInterval:
  def __init__(self,start,stop,name=None):
    if (start > stop):
      raise ValueError('Start time must be less than stop time')
    self._start = start
    self._stop = stop
    self._name = name
  
  def getName(self):
    return self._name
  def setName(self,name):
    self._name = name
    
  def start_t(self):
    return self._start
  
  def end_t(self):
    return self._stop
   
  def length(self):
    return self._stop - self._start
  
  def join(self,int2):
    #joins two time intervals
    #forms a new interval from the start of the first to the end of the last
    allvals = [self[0],self[1],int2[0],int2[1]]
    return TimeInterval(min(allvals), max(allvals))
  
  def __and__(self,int2):
    #defines the & operator
    return self.join(int2)
    
  def afterward(self, length):
    return TimeInterval(self._stop, self._stop+length)
  def afterStart(self, length):
    return TimeInterval(self._start, self._start+length)
  def beforeEnd(self,length):
    return TimeInterval(self._stop - length, self._stop)
  def beforeStart(self, length):
    return TimeInterval(self._start - length, self._start)
  
  def __getitem__(self,index):
    if index == 0:
      return self._start
    elif index == 1:
      return self._stop
    else:
      raise IndexError('Interval index must be 0 or 1')
  
  def __repr__(self):
    return (self._name or "Interval")+'('+str(self._start) + ', '+str(self._stop)+')'
  
  def __bool__(self):
    return self.length() > 0
  
  def __len__(self):
    return self.length()
  
class Intervaler:
  def __init__(self,startTime = 0):
    self._intervals = []
    self._prevStop = startTime
  
  def append(self,length,name=None):
    if (length < 0):
      raise ValueError('Interval length must be non-negative')
    if (type(length) is complex):
      raise ValueError('Interval length must be real')
      
    newInterval = TimeInterval(self._prevStop,self._prevStop+length,name)
    self._intervals.append(newInterval)
    self._prevStop += length
    return newInterval
    
  def appendMod(self, stamp, mod_num, name=None):
    stamp_period = stamp[-1][2] - stamp[0][0]
    length = stamp_period*mod_num
    newInterval = TimeInterval(self._prevStop, self._prevStop+length, name)
    self._intervals.append(newInterval)
    self._prevStop += length
    return newInterval
  
  def __getitem__(self,index):
    return self._intervals[index]
    
  def __len__(self):
    return len(self._intervals)