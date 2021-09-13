#!/usr/bin/python
# -*- coding: utf-8 -*-
import copy
from math import floor

from expctl.dat.all_channels import TriggerOut
from expctl.sequencer.sequence import Interval

#### Modifiable Variables ####
# Note: values must be integers or floats.

# Tab:Trigger_time
MV(Trigger_time_us, min=1., max=100., init=10., inc=1., digits=3)

# Tab:Digital_val
MV(Digital_val_time_us, min=0., max=1000., init=100., inc=1., digits=4)
MV(DCh01_val, min=0., max=1., init=1., inc=1., digits=1)
MV(DCh02_val, min=0., max=1., init=1., inc=1., digits=1)
MV(DCh03_val, min=0., max=1., init=1., inc=1., digits=1)
MV(DCh04_val, min=0., max=1., init=1., inc=1., digits=1)
MV(DCh05_val, min=0., max=1., init=1., inc=1., digits=1)
MV(DCh06_val, min=0., max=1., init=1., inc=1., digits=1)
MV(DCh07_val, min=0., max=1., init=1., inc=1., digits=1)
MV(DCh08_val, min=0., max=1., init=1., inc=1., digits=1)
MV(DCh09_val, min=0., max=1., init=1., inc=1., digits=1)
MV(DCh10_val, min=0., max=1., init=1., inc=1., digits=1)
MV(DCh11_val, min=0., max=1., init=1., inc=1., digits=1)
MV(DCh12_val, min=0., max=1., init=1., inc=1., digits=1)
MV(DCh13_val, min=0., max=1., init=1., inc=1., digits=1)
MV(DCh14_val, min=0., max=1., init=1., inc=1., digits=1)

# Tab:Digital_freq
MV(Digital_freq_time_us, min=0., max=10000., init=1000., inc=1., digits=4)
MV(DCh01_MHz, min=0., max=125., init=100., inc=1., digits=3)
MV(DCh02_MHz, min=0., max=125., init=100., inc=1., digits=3)
MV(DCh03_MHz, min=0., max=125., init=100., inc=1., digits=3)
MV(DCh04_MHz, min=0., max=125., init=100., inc=1., digits=3)
MV(DCh05_MHz, min=0., max=125., init=100., inc=1., digits=3)
MV(DCh06_MHz, min=0., max=125., init=100., inc=1., digits=3)
MV(DCh07_MHz, min=0., max=125., init=100., inc=1., digits=3)
MV(DCh08_MHz, min=0., max=125., init=100., inc=1., digits=3)
MV(DCh09_MHz, min=0., max=125., init=100., inc=1., digits=3)
MV(DCh10_MHz, min=0., max=125., init=100., inc=1., digits=3)
MV(DCh11_MHz, min=0., max=125., init=100., inc=1., digits=3)
MV(DCh12_MHz, min=0., max=125., init=100., inc=1., digits=3)
MV(DCh13_MHz, min=0., max=125., init=100., inc=1., digits=3)
MV(DCh14_MHz, min=0., max=125., init=100., inc=1., digits=3)

# Tab:Analog_val
MV(Analog_val_time_ms, min=0., max=1000., init=100., inc=1., digits=4)
MV(ACh00_val, min=-10., max=10., init=0., inc=1., digits=3)
MV(ACh01_val, min=-10., max=10., init=0., inc=1., digits=3)
MV(ACh02_val, min=-10., max=10., init=0., inc=1., digits=3)
MV(ACh03_val, min=-10., max=10., init=0., inc=1., digits=3)
MV(ACh04_val, min=-10., max=10., init=0., inc=1., digits=3)
MV(ACh05_val, min=-10., max=10., init=0., inc=1., digits=3)
MV(ACh06_val, min=-10., max=10., init=0., inc=1., digits=3)
MV(ACh07_val, min=-10., max=10., init=0., inc=1., digits=3)
MV(ACh08_val, min=-10., max=10., init=0., inc=1., digits=3)
MV(ACh09_val, min=-10., max=10., init=0., inc=1., digits=3)
MV(ACh10_val, min=-10., max=10., init=0., inc=1., digits=3)
MV(ACh11_val, min=-10., max=10., init=0., inc=1., digits=3)
MV(ACh12_val, min=-10., max=10., init=0., inc=1., digits=3)
MV(ACh13_val, min=-10., max=10., init=0., inc=1., digits=3)
MV(ACh14_val, min=-10., max=10., init=0., inc=1., digits=3)
MV(ACh15_val, min=-10., max=10., init=0., inc=1., digits=3)

