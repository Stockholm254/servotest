import numpy as np
from pts_iterator import pts_iterator
import logging
from servo_util import create_zigzag_X, format_para,a2p,r2nd,r2nr,ndmodr,nrselr,nrmodr,nraddr
from servo_const import *

#
spiral_params = {
    'I_meaningful': 0.01,
    'D': 2,
    'SPIRAL_RESOLUTION': 15,
    'SPIRAL_SPAN': 7,
    'SINGLE_SPIRAL_SPAN': 3.5,
    'N_LOOPS_BEFORE_RESET_ORIGIN': 0.5,
    'MAX_X0Y0_DISPLACEMENT': 10,
    'COEF_I_RESET_ORIGIN': 1.4,
    'alpha': 0.03,
    'COEF_I_DECAY': 0.995
}
BFGS_params = {"disp": True, "maxiter": 10,  "eps": 5}
#


def step_optimize(servos,
                  callback_func,
                  pos_mask=None,
                  p0=None,
                  zero=None,
                  method="spiral",
                  bounds_single = (-100,100),
                  )->np.ndarray:
    #
    if method == 'L-BFGS-B':
        servos.set_precision(1)
        options = BFGS_params
    elif method == 'spiral':
        servos.set_precision(5)
        options = spiral_params
    #
    N_var = np.sum(pos_mask)
    if p0 is None:
        p0 = np.zeros(N_var)
    bounds = [bounds_single for i in range(N_var)]
    cf = lambda x: callback_func(x,pos_mask,zero=zero)
    #
    para, Ibst = pts_iterator(N_var=N_var,callback_func=cf, p0=p0, bounds = bounds, options=options, method = method)
    #
    para = list(para)
    Inow = cf(para)[1]
    logging.info(f"Best position: {format_para(para)}, now I: {Inow}")
    #
    if Inow/Ibst > 0.8:
        logging.info(f"New Origin set to be {format_para(para)}")
        zero_fullnd = nraddr(zero,para,pos_mask)
    else:
        logging.info("The intensity is not high enough, operation cancelled.")
        zero_fullnd = np.array(zero)
    #
    logging.info(f"Zero = {zero_fullnd}")
    return zero_fullnd

