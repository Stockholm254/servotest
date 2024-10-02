# fit X,Y,Z to a 2D gaussian
from scipy.optimize import curve_fit
import numpy as np
import matplotlib.pyplot as plt


def gaussian_2d(x: float, y: float, mu, cov) -> float:
    inv_cov = np.linalg.inv(cov)
    det_cov = float(np.linalg.det(cov))
    r = np.array([x, y]).T - mu
    z = np.exp(-0.5 * (r @ inv_cov @ r.T))
    coeff = 1 / (2 * np.pi * np.sqrt(det_cov))
    return coeff * z

def gaussian_2d_smooth_heaviside(x: float, y: float, mu, cov, transition_width) -> float:
    inv_cov = np.linalg.inv(cov)
    r = np.array([x, y]) - mu
    quadratic_form = r.T @ inv_cov @ r

    # Define a smooth transition using a sigmoid-like function
    smooth_transition = 1 / (1 + np.exp((quadratic_form - 1) / transition_width))

    return smooth_transition



def statistics_for_gaussian2d(xdata, ydata, Idata):
    # Flatten the arrays in case they are not 1D
    xdata = xdata.flatten()
    ydata = ydata.flatten()
    Idata = Idata.flatten()

    # Calculate the sum of the data values
    sum_I = np.sum(Idata)

    # Calculate the weighted mean (mu)
    mu_x = np.sum(xdata * Idata) / sum_I
    mu_y = np.sum(ydata * Idata) / sum_I
    mu = np.array([mu_x, mu_y])

    # Center the coordinates by subtracting the mean
    x_centered = xdata - mu_x
    y_centered = ydata - mu_y

    # Calculate the elements of the covariance matrix
    sigma_xx = np.sum(Idata * x_centered * x_centered) / sum_I
    sigma_xy = np.sum(Idata * x_centered * y_centered) / sum_I
    sigma_yy = np.sum(Idata * y_centered * y_centered) / sum_I

    # Assemble the covariance matrix (cov)
    cov = np.array([[sigma_xx, sigma_xy],
                    [sigma_xy, sigma_yy]])

    return mu, cov


def fit_gaussian_2d(X,Y,Z,p0=None):
    X = np.array(X)
    Y = np.array(Y)
    Z = np.array(Z)
    # fit to gaussian_2d_cov using least square
    def _residuals(p, x, y, z):
        mu = p[:2]
        cov = np.array([[p[2], p[3]], [p[3], p[4]]])
        z_fit = np.array([gaussian_2d(x_, y_, mu, cov) for x_, y_ in zip(x, y)])
        return z - z_fit

    xdata = np.array(X).flatten()
    ydata = np.array(Y).flatten()
    zdata = np.array(Z).flatten()

    if p0 is None:
        mu, cov = statistics_for_gaussian2d(X, Y, Z)
        p0 = np.array([mu[0], mu[1], cov[0, 0], cov[0, 1], cov[1, 1]])
        print("Initial guess for p0: ", p0)

    from scipy.optimize import least_squares

    res = least_squares(_residuals, p0, args=(xdata, ydata, zdata))
    popt = res.x
    return popt

def fit_gaussian_2d_smooth_heaviside(X,Y,Z,p0=None):
    X = np.array(X)
    Y = np.array(Y)
    Z = np.array(Z)
    # fit to gaussian_2d_cov using least square
    def _residuals(p, x, y, z):
        mu = p[:2]
        cov = np.array([[p[2], p[3]], [p[3], p[4]]])
        z_fit = np.array([gaussian_2d_smooth_heaviside(x_, y_, mu, cov, p[5]) for x_, y_ in zip(x, y)])
        return z - z_fit

    xdata = np.array(X).flatten()
    ydata = np.array(Y).flatten()
    zdata = np.array(Z).flatten()

    if p0 is None:
        mu, cov = statistics_for_gaussian2d(X, Y, Z)
        p0 = np.array([mu[0], mu[1], cov[0, 0], cov[0, 1], cov[1, 1], 0.1])
        print("Initial guess for p0: ", p0)

    from scipy.optimize import least_squares

    res = least_squares(_residuals, p0, args=(xdata, ydata, zdata))
    popt = res.x
    return popt


def fit_and_plot(X,Y,Z,p0=None):
    popt = fit_gaussian_2d(X,Y,Z,p0=p0)
    bounds_x = (np.min(X),np.max(X))
    bounds_y = (np.min(Y),np.max(Y))
    X_new = np.linspace(*bounds_x,100)
    Y_new = np.linspace(*bounds_y,100)
    X_new,Y_new = np.meshgrid(X_new,Y_new)
    Z_new = np.array([gaussian_2d(x_,y_,popt[:2],np.array([[popt[2],popt[3]],[popt[3],popt[4]]]) ) for x_,y_ in zip(X_new.ravel(),Y_new.ravel())])
    #
    plt.imshow(Z.reshape(X.shape)/np.max(Z),origin="lower",extent=[bounds_x[0],bounds_x[1],bounds_y[0],bounds_y[1]])
    plt.contour(X_new,Y_new,Z_new.reshape(X_new.shape),cmap="jet")
    return popt

def fit_and_plot_smooth_heaviside(X,Y,Z,p0=None):
    popt = fit_gaussian_2d_smooth_heaviside(X,Y,Z,p0=p0)
    bounds_x = (np.min(X),np.max(X))
    bounds_y = (np.min(Y),np.max(Y))
    X_new = np.linspace(*bounds_x,100)
    Y_new = np.linspace(*bounds_y,100)
    X_new,Y_new = np.meshgrid(X_new,Y_new)
    Z_new = np.array([gaussian_2d_smooth_heaviside(x_,y_,popt[:2],np.array([[popt[2],popt[3]],[popt[3],popt[4]]]), popt[5]) for x_,y_ in zip(X_new.ravel(),Y_new.ravel())])
    #
    plt.imshow(Z.reshape(X.shape)/np.max(Z),origin="lower",extent=[bounds_x[0],bounds_x[1],bounds_y[0],bounds_y[1]])
    plt.contour(X_new,Y_new,Z_new.reshape(X_new.shape),cmap="jet")
    return popt

if __name__ == "__main__":
    # test
    x = np.linspace(-1,1,20)
    y = np.linspace(-1,1,20)
    X,Y = np.meshgrid(x,y)
    Z = gaussian_2d((X,Y),1,0,0,0.5,0.5,0,0)
    popt = fit_gaussian_2d(X,Y,Z)
    print(popt)
