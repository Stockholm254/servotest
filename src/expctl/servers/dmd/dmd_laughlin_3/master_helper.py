# General
import numpy as np
import os
import shutil

#####################################################################################


def get_main_directory_path():
    return os.path.dirname(os.path.abspath(__file__))
##    #Check computer/user
##    if os.getcwd()[9:13] == 'Bert':
##        return  "C:\\Users\\Bert\\slm_data"
##    else:
##        return "A:\\"

def make_directory(directory_path):
    try:
        shutil.rmtree(directory_path)
        os.mkdir(directory_path)
    except:
        os.mkdir(directory_path)
    

def make_directories(numRows, numCols, directory_path):
    for row_index in np.arange(numRows):
        for col_index in np.arange(numCols):
            os.mkdir(get_child_directory_path(directory_path, row_index, col_index))


def get_child_directory_path(parent_directory_path, row_index, col_index):
    return os.path.join(parent_directory_path, os.path.basename(parent_directory_path) + "_" + str(row_index) + "_" + str(col_index))
        

def get_rowAndColumnLists(numRows, numCols, numRows_sample, numCols_sample):

    MAXNUMROWS = 684
    MAXNUMCOLS = 608

    row_pixel_lst = np.arange(numRows) * int(round(MAXNUMROWS/numRows)) + int(round(MAXNUMROWS/(2*numRows)))
    col_pixel_lst = np.arange(numCols) * int(round(MAXNUMCOLS/numCols)) + int(round(MAXNUMCOLS/(2*numCols)))

    # Haven't decided whether to make this more general

##    print row_pixel_lst[numRows*2/3]
##    print row_pixel_lst[numRows*2/3]
##    print numSample

    sample_row_pixel_lst = np.round(np.linspace(row_pixel_lst[numRows*2/3], row_pixel_lst[numRows*2/3+1], numRows_sample))
    sample_col_pixel_lst = np.round(np.linspace(col_pixel_lst[numCols*2/3], col_pixel_lst[numCols*2/3+1], numCols_sample))
    
    return row_pixel_lst, col_pixel_lst, sample_row_pixel_lst, sample_col_pixel_lst


def roundToNthDecimal(number, n):
    number *= 10**n
    number = round(number)
    number /= 10**n
    return number


def convertSeconds(seconds):
    seconds = int(round(seconds))
    minutes = seconds / 60
    if minutes == 0:
        return "%d s" % seconds
    else:
        hours = minutes / 60
        if hours == 0:
            return "%d min, %d s" % (minutes, seconds%60)
        else:
            return "%d hr, %d min, %d s" % (hours, minutes%60, seconds%60)
    


    
    
