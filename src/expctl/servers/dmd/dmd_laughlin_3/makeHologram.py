# General
import numpy as np
import scipy
import os
import pickle as pickle

# Specific
from . import master_helper
from . import holo_maker

###########################################################################################

MAXNUMROWS = 684
MAXNUMCOLS = 608


def makeAllHolograms(row_pixel_lst,
                     col_pixel_lst,
                     hologram_directory_path,
                     fit_directory_path,
                     population_fit_directory_path,
                     phase_correct,
                     amplitude_correct,
                     simulated):                     

    numRows = row_pixel_lst.size
    numCols = row_pixel_lst.size

    # phase_correct
    if phase_correct:
        try:
            with open(os.path.join(population_fit_directory_path, "phaseMap_interpolated.txt"), 'r') as f:
                phaseMap_interpolated = pickle.load(f)
        except:
            print("Albert says: no interpolation available")
            print(os.path.join(fit_directory_path, "phaseMap_interpolated.txt"))
            
            phaseMap_interpolated = np.zeros((MAXNUMROWS,MAXNUMCOLS))
    else:
        phaseMap_interpolated = np.zeros((MAXNUMROWS,MAXNUMCOLS))


    #amplitude_correct
    if amplitude_correct:
        try:
            with open(os.path.join(population_fit_directory_path, "amplitudeMap_interpolated.txt"), 'r') as f:
                amplitudeMap_interpolated = pickle.load(f)
        except:
            print("Albert says: no interpolation available")
            print(os.path.join(fit_directory_path, "amplitudeMap_interpolated.txt"))
            
            amplitudeMap_interpolated = np.zeros((MAXNUMROWS,MAXNUMCOLS))+1.0
    else:
        amplitudeMap_interpolated = np.zeros((MAXNUMROWS,MAXNUMCOLS))+1.0



    ####
    phaseMap_interpolated = np.flipud(phaseMap_interpolated)
    amplitudeMap_interpolated = np.flipud(amplitudeMap_interpolated)
    ####

    print(phaseMap_interpolated)
            

    for row_index in np.arange(numRows):
        for col_index in np.arange(numCols):
            for phase_index in np.arange(3):

                print("Making %d of %d holograms: r=%d, c=%d, i=%d" % (1 + phase_index + 3*col_index + 3*numCols*row_index, numRows*numCols*3, row_index, col_index, phase_index))                  
                
                phaseOffset = phase_index * 2.*np.pi/3. 

                row_pixel = row_pixel_lst[row_index]
                col_pixel = col_pixel_lst[col_index]

                hologram, hologram_reversed = makeOneHologram(row_pixel,
                                                              col_pixel,
                                                              phaseOffset,
                                                              simulated,
                                                              phaseMap_interpolated,
                                                              amplitudeMap_interpolated)

                hologram_path = os.path.join(master_helper.get_child_directory_path(hologram_directory_path, row_index, col_index),
                                             os.path.basename(master_helper.get_child_directory_path(hologram_directory_path, row_index, col_index)) + "_" + str(phase_index) + ".bmp")
                hologram_reversed_path = os.path.join(master_helper.get_child_directory_path(hologram_directory_path, row_index, col_index),
                                                      "reversed_" + os.path.basename(master_helper.get_child_directory_path(hologram_directory_path, row_index, col_index)) + "_" + str(phase_index) + ".bmp")

                scipy.misc.imsave(hologram_path, hologram)
                scipy.misc.imsave(hologram_reversed_path, hologram_reversed)
                                                        
    

def makeOneHologram(row_pixel, \
                    col_pixel, \
                    phaseOffset, \
                    simulated, \
                    phaseMap_interpolated,
                    amplitudeMap_interpolated):

    # Conform to Ariel's convention for pixel indexing
    col = col_pixel - MAXNUMCOLS/2
    row = row_pixel - MAXNUMROWS/2 if simulated else round((row_pixel - MAXNUMROWS/2)*0.5)

    # Set hologram parameters
    w = 10 #hologram waist <-- this has to be small enoughm, otherwise it will skip
    n1 = 0 #nR
    n2 = 0 #nL
    
    a = 2 #sharpness
    d = 4 #carrier wave period in pixels
    angle_deg = 20.0 # carrier wave direction relative to horizontal (degrees)

    # Make a hologram
    holomaker = holo_maker.holo_maker(simulated, phaseMap_interpolated, amplitudeMap_interpolated, sharpness=a, period=d, angle=angle_deg)
    holomaker.addCircMode(w,n1,n2,(0,0), 0)
    holomaker.addCircMode(w,n1,n2,(col,row), phaseOffset)
    hologram = holomaker.makeHologram()

    # Make a hologram reversed
    holomaker_reversed = holo_maker.holo_maker(simulated, phaseMap_interpolated, amplitudeMap_interpolated, sharpness=a, period=d, angle=angle_deg)
    holomaker_reversed.addCircMode(w,n1,n2,(0,0), 0)
    holomaker_reversed.addCircMode(w,n1,n2,(col,-1*row), phaseOffset)
    hologram_reversed = holomaker_reversed.makeHologram()

    return hologram, hologram_reversed

    
