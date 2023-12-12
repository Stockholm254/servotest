import numpy as np
from PIL import Image
import os, sys, time
#from .gw_com import com
from .gw_lan import lan
from . import dso2ke
import matplotlib.pyplot as plt

def checkInterface(str):
    if str!= '':
        print(str)
    #Load config file if it exists
    elif os.path.exists('port.config'):
        f = open('port.config', 'r')
        while(1):
            str = f.readline()
            if(str == ''):
                f.close()
                return ''
            if(str[0] != '#'):
                break
        f.close()
       
    #Check ethernet connection(model name not checked)
    sInterface=str.split('\n')[0]
    #print 'sInterface=',sInterface
    if(sInterface.count('.') == 3 and sInterface.count(':') == 1): #Got ip address.
        ip_str=sInterface.split(':')
        ip=ip_str[0].split('.')
        if(ip_str[1].isdigit() and ip[0].isdigit() and ip[1].isdigit() and ip[2].isdigit() and ip[3].isdigit()):
            #print('ip addr=%s.%s.%s.%s:%s'%(ip[0],ip[1],ip[2],ip[3],ip_str[1]))
            str=lan.connection_test(sInterface)
            if(str != ''):
                return str
    # serial disabled for now...
    # #Check COM port connection(model name not checked)
    # elif('COM' in sInterface):
    #     if(com.connection_test(sInterface) != ''):
    #         return sInterface
    # elif('ttyACM' in sInterface):
    #     if 'ttyACM' == sInterface[0:6]:
    #         sInterface='/dev/'+sInterface
    #     if(com.connection_test(sInterface) != ''):
    #         return sInterface
    
    # return com.scanComPort()  #Scan all the USB port.

class ADCdso:
    def __init__(self, address) -> None:
        port=checkInterface(address)
        self.dso = dso2ke.Dso(port)
        
    def convert_volts(self, ch):
        # convert raw data to volts
        dv=self.dso.vdiv[ch]/25
        return  np.array(self.dso.iWave[ch])*dv

    def get_data(self, getCH1 = True, getCH2 = False):
        #clear the data
        self.dso.iWave=[[], [], [], []]
        self.dso.ch_list=[]

        #Get raw data.
        #Turn on the selected channels.
        if(getCH1 and (self.dso.isChannelOn(1)==False)):
            self.dso.write(":CHAN1:DISP ON\n")           #Set CH1 on.
        if(getCH2 and (self.dso.isChannelOn(2)==False)):
            self.dso.write(":CHAN2:DISP ON\n")           #Set CH2 on.
        
        #Get all the selected channel's raw datas.
        if getCH1:
            self.dso.getRawData(True, 1)              #Read CH1's raw data from DSO (including header).
        if getCH2:
            self.dso.getRawData(True, 2)              #Read CH2's raw data from DSO (including header).
        
        num=self.dso.points_num

        if getCH1 and getCH2:
            data = np.stack([self.convert_volts(0), self.convert_volts(1)], axis=1)
        else:
            data = self.convert_volts(0)
 
        dt      = self.dso.dt[0] #Get dt from the first opened channel.
        t_start = self.dso.hpos[0]-num*dt/2
        t_end   = self.dso.hpos[0]+num*dt/2

        meta = {'ti': t_start, 'tf': t_end, 'dt': dt, 'num': num}
        return data, meta


    def plot_data(self, data, meta):
        dt=meta['dt']
        t_start=meta['ti']
        t_end  =meta['tf']
        num = meta['num']
        t = np.arange(t_start, t_end, dt)
        if((len(t)-num)==1): #Avoid floating point rounding error.
            t=t[:-1]


        plt.figure()
        plt.plot(t, data)
        plt.xlabel('t [s]')
        plt.ylabel('V [V]')
        plt.show()




if __name__=='__main__':
    dso = ADCdso(address='192.168.1.99:3000')
    data, meta = dso.get_data(getCH1=True, getCH2=True)
    dso.plot_data(data, meta)



