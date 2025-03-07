from itertools import product

import multiprocessing
import os
import time
from tqdm import tqdm

import numpy as np
import matplotlib.pyplot as plt
import time,pickle
from expctl.servers.servoaligner.scservo_sdk import *                    # Uses SCServo SDK library
from expctl.servers.servoaligner.pts_iterator import pts_iterator
import logging

from smbus2 import SMBus,i2c_msg
import MCP342x

logging.basicConfig(
    level=logging.INFO,  # Set the logging level to DEBUG
    # level= logging.DEBUG,|
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from expctl.servers.servoaligner.servodriver import Servoset
import xarray as xr

from scipy.optimize import minimize

def iteration_actuator(servos, MCP3424_fiber, scan_xr):
    """
    Performs an iteration over a set of servo angles, reads sensor data at each configuration, and returns the results in an xarray.Dataset.
    Parameters:
        servos: An object that controls servo motors. It should have the following methods:
            - set_angle(knob_deg_list): Sets the servo angles to the specified list of degrees.
            - home(): Resets the servos to their home (default) position.
        MCP3424_fiber: An object interfacing with an analog-to-digital converter. It is expected to provide:
            - convert_and_read(): Reads a value from the ADC after conversion.
        scan_xr: An xarray.DataArray containing servo angle configurations. The last dimension represents the set of
                 angles (or knobs) to be applied to the servos, while the other dimensions define the overall grid or
                 set of coordinates for scanning.
    Returns:
        xr.Dataset: A dataset containing two variables:
            - 'knob_angles': The original scan_xr DataArray.
            - 'data': An xarray.DataArray of sensor readings obtained from MCP3424_fiber, reshaped to match the
                      dimensions of scan_xr (excluding the knob dimension).
    Behavior:
        The function performs the following steps:
            1. Flattens the scan_xr values along all dimensions except for the knob (angle) values.
            2. Iterates over each set of angles:
                   - Sets the servo angles using servos.set_angle().
                   - Reads the sensor data from MCP3424_fiber using convert_and_read() and appends the result.
            3. Reshapes the collected sensor readings to form an xarray.DataArray that aligns with the scanning
               dimensions (excluding the knob axis).
            4. Resets the servos to their home position by calling servos.home().
            5. Prints a final sensor reading after repositioning.
            6. Combines the original knob angles and the sensor data into a single xarray.Dataset and returns it.
    """
    flattened = scan_xr.values.reshape(-1, scan_xr.values.shape[-1])
    data_list=[]

    for knob_deg_list in tqdm(flattened):
        servos.set_angle(knob_deg_list)
        data_list.append(MCP3424_fiber.convert_and_read())

    data_xr = xr.DataArray(
        data=np.array(data_list).reshape(scan_xr.shape[:-1]),
        dims=scan_xr.dims[:-1],
        coords=scan_xr.drop_vars('knobs').coords
    )

    servos.home()
    print(MCP3424_fiber.convert_and_read())
    
    # Combine them into a single Dataset
    ds = xr.Dataset({
    'knob_angles': scan_xr,
    'data': data_xr
    })
    
    return ds

def diag_forw(x, y):
    return (x + y, x - y)

def anti_forw(x, y):
    return (x + y, -x + y)

def single_actuator_minimize(deg_list, servos, MCP3424_fiber, servos_name_list, knob_deg_list):
    data_list=[]
    servos_dict={'servo_1x':0, 'servo_1y':1, 'servo_2x':2, 'servo_2y':3, 'servo_3x':4, 'servo_3y':5, 'servo_4x':6, 'servo_4y':7}
    knob_deg_list=np.array(knob_deg_list)
    knob_index=np.array([servos_dict[key] for key in servos_name_list])
    knob_deg_list[knob_index]=np.array(deg_list) + knob_deg_list[knob_index]
    servos.set_angle(knob_deg_list)
    for i in range(10):
        data_list.append(-MCP3424_fiber.convert_and_read())
    data = np.mean(data_list)
    return data

def wrapper_x(par, knob_deg_list, servos, MCP3424_fiber):
    x = par[0]
    y = par[1]
    val = single_actuator_minimize(deg_list=diag_forw(x,y), servos=servos, MCP3424_fiber=MCP3424_fiber, servos_name_list=['servo_3x','servo_4x'], knob_deg_list=knob_deg_list)
    return val

def wrapper_y(par, knob_deg_list, servos, MCP3424_fiber):
    x = par[0]
    y = par[1]
    val = single_actuator_minimize(deg_list=anti_forw(x,y), servos=servos, MCP3424_fiber=MCP3424_fiber, servos_name_list=['servo_3y','servo_4y'], knob_deg_list=knob_deg_list)
    return val

def actuator_minimize(servos, MCP3424_fiber, knob_deg_list):
    initial_simplex = np.array([[0, 0], [10, 0], [0, 3]])
    res_x = minimize(wrapper_x, [0, 0], method='Nelder-Mead', bounds=[(-180, 180), (-40, 40)], args=(knob_deg_list, servos, MCP3424_fiber),
         options={'initial_simplex': initial_simplex, 'xatol': 5.0, 'fatol': 1e-1, 'disp': True, 'maxiter': 20})

    servos_dict={'servo_1x':0, 'servo_1y':1, 'servo_2x':2, 'servo_2y':3, 'servo_3x':4, 'servo_3y':5, 'servo_4x':6, 'servo_4y':7}
    knob_angles_postx = knob_deg_list.copy()
    knob_angles_postx[servos_dict['servo_3x']] += diag_forw(*res_x.x)[0]
    knob_angles_postx[servos_dict['servo_4x']] += diag_forw(*res_x.x)[1]

    res_y = minimize(wrapper_y, [0, 0], method='Nelder-Mead', bounds=[(-180, 180), (-40, 40)], args=(knob_angles_postx, servos, MCP3424_fiber),
         options={'initial_simplex': initial_simplex, 'xatol': 5.0, 'fatol': 1e-1, 'disp': True, 'maxiter': 20})

    knob_angles_posty = knob_angles_postx.copy()
    knob_angles_posty[servos_dict['servo_3y']] += anti_forw(*res_y.x)[0] #res.x[0]-res.x[1]
    knob_angles_posty[servos_dict['servo_4y']] += anti_forw(*res_y.x)[1]

    return knob_angles_posty

if __name__=="__main__":
    servos = Servoset(board_id=0,servo_channel_list=[0,1,2,3,4,5,6,7])
    i2cbus = SMBus(1)
    MCP3424_fiber=MCP342x.MCP342x(i2cbus, 0x68, device='MCP3424', channel=0, gain=1, resolution=12, continuous_mode=False, scale_factor=1.0, offset=0.0)
    servos.home()
    print(MCP3424_fiber.convert_and_read())
    scan_xr=xr.open_dataarray("..//src//expctl//servers//servoaligner//angles0304_4.nc")
    ds=iteration_actuator(servos, MCP3424_fiber, scan_xr)
    ds.to_netcdf("data0304_3.nc")