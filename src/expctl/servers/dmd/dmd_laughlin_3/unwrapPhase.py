import numpy as np
import matplotlib.pyplot as plt
import os
##import cPickle as pickle


def phaseUnwrap1D(sampleX, sampleY, populationX, populationY):

    phases = np.copy(populationY)

    p_sample = np.poly1d(np.polyfit(sampleX, sampleY, 1))

    print(sampleX)
    print(sampleY)
    
    print(populationX)
    print(populationY)
    
    print(p_sample)

    # Forward

    # Calculate third point

    sharedX = np.intersect1d(sampleX, populationX)
    first_index = np.where(populationX==sharedX[0])[0][0] 
    second_index = first_index+1
    third_index = second_index+1

    #####
    phases[first_index] = sampleY[0]
    phases[second_index] = sampleY[-1]
    #####

    if third_index < populationX.size:
   
        pval = p_sample(populationX[third_index])
        fval = populationY[third_index]

        minimum = np.abs(pval - fval)

        while True:
            if pval > fval:
                fval += 1
            else:
                fval -= 1
            new_minimum = np.abs(pval - fval)
            if new_minimum < minimum:
                minimum = new_minimum
                phases[third_index] = fval
            else:
                print(phases[third_index])
                break

                

    # Calculate fourth and forward
    fourth_index = third_index+1
    for i in np.arange(populationY.size-fourth_index)+fourth_index:
##        print "forward", i

        p = np.poly1d(np.polyfit(populationX[i-2:i],phases[i-2:i],1))

        pval = p(populationX[i])
        fval = phases[i]

        minimum = np.abs(pval - fval)

        while True:
            if pval > fval:
                fval += 1
            else:
                fval -= 1
            new_minimum = np.abs(pval - fval)
            if new_minimum < minimum:
                minimum = new_minimum
                phases[i] = fval
            else:
                break

    # Backward

    # Calculate -1st point

    negative_index = first_index-1
    if negative_index > 0:    
        pval = p_sample(populationX[negative_index])
        fval = populationY[negative_index]

        minimum = np.abs(pval - fval)
        
        while True:
            if pval > fval:
                fval += 1
            else:
                fval -= 1
            new_minimum = np.abs(pval - fval)
            if new_minimum < minimum:
                minimum = new_minimum
                phases[negative_index] = fval
            else:
                break

    # Calculate -2nd and backward
    negative_second_index = negative_index-1
        
    for i in np.arange(negative_second_index+1):
##        print np.arange(negative_second_index+1)
##        print "backward", i

        j = negative_second_index-i

        p = np.poly1d(np.polyfit(populationX[j+1:j+3],phases[j+1:j+3],1))

        pval = p(populationX[j])
        fval = phases[j]

        minimum = np.abs(pval - fval)

        while True:
            if pval > fval:
                fval += 1
            else:
                fval -= 1
            new_minimum = np.abs(pval - fval)
            if new_minimum < minimum:
                minimum = new_minimum
                phases[j] = fval
            else:
                break

    return phases



def phaseUnwrap2D(sample_row_pixel_lst, \
                  sample_col_pixel_lst, \
                  sample_phaseMap, \
                  population_row_pixel_lst, \
                  population_col_pixel_lst, \
                  population_phaseMap, \
                  fit_directory_path):

    numRows_sample = sample_row_pixel_lst.size
    numCols_sample = sample_col_pixel_lst.size
    numRows_population = population_row_pixel_lst.size
    numCols_population = population_col_pixel_lst.size


    phase_column0_index = np.where(population_col_pixel_lst == sample_col_pixel_lst[0])[0][0]
    phase_column1_index = phase_column0_index+1

    phase_column0 = phaseUnwrap1D(sample_row_pixel_lst, \
                                  sample_phaseMap[:,0], \
                                  population_row_pixel_lst, \
                                  population_phaseMap[:,phase_column0_index])
    phase_column1 = phaseUnwrap1D(sample_row_pixel_lst, \
                                  sample_phaseMap[:,-1], \
                                  population_row_pixel_lst, \
                                  population_phaseMap[:,phase_column1_index])

    plt.plot(phase_column0,'b.')
    plt.plot(phase_column1,'r.')
    plt.savefig(os.path.join(fit_directory_path, "column0_column1.png"))
    plt.close()


    phases = np.zeros(population_phaseMap.shape)

    
    phases[:,phase_column0_index] = phase_column0
    phases[:,phase_column1_index] = phase_column1


    for r in np.arange(numRows_population):
        phases[r,:] = phaseUnwrap1D(population_col_pixel_lst[phase_column0_index:phase_column1_index+1], \
                                    phases[r, phase_column0_index:phase_column1_index+1], \
                                    population_col_pixel_lst, \
                                    population_phaseMap[r,:])



        #plot
        for i in np.arange(5)-2:
            b = population_phaseMap[r,:]+i
            plt.plot(population_col_pixel_lst, b,'g.')
        plt.plot(population_col_pixel_lst, population_phaseMap[r,:],'r.')

        plt.plot([0, 608],[0,0],'k--')
        plt.plot([0, 608],[1,1],'k--')
        plt.plot([0, 608],[-1,-1],'k--')
        
        plt.plot(np.array([sample_col_pixel_lst[0], sample_col_pixel_lst[-1]]),phases[r, phase_column0_index:phase_column1_index+1],'b.')
        


        plt.plot(population_col_pixel_lst,phases[r,:],'r-')

        title = "row_%d" % r
        plt.suptitle(title)
        
        plt.savefig(os.path.join(fit_directory_path, title + ".png"))
        plt.close()


    return phases





