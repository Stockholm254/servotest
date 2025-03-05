import sys
import math
import time
import numpy as np
from dataclasses import dataclass
from ..ServerClass import Server, logger
from pathlib import Path
from ..util.SequenceProcessor import *
from .servodriver import Servoset
import argparse
import logging
from .model_setting import params
from .iterator_compute import angle_calc_single
logging.basicConfig(level=logging.INFO)

@dataclass(frozen=True, eq=True)
class VLATSettings:
    servo_1x_deg: float
    servo_1y_deg: float
    servo_2x_deg: float
    servo_2y_deg: float
    servo_3x_deg: float
    servo_3y_deg: float
    servo_4x_deg: float
    servo_4y_deg: float
    MOT_pos_1: float
    MOT_pos_2: float
    Cav_pos_1: float
    Cav_pos_2: float
    MOT_pos_rel: float


class STSServer(Server):

    def __init__(self, name, port, message,board_id=0, servo_channel_list=[]):
        super().__init__(name, port, message)
        self.servo_channel_list=servo_channel_list
        self.servos=Servoset(board_id,servo_channel_list)
        self.servos.torques_enable()
        self.settings: VLATSettings = None
        self.angle_set_list=[]

        # Unified configuration dictionary
        self.config = {
            'servo_1x_deg': {
                'channel_id': 0,
                'encoder_names': ['1X'],
                'move_function': self.plan_angle_single
            },
            'servo_1y_deg': {
                'channel_id': 1,
                'encoder_names': ['1Y'],
                'move_function': self.plan_angle_single
            },
            'servo_2x_deg': {
                'channel_id': 2,
                'encoder_names': ['2X'],
                'move_function': self.plan_angle_single
            },
            'servo_2y_deg': {
                'channel_id': 3,
                'encoder_names': ['2Y'],
                'move_function': self.plan_angle_single
            },
            'servo_3x_deg': {
                'channel_id': 4,
                'encoder_names': ['3X'],
                'move_function': self.plan_angle_single
            },
            'servo_3y_deg': {
                'channel_id': 5,
                'encoder_names': ['3Y'],
                'move_function': self.plan_angle_single
            },
            'servo_4x_deg': {
                'channel_id': 6,
                'encoder_names': ['4X'],
                'move_function': self.plan_angle_single
            },
            'servo_4y_deg': {
                'channel_id': 7,
                'encoder_names': ['4Y'],
                'move_function': self.plan_angle_single
            },
            'MOT_pos_1': {
                'channel_id': 8,
                'encoder_names': ['1X','1Y','2X','2Y','3X','3Y','4X','4Y'],
                'move_function': self.plan_angle_model
            },
            'MOT_pos_2': {
                'channel_id': 9,
                'encoder_names': ['1X','1Y','2X','2Y','3X','3Y','4X','4Y'],
                'move_function': self.plan_angle_model
            },
            'Cav_pos_1': {
                'channel_id': 10,
                'encoder_names': ['1X','1Y','2X','2Y','3X','3Y','4X','4Y'],
                'move_function': self.plan_angle_model
            },
            'Cav_pos_2': {
                'channel_id': 11,
                'encoder_names': ['1X','1Y','2X','2Y','3X','3Y','4X','4Y'],
                'move_function': self.plan_angle_model
            },
            'MOT_pos_rel': {
                'channel_id': 12,
                'encoder_names': ['1X','1Y','2X','2Y','3X','3Y','4X','4Y'],
                'move_function': self.plan_angle_model
            },
        }

    def __del__(self):
        self.servos.close()

    def plan_angle_model(self, angles):

        params.update(angles)
        params['MOT_pos_1']=params['MOT_pos_1']*1e-6
        params['MOT_pos_2']=params['MOT_pos_2']*1e-6
        params['Cav_pos_1']=params['Cav_pos_1']*1e-6
        params['Cav_pos_2']=params['Cav_pos_2']*1e-6
        params['MOT_pos_rel']=params['MOT_pos_rel']*1e-3

        value_list=angle_calc_single(params)

        return value_list

    def plan_angle_single(self):
        
        pos_mask = [0 for i in range(len(self.servo_channel_list))]
        value_list= [0,]*len(self.servo_channel_list)

        #turn _eps channels into servo angles
        for prop, ch in self.config.items():
            ch_id = ch['channel_id']
            if ch_id in self.servo_channel_list:
                val = getattr(self.settings, prop)
                pos_mask[self.servo_channel_list.index(ch_id)] = 1
                value_list[ch_id] = val

        logger.debug(f"Servo angles: {value_list}, mask: {pos_mask}")
        
        return value_list

    def set_angle(self, value_list):
        self.servos.set_angle(value_list)

    def update(self, settings: VLATSettings, angles):
        if self.settings is None or settings != self.settings:
            logger.info(f"Updating settings to {settings}")
            self.settings = settings

            list_1=self.plan_angle_single()
            list_2=self.plan_angle_model(angles)
            list_final=list(np.array(list_1)+np.array(list_2))
            logger.info(f"Servo angles: {list_final}")
            self.set_angle(list_final)

    def cmd_seq(self, data):
        self.seq = data # unpack the sequence
        numChannels = 0
        for chan in self.seq.allChannels:
            if chan != None: numChannels += 1
        logger.debug("Received sequence ({} channels): {}".format(numChannels, self.seq.name))
        # self.set_angle()
        reply = "Received sequence ({} channels): {}".format(numChannels, self.seq.name)
        self.send_msg(self.ReplyHeader() + reply)

    def parse(self):
        angles = {}
        for chan in self.seq.allChannels:
            try:
                val = chan._TransValues[0][1]  # find the first value
                for attr, config in self.config.items():
                    if config['channel_id'] == chan.chanid:
                        angles[attr] = float(val)
                        break
            except (AttributeError, IndexError):
                logger.exception(f"Error parsing channel {chan.chanid}")
        
        if len(angles) == 13:
            settings = VLATSettings(**angles)
            self.update(settings, angles)
        else:
            logger.error("Not all angles specified in the sequence")

    def queue(self):
        self.parse()
        #self.set_angle() # move the stage during the QUEUE phase
        return 1

    def run(self):
        return 1

    def plotdata(self):
        return [0,], [0,]
    
    def set_zero_args(self):
        self.servos.set_zero()

    def home_args(self,args):
        self.servos.home()

    def set_angle_args(self, args):
        self.servos.set_angle(args.angle)

    def set_single_args(self, args):
        self.servos.set_single(args.index, args.angle)
    
    def set_dehys_args(self, args):
        print(args.dehys_state)
        if int(args.dehys_state) == 0:
            logger.info("Dehysterisis is turned off")
            self.servos.de_hysterisis = False
        elif int(args.dehys_state) == 1:
            logger.info("Dehysterisis is turned on")
            self.servos.de_hysterisis = True


