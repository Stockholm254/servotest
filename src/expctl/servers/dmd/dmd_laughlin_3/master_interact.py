# General
import numpy as np
import scipy
import os
import pickle as pickle

# Specific
from . import holo_maker
from . import DMDwrapper
from . import master_helper

main_directory_path = master_helper.get_main_directory_path()
maps_directory_path = os.path.join(main_directory_path, "maps")

##############################################################################
def initHolomaker(waveperiod, verbose=False):

    MAXNUMROWS = 684
    MAXNUMCOLS = 608

    #phaseMap
    main_directory_path = master_helper.get_main_directory_path()
    maps_directory_path = os.path.join(main_directory_path, "maps")
    with open(os.path.join(maps_directory_path, "phaseMap_interpolated.txt"), 'r') as f:
        phaseMap_interpolated = pickle.load(f)
    phaseMap_interpolated = np.flipud(phaseMap_interpolated)

    #amplitudeMap
    phaseMap_interpolated = np.zeros((MAXNUMROWS,MAXNUMCOLS))+0.0
    amplitudeMap_interpolated = np.zeros((MAXNUMROWS,MAXNUMCOLS))+1.0


    #create blank
    a = 2 #sharpness
    d = waveperiod #4 carrier wave period in pixels
    angle_deg = 20.0 # carrier wave direction relative to horizontal (degrees)
    if (verbose):
        print("Initializating holomaker")
    holomaker = holo_maker.holo_maker(0, \
                                      phaseMap_interpolated, \
                                      amplitudeMap_interpolated, \
                                      sharpness=a, \
                                      period=d, \
                                      angle=angle_deg)
    return holomaker

def saveHologram(hologram, save=0):
    saveTo =  os.path.join(main_directory_path, "test")
    hologram_path = os.path.join(saveTo, "hologram"+str(save)+".bmp")
    scipy.misc.imsave(hologram_path, hologram)
    return hologram_path
    
def makeHG(waistX, waistY, nx, ny, phi, epsilon_phi, center, wp, verbose=False, save=0):
    holomaker = initHolomaker(wp, verbose)
    #add HG
    if (verbose):
        print("Adding HG")
    holomaker.addHG(waistX, waistY, nx, ny, phi, epsilon_phi, center, 0)
    if (verbose):
        print("making hologram")
    hologram = holomaker.makeHologram()

    #save
    hologram_path=saveHologram(hologram, save)
    
    #display on DMD
    DMDwrapper.display_bitmap(hologram_path,1)
    return hologram_path



def makeNPC(waists, nxs, nys, rotate, center=(0,0), defocus=0, tilt=(0.0,0.0), phaseOffset=0, save=0, wp=4, verbose=False, intensities=1):
    holomaker = initHolomaker(wp, verbose)
    if isinstance(nxs,int)&isinstance(nys,int):
        nxs = [nxs]
        nys = [nys]
    elif isinstance(nxs,int):
        nxs = [nxs]*len(nys)
    elif isinstance(nys,int):
        nys = [nys]*len(nxs)
    if isinstance(intensities,int):
        intensities = [intensities]*len(nys)
    
    # make the single NPC mode
    for ii in range(len(nxs)):
        nx = nxs[ii]
        ny = nys[ii]
        intensity = intensities[ii]
        print((nx,ny))
        holomaker.addNPC(waists, nx, ny, rotate, center=center, defocus=defocus, tilt=tilt, phaseOffset=phaseOffset, intensity=intensity)
    hologram = holomaker.makeHologram()
    
    # save
    hologram_path = saveHologram(hologram, save)
    
    #display on DMD
    DMDwrapper.display_bitmap(hologram_path,1)
    return hologram_path



def makeLG(waists, n1s, n2s, phis, epsilon_phis, centers, wp=4, verbose=False,save=0,defocuses=[0],tilts=[(0.0,0.0)], phaseOff = [0]):
    holomaker = initHolomaker(wp,verbose)
    #add LG
    for i in range(len(waists)):
        holomaker.addLG(waists[i], n1s[i], n2s[i], phis[i], epsilon_phis[i], centers[i],phaseOffset = phaseOff[i],defoc=defocuses[i], tlt=tilts[i])
    hologram = holomaker.makeHologram()

    #save
    hologram_path=saveHologram(hologram, save)

    #display on DMD
    DMDwrapper.display_bitmap(hologram_path,1)
    return hologram_path




def displacedLG(waist=68,n1=0,n2=0,phi=0,epsilon_phi=0,center=(0,0), verbose=False,save=0,defocus = 0.,t=(0,0),relPhase=0,globalPhase=0,localOrGlobalCoord=0):
    holomaker = initHolomaker(verbose)

    ws = [waist, waist, waist]
    n1s = [n1, n1, n1]
    n2s = [n2, n2, n2]
    phis = [phi, phi, phi]
    ep_phis = [epsilon_phi, epsilon_phi, epsilon_phi]
    defocuses = [defocus, defocus, defocus]
    phaseOffsets = [globalPhase*2.0*np.pi/3.0, (relPhase+globalPhase)*2.0*np.pi/3.0, (relPhase+globalPhase)*4.0*np.pi/3.0]
    
    if center[0]==0:
      centers = [(0,0),(0,0),(0,0)]
    else:
      r = center[0]
      if localOrGlobalCoord==1: # 1=Global (unrotated), 0=Local(rotated) coordinates
        theta = center[1]*np.pi/180.0
      else:
        theta = (center[1]+t[1])*np.pi/180.0
      centers = [(r*np.cos(theta),r*np.sin(theta)), (r*np.cos(theta+2*np.pi/3.0),r*np.sin(theta+2*np.pi/3.0)), (r*np.cos(theta+4*np.pi/3.0),r*np.sin(theta+4*np.pi/3.0))]
    
    if t[0]==0:
      tilts = [(0,0),(0,0),(0,0)]
    else:
      rt = t[0]      
      thetat= t[1]*np.pi/180.0
      tilts = [(rt*np.cos(thetat),rt*np.sin(thetat)), (rt*np.cos(thetat+2*np.pi/3.0),rt*np.sin(thetat+2*np.pi/3.0)), (rt*np.cos(thetat+4*np.pi/3.0),rt*np.sin(thetat+4*np.pi/3.0))]
        
    hologram_path = makeLG(ws, n1s, n2s, phis, ep_phis, centers, verbose, save, defocuses, tilts, phaseOffsets)
    return hologram_path