# Tab:Analog_freq
MV(Analog_freq_time_ms, min=0., max=2000., init=1000., inc=10., digits=4)
MV(ACh00_kHz, min=0., max=15., init=5., inc=1., digits=3)
MV(ACh01_kHz, min=0., max=15., init=5., inc=1., digits=3)
MV(ACh02_kHz, min=0., max=15., init=5., inc=1., digits=3)
MV(ACh03_kHz, min=0., max=15., init=5., inc=1., digits=3)
MV(ACh04_kHz, min=0., max=15., init=5., inc=1., digits=3)
MV(ACh05_kHz, min=0., max=15., init=5., inc=1., digits=3)
MV(ACh06_kHz, min=0., max=15., init=5., inc=1., digits=3)
MV(ACh07_kHz, min=0., max=15., init=5., inc=1., digits=3)
MV(ACh08_kHz, min=0., max=15., init=5., inc=1., digits=3)
MV(ACh09_kHz, min=0., max=15., init=5., inc=1., digits=3)
MV(ACh10_kHz, min=0., max=15., init=5., inc=1., digits=3)
MV(ACh11_kHz, min=0., max=15., init=5., inc=1., digits=3)
MV(ACh12_kHz, min=0., max=15., init=5., inc=1., digits=3)
MV(ACh13_kHz, min=0., max=15., init=5., inc=1., digits=3)
MV(ACh14_kHz, min=0., max=15., init=5., inc=1., digits=3)
MV(ACh15_kHz, min=0., max=15., init=5., inc=1., digits=3)

#### End Modifiable Variables ###n

########################################################################va
#======================== Main Instance ===============================#
########################################################################

#### Set Time Intervals ####
times = Intervaler(0.) # THIS COMMAND IS REQUIRED TO CREATE THE TIME OBJECT!
trigger = times.append(Trigger_time_us*Unit.us(), name="Trigger")
digital_val_interval = times.append(Digital_val_time_us*Unit.us(), name="Digital value")
digital_freq_interval = times.append(Digital_freq_time_us*Unit.us(), name="Digital freq")
analog_val_interval = times.append(Analog_val_time_ms*Unit.ms(), name="Analog value")
analog_freq_interval = times.append(Analog_freq_time_ms*Unit.ms(), name="Analog freq")


#### Sequence Actions ####
### Initiation ###

# Trigger
TriggerOut.SetInterval(trigger, 0)
TriggerOut.SetInterval(trigger.afterward(10*Unit.us()), 1)


# Digital seq
Digital01.SetInterval(digital_val_interval, DCh01_val)
Digital02.SetInterval(digital_val_interval, DCh02_val)
Digital03.SetInterval(digital_val_interval, DCh03_val)
Digital04.SetInterval(digital_val_interval, DCh04_val)
Digital05.SetInterval(digital_val_interval, DCh05_val)
Digital06.SetInterval(digital_val_interval, DCh06_val)
Digital07.SetInterval(digital_val_interval, DCh07_val)
Digital08.SetInterval(digital_val_interval, DCh08_val)
Digital09.SetInterval(digital_val_interval, DCh09_val)
Digital10.SetInterval(digital_val_interval, DCh10_val)
Digital11.SetInterval(digital_val_interval, DCh11_val)
Digital12.SetInterval(digital_val_interval, DCh12_val)
Digital13.SetInterval(digital_val_interval, DCh13_val)
Digital14.SetInterval(digital_val_interval, DCh14_val)

