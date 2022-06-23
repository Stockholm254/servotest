# General                         
import numpy as np
import os                                   
import pickle as pickle                    
import matplotlib.pyplot as plt

# Specific
from . import master_helper
from . import calculatePhase                       
from . import unwrapPhase

##################################################################################

numRows = 19
numCols = 19

numPhases = 3

numRows_sample = 9
numCols_sample = 3

simulated = 0

#############################################################################################

MAXNUMROWS = 684
MAXNUMCOLS = 608

# Get directory paths

main_directory_path = master_helper.get_main_directory_path()

maps_directory_path = os.path.join(main_directory_path, "maps")

if not simulated:
    hologram_directory_path = os.path.join(main_directory_path, "DMD_hologram_" + str(numRows) + "_" + str(numCols))
    image_directory_path = os.path.join(main_directory_path, "DMD_image_" + str(numRows) + "_" + str(numCols))
    fit_directory_path = os.path.join(main_directory_path, "DMD_fit_" + str(numRows) + "_" + str(numCols))

    sample_hologram_directory_path = os.path.join(main_directory_path, "DMD_sample_hologram_" + str(numRows) + "_" + str(numCols))
    sample_image_directory_path = os.path.join(main_directory_path, "DMD_sample_image_" + str(numRows) + "_" + str(numCols))
    sample_fit_directory_path = os.path.join(main_directory_path, "DMD_sample_fit_" + str(numRows) + "_" + str(numCols))

else:
    hologram_directory_path = os.path.join(main_directory_path, "simulated_hologram_" + str(numRows) + "_" + str(numCols))
    image_directory_path = os.path.join(main_directory_path, "simulated_image_" + str(numRows) + "_" + str(numCols))
    fit_directory_path = os.path.join(main_directory_path, "simulated_fit_" + str(numRows) + "_" + str(numCols))

    sample_hologram_directory_path = os.path.join(main_directory_path, "simulated_sample_hologram_" + str(numRows) + "_" + str(numCols))
    sample_image_directory_path = os.path.join(main_directory_path, "simulated_sample_image_" + str(numRows) + "_" + str(numCols))
    sample_fit_directory_path = os.path.join(main_directory_path, "simulated_sample_fit_" + str(numRows) + "_" + str(numCols))


# Calculate row_pixel_lst, col_pixel_lst
row_pixel_lst, col_pixel_lst, sample_row_pixel_lst, sample_col_pixel_lst = master_helper.get_rowAndColumnLists(numRows,numCols,numRows_sample,numCols_sample)
print("row_pixel_lst:", row_pixel_lst)
print("col_pixel_lst:", col_pixel_lst)
print("sample_row_pixel_lst:", sample_row_pixel_lst)
print("sample_col_pixel_lst:", sample_col_pixel_lst)



# Make directories
if not simulated:
    master_helper.make_directory(fit_directory_path)
    master_helper.make_directory(sample_fit_directory_path)
else:
    master_helper.make_directory(simulated_fit_directory_path)
    master_helper.make_directory(simulated_sample_fit_directory_path)


#########################################################################################################################################

# select boundary pixels --- how to improve this??
crop1_boundaries = np.array([0,960,0,1280])
crop2_boundaries = np.array([580,582,680,682])

if simulated:
    crop1_boundaries = np.array([2400,2650,3600,3900]) #simulated
    crop2_boundaries = np.array([100,106,156,162]) #simulated

#########################################################################################################################################


population_phaseMap, population_amplitudeMap = calculatePhase.calculatePhase(row_pixel_lst, \
                                                                             col_pixel_lst, \
                                                                             hologram_directory_path, \
                                                                             image_directory_path, \
                                                                             fit_directory_path, \
                                                                             crop1_boundaries, \
                                                                             crop2_boundaries)

with open(os.path.join(fit_directory_path, "population_phaseMap.txt"), 'w') as f:
    pickle.dump(population_phaseMap,f)
with open(os.path.join(fit_directory_path, "population_amplitudeMap.txt"), 'w') as f:
    pickle.dump(population_amplitudeMap,f)



sample_phaseMap, sample_amplitudeMap = calculatePhase.calculatePhase(sample_row_pixel_lst, \
                                                                     sample_col_pixel_lst, \
                                                                     sample_hologram_directory_path, \
                                                                     sample_image_directory_path, \
                                                                     sample_fit_directory_path, \
                                                                     crop1_boundaries, \
                                                                     crop2_boundaries)

##with open(os.path.join(sample_fit_directory_path, "sample_phaseMap.txt"), 'w') as f:
##    pickle.dump(sample_phaseMap,f)


plt.imshow(sample_phaseMap, interpolation="nearest")
plt.colorbar()
plt.show()
plt.close()

calculatePhase.plotPhaseMap(sample_phaseMap, numRows_sample, numCols_sample, sample_fit_directory_path, \
                            "sample_phaseMap")

sample_phaseMap = unwrapPhase.removeZero(sample_phaseMap)
sample_phaseMap = unwrapPhase.unwrapPixel(sample_phaseMap)

plt.imshow(sample_phaseMap, interpolation="nearest")
plt.colorbar()
plt.show()
plt.close()

calculatePhase.plotPhaseMap(sample_phaseMap, numRows_sample, numCols_sample, sample_fit_directory_path, \
                            "sample_phaseMap_unwrapped")

##with open(os.path.join(sample_fit_directory_path, "sample_phaseMap_unwrapped.txt"), 'w') as f:
##    pickle.dump(sample_phaseMap,f)



# Unwrap phase
unwrapped_phaseMap = unwrapPhase.phaseUnwrap2D(sample_row_pixel_lst, \
                                               sample_col_pixel_lst, \
                                               sample_phaseMap, \
                                               row_pixel_lst, \
                                               col_pixel_lst, \
                                               population_phaseMap, \
                                               fit_directory_path)

with open(os.path.join(fit_directory_path, "unwrapped_phaseMap.txt"), 'w') as f:
    pickle.dump(unwrapped_phaseMap,f)

    



plt.imshow(population_phaseMap, interpolation="nearest")
plt.colorbar()
plt.show()
plt.close()

plt.imshow(unwrapped_phaseMap, interpolation="nearest")
plt.colorbar()
plt.show()
plt.close()
calculatePhase.plotPhaseMap(unwrapped_phaseMap,numRows,numCols,fit_directory_path,"unwrapped_phaseMap")


# Filter amplitude
amplitudeMap_filtered = calculatePhase.GaussFilter(population_amplitudeMap, numRows, numCols, 3)


# Interpolate to 684 x 608
phaseMap_interpolated = calculatePhase.interpolatePhase(row_pixel_lst, \
                                                        col_pixel_lst, \
                                                        unwrapped_phaseMap, \
                                                        fit_directory_path,
                                                        "phaseMap_interpolated")
amplitudeMap_interpolated = calculatePhase.interpolatePhase(row_pixel_lst, \
                                                            col_pixel_lst, \
                                                            amplitudeMap_filtered, \
                                                            fit_directory_path, \
                                                            "amplitudeMap_interpolated")

with open(os.path.join(fit_directory_path, "phaseMap_interpolated.txt"), 'w') as f:
    pickle.dump(phaseMap_interpolated,f)
with open(os.path.join(fit_directory_path, "amplitudeMap_interpolated.txt"), 'w') as f:
    pickle.dump(amplitudeMap_interpolated,f)



print("\nDone")


