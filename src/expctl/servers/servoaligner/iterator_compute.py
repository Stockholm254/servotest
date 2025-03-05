import sympy
from sympy import symbols, sin, cos
from sympy import Matrix, nsolve
from itertools import product
from functools import partial

import multiprocessing
import os
from tqdm import tqdm

from expctl.servers.servoaligner.solver_plotter import Optical_system_solver, Mirror, Lens

import numpy as np
import matplotlib.pyplot as plt

import xarray as xr

#we simplify the problem by assuming that the two planes share the same values

#mirror spacing
x1 = 0.155
x2 = 0.27
x3 = 0.14
x4 = 0.15
#lens spacing
dy0 = 0.35
dy1 = 0.16
#focal length
fl1 = 0.1925
fl2 = 0.15
fl3 = 1
#MOT and Cavity
MOT_pos_1=0
Cav_pos_1=0

MOT_pos_2=0
Cav_pos_2=0

MOT_pos_rel = 0.2
MOT_Cav_dist = -0.044

params={'x1':x1, 'x2':x2, 'x3': x3, 'x4':x4, 'dy0':dy0, 'dy1':dy1, 'fl1': fl1, 'fl2': fl2, 'fl3': fl3, 'MOT_pos_rel': MOT_pos_rel, 'MOT_Cav_dist': MOT_Cav_dist, 'MOT_pos_1': MOT_pos_1, 'Cav_pos_1': Cav_pos_1, 'MOT_pos_2': MOT_pos_2, 'Cav_pos_2': Cav_pos_2}

def angle_calc_multi(args, **kwargs):
    var_list=args[0]
    solver_0=kwargs.pop('solver')
    var_list=kwargs.pop('var_str_list')
    params_loop=params.copy()
    params_loop.update(dict(zip(var_list, args)))
    Mrr1_y, Mrr2_y, Mrr3_y, Mrr4_y = solver_0.default_setup_solver_y(params=params_loop, tl_list=[0, 0, 0, 0], comp_list=[0, 0, 0, 0], plot_switch=0)
    solver_0.plot_size=(6,10)
    Mrr1_x, Mrr2_x, Mrr3_x, Mrr4_x = solver_0.default_setup_solver(params=params_loop, tl_list=[0, 0, 0, 0], comp_list=[Mrr1_y.tl, Mrr2_y.tl, Mrr3_y.tl, Mrr4_y.tl], plot_switch=0)
    knob_deg_list=[Mrr1_x.knob_deg(), Mrr1_y.knob_deg(), Mrr2_x.knob_deg(), Mrr2_y.knob_deg(), Mrr3_x.knob_deg(), Mrr3_y.knob_deg(), Mrr4_x.knob_deg(), Mrr4_y.knob_deg()]
    return knob_deg_list
    
def scan_xarray_gen(solver, var_str_list=['MOT_pos_1','MOT_pos_2'], range_list=[3e-4, 3e-4], num_list=[10,10], start_value_list=[0,0]):
    #result_xr=xr.DataArray(np.reshape(result, (N_x, N_y, 8)), dims=['MOT_x', 'MOT_y', 'knob'], coords={'x':x_array, 'y':y_array, 'knob':['Mrr1_x', 'Mrr1_y', 'Mrr2_x', 'Mrr2_y', 'Mrr3_x', 'Mrr3_y', 'Mrr4_x', 'Mrr4_y']})
    iter_list=[]
    coords_dict={}

    for i in range(len(var_str_list)):
        iter_list.append(np.linspace(start_value_list[i]-range_list[i], start_value_list[i]+range_list[i], num_list[i]))
        coords_dict[var_str_list[i]]=iter_list[-1]

    array_products=list(product(*iter_list))

    angle_calc_multi_partial=partial(angle_calc_multi, solver=solver, var_str_list=var_str_list)
    pool=multiprocessing.Pool()
    result=list(tqdm(pool.imap_unordered(angle_calc_multi_partial, array_products), total=len(array_products)))
    pool.close()
    pool.join()
    coords_dict.update({'knobs':['Mrr1_x', 'Mrr1_y', 'Mrr2_x', 'Mrr2_y', 'Mrr3_x', 'Mrr3_y', 'Mrr4_x', 'Mrr4_y']})
    scan_xr=xr.DataArray(np.reshape(result, num_list+[8]), dims=var_str_list+['knobs'], coords=coords_dict)
    return scan_xr

if __name__=="__main__":
    solver_0=Optical_system_solver()
    #result_xr=scan_xarray_gen(solver_0, var_str_list=['MOT_pos_1','MOT_pos_2'], range_list=[3e-4, 3e-4], num_list=[10, 10], start_value_list=[0,0])
    #result_xr=scan_xarray_gen(solver_0, var_str_list=['fl1','MOT_pos_1','MOT_pos_2'], range_list=[5e-3, 3e-4, 3e-4], num_list=[5, 10, 10], start_value_list=[fl1,0,0])
    result_xr=scan_xarray_gen(solver_0, var_str_list=['fl1','fl2','MOT_pos_1','MOT_pos_2'], range_list=[5e-3, 5e-3, 2e-4, 2e-4], num_list=[5,5,10,10], start_value_list=[fl1, fl2, MOT_pos_1, MOT_pos_2])
    current_dir=os.path.dirname(__file__)
    file_path=os.path.join(current_dir, "angles0304_3.nc")
    result_xr.to_netcdf(file_path)
