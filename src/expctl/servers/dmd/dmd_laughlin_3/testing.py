import CavityModes as CM
import string
import matplotlib.pyplot as plt
import numpy as np


testfile = "C:\\Users\\RydFries\\Documents\\DMD_code_forlaugh\\UpperModeProfiles\\dmode_6,0.txt"

# test = lambda s: np.complex(s.translate(translation))

#
# print fixer("1.531*^-05*I")
# a = np.loadtxt(testfile, converters={2: fixer}, dtype=complex)
# print a

x=np.linspace(-200, 200, 100)
xx, yy = np.meshgrid(x, x)

a=CM.NPCMode((1,0.5), 0, 0, 50, defocus = 0.5, tilt=[0.0,0.0])
test = [[0],[0]]
b = a.modeProfile([xx, yy])

thefig = plt.figure(num=101, figsize = (5,5))
plt.clf()
plt.subplot(2,1,1)
theplot = plt.imshow(np.abs(b))
plt.colorbar()
plt.subplot(2,1,2)
plt.imshow(np.angle(b))
plt.colorbar()


##%%
#
#plt.figure(num=102)
#avg = np.mean(np.abs(b), axis=0)
#plt.plot(x, avg/np.max(avg)*np.exp(2), 'b')
#
##%%
#
#
#a=CM.HGMode(50, 50, 0,0,0,0,0,0)
#
#b = a.modeProfile([xx, yy])
#
##theplot = plt.imshow(np.abs(b))
#avg = np.mean(np.abs(b), axis=1)
#plt.plot(x, avg/np.max(avg)*np.exp(2), 'r')
