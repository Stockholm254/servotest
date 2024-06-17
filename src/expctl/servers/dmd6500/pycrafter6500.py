import usb.core
import usb.util
import time
import numpy
import sys
from .erle import encode


##function that converts a number into a bit string of given length

def convlen(a,l):
    b=bin(a)[2:]
    padding=l-len(b)
    b='0'*padding+b

    return b

##function that converts a bit string into a given number of bytes

def bitstobytes(a):
    bytelist=[]
    if len(a)%8!=0:
        padding=8-len(a)%8
        a='0'*padding+a
    for i in range(len(a)//8):
        bytelist.append(int(a[8*i:8*(i+1)],2))

    bytelist.reverse()

    return bytelist

##a dmd controller class

class dmd():
    def __init__(self):
        self.dev=usb.core.find(idVendor=0x0451 ,idProduct=0xc900 )

        self.dev.set_configuration()

        self.ans=[]

## standard usb command function

    def command(self,mode,sequencebyte,com1,com2,data=None,get_answer=True):
        buffer = []

        flagstring=''
        # if mode=='r':
        #     flagstring+='1'
        # else:
        #     flagstring+='0'        
        # flagstring+='1000000'
        if mode=='r':
            flagstring+='11'
        else:
            if get_answer:
                flagstring+='01'   
            else:
                flagstring+='00' # don't request reply with reply bit (#7) ---- I think the reply bit is bit #6 (but counting from bit #0) 
        flagstring+='000000'
        #print('flagstring :', flagstring, bin(bitstobytes(flagstring)[0]))
        buffer.append(bitstobytes(flagstring)[0])
        buffer.append(sequencebyte)
        temp=bitstobytes(convlen(len(data)+2,16))
        buffer.append(temp[0])
        buffer.append(temp[1])
        buffer.append(com2)
        buffer.append(com1)

        if len(buffer)+len(data)<65:
        
            for i in range(len(data)):
                buffer.append(data[i])

            for i in range(64-len(buffer)):
                buffer.append(0x00)


            self.dev.write(1, buffer)

        else:
            for i in range(64-len(buffer)):
                buffer.append(data[i])

            self.dev.write(1, buffer)

            buffer = []

            j=0
            while j<len(data)-58:
                buffer.append(data[j+58])
                j=j+1
                if j%64==0:
                    self.dev.write(1, buffer)

                    buffer = []

            if j%64!=0:

                while j%64!=0:
                    buffer.append(0x00)
                    j=j+1


                self.dev.write(1, buffer)

        if get_answer:
            self.ans=self.dev.read(0x81,64)
            # self.ans=self.dev.read(0x01,64)
            

## functions for checking error reports in the dlp answer

    def checkforerrors(self):
        self.command('r',0x22,0x01,0x00,[])
        if self.ans[6]!=0:
            print (self.ans[6])    

## function printing all of the dlp answer

    def readreply(self):
        for i in self.ans:
            print (hex(i))

## functions for idle mode activation

    def idle_on(self):
        self.command('w',0x00,0x02,0x01,[int('00000001',2)])
        self.checkforerrors()

    def idle_off(self):
        self.command('w',0x00,0x02,0x01,[int('00000000',2)])
        self.checkforerrors()

## functions for power management

    def standby(self):
        self.command('w',0x00,0x02,0x00,[int('00000001',2)])
        self.checkforerrors()

    def wakeup(self):
        self.command('w',0x00,0x02,0x00,[int('00000000',2)])
        self.checkforerrors()

    def reset(self):
        self.command('w',0x00,0x02,0x00,[int('00000010',2)])
        self.checkforerrors()

## test write and read operations, as reported in the dlpc900 programmer's guide

    def testread(self):
        self.command('r',0xff,0x11,0x00,[])
        self.readreply()

    def testwrite(self):
        self.command('w',0x22,0x11,0x00,[0xff,0x01,0xff,0x01,0xff,0x01])
        self.checkforerrors()

## some self explaining functions

    def changemode(self,mode):
        self.command('w',0x00,0x1a,0x1b,[mode])
        self.checkforerrors()

    def startsequence(self):
        self.command('w',0x00,0x1a,0x24,[2])
        self.checkforerrors()

    def pausesequence(self):
        self.command('w',0x00,0x1a,0x24,[1])
        self.checkforerrors()

    def stopsequence(self):
        self.command('w',0x00,0x1a,0x24,[0])
        self.checkforerrors()


    def configurelut(self,imgnum,repeatnum):
        img=convlen(imgnum,11)
        repeat=convlen(repeatnum,32)

        string=repeat+'00000'+img

        bytes=bitstobytes(string)

        self.command('w',0x00,0x1a,0x31,bytes)
        self.checkforerrors()
        

    def definepattern(self,index,exposure,bitdepth,color,triggerin,darktime,triggerout,patind,bitpos):
        payload=[]
        index=convlen(index,16)
        index=bitstobytes(index)
        for i in range(len(index)):
            payload.append(index[i])

        exposure=convlen(exposure,24)
        exposure=bitstobytes(exposure)
        for i in range(len(exposure)):
            payload.append(exposure[i])
        optionsbyte=''
        optionsbyte+='1'
        bitdepth=convlen(bitdepth-1,3)
        optionsbyte=bitdepth+optionsbyte
        optionsbyte=color+optionsbyte
        if triggerin:
            optionsbyte='1'+optionsbyte
        else:
            optionsbyte='0'+optionsbyte

        payload.append(bitstobytes(optionsbyte)[0])

        darktime=convlen(darktime,24)
        darktime=bitstobytes(darktime)
        for i in range(len(darktime)):
            payload.append(darktime[i])

        triggerout=convlen(triggerout,8)
        triggerout=bitstobytes(triggerout)
        payload.append(triggerout[0])

        patind=convlen(patind,11)
        bitpos=convlen(bitpos,5)
        lastbits=bitpos+patind
        lastbits=bitstobytes(lastbits)
        for i in range(len(lastbits)):
            payload.append(lastbits[i])



        self.command('w',0x00,0x1a,0x34,payload)
        self.checkforerrors()
        


    def setbmp(self,index,size):
        payload=[]

        index=convlen(index,5)
        index='0'*11+index
        index=bitstobytes(index)
        for i in range(len(index)):
            payload.append(index[i]) 


        total=convlen(size,32)
        total=bitstobytes(total)
        for i in range(len(total)):
            payload.append(total[i])         
        
        self.command('w',0x00,0x1a,0x2a,payload)
        self.checkforerrors()

## bmp loading function, divided in 56 bytes packages
## max  hid package size=64, flag bytes=4, usb command bytes=2
## size of package description bytes=2. 64-4-2-2=56

    def bmpload(self,image,size):

        packnum=size//504+1

        counter=0

        for i in range(packnum):
            if i %100==0:
                print (i,packnum)
            payload=[]
            if i<packnum-1:
                leng=convlen(504,16)
                bits=504
            else:
                leng=convlen(size%504,16)
                bits=size%504
            #print(size, bits, leng, bitstobytes(leng))
            leng=bitstobytes(leng)
            for j in range(2):
                payload.append(leng[j])
            for j in range(bits):
                payload.append(image[counter])
                counter+=1
            self.command('w',0x11,0x1a,0x2b,payload,get_answer=False)


        # try sending the image as only a few big packages
        # according to the documentation https://www.ti.com/lit/ug/dlpu018i/dlpu018i.pdf?ts=1702915572931&ref_url=https%253A%252F%252Fwww.google.com%252F
        # you can send a big package by sending the header only once and
        # followed by only data packages
        # maximum size for length header is 16 bit so slice into 2^16 bit packages
        # consecotive bytes have no header and USB command

        # max  hid package size=64, flag bytes=4, usb command bytes=2
        # size of package description bytes=2 
        # first transfer 64-4-2-2=56 bytes
            #self.checkforerrors()
        self.checkforerrors()


    def defsequence(self,images,exp,ti,dt,to,rep):

        self.stopsequence()

        arr=[]

        for i in images:
            arr.append(i)

##        arr.append(numpy.ones((1080,1920),dtype='uint8'))

        num=len(arr)

        encodedimages=[]
        sizes=[]
        t0 = time.perf_counter()
        for i in range((num-1)//24+1):
            print (f'merging i={i}')
            if i<((num-1)//24):
                imagedata=arr[i*24:(i+1)*24]
            else:
                imagedata=arr[i*24:]
            print ('encoding...')
            imagedata,size=encode(imagedata)
            t1 = time.perf_counter()
            print (f'encoding took {t1-t0} s')
            encodedimages.append(imagedata)
            sizes.append(size)
            print ('definepattern...')
            if i<((num-1)//24):
                for j in range(i*24,(i+1)*24):
                    print(f"definepattern j={j}, {i}, ti={ti[j]}, dt={dt[j]}, to={to[j]}, idx={j-i*24}")
                    self.definepattern(j,exp[j],1,'111',ti[j],dt[j],to[j],i,j-i*24)
            else:
                for j in range(i*24,num):
                    print(f"definepattern j={j}, {i}, ti={ti[j]}, dt={dt[j]}, to={to[j]}, idx={j-i*24}")
                    self.definepattern(j,exp[j],1,'111',ti[j],dt[j],to[j],i,j-i*24)
        t2 = time.perf_counter()
        print (f'definepattern took {t2-t1} s')
        print ('configurelut...')
        self.configurelut(num,rep)
        t3 = time.perf_counter()
        print (f'configurelut took {t3-t2} s')

        for i in range((num-1)//24+1):
        
            self.setbmp((num-1)//24-i,sizes[(num-1)//24-i])

            print ('uploading...')
            self.bmpload(encodedimages[(num-1)//24-i],sizes[(num-1)//24-i])
            t4 = time.perf_counter()
            print (f'uploading took {t4-t3} s')
        
        print ('done...')





