# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 14:28:00 2013

@author: Ariel
The CavityModes class provides the resonant frequencies,
linewidths, and mode profiles of a cavity.
* Note that the above is not true - this class has nothing to 
do with the resonant frequencies or linewidths of a cavity.

"""
#import numpy.polynomial.hermite as herm
from scipy.special import factorial
import numpy as np
from scipy.integrate import dblquad
from pathlib import Path
import re
pi = np.pi
Inf = np.Inf

def hermitePoly(n,x):
    #c = np.zeros(n+1)
    #c[n]=1
    #return herm.hermval(x,c)
    if (n==0):
        return 1
    if (n==1):
        return 2*x
    if (n==2):
        return 4*x**2 -2 
    if (n==3):
        return 8*x**3-12*x
    else:
        print("Un-implemented Hermite polynomial")

def circPoly(nR,nL,x):
    n = nR+nL
    m = nR-nL
    if (abs(m)>n):
        print("Illegal index for circular polynomial, abs(m)>n")
        return None
    if ((n-m) % 2 != 0):
        print("Illegal index for circular polynomial, odd difference n-m")
        return None
    if (n==0):
        return 1
    elif (n==1):
        return x
    elif (n==2 and abs(m)==2):
        return x**2
    elif (n==2 and m==0):
        return x**2 - 1
    
        
        
ONE_D_X = 0
TWO_D = 1
RUNNING = 2

class AbstractMode(object):
    def __init__(self,freq,linewidth,direction=1,offset=(0,0)):
        self.freq=freq
        self.linewidth=linewidth
        self.direction = direction #for running wave modes
        if offset:
            self.offset = offset
        else:
            self.offset = (0,0)
    
    def getComplexFreq(self):
        return self.freq - 1j * self.linewidth/2
        
    def evalPoly(self,coefs,x):
        f=0
        for m in range(len(coefs)):
            f += coefs[m] * x**m
        return f
    
    def findOverlap(self,mode):
        #x0=0;y0=0
        #if offset:
        #    x0=offset[0];y0=offset[1]
            
        f = lambda x,y: self.modeProfWithOffset([x,y])*np.conj(mode.modeProfWithOffset([x,y]))
        fr = lambda x,y: np.real(f(x,y))
        fi = lambda x,y: np.imag(f(x,y))
        lim1 = lambda x: -Inf
        lim2 = lambda x: Inf
        epsabs = 1e-2; epsrel=1e-2
        ir, irerr = dblquad(fr,-Inf,Inf,lim1,lim2,(),epsabs,epsrel)
        ii, iierr = dblquad(fi,-Inf,Inf,lim1,lim2,(),epsabs,epsrel)
        return ir + 1j*ii

    def modeProfWithOffset(self,pos):
        shifted = [pos[0]-self.offset[0], pos[1]-self.offset[1]]
        return self.modeProfile(shifted)
        
    def modeProfile(self,pos):
        print("Abstract base class method modeProfile implemented")
        return None
    
    def getDirection(self):
        return self.direction
   

class NPCcache:
    def __init__(self):
        DIR = Path(__file__).resolve().parent/"UpperModeProfiles/"
        print(f"UpperModeProfiles dir is {DIR}")
        self.cache = {}
        
        for f in DIR.glob('*.txt'):
            m = re.match("mode_(\d+),(\d+).txt", f.name)
            i, j = m.groups()
            i = int(i)
            j = int(j)
            self.cache[(i, j)] = np.loadtxt(f, converters={2: self.coef_fixer}, dtype=complex)
            print(f"caching mode {f}")
    
    def coef_fixer(self, instring):
        # for "fixing" the txt files produced by mathematica, to put them in a format that can be easily loaded by numpy
        return np.complex(instring.decode("utf-8").replace("*I", "j").replace("*^", "e"))

    def get(self, n1, n2):
        n1 = int(n1)
        n2 = int(n2)
        return self.cache[(n1, n2)]

npc_cache = NPCcache()

class NPCMode(AbstractMode):
    """
    Modes of the experimental non-planar cavity (NPC) in which we will first make Laughlin states
    RELIES ON "UpperModeProfiles" from Mathematica to be already normalized
    """
    def __init__(self, waists, n1, n2, rotate, offset=(0,0), defocus=0, tilt=(0,0), intensity=1):
        super(NPCMode, self).__init__(0, 0, 0, offset)
        self.waists = waists
        self.n1 = int(n1)
        self.n2 = int(n2)
        self.rotate = rotate  # angle, for rotating the principal mode axes, in degrees
        self.offset = offset
        self.defocus = defocus
        self.tilt = tilt
        #DIR = Path(__file__).resolve().parent/"UpperModeProfiles/"
        #print(f"UpperModeProfiles dir is {DIR}")
        #self.coefpath = DIR#"./UpperModeProfiles/"
        self.intensity = intensity
        
        if defocus:
          #self.defocFac = 1.j*np.pi/(self.wavelength*self.defocus*(1+(self.Zr/self.defocus)**2))
          self.defocFac = 1.j*np.pi*defocus
        else:
          self.defocFac = 0

        #self.gauss_coefs = np.loadtxt(self.coefpath/"mode_0,0.txt", converters={2: self.coef_fixer}, dtype=complex)
        #self.poly_coefs = np.loadtxt(self.coefpath/f"mode_{str(n1)},{str(n2)}.txt", converters={2: self.coef_fixer}, dtype=complex)
        self.gauss_coefs = npc_cache.get(0,0)
        self.poly_coefs = npc_cache.get(n1,n2)
        # print self.gauss_coefs
        # print self.poly_coefs

    def coef_fixer(self, instring):
        # for "fixing" the txt files produced by mathematica, to put them in a format that can be easily loaded by numpy
        return np.complex(instring.decode("utf-8").replace("*I", "j").replace("*^", "e"))

    def modeProfile(self, pos):
        # NOT SURE ABOUT THE UNITS LOADED FROM MATHEMATICA - MAY WANT ANOTHER SCALE FACTOR HERE
#        print("WARNING: Need scale factor?")
        # The typical mode functions in this code are deifned on spaces with units sqrt(2)*DMD pixels
        # since the coordinate space on which the modes were defined in mathematica used microns,
        # I will add a conversion factor here
        mirror_size = 1  # microns??? at any rate, this is the 
                            # scale factor required to make 
                            
        # COORDINATES OF THE MODE; these will be rotated and scaled as the mode gets rotated and scaled
        x = mirror_size / self.waists[0] * (np.cos(np.deg2rad(self.rotate))*pos[0]+np.sin(np.deg2rad(self.rotate))*pos[1])
        y = mirror_size / self.waists[1] * (-np.sin(np.deg2rad(self.rotate))*pos[0]+np.cos(np.deg2rad(self.rotate))*pos[1])
        # COORDINATES OF THE DMD; these are fixed to the DMD plane (useful for things like "tilt" corrections, which should be independent of the mode shape corrections)
        xDMD = pos[0]
        yDMD = pos[1]
        
        # Start with the "gaussian"
        # print((self.gauss_coefs))
        exp_arg = x*np.complex(0)
        for i in range(self.gauss_coefs.shape[0]):
            exp_arg += self.gauss_coefs[i, 2]*(x**self.gauss_coefs[i, 0])*(y**self.gauss_coefs[i,1])
        mode = np.exp(exp_arg)

        # Account for polynomial coefficients (for all modes beyond 0,0)
        # if self.n1 > 0 or self.n2 > 0:
        #     print self.poly_coefs.shape[0]
        #     print self.poly_coefs.shape[1]
        if self.n1 > 0 or self.n2 > 0:
            poly = x*np.complex(0) # initialize
            for i in range(self.poly_coefs.shape[0]):
                if self.poly_coefs[i, 2] != 0:
                    poly += 10**(-2*(self.poly_coefs[i, 0]+self.poly_coefs[i, 1]))*self.poly_coefs[i, 2]*(x**self.poly_coefs[i, 0])*(y**self.poly_coefs[i, 1])
            mode *= poly 
        
        
        # Multiply by tilt and defocusing factors
        mode *= self.intensity*np.exp(self.defocFac*(xDMD**2+yDMD**2)/10000)*np.exp(1.j*(xDMD*self.tilt[0]/10 + yDMD*self.tilt[1]/10))
        return mode




    
class LGMode(AbstractMode):
    """
    Represents a Laguerre-Gauss mode
    p - polynomial order
    l - angular momentum
    """
    def __init__(self,waist,freq,linewidth,p,l, phi, epsilon_phi, direction=1,offset=(0,0),defocus=0, tilt=(0,0)):
        super(LGMode,self).__init__(freq,linewidth,direction,offset)
        self.waist = 1.0*waist
        #self.defocus = 1.0*defocus
        #self.wavelength = (0.780)*(1/10.8) #wavelength in um converted to pixel number
        #self.Zr = np.pi*self.waist**2/(self.wavelength) #convert Zr from um to funny units used
        #self.freq = freq
        #self.linewidth = linewidth
        self.p=p
        self.l=l
        self.coefs = [] #Laguerre polynomial coefficients
        for m in range(p+1):
            self.coefs.append(self.LGcoef(l,p,m))
        k=abs(l)
        self.preFactor = 1.0/waist*np.sqrt(2/pi*factorial(p)/factorial(p+k))
        if defocus:
          #self.defocFac = 1.j*np.pi/(self.wavelength*self.defocus*(1+(self.Zr/self.defocus)**2))
          self.defocFac = 1.j*np.pi*defocus
        else:
          self.defocFac = 0
        
        self.phi = phi
        self.epsilon_phi = epsilon_phi
        self.tilt=tilt
        
        
    def LGcoef(self,l,p,m):
        """
        Returns the coefficient of the m-th orer term of the Assoc. Laguerre 
        polynomial of upper index abs(l) and order p
        """
        k=abs(l)
        num = (-1)**m * factorial(p+k)
        den = factorial(p-m)*factorial(k+m)*factorial(m)
        return num/den
        
    def evalLaguerre(self,x):
        f =0
        for m in range(len(self.coefs)):
            f += self.coefs[m] * x**m
        return f
        
    def modeProfile(self,pos):
        x = np.sqrt(2)/self.waist * np.sqrt(1. - 1.j*self.phi*(1+self.epsilon_phi)) * pos[0] #dimensionless coordinates
        y = np.sqrt(2)/self.waist * np.sqrt(1. - 1.j*self.phi*(1-self.epsilon_phi)) * pos[1]
        z = x + 1j*y
        R2 = abs(z)**2
        xd = np.sqrt(2)/self.waist * np.sqrt(1. - 1.j*self.phi*(1+self.epsilon_phi)) * (pos[0] + self.offset[0]) #dimensionless coordinates
        yd = np.sqrt(2)/self.waist * np.sqrt(1. - 1.j*self.phi*(1-self.epsilon_phi)) * (pos[1] + self.offset[1])
        R2def = xd**2 + yd**2
        zl = z**abs(self.l)
        if (self.l<0):
            zl = np.conj(zl)
        laguerre = self.evalPoly(self.coefs,R2)#self.evalLaguerre(R2)
##        print laguerre
        return self.preFactor * zl * np.exp(-0.5*R2) * laguerre * np.exp(self.defocFac*R2def) * np.exp(1.j*(x*self.tilt[0] + y*self.tilt[1]))
     

class CircMode(LGMode):
    def __init__(self,waist,freq,linewidth,nR,nL,direction=1,offset=(0,0)):
        p = min(nR,nL)
        l = nR - nL
        #For python 2.7:
        #super(LGMode,self).__init__(waist,freq,linewidth,p,l)
        super(CircMode,self).__init__(waist,freq,linewidth,p,l,direction,offset)
        
class HGMode(AbstractMode):
    def __init__(self,waistX,waistY,freq,linewidth,nx,ny, phi, epsilon_phi, direction=1,offset=(0,0)):
        super(HGMode,self).__init__(freq,linewidth,direction,offset)
        self.waistX=waistX
        self.waistY=waistY
        self.hcoefsX = []
        self.hcoefsY = []
        for k in range(nx+1):
            self.hcoefsX.append(self.hcoef(nx,k))
        for k in range(ny+1):
            self.hcoefsY.append(self.hcoef(ny,k))
        self.preFactor =np.sqrt(2/(pi*waistX*waistY*2**(nx+ny)*factorial(nx)*factorial(ny)))

        self.phi = phi
        self.epsilon_phi = epsilon_phi
        
    def hcoef(self,n,k):
        #Recursively finds the k-th coefficient of H_n
        if (n%2 != k%2 or k > n):
            return 0
        if (n==0 and k==0):
            return 1
        elif (n==1 and k==1):
            return 2
        elif (k>0):
            return 2*self.hcoef(n-1,k-1)-2*(n-1)*self.hcoef(n-2,k)
        elif (k==0):
            return -2*(n-1)*self.hcoef(n-2,0)
        print("Error in hcoef: how did I get here?")

##    def modeProfile(self,pos):
##        x = np.sqrt(2)/self.waistX * pos[0] #dimensionless coordinates
##        y = np.sqrt(2)/self.waistY * pos[1]
##        R2 = x**2 + y**2
##        hx = self.evalPoly(self.hcoefsX,x)
##        hy = self.evalPoly(self.hcoefsY,y)
##        return self.preFactor*np.exp(-0.5*R2)*hx*hy

    def modeProfile(self,pos):
        x = np.sqrt(2)/self.waistX * np.sqrt(1. - 1.j*self.phi*(1+self.epsilon_phi)) * pos[0] #dimensionless coordinates
        y = np.sqrt(2)/self.waistY * np.sqrt(1. - 1.j*self.phi*(1-self.epsilon_phi)) * pos[1]
        R2 = x**2 + y**2
        hx = self.evalPoly(self.hcoefsX,x)
        hy = self.evalPoly(self.hcoefsY,y)
        return self.preFactor*np.exp(-0.5*R2)*hx*hy

        
class CavityModes2:
    def __init__(self,params):
        self.waistX = params.waistX
        self.waistY = params.waistY
        self.Nmodes = params.Nmodes
        self.modeSpacing = params.modeSpacing
        self.offsetFreq = params.omega_C
        self.modes = []
        self.linewidth = params.kappa
        if (params.CavityType == "LowestLandauLevel"):
            self.addLandauLevel(self.Nmodes,0,1)
            self.backscattering = False
        elif (params.CavityType == "LowestLandauLevel2"):
            self.addLandauLevel(self.Nmodes,0,1,1,2)
            self.backscattering = False
        elif (params.CavityType == "LowestLandauLevel3"):
            self.addLandauLevel(self.Nmodes,0,1,1,3)
            self.backscattering = False
        elif (params.CavityType == "LandauLevelBack"):
            self.addLandauLevelBack(self.Nmodes,0,1,1)
            self.backscattering = True
        elif (params.CavityType == "LinX"):
            self.addHermiteX(self.Nmodes)
            self.backscattering = False
        elif (params.CavityType == "LinXBack"):
            self.addHermiteXBack(self.Nmodes)
            self.backscattering = True
        else:
            print("Mode structure not defined")
            
    def addMode(self,mode):
        self.modes.append(mode)
        
    def addHermiteX(self,Nmodes,direction=1):
        for n in range(Nmodes):
            f=self.offsetFreq+n*self.modeSpacing
            self.addMode(HGMode(self.waistX,self.waistY,f,self.linewidth,n,0,direction))
    def addHermiteXBack(self,Nmodes,direction=1):
        if (Nmodes % 2 == 1):
            print("Need an even number of modes for back-scattering")
            return
        Nhalf = int(Nmodes/2)
        self.addHermiteX(Nhalf,direction)
        self.addHermiteX(Nhalf,-direction)
        
    def addLandauLevel(self,Nmodes,landauInd=0,sgn=1,direction=1,step=1):
        if (sgn != 1 and sgn !=-1):#check sign of angular momentum
            print("Expected sgn=1 or -1")
            return
        waist = np.sqrt(self.waistX*self.waistY)
        for i in range(Nmodes):
            nR = i*step if sgn==1 else landauInd
            nL = landauInd if sgn==1 else i*step
            f=self.offsetFreq+i*self.modeSpacing
            self.addMode(CircMode(waist,f,self.linewidth,nR,nL,direction))
    
    def addLandauLevelBack(self,Nmodes,landauInd=0,sgn=1,direction=1):
        if (Nmodes % 2 == 1):
            print("Need an even number of modes for back-scattering")
            return
        Nhalf = int(Nmodes/2)
        self.addLandauLevel(Nhalf,landauInd,sgn,direction)
        self.addLandauLevel(Nhalf,landauInd,-sgn,-direction)
    
    def getNModes(self):
        return len(self.modes)
    def modeprofile(self,ind,pos):
        return self.modes[ind].modeProfile(pos) 
    def modeFreq(self,ind):
        return self.modes[ind].getComplexFreq()
    def modeDirection(self,ind):
        return self.modes[ind].getDirection()

""" 
    
