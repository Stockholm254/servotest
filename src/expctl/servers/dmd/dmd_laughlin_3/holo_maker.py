# General
import numpy as np
import time
import os ####################
import pickle as pickle

# Specific
from . import CavityModes as CM

pi=np.pi
##rand.seed(time.time())

class holo_maker:
    def __init__(self,simulated,phaseMap_interpolated,amplitudeMap_interpolated,sharpness,period,angle,DMD_rows=684,DMD_cols=608):
        self.a = sharpness
        self.d = period
        self.angle_deg = angle
        
        self.DMD_rows=DMD_rows
        self.DMD_cols=DMD_cols
        self.DMD_shape=(DMD_rows,DMD_cols)
        
        xs = np.arange(DMD_cols)-DMD_cols/2
        ys = (-np.arange(DMD_rows) + DMD_rows/2) if simulated else (-np.arange(DMD_rows) + DMD_rows/2)*.5
        
        self.X, self.Y = np.meshgrid(xs,ys)
        
        self.mirrorOn = 0
        self.mirrorOff =255

        self.phaseMap_interpolated = phaseMap_interpolated*2*pi
        self.amplitudeMap_interpolated = amplitudeMap_interpolated
        self.cm = CM

        ####################################################################################################
        
##        self.targetFunction = None#np.exp(-1j * 2*np.pi * phaseMap_extrapolated)
        self.resetTargetFunction()
    
    def resetTargetFunction(self):
      self.targetFunction=np.zeros(self.DMD_shape,np.complex)
      
    def getMesh(self):
        return self.X,self.Y
    
    def addMode(self,mode,phaseOffset):
      self.targetFunction += mode.modeProfWithOffset([self.X,self.Y]) * np.exp(1j*phaseOffset) ################
##      print mode.modeProfWithOffset([self.X,self.Y])
     
    def addHG(self,waistX,waistY,nx,ny, phi, epsilon_phi, center=(0,0), phaseOffset=0):
      mode = CM.HGMode(waistX,waistY,0,0,nx,ny, phi, epsilon_phi, offset=center)
      self.addMode(mode,phaseOffset)
      
      
    def addNPC(self,waists, nx,ny, rotate, center=(0,0), phaseOffset=0, defocus=0, tilt=(0.0, 0.0), intensity = 1):
        # rotate - rotation in degrees
      mode = CM.NPCMode(waists, nx,ny, rotate, offset=center, defocus=defocus, tilt=tilt, intensity=intensity)
      self.addMode(mode,phaseOffset)
      
      
    def addLG(self,waist,n1,n2, phi, epsilon_phi, center=(0,0),phaseOffset=0,defoc=0,tlt=(0.0,0.0)):
      # if l>0:
        # n1 = p+l
        # n2 = p
      # else l<0:
        # n1 = p
        # n2 = p-l
      p = min([n1,n2])
      l = n1-n2
      
      mode = CM.LGMode(waist,0,0,p,l, phi, epsilon_phi, offset=center, defocus=defoc, tilt=tlt)
      self.addMode(mode,phaseOffset)
    
    def addCircMode(self,waist,n1,n2,center=(0,0),phaseOffset=0):
      mode = CM.CircMode(waist,0,0,n1,n2,offset=center)
      self.addMode(mode,phaseOffset)
    
    def setTargetFunction(self,targetFunction):
        if np.shape(targetFunction) != (self.DMD_shape):
            print("Wrong shape")
            return None
        self.targetFunction=targetFunction
        
    def makeHologram(self): 
        targetFunction=self.targetFunction
        targetMag = np.abs(targetFunction)
        targetPhase = np.angle(targetFunction)# in range (-pi,pi]#####################
        targetPhase +=  self.phaseMap_interpolated #### watch out for the sign (change as fit)!
        mag = targetMag * self.amplitudeMap_interpolated #############################
  
        mag -= np.min(mag)
        maxV = np.max(mag)
        if maxV != 0:
            mag /= maxV
        else:
            mag += 1
        #mag is now in range [0,1]

        angle_rad = self.angle_deg * pi/180.0
        kx = np.cos(angle_rad)*2*pi/self.d  
        ky = np.sin(angle_rad)*2*pi/self.d
        phase = np.mod(kx*self.X + ky*self.Y + targetPhase,2*pi)
        phase[phase > pi] -= 2*pi
        prob =0.5*(np.tanh(self.a*(phase+pi*mag/2))+np.tanh(self.a*(pi*mag/2-phase)))

        bimage = np.zeros((self.DMD_rows,self.DMD_cols),dtype=np.uint8)
        r = np.random.rand(self.DMD_rows,self.DMD_cols) 
        bimage = 1 - ((r>prob).astype(int))
        bimage *= self.mirrorOff
        
        return bimage
        
