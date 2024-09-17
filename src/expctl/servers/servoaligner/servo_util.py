import numpy as np

def create_zigzag_X(X):
    X_zigzag = np.copy(X)  # Create a copX of X to modifX
    index_map = np.zeros_like(X, dtype=int)  # To track the original indices, elements in X_zigzag and their original index in X

    # Alter rows in a zigzag pattern
    for i in range(X_zigzag.shape[0]):
        if i % 2 == 0:
            # Even rows: keep as is
            X_zigzag[i, :] = X[i, :]
            index_map[i, :] = np.arange(X_zigzag.shape[1]) + i * X_zigzag.shape[1]
        else:
            # Odd rows: reverse the order
            X_zigzag[i, :] = np.flip(X[i, :])
            index_map[i, :] = np.flip(np.arange(X_zigzag.shape[1])) + i * X_zigzag.shape[1]
    return X_zigzag, index_map

def a2p(angle):
    return int(angle*(4096/360)+2048)

def xy2nd(x,y,xy_mask):
    # assert there are only 2 "1" in the mask
    assert sum(xy_mask) == 2
    x_idx = np.where(xy_mask)[0][0]
    y_idx = np.where(xy_mask)[0][1]
    pos = np.ones(len(xy_mask),dtype=np.int_)*a2p(0)
    pos[x_idx] = a2p(x)
    pos[y_idx] = a2p(y)
    return pos

# ADS1115_fiber
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_ads1x15.ads1115 as ADS1115
import adafruit_ads1x15
import board
import busio
import time

# Create the I2C bus interface
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADS1115 instance
ads = ADS1115.ADS1115(i2c)
# PDA8A with 50 ohm load, will be 0 - 1.8 V
# ADS1115.PGA_2: ±2.048V
ads.gain = 4
ads.data_rate = 860

# Create analog input channels
ADS1115_fiber = AnalogIn(ads, ADS1115.P0)  # Channel 0

print(f"Fiber channel reading: {ADS1115_fiber.value}")

t0 = time.time()
for i in range(100):
    # print(f"Fiber channel reading: {ADS1115_fiber.value}")
    a= ADS1115_fiber.value
t1 = time.time()
print(f"Time elapsed: {t1-t0}")

# fit X,Y,Z to a 2D gaussian
from scipy.optimize import curve_fit

def gaussian_2d(xy, amplitude, xo, yo, sigma_x, sigma_y, theta, offset):
    x, y = xy
    a = (np.cos(theta)**2)/(2*sigma_x**2) + (np.sin(theta)**2)/(2*sigma_y**2)
    b = -(np.sin(2*theta))/(4*sigma_x**2) + (np.sin(2*theta))/(4*sigma_y**2)
    c = (np.sin(theta)**2)/(2*sigma_x**2) + (np.cos(theta)**2)/(2*sigma_y**2)
    g = offset + amplitude*np.exp( - (a*((x-xo)**2) + 2*b*(x-xo)*(y-yo) + c*((y-yo)**2)))
    return g.ravel()


def fit_gaussian_2d(X,Y,Z):
    X = np.array(X)
    Y = np.array(Y)
    Z = np.array(Z)
    xydata = np.vstack([X.ravel(),Y.ravel()])
    zdata = Z.ravel()
    popt, pcov = curve_fit(gaussian_2d, xydata, zdata)
    return popt

