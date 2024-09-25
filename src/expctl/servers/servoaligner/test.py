import os
import numpy as np
import matplotlib.pyplot as plt
import time
from smbus2 import SMBus,i2c_msg
import MCP342x
from scservo_sdk import *                    # Uses SCServo SDK library
import MCP342x
import logging
from pts_iterator import pts_iterator

logging.basicConfig(
    # level=logging.INFO,  # Set the logging level to DEBUG
    level= logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from servodriver import Servoset
from servo_util import create_zigzag_X, format_para,a2p,r2nd,r2nr,ndmodr,nrselr,nrmodr,nraddr,compose_para
from spiral import SpiralPath
from scipy.optimize import differential_evolution
from fit_gaussian import gaussian_2d,fit_and_plot,fit_gaussian_2d
from motor_2d_scan import motor_2d_scan
from servo_const import A_X_XDOT_MASK,A_Y_YDOT_MASK,A_X_Y_MASK,A_XDOT_YDOT_MASK,A_POS_ALL_MASK,B_X_XDOT_MASK,B_Y_YDOT_MASK,B_X_Y_MASK,B_XDOT_YDOT_MASK,B_POS_ALL_MASK,POS_ALL_MASK
from step_optimize import step_optimize
from pd import MCP3424_fiber

servos = Servoset(board_id=1,servo_channel_list=[0])
# servos.set_zero()
servos.torques_enable()
servos.set_angle([4096])
# time.sleep(2)
# servos.set_angle([2048])
servos.home()
# MCP3424_fiber.convert_and_read()