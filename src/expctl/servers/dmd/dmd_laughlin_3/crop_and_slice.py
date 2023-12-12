import numpy as np
import scipy.ndimage
import matplotlib.pyplot as plt
import matplotlib.image as mpimg            



maxRowNum = 684
maxColNum = 608


# deprecated
def showCrop(img, crop_boundaries):

    img_with_crop = np.copy(img)
    img_with_crop[crop_boundaries[0]:crop_boundaries[1],crop_boundaries[2]] = 255#np.max(img)
    img_with_crop[crop_boundaries[0]:crop_boundaries[1],crop_boundaries[3]] = 255#np.max(img)
    img_with_crop[crop_boundaries[0],crop_boundaries[2]:crop_boundaries[3]] = 255#np.max(img)
    img_with_crop[crop_boundaries[1],crop_boundaries[2]:crop_boundaries[3]] = 255#np.max(img)

    return img_with_crop

##    img[crop_boundaries[0]:crop_boundaries[1],crop_boundaries[2]] = np.max(img)
##    img[crop_boundaries[0]:crop_boundaries[1],crop_boundaries[3]] = np.max(img)
##    img[crop_boundaries[0],crop_boundaries[2]:crop_boundaries[3]] = np.max(img)
##    img[crop_boundaries[1],crop_boundaries[2]:crop_boundaries[3]] = np.max(img)
##
##    return img


def getCrop(img, crop_boundaries):
    return img[crop_boundaries[0]:crop_boundaries[1], crop_boundaries[2]:crop_boundaries[3]]


def getSlice(img, x0, y0, x1, y1, object_path_absolute, num):

    # Make a line with "num" points...
##    num = 1000
    x, y = np.linspace(x0, x1, num), np.linspace(y0, y1, num)

##    # Extract the values along the line, using cubic interpolation
##    print x.size
##    print y.size
##    print img.shape#FIXXX
    y2 = scipy.ndimage.map_coordinates(np.transpose(img), np.vstack((x,y)))

    return y2