# dch01mod = [[0, 0, 0, 1], [0.5/DCh01_MHz/Unit.MHz(), 1, 0.5/DCh01_MHz/Unit.MHz(), 0], [0.5/DCh01_MHz/Unit.MHz(), 0, 1./DCh01_MHz/Unit.MHz(), 0]]
# dch02mod = [[0, 0, 0, 1], [0.5/DCh02_MHz/Unit.MHz(), 1, 0.5/DCh02_MHz/Unit.MHz(), 0], [0.5/DCh02_MHz/Unit.MHz(), 0, 1./DCh02_MHz/Unit.MHz(), 0]]
# dch03mod = [[0, 0, 0, 1], [0.5/DCh03_MHz/Unit.MHz(), 1, 0.5/DCh03_MHz/Unit.MHz(), 0], [0.5/DCh03_MHz/Unit.MHz(), 0, 1./DCh03_MHz/Unit.MHz(), 0]]
# dch04mod = [[0, 0, 0, 1], [0.5/DCh04_MHz/Unit.MHz(), 1, 0.5/DCh04_MHz/Unit.MHz(), 0], [0.5/DCh04_MHz/Unit.MHz(), 0, 1./DCh04_MHz/Unit.MHz(), 0]]
# dch05mod = [[0, 0, 0, 1], [0.5/DCh05_MHz/Unit.MHz(), 1, 0.5/DCh05_MHz/Unit.MHz(), 0], [0.5/DCh05_MHz/Unit.MHz(), 0, 1./DCh05_MHz/Unit.MHz(), 0]]
# dch06mod = [[0, 0, 0, 1], [0.5/DCh06_MHz/Unit.MHz(), 1, 0.5/DCh06_MHz/Unit.MHz(), 0], [0.5/DCh06_MHz/Unit.MHz(), 0, 1./DCh06_MHz/Unit.MHz(), 0]]
# dch07mod = [[0, 0, 0, 1], [0.5/DCh07_MHz/Unit.MHz(), 1, 0.5/DCh07_MHz/Unit.MHz(), 0], [0.5/DCh07_MHz/Unit.MHz(), 0, 1./DCh07_MHz/Unit.MHz(), 0]]
# dch08mod = [[0, 0, 0, 1], [0.5/DCh08_MHz/Unit.MHz(), 1, 0.5/DCh08_MHz/Unit.MHz(), 0], [0.5/DCh08_MHz/Unit.MHz(), 0, 1./DCh08_MHz/Unit.MHz(), 0]]
# dch09mod = [[0, 0, 0, 1], [0.5/DCh09_MHz/Unit.MHz(), 1, 0.5/DCh09_MHz/Unit.MHz(), 0], [0.5/DCh09_MHz/Unit.MHz(), 0, 1./DCh09_MHz/Unit.MHz(), 0]]
# dch10mod = [[0, 0, 0, 1], [0.5/DCh10_MHz/Unit.MHz(), 1, 0.5/DCh10_MHz/Unit.MHz(), 0], [0.5/DCh10_MHz/Unit.MHz(), 0, 1./DCh10_MHz/Unit.MHz(), 0]]
# dch11mod = [[0, 0, 0, 1], [0.5/DCh11_MHz/Unit.MHz(), 1, 0.5/DCh11_MHz/Unit.MHz(), 0], [0.5/DCh11_MHz/Unit.MHz(), 0, 1./DCh11_MHz/Unit.MHz(), 0]]
# dch12mod = [[0, 0, 0, 1], [0.5/DCh12_MHz/Unit.MHz(), 1, 0.5/DCh12_MHz/Unit.MHz(), 0], [0.5/DCh12_MHz/Unit.MHz(), 0, 1./DCh12_MHz/Unit.MHz(), 0]]
# dch13mod = [[0, 0, 0, 1], [0.5/DCh13_MHz/Unit.MHz(), 1, 0.5/DCh13_MHz/Unit.MHz(), 0], [0.5/DCh13_MHz/Unit.MHz(), 0, 1./DCh13_MHz/Unit.MHz(), 0]]
# dch14mod = [[0, 0, 0, 1], [0.5/DCh14_MHz/Unit.MHz(), 1, 0.5/DCh14_MHz/Unit.MHz(), 0], [0.5/DCh14_MHz/Unit.MHz(), 0, 1./DCh14_MHz/Unit.MHz(), 0]]
    

