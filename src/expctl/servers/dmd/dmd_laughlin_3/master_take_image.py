# General
import os                              
import pickle as pickle               
import time

# Specific
import master_helper
import makeHologram
import captureImage
##import simulateImage


###############################################################################################
###############################################################################################



# 1. Specify the number of patches to segment the DMD into 

numRows = 7 # <=684 These have to be the same as those used for making the holograms   
numCols = 7 # <=608

numPhases = 3

# 2. Specify numImages where phaseOffset ranges in steps of 2*np.pi/numImages

numRows_sample = 9
numCols_sample = 3

# 3. Set flags (0 means off, 1 means on)

simulated = 0




###############################################################################################
###############################################################################################

# Declare directories

main_directory_path = master_helper.get_main_directory_path()

#real
hologram_directory_path = os.path.join(main_directory_path, "DMD_hologram_" + str(numRows) + "_" + str(numCols))
image_directory_path = os.path.join(main_directory_path, "DMD_image_" + str(numRows) + "_" + str(numCols))

sample_hologram_directory_path = os.path.join(main_directory_path, "DMD_sample_hologram_" + str(numRows) + "_" + str(numCols))
sample_image_directory_path = os.path.join(main_directory_path, "DMD_sample_image_" + str(numRows) + "_" + str(numCols))

temp_directory_path = os.path.join(main_directory_path, "DMD_temp")

#simulated
simulated_hologram_directory_path = os.path.join(main_directory_path, "simulated_hologram_" + str(numRows) + "_" + str(numCols))
simulated_image_directory_path = os.path.join(main_directory_path, "simulated_image_" + str(numRows) + "_" + str(numCols))

simulated_sample_hologram_directory_path = os.path.join(main_directory_path, "simulated_sample_hologram_" + str(numRows) + "_" + str(numCols))
simulated_sample_image_directory_path = os.path.join(main_directory_path, "simulated_sample_image_" + str(numRows) + "_" + str(numCols))



# Calculate row_pixel_lst, col_pixel_lst
row_pixel_lst, col_pixel_lst, sample_row_pixel_lst, sample_col_pixel_lst = master_helper.get_rowAndColumnLists(numRows,numCols,numRows_sample, numCols_sample)
print("row_pixel_lst:", row_pixel_lst)
print("col_pixel_lst:", col_pixel_lst)
print("sample_row_pixel_lst:", sample_row_pixel_lst)
print("sample_col_pixel_lst:", sample_col_pixel_lst)


# Make directories
if not simulated:
    master_helper.make_directory(image_directory_path)
    master_helper.make_directories(numRows, numCols, image_directory_path)
    master_helper.make_directory(sample_image_directory_path)
    master_helper.make_directories(numRows_sample, numCols_sample, sample_image_directory_path)
else:
    master_helper.make_directory(simulated_image_directory_path)
    master_helper.make_directories(numRows, numCols, simulated_image_directory_path)
    master_helper.make_directory(simulated_sample_image_directory_path)
    master_helper.make_directories(numRows_sample, numCols_sample, simulated_sample_image_directory_path)

master_helper.make_directory(temp_directory_path)


###############################################################################################


image_start = time.clock()
# Take image
if not simulated:
    print("checkpoint 1")
    captureImage.captureImage(row_pixel_lst, \
                              col_pixel_lst, \
                              hologram_directory_path, \
                              image_directory_path, \
                              temp_directory_path, \
                              sampleCount=0)
    print("checkpoint2")
    captureImage.captureImage(sample_row_pixel_lst, \
                              sample_col_pixel_lst, \
                              sample_hologram_directory_path, \
                              sample_image_directory_path, \
                              temp_directory_path, \
                              sampleCount=numRows*numCols*numPhases)
    print("checkpoint3")
        
else:
    
    simulateImage.simulateImage(row_pixel_lst, \
                                col_pixel_lst, \
                                simulated_hologram_directory_path, \
                                simulated_image_directory_path)
        
    simulateImage.simulateImage(sample_row_pixel_lst, \
                                sample_col_pixel_lst, \
                                simulated_sample_hologram_directory_path, \
                                simulated_sample_image_directory_path)
        
image_end = time.clock()    



# Print
print("\n")
print("Time taken total: " + master_helper.convertSeconds(image_end-image_start))
print("\n")
        
                               
                               





