#helperfunctions.py
import numpy as np
from scipy import stats
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import math

def fitfunc(x, TotFluor, xc, sigma, offset, slope): #THIS IS THE FIT FUNCTION
    return (TotFluor/(math.sqrt(2.0*math.pi)*sigma)) * np.exp(-((x-xc)**2)/(2*(sigma**2))) + offset + (x-xc)*slope

def fitfunc_guess(indsIN, heightsIN): #THIS GENERATES INITIAL GUESSES FOR THE FIT ROUTINE!
    weightArray = heightsIN
    if (sum(weightArray) == 0.0):
      weightArray = np.ones(len(heightsIN))
      print("Weights sum to zero, setting to ones")
    try:  
      meanGuess=np.average(indsIN, weights=weightArray)
      sGuess =math.sqrt( np.abs(np.average((indsIN-meanGuess)**2, weights = weightArray)))#need abs because weights can be negative
      ampGuess=max(heightsIN)-min(heightsIN)
      OffsetGuess=min(heightsIN)
      totfluorGuess=math.sqrt(2.0*math.pi)*ampGuess*sGuess
      return [totfluorGuess, meanGuess, sGuess, OffsetGuess, 0]
    except ZeroDivisionError:
      return [0, 0, 0, 0, 0]



def stringpad(sin, lmin):
    #PAD string sin up to a minimum length of lmin with spaces " " useful for formatting output data. TRUNCATES to lmin if longer!
    sout=str(sin)
    while len(sout)<lmin:
        sout+=" "
    return sout[0:lmin] #THIS TRUNCATES TO THE FIRST lmin CHARACTERS!


def to_precision(x, p):
    """
        returns a string representation of x formatted with a precision of p --useful for formatted data output with fixed number of digits!
        
        Based on the webkit javascript implementation taken from here:
        https://code.google.com/p/webkit-mirror/source/browse/JavaScriptCore/kjs/number_object.cpp
        """
    
    x = float(x)
    if x == 0.:
        return "0." + "0"*(p-1)
    out = []
    if x < 0:
        out.append("-")
        x = -x
    e = int(math.log10(x))
    tens = math.pow(10, e - p + 1)
    n = math.floor(x/tens)
    if n < math.pow(10, p - 1):
        e = e -1
        tens = math.pow(10, e - p+1)
        n = math.floor(x / tens)
    if abs((n + 1.) * tens - x) <= abs(n * tens -x):
        n = n + 1
    if n >= math.pow(10,p):
        n = n / 10.
        e = e + 1
    m = "%.*g" % (p, n)
    if e < -2 or e >= p:
        out.append(m[0])
        if p > 1:
            out.append(".")
            out.extend(m[1:p])
        out.append('e')
        if e > 0:
            out.append("+")
        out.append(str(e))
    elif e == (p -1):
        out.append(m)
    elif e >= 0:
        out.append(m[:e+1])
        if e+1 < len(m):
            out.append(".")
            out.extend(m[e+1:])
    else:
        out.append("0.")
        out.extend(["0"]*-(e+1))
        out.append(m)
    return "".join(out)