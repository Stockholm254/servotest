import os
import numpy as np
import matplotlib.pyplot as plt
import time
from scservo_sdk import *                    # Uses SCServo SDK library
from pd import MCP3424_fiber
import logging
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,  # Set the logging level to DEBUG
    # level= logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from servodriver import Servoset
from servo_util import create_zigzag_X, format_para,a2p,r2nd,r2nr,ndmodr,nrselr,nrmodr,nraddr
from spiral import SpiralPath
from scipy.optimize import differential_evolution
from fit_gaussian import gaussian_2d,fit_and_plot,fit_gaussian_2d
import tqdm
from servo_const import A_X_XDOT_MASK,A_Y_YDOT_MASK,A_X_Y_MASK,A_XDOT_YDOT_MASK,A_POS_ALL_MASK,B_X_XDOT_MASK,B_Y_YDOT_MASK,B_X_Y_MASK,B_XDOT_YDOT_MASK,B_POS_ALL_MASK,POS_ALL_MASK
from step_optimize import step_optimize

servos = Servoset(board_id=0,servo_channel_list=[0,1,2,3,4,5,6,7])
servos.torques_enable()
servos.home()


def callback_func(para,
                  pos_mask,
                  zero=None,
                  jac=None,
                  jac_master_mask=None):
    # start from zero point, step para
    if zero is None:
        zero = np.zeros(len(pos_mask))
    para_nr_move = nraddr(zero,para,pos_mask)
    # set slave knobs according to jac
    if jac is not None:
        assert jac_master_mask is not None, "jac_master_mask is not provided"
        dr = r2nr(para,r_mask = pos_mask)
        dr = nrselr(dr,jac_master_mask)
        # print(dr)
        d_slave_r = np.dot(jac,dr)
        # print(d_slave_r)
        jac_slave_mask = 1-np.array(jac_master_mask)
        para_nr_move = nraddr(para_nr_move,d_slave_r,jac_slave_mask)
        # print(para_nr_move)

    #
    goal_position_list  = r2nd(list(para_nr_move))
    # print(goal_position_list)
    servos.set_angle(goal_position_list)
    #
    data_cache = []
    for m in range(2):
        # data = ADS1115_fiber.value
        data = MCP3424_fiber.convert_and_read()
        data_cache.append(data)
    z = float(np.mean(np.array(data)))
    print(para,z)
    return tuple(para),z

cf0 = lambda para: callback_func(para, pos_mask=POS_ALL_MASK)
print(cf0([0,0,0,0,0,0,0,0]))

jac_assume = np.array(np.load('/home/rydpiservo/servodata/jac_pm_50.npy',allow_pickle=True))
print(jac_assume)

def cord_pm_offset(N,normd,i):
    # choose a position in offset to be +-30, each sample 5 times
    j = i%4
    pm = 1 if i//4%2==0 else -1
    normd = N
    offset = np.zeros(4)
    offset[j] = pm*normd
    return offset
#
N=40
normd = 100
#
for i in range(N):
    filename='/home/rydpiservo/servodata/jacobian_pm_{:d}.npy'.format(normd)
    if not os.path.exists(filename):
        dataset = defaultdict(list)
        np.save(filename,dataset)
    dataset = np.load(filename,allow_pickle=True)
    dataset = dataset.item()
    # print(dataset)

    #
    zero = np.array([0,0,0,0,0,0,0,0],dtype=float)
    offset = cord_pm_offset(N,normd,i)
    offset_mask = A_POS_ALL_MASK
    zero = nraddr(zero,offset,offset_mask)
    logging.info(f"Zero = {zero}")
    #

    try:
        logging.info(f"Start optimization with zero = {zero}")
        # print(jac_assume)
        # print(np.array(offset))
        p0 = np.dot(jac_assume,np.array(offset))
        logging.info(f"p0 = {p0}")
        # zero = step_optimize(servos,callback_func,pos_mask = B_X_Y_MASK,zero=zero,bounds_single = (-200,200),p0=p0)
        # zero = step_optimize(servos,callback_func,pos_mask = B_X_XDOT_MASK,zero=zero)
        # zero = step_optimize(servos,callback_func,pos_mask = B_Y_YDOT_MASK,zero=zero)
        # zero = step_optimize(servos,callback_func,pos_mask = B_POS_ALL_MASK,zero=zero,method='L-BFGS-B')
        #
        _,I = callback_func(zero,pos_mask=POS_ALL_MASK)
        print(I)
        #
        dataset[tuple(offset)].append((list(zero),I))
        # print(dataset)
        np.save(filename,dataset)
        print("i=",i)

    except Exception as e:
        servos.close()
        logging.error(f"Error in iterative_optimize: {e}")