# Digital01.SetModulation(digital_freq_interval, dch01mod)
# Digital02.SetModulation(digital_freq_interval, dch02mod)
# Digital03.SetModulation(digital_freq_interval, dch03mod)
# Digital04.SetModulation(digital_freq_interval, dch04mod)
# Digital05.SetModulation(digital_freq_interval, dch05mod)
# Digital06.SetModulation(digital_freq_interval, dch06mod)
# Digital07.SetModulation(digital_freq_interval, dch07mod)
# Digital08.SetModulation(digital_freq_interval, dch08mod)
# Digital09.SetModulation(digital_freq_interval, dch09mod)
# Digital10.SetModulation(digital_freq_interval, dch10mod)
# Digital11.SetModulation(digital_freq_interval, dch11mod)
# Digital12.SetModulation(digital_freq_interval, dch12mod)
# Digital13.SetModulation(digital_freq_interval, dch13mod)
# Digital14.SetModulation(digital_freq_interval, dch14mod)


# Analog seq
Analog00.SetInterval(analog_val_interval, 0, ACh00_val)
Analog01.SetInterval(analog_val_interval, 0, ACh01_val)
Analog02.SetInterval(analog_val_interval, 0, ACh02_val)
Analog03.SetInterval(analog_val_interval, 0, ACh03_val)
Analog04.SetInterval(analog_val_interval, 0, ACh04_val)
Analog05.SetInterval(analog_val_interval, 0, ACh05_val)
Analog06.SetInterval(analog_val_interval, 0, ACh06_val)
Analog07.SetInterval(analog_val_interval, 0, ACh07_val)
Analog08.SetInterval(analog_val_interval, 0, ACh08_val)
Analog09.SetInterval(analog_val_interval, 0, ACh09_val)
Analog10.SetInterval(analog_val_interval, 0, ACh10_val)
Analog11.SetInterval(analog_val_interval, 0, ACh11_val)
Analog12.SetInterval(analog_val_interval, 0, ACh12_val)
Analog13.SetInterval(analog_val_interval, 0, ACh13_val)
Analog14.SetInterval(analog_val_interval, 0, ACh14_val)
Analog15.SetInterval(analog_val_interval, 0, ACh15_val)

