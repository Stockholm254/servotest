import sympy
from sympy import symbols, sin, cos
from sympy import Matrix, nsolve
from sympy.parsing.sympy_parser import parse_expr
from itertools import product

import multiprocessing
import os
import time
from tqdm import tqdm

from expctl.servers.servoaligner.solver_plotter import Optical_system_solver, Mirror, Lens

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
from expctl.servers.servoaligner.servo_util import create_zigzag_X, format_para,a2p,r2nd,r2nr,ndmodr,nrselr,nrmodr,nraddr,compose_para
from expctl.servers.servoaligner.fit_gaussian import gaussian_2d,gaussian_2d_smooth_heaviside,fit_and_plot,fit_gaussian_2d,fit_gaussian_2d_smooth_heaviside,fit_and_plot_smooth_heaviside,popt_get_mu_cov,statistics_skewness
from expctl.servers.servoaligner.motor_scan import motor_1d_scan,motor_2d_scan
from expctl.servers.servoaligner.servo_const import A_X_XDOT_MASK,A_Y_YDOT_MASK,A_X_Y_MASK,A_XDOT_YDOT_MASK,A_POS_ALL_MASK,B_X_XDOT_MASK,B_Y_YDOT_MASK,B_X_Y_MASK,B_XDOT_YDOT_MASK,B_POS_ALL_MASK,POS_ALL_MASK, posmask2str
#from expctl.servers.servoaligner.pd import MCP3424_fiber
from expctl.servers.servoaligner.step_optimize import step_optimize

import xarray as xr

def iteration_actuator(servos, MCP3424_fiber, scan_xr):
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

if __name__=="__main__":
    servos = Servoset(board_id=0,servo_channel_list=[0,1,2,3,4,5,6,7])
    i2cbus = SMBus(1)
    MCP3424_fiber=MCP342x.MCP342x(i2cbus, 0x68, device='MCP3424', channel=0, gain=1, resolution=12, continuous_mode=False, scale_factor=1.0, offset=0.0)
    servos.home()
    print(MCP3424_fiber.convert_and_read())
    scan_xr=xr.open_dataarray("..//src//expctl//servers//servoaligner//angles0304_4.nc")
    ds=iteration_actuator(servos, MCP3424_fiber, scan_xr)
    ds.to_netcdf("data0304_3.nc")