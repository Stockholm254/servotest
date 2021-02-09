import numpy as np

class DataGenerator:
    def __init__(self, func, df=20., nbins=1000):
        self.nbins = nbins
        self.x = np.linspace(-df, df, nbins+1, endpoint=True) #yields 1024 bins for the counter
        y = func(self.x)
        yc = np.cumsum(y)
        yc *= 1/yc[-1]
        self.y = y
        self.yc = yc
        
    def sample(self, nsamples=1):
        samp = np.empty(nsamples)
        for i in range(nsamples):
            idx = np.where(np.random.rand()<=self.yc)[0][0]
            samp[i] = self.x[idx]
        return samp
    
    def hist(self, nsamples=1):
        frequencies, edges = np.histogram(self.sample(nsamples), bins=self.x)
        return 0.5*(edges[1:]+edges[:-1]), frequencies

def Lorentzian(x, x0=0., gamma=1.):
    return 1/np.pi*0.5*gamma/((x-x0)**2 + (0.5*gamma)**2)

def samplefunc(x, vrs=10., x0=0.):
    return Lorentzian(x-x0,-vrs, 1.3) + Lorentzian(x-x0,vrs-2, 1.7) + Lorentzian(x-x0,0, 0.2)