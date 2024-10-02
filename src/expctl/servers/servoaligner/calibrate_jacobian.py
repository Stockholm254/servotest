import os
import numpy as np
import matplotlib.pyplot as plt
import time
from scservo_sdk import *                    # Uses SCServo SDK library
from pd import MCP3424_fiber
import logging
from collections import defaultdict

logging.basicConfig(
    # level=logging.INFO,  # Set the logging level to DEBUG
    level= logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from servodriver import Servoset
from servo_util import create_zigzag_X, format_para,a2p,r2nd,r2nr,ndmodr,nrselr,nrmodr,nraddr,compose_para
import tqdm
from servo_const import A_X_XDOT_MASK,A_Y_YDOT_MASK,A_X_Y_MASK,A_XDOT_YDOT_MASK,A_POS_ALL_MASK,B_X_XDOT_MASK,B_Y_YDOT_MASK,B_X_Y_MASK,B_XDOT_YDOT_MASK,B_POS_ALL_MASK,POS_ALL_MASK
from step_optimize import step_optimize
from callback_func import callback_func

servos = Servoset(board_id=0,servo_channel_list=[0,1,2,3,4,5,6,7])
servos.torques_enable()
servos.home()

cf0 = lambda para: callback_func(para, pos_mask=POS_ALL_MASK)
cf0([0,0,0,0,0,0,0,0])

# jac_assume = np.array(np.load('/home/rydpiservo/servodata/servosetup/jac_pm_250.npy',allow_pickle=True))
# print(jac_assume)
jac_assume = None

def cord_pm_offset(N,normd,i):
    # choose a position in offset to be +-30, each sample 5 times
    j = i%4
    pm = 1 if i//4%2==0 else -1
    offset = np.zeros(4)
    offset[j] = pm*normd
    return offset

def random_norm_offset(N,normd):
    # offset with arbitrary direction with norm=normd
    offset = np.random.randn(4)
    offset = offset/np.linalg.norm(offset)*normd
    return offset
#
N=12
normd = 360
offset_type = 'pm' # 'pm' or 'rand'
#
for i in range(N):
    filename='/home/rydpiservo/servodata/servosetup/jacobian_{:s}_{:d}.npy'.format(offset_type,normd)
    if not os.path.exists(filename):
        dataset = defaultdict(list)
        np.save(filename,dataset)
    dataset = np.load(filename,allow_pickle=True)
    dataset = dataset.item()
    # print(dataset)

    #
    zero = np.array([0,0,0,0,0,0,0,0],dtype=float)
    if offset_type == 'pm':
        offset = cord_pm_offset(N,normd,i)
    elif offset_type == 'rand':
        offset = random_norm_offset(N,normd)
    #
    offset_mask = A_POS_ALL_MASK
    zero = compose_para(para=offset,pos_mask = offset_mask, zero=zero,jac=jac_assume,jac_master_mask=A_POS_ALL_MASK)
    logging.info(f"Offset = {offset}, Zero = {zero}")
    #
    #
    try:
        logging.info(f"Start optimization with zero = {zero}")
        zero = step_optimize(servos,callback_func,pos_mask = B_X_Y_MASK,zero=zero,bounds_single = (-100,100))
        zero = step_optimize(servos,callback_func,pos_mask = B_X_XDOT_MASK,zero=zero)
        zero = step_optimize(servos,callback_func,pos_mask = B_Y_YDOT_MASK,zero=zero)
        zero = step_optimize(servos,callback_func,pos_mask = B_POS_ALL_MASK,zero=zero,method='L-BFGS-B')
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