# ach00mod = [[0, -1, 0.5/ACh00_kHz/Unit.kHz(), 1], [0.5/ACh00_kHz/Unit.kHz(), 1, 1./ACh00_kHz/Unit.kHz(), -1]]
# ach01mod = [[0, -1, 0.5/ACh01_kHz/Unit.kHz(), 1], [0.5/ACh01_kHz/Unit.kHz(), 1, 1./ACh01_kHz/Unit.kHz(), -1]]
# ach02mod = [[0, -1, 0.5/ACh02_kHz/Unit.kHz(), 1], [0.5/ACh02_kHz/Unit.kHz(), 1, 1./ACh02_kHz/Unit.kHz(), -1]]
# ach03mod = [[0, -1, 0.5/ACh03_kHz/Unit.kHz(), 1], [0.5/ACh03_kHz/Unit.kHz(), 1, 1./ACh03_kHz/Unit.kHz(), -1]]
# ach04mod = [[0, -1, 0.5/ACh04_kHz/Unit.kHz(), 1], [0.5/ACh04_kHz/Unit.kHz(), 1, 1./ACh04_kHz/Unit.kHz(), -1]]
# ach05mod = [[0, -1, 0.5/ACh05_kHz/Unit.kHz(), 1], [0.5/ACh05_kHz/Unit.kHz(), 1, 1./ACh05_kHz/Unit.kHz(), -1]]
# ach06mod = [[0, -1, 0.5/ACh06_kHz/Unit.kHz(), 1], [0.5/ACh06_kHz/Unit.kHz(), 1, 1./ACh06_kHz/Unit.kHz(), -1]]
# ach07mod = [[0, -1, 0.5/ACh07_kHz/Unit.kHz(), 1], [0.5/ACh07_kHz/Unit.kHz(), 1, 1./ACh07_kHz/Unit.kHz(), -1]]
# ach08mod = [[0, -1, 0.5/ACh08_kHz/Unit.kHz(), 1], [0.5/ACh08_kHz/Unit.kHz(), 1, 1./ACh08_kHz/Unit.kHz(), -1]]
# ach09mod = [[0, -1, 0.5/ACh09_kHz/Unit.kHz(), 1], [0.5/ACh09_kHz/Unit.kHz(), 1, 1./ACh09_kHz/Unit.kHz(), -1]]
# ach10mod = [[0, -1, 0.5/ACh10_kHz/Unit.kHz(), 1], [0.5/ACh10_kHz/Unit.kHz(), 1, 1./ACh10_kHz/Unit.kHz(), -1]]
# ach11mod = [[0, -1, 0.5/ACh11_kHz/Unit.kHz(), 1], [0.5/ACh11_kHz/Unit.kHz(), 1, 1./ACh11_kHz/Unit.kHz(), -1]]
# ach12mod = [[0, -1, 0.5/ACh12_kHz/Unit.kHz(), 1], [0.5/ACh12_kHz/Unit.kHz(), 1, 1./ACh12_kHz/Unit.kHz(), -1]]
# ach13mod = [[0, -1, 0.5/ACh13_kHz/Unit.kHz(), 1], [0.5/ACh13_kHz/Unit.kHz(), 1, 1./ACh13_kHz/Unit.kHz(), -1]]
# ach14mod = [[0, -1, 0.5/ACh14_kHz/Unit.kHz(), 1], [0.5/ACh14_kHz/Unit.kHz(), 1, 1./ACh14_kHz/Unit.kHz(), -1]]
# ach15mod = [[0, -1, 0.5/ACh15_kHz/Unit.kHz(), 1], [0.5/ACh15_kHz/Unit.kHz(), 1, 1./ACh15_kHz/Unit.kHz(), -1]]

# Analog00.SetModulation(analog_freq_interval, ach00mod)
# Analog01.SetModulation(analog_freq_interval, ach01mod)
# Analog02.SetModulation(analog_freq_interval, ach02mod)
# Analog03.SetModulation(analog_freq_interval, ach03mod)
# Analog04.SetModulation(analog_freq_interval, ach04mod)
# Analog05.SetModulation(analog_freq_interval, ach05mod)
# Analog06.SetModulation(analog_freq_interval, ach06mod)
# Analog07.SetModulation(analog_freq_interval, ach07mod)
# Analog08.SetModulation(analog_freq_interval, ach08mod)
# Analog09.SetModulation(analog_freq_interval, ach09mod)
# Analog10.SetModulation(analog_freq_interval, ach10mod)
# Analog11.SetModulation(analog_freq_interval, ach11mod)
# Analog12.SetModulation(analog_freq_interval, ach12mod)
# Analog13.SetModulation(analog_freq_interval, ach13mod)
# Analog14.SetModulation(analog_freq_interval, ach14mod)
# Analog15.SetModulation(analog_freq_interval, ach15mod)