class CavityModes:
    def __init__(self, params,config):#modeIndices=[],modeFreqs=[]):
        self.waistX = params.waistX
        self.waistY = params.waistY
        self.Nmodes = params.Nmodes
        offsetFreq = params.omega_C
        
        if (config == ONE_D_X):
            self.makeONE_D_X(offsetFreq,params.modeSpacing,params.kappa)
            self.isTEM = True
        elif (config == TWO_D):
            self.makeTWO_D(offsetFreq,params.modeSpacing,params.kappa)
            self.isTEM = True
        else:
            print("Unknown cavity configuration")
    
    def makeONE_D_X(self,offsetFreq,modeSpacing,linewidth):
        #defines the mode frequencies and indices for a 1D manifold
        modeIndices=[]
        modeFreqs=[]
        for m in range(self.Nmodes):
            modeIndices.append([2*m,0])
            modeFreqs.append(offsetFreq+np.sum(modeIndices[m])*modeSpacing - 1j*linewidth/2)
        self.modeIndices = modeIndices
        self.modeFreqs = modeFreqs
    
    def makeTWO_D(self,offsetFreq,modeSpacing,linewidth):
        #need to deal with Nmodes in 2D
        #TO BE FINISHED LATER!!!
        modeIndices=[]
        modeFreqs=[]
        self.modeIndices = modeIndices
        self.modeFreqs = modeFreqs
        print("ERROR:not implemented")

        
    def _getTEMindices(self,ind):
        return self.modeIndices[ind]
    
    def modeprofile(self,ind,pos):
        #assumes Hermite Gauss modes
        wx=self.waistX;wy=self.waistY
        x=pos[0];y=pos[1]
        [mx,my]=self._getTEMindices(ind)#look up indices
        Ax = (2/pi)**(1/4)/np.sqrt(2**mx*factorial(mx)*wx)
        Ay = (2/pi)**(1/4)/np.sqrt(2**my*factorial(my)*wy)
        hx = hermitePoly(mx,np.sqrt(2)*x/wx)
        hy = hermitePoly(my,np.sqrt(2)*y/wy)
        return Ax*Ay*hx*hy*np.exp(- ((x/wx)**2+(y/wy)**2) )
    
    def modeFreq(self,ind):
        return self.modeFreqs[ind]
"""
