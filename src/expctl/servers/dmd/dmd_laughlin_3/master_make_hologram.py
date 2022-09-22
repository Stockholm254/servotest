# General
import numpy as np
import scipy
import os
import pickle as pickle
import time
from joblib import Parallel, delayed

# Specific
import master_helper
import holo_maker


##############################################################################################
### DON'T CHANGE BELOW
##############################################################################################

def makeOneHologram(row_index, col_index, phase_index, \
                    row_pixel, col_pixel, phaseOffset, \
                    numRows, numCols, numPhases, \
                    simulated, \
                    phaseMap_interpolated, \
                    amplitudeMap_interpolated, \
                    hologram_directory_path, \
                    maps_directory_path):

    """Creates bmp images used as holograms""" 

    MAXNUMROWS = 684
    MAXNUMCOLS = 608

    print("Making %d of %d holograms: r=%d, c=%d, i=%d" % (1 + phase_index + numPhases*col_index + numPhases*numCols*row_index, numRows*numCols*numPhases, row_index, col_index, phase_index))

    # Conform to Ariel's convention for pixel indexing, i.e., the center of the DMD is now the coordinate center
    col = col_pixel - MAXNUMCOLS/2
    row = row_pixel - MAXNUMROWS/2 if simulated else round((row_pixel - MAXNUMROWS/2)*0.5) # accounts for row squeeze

    # Set hologram parameters
    w = 10 #hologram waist <-- this has to be small enough to fit within 
    n1 = 0 #nR
    n2 = 0 #nL
    
    a = 2 #sharpness
    d = 4 #carrier wave period in pixels
    angle_deg = 20.0 # carrier wave direction relative to horizontal (degrees)

    # Make a hologram
    holomaker = holo_maker.holo_maker(simulated, \
                                      phaseMap_interpolated, \
                                      amplitudeMap_interpolated, \
                                      sharpness=a, \
                                      period=d, \
                                      angle=angle_deg)
    holomaker.addLG(w,n1,n2,0,0,(0,0),0)
    holomaker.addLG(w,n1,n2,0,0,(col,row), phaseOffset)
    hologram = holomaker.makeHologram()

##    # Make a hologram reversed
##    holomaker_reversed = holo_maker.holo_maker(simulated, \
##                                               phaseMap_interpolated, \
##                                               amplitudeMap_interpolated, \
##                                               sharpness=a, \
##                                               period=d, \
##                                               angle=angle_deg)
##    holomaker_reversed.addLG(w,n1,n2,0,0,(0,0),0)
##    holomaker_reversed.addLG(w,n1,n2,0,0,(col,-1*row), phaseOffset)
##    hologram_reversed = holomaker_reversed.makeHologram()

    # Save
    hologram_path = os.path.join(master_helper.get_child_directory_path(hologram_directory_path, row_index, col_index), \
                                             os.path.basename(master_helper.get_child_directory_path(hologram_directory_path, row_index, col_index)) + "_" + str(phase_index) + ".bmp")
##    hologram_reversed_path = os.path.join(master_helper.get_child_directory_path(hologram_directory_path, row_index, col_index), \
##                                                      "reversed_" + os.path.basename(master_helper.get_child_directory_path(hologram_directory_path, row_index, col_index)) + "_" + str(phase_index) + ".bmp")

    scipy.misc.imsave(hologram_path, hologram)
##    scipy.misc.imsave(hologram_reversed_path, hologram_reversed)





####################################################################################################################
### CHANGE BELOW
####################################################################################################################

if __name__ == '__main__':

    # Specify
    numRows = 7 # 7<= numRows <=684 
    numCols = 7 # 7<= numCols <=608

    numRows_sample = 9
    numCols_sample = 3

    phase_correct = 0
    amplitude_correct = 0

    simulated = 0