if __name__ == '__main__':

    message = """
    ===========================================
    ==           Servo Aligner Server 1      ==
    ==                STS3032                ==
    ===========================================`
    """
    server = STSServer("STS1", 60627, message=message, board_id=0, servo_channel_list=[0,1,2,3,4,5,6,7])
    # Create a servozero subcommand
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    DE_HYSTERESIS = True
    server.servos.de_hysterisis = DE_HYSTERESIS

    # set_zero
    parser_zero = subparsers.add_parser('set_zero', help='Set the current position as zero')
    parser_zero.set_defaults(func=server.set_zero_args)
    # go home
    parser_home = subparsers.add_parser('home', help='Move to the home position')
    parser_home.set_defaults(func=server.home_args)
    # set_angle
    parser_angle = subparsers.add_parser('set_angle', help='Move to the specified angle')
    parser_angle.add_argument('angle', nargs='+', type=float, help='Angle to move to')
    parser_angle.set_defaults(func=server.set_angle_args)
    # set single angle
    parser_single = subparsers.add_parser('set_single', help='Move a single servo to the specified angle')
    parser_single.add_argument('index', type=int, help='Channel to move')
    parser_single.add_argument('angle', type=float,help='Angle to move to')
    parser_single.set_defaults(func=server.set_single_args)
    # set dehyisteresis
    parser_dehys = subparsers.add_parser('dehys', help='Set the dehysterisis')
    parser_dehys.add_argument('dehys_state', type=int, help='Dehysterisis, 0 or 1')
    parser_dehys.set_defaults(func=server.set_dehys_args)


    # if len(sys.argv) <= 1:
    # 	sys.argv.append('--help')
    try:
        options = parser.parse_args()
        options.func(options)
    except:
        pass

    server.main_loop()