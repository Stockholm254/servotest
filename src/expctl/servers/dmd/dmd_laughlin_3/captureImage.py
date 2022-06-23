# General
import numpy as np
import os
import time
import shutil

# Specific
from . import master_helper
from . import DMDwrapper
import telnetlib

host = "192.168.1.122" #Check these for a new setup
port = "5024"

#######################################################################

def captureImage(row_pixel_lst, \
                 col_pixel_lst, \
                 hologram_directory_path, \
                 image_directory_path, \
                 temp_directory_path, \
                 sampleCount):

    

    numRows = row_pixel_lst.size
    numCols = col_pixel_lst.size

    for row_index in np.arange(numRows):
        for col_index in np.arange(numCols):

            child_hologram_directory_path = master_helper.get_child_directory_path(hologram_directory_path, row_index, col_index)
            child_image_directory_path = master_helper.get_child_directory_path(image_directory_path, row_index, col_index)
            
            for phase_index in np.arange(3):

                print("Capturing %d of %d holograms: r=%d, c=%d, i=%d" % \
                      (1 + phase_index + 3*col_index + 3*numCols*row_index, numRows*numCols*3, row_index, col_index, phase_index))

                # Display hologram on DMD; 
                hologram_path = os.path.join(child_hologram_directory_path, \
                                             os.path.basename(child_hologram_directory_path + "_" + str(phase_index) + ".bmp"))
                DMDwrapper.display_bitmap(hologram_path,1)

                while np.array(os.listdir(temp_directory_path)).size != (1 + phase_index + 3*col_index + 3*numCols*row_index + sampleCount):
##                    print temp_directory_path
                    print(np.array(os.listdir(temp_directory_path)).size)
                    print(1 + phase_index + 3*col_index + 3*numCols*row_index + sampleCount)
                    print("checkpoint A")
                    
                    #Connect the device
                    tn = telnetlib.Telnet(host, port)
                    print("checkpoint B")
                    wel = tn.read_until("3390>")
##                    print wel
##                  print "1"

##                    print "hu"
                
                    sd = tn.write("*IDN?"+"\n")
               #     print sd
                    rt = tn.read_until("3390>")
##                    print rt
##                    print "2"

##                    print "yo"
                
                    #Software trigger
                    sd = tn.write("TRIG"+"\n")
                    rt = tn.read_until("3390>")
##                  print rt
##                  print "3"

                    tn.close()

                    time.sleep(0.25) #super important

##                    print "hello there"


                    # Rename the files individually (if saved correctly)
                    if np.array(os.listdir(temp_directory_path)).size == (1 + phase_index + 3*col_index + 3*numCols*row_index + sampleCount):

                        image_files = getSortedFiles(temp_directory_path)
##                        print "from", os.path.join(temp_directory_path, image_files[-1])
##                        print "im here"
##                        print "to", os.path.basename(master_helper.get_child_directory_path(image_directory_path, row_index, col_index)) + "_" + str(phase_index) + ".png"
                        shutil.copyfile(os.path.join(temp_directory_path, image_files[-1]), \
                                        os.path.join(child_image_directory_path, \
                                                     os.path.basename(child_image_directory_path) + "_" + str(phase_index) + ".png"))

                    

                
# Sort by time
def getSortedFiles(dir_path):
    os.chdir(dir_path)
    files = os.listdir(dir_path)
    files.sort(key=os.path.getmtime)
    return np.array(files)















                