####################################################################################################################
### DON'T CHANGE BELOW
####################################################################################################################


    MAXNUMROWS = 684
    MAXNUMCOLS = 608

    main_directory_path = master_helper.get_main_directory_path() #returns the directory of this script

    maps_directory_path = os.path.join(main_directory_path, "maps")

    hologram_directory_path = os.path.join(main_directory_path, "DMD_hologram_" + str(numRows) + "_" + str(numCols))
    sample_hologram_directory_path = os.path.join(main_directory_path, "DMD_sample_hologram_" + str(numRows) + "_" + str(numCols))

    temp_directory_path = os.path.join(main_directory_path, "DMD_temp")


    # Calculate row_pixel_lst, col_pixel_lst
    row_pixel_lst, col_pixel_lst, sample_row_pixel_lst, sample_col_pixel_lst = master_helper.get_rowAndColumnLists(numRows,numCols,numRows_sample,numCols_sample)
    print("row_pixel_lst:", row_pixel_lst)
    print("col_pixel_lst:", col_pixel_lst)
    print("sample_row_pixel_lst:", sample_row_pixel_lst)
    print("sample_col_pixel_lst:", sample_col_pixel_lst)

    print("phase_correct: Yes" if phase_correct else "phase_correct: No")
    print("amplitude_correct: Yes" if amplitude_correct else "amplitude_correct: No")

    
    # Make hologram directories
    master_helper.make_directory(hologram_directory_path)
    master_helper.make_directories(numRows, numCols, hologram_directory_path)

    # Make sample hologram directories
    master_helper.make_directory(sample_hologram_directory_path)
    master_helper.make_directories(numRows_sample, numCols_sample, sample_hologram_directory_path)

##    # Make temp directory
##    master_helper.make_directory(temp_directory_path)


    # phase_correct
    if phase_correct:
        try:
            with open(os.path.join(maps_directory_path, "phaseMap_interpolated.txt"), 'r') as f:
                phaseMap_interpolated = pickle.load(f)
        except:
            print("No phase interpolation available")
            print(os.path.join(maps_directory_path, "phaseMap_interpolated.txt"))            
            phaseMap_interpolated = np.zeros((MAXNUMROWS,MAXNUMCOLS))
    else:
        phaseMap_interpolated = np.zeros((MAXNUMROWS,MAXNUMCOLS))

    # amplitude_correct
    if amplitude_correct:
        try:
            with open(os.path.join(maps_directory_path, "amplitudeMap_interpolated.txt"), 'r') as f:
                amplitudeMap_interpolated = pickle.load(f)
        except:
            print("No amplitude interpolation available")
            print(os.path.join(maps_directory_path, "amplitudeMap_interpolated.txt"))            
            amplitudeMap_interpolated = np.zeros((MAXNUMROWS,MAXNUMCOLS))+1.0
    else:
        amplitudeMap_interpolated = np.zeros((MAXNUMROWS,MAXNUMCOLS))+1.0

    #### gotta flip these
    phaseMap_interpolated = np.flipud(phaseMap_interpolated)
    amplitudeMap_interpolated = np.flipud(amplitudeMap_interpolated)
    ####

    print(phaseMap_interpolated)
  



    total_start = time.clock()

    # Make holograms

    indexList = []
    for r in np.arange(numRows):
        for c in np.arange(numCols):
            for i in np.arange(3):
                indexList.append((r,c,i,row_pixel_lst[r],col_pixel_lst[c],i*2.*np.pi/3))

    hologram_start = time.clock()

    Parallel(n_jobs=-1)(delayed(makeOneHologram)(x[0], x[1], x[2], \
                                                 x[3], x[4], x[5], \
                                                 numRows, numCols, 3,\
                                                 simulated, \
                                                 phaseMap_interpolated,
                                                 amplitudeMap_interpolated, \
                                                 hologram_directory_path, \
                                                 maps_directory_path) for x in indexList)

    hologram_end = time.clock()
    print("\n")


    # Make sample holograms

    indexList = []
    for r in np.arange(numRows_sample):
        for c in np.arange(numCols_sample):
            for i in np.arange(3):
                indexList.append((r,c,i,sample_row_pixel_lst[r],sample_col_pixel_lst[c],i*2.*np.pi/3))

    sample_hologram_start = time.clock()

    Parallel(n_jobs=-1)(delayed(makeOneHologram)(x[0], x[1], x[2], \
                                                 x[3], x[4], x[5], \
                                                 numRows_sample, numCols_sample, 3, \
                                                 simulated, \
                                                 phaseMap_interpolated,
                                                 amplitudeMap_interpolated, \
                                                 sample_hologram_directory_path, \
                                                 maps_directory_path) for x in indexList)

    sample_hologram_end = time.clock()

    print("\n")
    print("Time taken for making holograms: " + master_helper.convertSeconds(hologram_end-hologram_start))
    print("\n")
    print("Time taken for making sample holograms: " + master_helper.convertSeconds(sample_hologram_end-sample_hologram_start))
    print("\n")
    print("Time taken total: " + master_helper.convertSeconds(sample_hologram_end-hologram_start))
    print("\n")
    