def makeCirc(waist, n1, n2, phi, epsilon_phi, center,verbose = False, save=0):
    holomaker = initHolomaker(verbose)

    #add HG
    holomaker.addCircMode(waist, n1, n2, center, 0)
    hologram = holomaker.makeHologram()

    #save
    hologram_path=saveHologram(hologram, save)

    #display on DMD
    DMDwrapper.display_bitmap(hologram_path,1)
    return hologram_path

def run2(defoc=[0]):
    print("connecting")
    nx = 1
    ny = 1
    w = 40
    
    hologram_path1 = makeLG([w], [nx],[ny] ,[0],[0], [(-80,0)],verbose=True,save=1,defocuses=[defoc])
    hologram_path2 = makeLG([w], [nx],[ny] ,[0],[0], [(80,0)],verbose=True,save=2,defocuses=[defoc])
    while (True):
        DMDwrapper.display_bitmap(hologram_path1,1)
        DMDwrapper.display_bitmap(hologram_path2,1)
    
def runD(nx, ny, disp, w=68, defoc=0.,tlt=(0,0)):
    hologram_path1 = displacedLG(w, nx, ny, 0, 0, disp,verbose=True,save=1,defocus=defoc,t=tlt)

    DMDwrapper.display_bitmap(hologram_path1,1)

def run(nxs,nys,centers=(0,0),ws=68,defocs=0.0,tlts=(0,0),phaseOffset=0):
    print("connecting")
    #nx=0
    #ny=0
    #w=80
    '''
    hologram_path1 = makeHG(w,w, nx,ny ,0,0, (-80,0),verbose=True,save=1)
    hologrampath2 = makeHG(w,w, nx,ny ,0,0, (80,0),verbose=True,save=2)
    while (True):
        DMDwrapper.display_bitmap(hologram_path1,1)
        DMDwrapper.display_bitmap(hologram_path2,1)
    '''
    '''
    hologram_path1 = makeLG(w, 0, 0,0,0, (0,0),verbose=True,save=1)
    hologram_path2 = makeLG(w, nx,ny ,0,0, (0,0),verbose=True,save=2)
    while (True):
        DMDwrapper.display_bitmap(hologram_path1,1)
        DMDwrapper.display_bitmap(hologram_path2,1)
    '''
    indlist = list(range(len(nxs)))
    if type(centers)==tuple:
        centerlist = [centers for i in indlist]
        centers = centerlist
    if type(ws)==int or type(ws)==float:
        wslist = [ws for i in indlist]
        ws = wslist
    if type(defocs)==int or type(defocs)==float:
        defoclist = [defocs for i in indlist]
        defocs = defoclist
    if type(tlts)==tuple:
        tltlist = [tlts for i in indlist]
        tlts = tltlist
    if type(phaseOffset)==int or type(phaseOffset)==float:
        phaseOffsetList = [phaseOffset for i in indlist]
        phaseOffset = phaseOffsetList

    phis = [0 for i in indlist]
    epsilon_phis = [0 for i in indlist]

    print(tlts)
    
    hologram_path1 = makeLG(ws, nxs,nys ,phis,epsilon_phis, centers,verbose=True,save=1,defocuses=defocs,tilts = tlts, phaseOff = phaseOffset)

    DMDwrapper.display_bitmap(hologram_path1,1)


if __name__ == "__main__":
    #run()
    print("loaded")
    nR = 2
    nL = 0
    nx=min(nR,nL)
    ny=nR-nL
    n1=1
    n2=1
    w=600
    #hologram_path = os.path.join(DMD_sample_hologram_7_7, os.path.basename(child_hologram_directory_path + "_" + str(phase_index) + ".bmp"))
    #DMDwrapper.display_bitmap(hologram_path,1)
    #hologram_path1 = makeHG(w,w, n1,n2 ,0,0, (0,0),verbose=True,save=1)
    #hologram_path1 = makeLG([w], [nx],[ny] ,[0],[0], [(0,0)], save=1)
    #hologram_path1 = makeCirc(w, nx,ny ,0,0, (0,0))    
    #DMDwrapper.display_bitmap(hologram_path1,1)
    
    hologram_path1 = makeHG(w,w, n1,n2 ,0,0, (0,0), 4, verbose=True,save=1)
    hologram_path2 = makeHG(w,w, n1,n2 ,0,0, (0,0), 25,verbose=True,save=2)
    
    # DMDwrapper.display_bitmap(hologram_path1,1)

    while (True):
        DMDwrapper.display_bitmap(hologram_path1,1)
        DMDwrapper.display_bitmap(hologram_path2,1)
    
    
    