##hologram_directory_path = r"C:\Users\Bert\slm_data\simulated_hologram_5_5"
##
### Get row and column information 
##with open(os.path.join(hologram_directory_path, "row_pixel_lst.txt"), 'r') as f:
##    row_pixel_lst = pickle.load(f)
##with open(os.path.join(hologram_directory_path, "col_pixel_lst.txt"), 'r') as f:
##    col_pixel_lst = pickle.load(f)
##    
####print "row_pixel_lst", row_pixel_lst
####print "col_pixel_lst", col_pixel_lst
##
##fit_directory_path = r"C:\Users\Bert\slm_data\simulated_fit_5_5"
### Get phaseMap
##with open(os.path.join(fit_directory_path, "phaseMap_2pi_normalized.txt"), 'r') as f:
##    phaseMap_2pi_normalized = pickle.load(f)
##
##
##sample_row_pixel_lst = row_pixel_lst[2:4]
##sample_col_pixel_lst = col_pixel_lst[2:4]
##sample_phaseMap = phaseMap_2pi_normalized[2:4,2:4]
##
##population_row_pixel_lst = row_pixel_lst
##population_col_pixel_lst = col_pixel_lst
##population_phaseMap = phaseMap_2pi_normalized
##
##
##phaseMap = phaseUnwrap2D(sample_row_pixel_lst, \
##                         sample_col_pixel_lst, \
##                         sample_phaseMap, \
##                         population_row_pixel_lst, \
##                         population_col_pixel_lst, \
##                         population_phaseMap)
##
##
##print sample_phaseMap
##
##print population_phaseMap
##
##print phaseMap
##
##
##plt.imshow(sample_phaseMap, interpolation="nearest")
##plt.colorbar()
##plt.show()
##
##plt.imshow(population_phaseMap, interpolation="nearest")
##plt.colorbar()
##plt.show()
##
##plt.imshow(phaseMap, interpolation="nearest")
##plt.colorbar()
##plt.show()
##              
##
##
##    
##        
##    
##


##def func(lst):
##    return (lst*(2*np.pi/10))
##
##popX = np.arange(10)
##popY = func(popX) +np.random.rand(10)/2.
##
##samX = np.linspace(4,5,4)
##samY = func(samX) + np.random.rand(4)/2.
##
##
##plt.plot(popX,popY,'g.')
##plt.plot(samX,samY,'b.')
##
##b = popY
##b1 = b+1
##b2 = b+2
##b3 = b+3
##b4 = b+4
##b5 = b-1
##b6 = b-2
##b7 = b-3
##b8 = b-4
##b9 = b-5
##b10 = b-6
##
##plt.plot(popX,b1,'g.', \
##         popX,b2,'g.', \
##         popX,b3,'g.', \
##         popX,b4,'g.', \
##         popX,b5,'g.', \
##         popX,b6,'g.', \
##         popX,b7,'g.', \
##         popX,b8,'g.', \
##         popX,b9,'g.', \
##         popX,b10,'g.')
##
##phases = phaseUnwrap1D(samX,samY,popX,popY)
##
##plt.plot(popX,phases,'r-')
##
##plt.show()


def getNeighbors(r,c,someArray):
    numRows, numCols = someArray.shape

    r_min = max(0,r-1)
    r_max = min(numRows,r+1)

    c_min = max(0,c-1)
    c_max = min(numCols,c+1)

    newArray = someArray[r_min:r_max+1,c_min:c_max+1].flatten()

    return np.delete(newArray, np.where(newArray==someArray[r,c])[0][0])
    

def removeZero(someArray):
    numRows, numCols = someArray.shape
    for r in np.arange(numRows):
        for c in np.arange(numCols):
            if someArray[r,c] == 0:
                someArray[r,c] = np.mean(getNeighbors(r,c,someArray))
    return someArray


def unwrapPixel(someArray):
    numRows, numCols = someArray.shape

    for r in np.arange(numRows):
        for c in np.arange(numCols):
            val = someArray[r,c]
            mean = np.mean(getNeighbors(r,c,someArray))
            diff = np.abs(val-mean)
            while True:
                if val > mean:
                    val -= 1
                else:
                    val += 1
                new_diff = np.abs(val-mean)
                if new_diff < diff:
                    diff = new_diff
                    someArray[r,c] = val
                else:
                    break
    return someArray











    
