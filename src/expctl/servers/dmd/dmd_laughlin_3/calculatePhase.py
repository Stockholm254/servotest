# General
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
from scipy.optimize import curve_fit
from scipy import interpolate
import pickle as pickle
from scipy.ndimage.filters import gaussian_filter

# Specific
from . import master_helper
from . import crop_and_slice

MAXNUMROWS = 684
MAXNUMCOLS = 608

##########################################################################################################


def calculatePhase(row_pixel_lst, \
                   col_pixel_lst, \
                   hologram_directory_path, \
                   image_directory_path, \
                   fit_directory_path, \
                   crop1_boundaries, \
                   crop2_boundaries):

    # call get_crops
    save_crop(image_directory_path, fit_directory_path, crop1_boundaries, crop2_boundaries)

    numRows = row_pixel_lst.size
    numCols = col_pixel_lst.size

    phaseMap = np.zeros((numRows, numCols))
    amplitudeMap = np.zeros((numRows, numCols))

    #initial
    k_guess = 1
    phase_guess = 0.0

    numPhases = 3

    for row_index in np.arange(numRows):
        for col_index in np.arange(numCols):

            child_image_directory_path = master_helper.get_child_directory_path(image_directory_path, row_index, col_index)

            phaseOffset = np.zeros(3)
            intensity = np.zeros(3)
            
            for phase_index in np.arange(numPhases):

                print("Fitting %d of %d images: r=%d, c=%d, i=%d" % \
                      (1 + phase_index + numPhases*col_index + numPhases*numCols*row_index, numRows*numCols*numPhases, row_index, col_index, phase_index))

                # phaseOffset
                phaseOffset[phase_index] = phase_index * 2.*np.pi/3. 

                image_path = os.path.join(child_image_directory_path, \
                                          os.path.basename(child_image_directory_path) + "_" + str(phase_index) + ".png")
                img = np.asarray(Image.open(image_path))
                img_cropped = crop_and_slice.showCrop(crop_and_slice.getCrop(img,crop1_boundaries),crop2_boundaries)
                region = crop_and_slice.getCrop(crop_and_slice.getCrop(img,crop1_boundaries),crop2_boundaries)
                
                # intensity
                intensity[phase_index] = np.sum(region)

            # Fit
            phasor = -1./3.*(intensity[1]+intensity[2]-2*intensity[0]) + (1.j/np.sqrt(3)) * (intensity[1]-intensity[2])
            phase = np.angle(phasor)
            amplitude = np.abs(phasor)
            
            phaseMap[row_index,col_index] = phase
            amplitudeMap[row_index,col_index] = amplitude

    


    


    phaseMap_2pi_normalized = phaseMap/(2*np.pi)

    phaseMap_2pi_normalized[phaseMap_2pi_normalized==0]=0.00001
##    print phaseMap_2pi_normalized


    # Force -0.5<phi<0.5
    signMap = phaseMap_2pi_normalized/np.abs(phaseMap_2pi_normalized)
    phaseMap_2pi_normalized = phaseMap_2pi_normalized % signMap
    
    #mid pixel
    if numRows%2==1 and numCols%2==1:
        phaseMap_2pi_normalized[numRows/2,numCols/2]=0
    #sample; fix this later
    if numRows==4 and numCols==4:
        phaseMap_2pi_normalized[0,0]=0
        
##    print phaseMap_2pi_normzlied
    
    for r in np.arange(numRows):
        for c in np.arange(numCols):
            if phaseMap_2pi_normalized[r,c] > 0.5:
                phaseMap_2pi_normalized[r,c] -= 1
            elif phaseMap_2pi_normalized[r,c] < -0.5:
                phaseMap_2pi_normalized[r,c] += 1

##    print phaseMap_2pi_normzlied
                
        
    
    
    plotPhaseMap(phaseMap_2pi_normalized, numRows, numCols, fit_directory_path, "phaseMap")

    plotPhaseMap(amplitudeMap, numRows, numCols, fit_directory_path, "amplitudeMap")

    return phaseMap_2pi_normalized, amplitudeMap

    


def save_crop(image_directory_path, \
              fit_directory_path, \
              crop1_boundaries, \
              crop2_boundaries):
    
    #future: show the image in GUI: ok to proceed, cancel to cancel :)
    image_path = os.path.join(master_helper.get_child_directory_path(image_directory_path, 0, 0), \
                              os.path.basename(master_helper.get_child_directory_path(image_directory_path, 0, 0)) + "_0.png")
    
    # Apply crops
    img = np.asarray(Image.open(image_path))
    img_cropped = crop_and_slice.getCrop(img, crop1_boundaries)
    img_cropped_with_crop = crop_and_slice.showCrop(img_cropped, crop2_boundaries)
    region = crop_and_slice.getCrop(img_cropped, crop2_boundaries)

    # Visual check
    img_cropped_with_crop_plot = plt.imshow(img_cropped_with_crop, interpolation="nearest")
    img_cropped_with_crop_plot.set_clim(0, 255)
    plt.colorbar()
    plt.savefig(os.path.join(fit_directory_path, "img_cropped_with_crop.png"))
    plt.close()

    # Visual check
    region_plot = plt.imshow(region, interpolation="nearest")
    region_plot.set_clim(0, 255)
    plt.colorbar()
    plt.savefig(os.path.join(fit_directory_path, "region.png"))
    plt.close()



    

def plotPhaseMap(phaseMap, numRows, numCols, fit_directory_path, title):

    # Plot
    phaseMap_plot = plt.imshow(phaseMap, interpolation="nearest")
   
    # Text
    for row_index in np.arange(numRows):
        for col_index in np.arange(numCols):
            plt.text(col_index, row_index, master_helper.roundToNthDecimal(phaseMap[row_index,col_index],2), va='center', ha='center')

##    phaseMap_raw_plot.set_clim(-1., 1.)
    plt.colorbar()
    
    plt.suptitle(title)
    plt.savefig(os.path.join(fit_directory_path, title + ".png"), dpi=200)

    plt.close()



def interpolatePhase(row_pixel_lst, \
                     col_pixel_lst, \
                     phaseMap, \
                     fit_directory_path, \
                     title):
    
    x = col_pixel_lst
    y = row_pixel_lst
    z = phaseMap

    f = interpolate.interp2d(x,y,z,kind='linear')

    xnew = np.arange(MAXNUMCOLS)
    ynew = np.arange(MAXNUMROWS)
    znew = f(xnew,ynew)

##    plt.imshow(z,interpolation='nearest')
##    plt.colorbar()
##    plt.show()

    img = plt.imshow(znew,interpolation='nearest')

##    img.set_clim(-1, 1)

    plt.colorbar()

    plt.savefig(os.path.join(fit_directory_path, title + ".png"))
    
    plt.close()

    return znew



def GaussFilter(amplitudeMap, numRows, numCols, sigma):

    amplitudeMap_filtered = np.copy(amplitudeMap)

    # Fix center
    neighbors = amplitudeMap_filtered[numRows/2-1:numRows/2+2,numCols/2-1:numCols/2+2]
    amplitudeMap_filtered[numRows/2,numCols/2] = np.average(neighbors)

    # Apply Gaussian filter
    amplitudeMap_filtered = gaussian_filter(amplitudeMap_filtered,sigma)
    
    amplitudeMap_filtered /= np.min(amplitudeMap_filtered)

    return amplitudeMap_filtered


