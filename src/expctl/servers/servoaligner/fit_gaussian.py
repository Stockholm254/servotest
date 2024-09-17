# fit X,Y,Z to a 2D gaussian
from scipy.optimize import curve_fit
import numpy as np
import matplotlib.pyplot as plt

def gaussian_2d(xy, amplitude, xo, yo, sigma_x, sigma_y, theta, offset):
    x, y = xy
    a = (np.cos(theta)**2)/(2*sigma_x**2) + (np.sin(theta)**2)/(2*sigma_y**2)
    b = -(np.sin(2*theta))/(4*sigma_x**2) + (np.sin(2*theta))/(4*sigma_y**2)
    c = (np.sin(theta)**2)/(2*sigma_x**2) + (np.cos(theta)**2)/(2*sigma_y**2)
    g = offset + amplitude*np.exp( - (a*((x-xo)**2) + 2*b*(x-xo)*(y-yo) + c*((y-yo)**2)))
    return g.ravel()


def fit_gaussian_2d(X,Y,Z,p0=None):
    X = np.array(X)
    Y = np.array(Y)
    Z = np.array(Z)
    xydata = np.vstack([X.ravel(),Y.ravel()])
    zdata = Z.ravel()
    popt, pcov = curve_fit(gaussian_2d, xydata, zdata,p0=p0)
    return popt

def fit_and_plot(X,Y,Z,p0=None):
    popt = fit_gaussian_2d(X,Y,Z,p0=p0)
    bounds_x = (np.min(X),np.max(X))
    bounds_y = (np.min(Y),np.max(Y))
    X_new = np.linspace(*bounds_x,100)
    Y_new = np.linspace(*bounds_y,100)
    X_new,Y_new = np.meshgrid(X_new,Y_new)
    Z_new = gaussian_2d((X_new,Y_new),*popt)
    #
    plt.imshow(Z_new.reshape(X_new.shape)/np.max(Z_new),origin="lower",extent=[bounds_x[0],bounds_x[1],bounds_y[0],bounds_y[1]])
    plt.contour(X_new,Y_new,Z_new.reshape(X_new.shape),cmap="jet")