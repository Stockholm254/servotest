#!/usr/bin/python
# -*- coding: utf-8 -*-

## All numbers from Daniel Steck's data

import numpy as np
pi = np.pi

####################################
## Fundamental Physical Constants ##
####################################
c = 2.99792458e8 # Speed of light in m/s
mu_0 = 4*pi*1e-7 # Permeability of vacuum in N/A^2
epsilon_0 = 1/(mu_0*c**2) # Permittivity of vacuum in F/m
h = 6.62606876e-34 # Planck's constant in J*s
hbar = 1.054571596e-34 # Planck's constant in J*s
e = 1.602176462e-19 # Elementary charge in C
mu_B = 1.399624624 # Bohr magneton in MHz/G
u = 1.66053873e-27 # Atomic mass unit in kg
m_e = 5.485799110e-4*u # Electron mass in kg
a_0 = 0.5291772083e-10 # Bohr radius in m
k_B = 1.3806503e-23 # Boltzmann's constant in J/K

############################################
## Rb-87 D2 Transition Optical Properties ##
############################################
omega_0 = 2*pi*384.2304844685 # Transition frequency in THz
lambda_vac = 780.241209686 # Wavelength (cavuum) in nm
Gamma_Rb = 2*pi*6.065 # Natural line width (FWHM) in MHz
