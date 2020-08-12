import numpy as np
import matplotlib.pyplot as plt
import inspect
from scipy import signal

#################################################################################
#                                    Utilities                                  #
#################################################################################

def FWHM(xdata, ydata):
	return 1

def find_peaks(data_array, CWT=np.array([9,10])):
	CWT_array = CWT
	peakind = signal.find_peaks_cwt(data_array, CWT_array)
	return peakind

def fix_func(func, fixed):
	'''
	Fix some parameters of a function, and return a new function.

	Parameters
	----------
	func: function
	fixed: [(variable name, value), ...]

	Returns
	----------
	out: function with specified varables fixed
	'''
	funcname = func.__name__

	fixname = np.array(fixed)[::, 0]
	fixval  = np.array(fixed)[::, 1]

	raw_parms = np.array(inspect.getargspec(func)[0][1:])
	parms = raw_parms
	fix_ind = np.where(np.in1d(parms, fixname))

	unfixed_parms = np.delete(parms, fix_ind)
	np.put(parms, fix_ind, fixval)

	fstr = 'lambda x,'+','.join(list(unfixed_parms))+":"+funcname+'(x,'+','.join(list(parms))+')'

	return eval(fstr)

#################################################################################
#                   Math functions and guessing fuctions                        #
#################################################################################

__functions__ = ['Lorentzian', 'Gaussian', 'VRS', 'EIT', 'EIT_FixG', 'EIT_NewCav', 'EIT_CavPk', 'TwoLorentzian']

def EIT_FixG(xx, g_val):
	return fix_func(EIT, ['g', g_val])

def Lorentzian(x, x0, Gamma, amp, offset):
	f = amp/np.pi*Gamma/2./((x-x0)**2.+(Gamma/2.)**2.)+offset
	return f

def Lorentzian_guess(xdata, ydata):
	peak_val = max(ydata)
	peak_ind = np.argmax(ydata)
	min_val  = min(ydata)
	hm_val = min_val+(peak_val-min_val)/2.

	if peak_ind != 0:
		hml_ind = np.argmin(abs(ydata[0:peak_ind]-hm_val))
		hml_val = xdata[hml_ind]
	else:
		hml_ind = np.argmin(abs(ydata-hm_val))
		hml_val = xdata[0]-xdata[hmr_ind]
	if peak_ind != len(ydata)-1:
		hmr_ind = np.argmin(abs(ydata[peak_ind:len(ydata)]-hm_val))+peak_ind
		hmr_val = xdata[hmr_ind]
	else:
		hmr_ind = np.argmin(abs(ydata-hm_val))
		hmr_val = 2*xdata[-1]-xdata[hmr_ind]

	x0_guess     = xdata[peak_ind]
	Gamma_guess  = abs(hmr_val-hml_val)
	amp_guess    = (peak_val-min_val)*np.pi*Gamma_guess/2.
	offset_guess = np.amin(ydata)

	guesses = [x0_guess, Gamma_guess, amp_guess, offset_guess]

	return guesses

def Gaussian(x, x0, sigma, amp, offset):
	f = amp/(sigma*np.sqrt(2*np.pi))*np.exp(-(x-x0)**2/(2*sigma**2))+offset
	return f

def VRS(d, d0, dc, g, a, c): # Fitting function
	Gamma = 6.065 # From Daniel Steck's paper
	# kappa = 2.0 # For Albert's four mirror cavity
	# kappa = 1.6 # For Nathan's planar four mirror cavity
	kappa = 1.3 # Nathan's cavity #2 
	return a*(kappa/2.)**2*4*(Gamma**2+4*(d-d0)**2)/(16*g**4+8*g**2*(-4*(d-d0)*((d-d0)+dc)+Gamma*kappa)+(Gamma**2+4*(d-d0)**2)*(4*((d-d0)+dc)**2+kappa**2))+c

def VRS_guess(xdata, ydata):
	peak_ind = np.array(find_peaks(ydata[1:])) #Get rid of the first data point which is always 1 to avoid confusing
	if len(peak_ind) == 1: #If the cavity is far detuned, there might be only one peak. To compensate that, append a virtual peak a the middle.
		peak_ind = np.append(peak_ind, len(ydata)/2)
	peak_ind = sorted(peak_ind, key=lambda x:-ydata[x]) #Find the two maximum peak which corresponds to the real VRS peaks

	d0_guess = 0
	dc_guess = -(xdata[peak_ind[0]+1]+xdata[peak_ind[1]+1])
	g_guess  = abs(xdata[peak_ind[0]+1]-xdata[peak_ind[1]+1])/2
	a_guess  = 10*max(ydata)
	c_guess  = 0

	guesses = [d0_guess, dc_guess, g_guess, a_guess, c_guess] # For VRS fitting

	return guesses

def EIT(d, d0, dc, dr, gamma, g, Omega, amp, offset):
	# kappa = 1.7 # Albert's cavity
	# kappa = 1.5 # Nathan's cavity
	kappa = 1.3 # Nathan's cavity #2
	Gamma = 6.065

	tgamma = (d-d0)+dr+1j*gamma/2
	tkappa = (d-d0)+dc+1j*kappa/2
	tGamma = (d-d0)+1j*Gamma/2

	y = amp*(kappa/2)**2*abs(1/(tkappa-g**2*(tgamma/(tGamma*tgamma-Omega**2))))**2+offset
	return y

def EIT_NewCav(d, d0, dc, dr, gamma, g, Omega, amp, offset):
	# kappa = 1.7 # Albert's cavity
	kappa = 1.3 # Nathan's cavity
	Gamma = 6.065

	tgamma = (d-d0)+dr+1j*gamma/2
	tkappa = (d-d0)+dc+1j*kappa/2
	tGamma = (d-d0)+1j*Gamma/2

	y = amp*(kappa/2)**2*abs(1/(tkappa-g**2*(tgamma/(tGamma*tgamma-Omega**2))))**2+offset
	return y

def EIT_CavPk(d, d0, dc, dr, gamma, g, Omega, amp, offset, d0_cav, amp_cav):
	kappa = 1.3 # Nathan's cavity #2
	Gamma = 6.065

	tgamma = (d-d0)+dr+1j*gamma/2
	tkappa = (d-d0)+dc+1j*kappa/2
	tGamma = (d-d0)+1j*Gamma/2

	
	y = amp*(kappa/2)**2*abs(1/(tkappa-g**2*(tgamma/(tGamma*tgamma-Omega**2))))**2\
		+amp_cav/np.pi*Gamma/2./((d-d0_cav)**2.+(Gamma/2.)**2.)+offset
	return y

def Polynomial(x, *args):
	c = args[0]
	f = np.sum(np.array([c[ii]*x**ii for ii in range(len(c))]), axis=0)
	return f

def ExpDecay(t, t0, tau, amp, offset):
	return amp*np.exp(-(t-t0)/tau)+offset

def DCStark(E, E0, alpha, d0):
	return 1./2.*alpha*(E-E0)**2+d0

def TwoLorentzian(x, x1, x2, Gamma1, Gamma2, amp1, amp2, offset):
	f = amp1/np.pi*Gamma1/2./((x-x1)**2.+(Gamma1/2.)**2.)+amp2/np.pi*Gamma2/2./((x-x2)**2.+(Gamma2/2.)**2.)+offset
	return f