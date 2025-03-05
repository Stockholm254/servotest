import sys
from dataclasses import dataclass
from typing import Dict, List, Callable
from ..ServerClass import Server, logger
from ..util.SequenceProcessor import *
from .pico import PicomotorController
from .rpi_picomotor import Encoder, AS5600Reader, EncoderConfig
import math

@dataclass(frozen=True, eq=True)
class ELATSettings:
    top_x: float
    top_y: float
    top_z: float
    bottom_x: float
    bottom_y: float
    bottom_z: float

class PicoMotorServer(Server):
    def __init__(self, name, port, message, ip="127.0.0.1"):
        super().__init__(name, port, message)
        self.ip = ip
        self.settings: ELATSettings = None
        self.pico = None
        self.as5600 = None
        self.encoders: Dict[str, Encoder] = {}
        
        # Unified configuration dictionary
        self.config = {
            'top_x': {
                'channel_id': 0,
                'encoder_names': ['1A'],
                'move_function': self.plan_single_angle
            },
            'top_y': {
                'channel_id': 1,
                'encoder_names': ['1B'],
                'move_function': self.plan_single_angle
            },
            'top_z': {
                'channel_id': 2,
                'encoder_names': ['1A', '1B', '1C'],
                'move_function': self.plan_top_z
            },
            'bottom_x': {
                'channel_id': 3,
                'encoder_names': ['2A'],
                'move_function': self.plan_single_angle
            },
            'bottom_y': {
                'channel_id': 4,
                'encoder_names': ['2B'],
                'move_function': self.plan_single_angle
            },
            'bottom_z': {
                'channel_id': 5,
                'encoder_names': ['2A', '2B', '2C'],
                'move_function': self.plan_bottom_z
            }
        }

    def connect(self):
        try:
            self.pico = PicomotorController(self.ip)
            self.as5600 = AS5600Reader([0x70, 0x72])
            
            # Create encoders
            encoder_configs = [
                ('1A', (1,0), 0, 0x72),
                ('1B', (1,1), 1, 0x72),
                ('1C', (1,2), 2, 0x72),
                ('2A', (2,0), 0, 0x70),
                ('2B', (2,1), 1, 0x70),
                ('2C', (2,2), 2, 0x70),
            ]
            
            for name, pins, channel, i2c_addr in encoder_configs:
                self.encoders[name] = Encoder(
                    self.as5600, 
                    self.pico, 
                    EncoderConfig(name, pins, channel, i2c_addr),
                    Pgain=30, 
                    Igain=1
                )
            
            # Special case for 2C
            #self.encoders['2C'].config.deadzone_velocity = 70
            
        except Exception as e:
            logger.exception(f"Could not connect to picomotor controller: {e}")
        else:
            logger.info("Successfully connected to picomotor controller")

    def close(self):
        for enc in self.encoders.values():
            enc.close()
        if self.pico:
            self.pico.close()
        if self.as5600:
            self.as5600.close()

    def plan_single_angle(self, encoder_name: str, angle: float, planned_moves: Dict[str, float]):
        if encoder_name not in self.encoders:
            logger.error(f"Invalid encoder name: {encoder_name}")
            return
        
        # planned_moves[encoder_name] = angle
        planned_moves[encoder_name] = planned_moves.get(encoder_name, 0) + angle
        logger.debug(f"Planned move for {encoder_name} to angle {angle}")

    def plan_top_z(self, angle: float, planned_moves: Dict[str, float]):
        # Example calculation for moving top Z (adjust as needed)
        planned_moves['1A'] = planned_moves.get('1A', 0) + angle
        planned_moves['1B'] = planned_moves.get('1B', 0) + angle
        planned_moves['1C'] = planned_moves.get('1C', 0) + angle
        logger.debug(f"Planned move for top Z to angle {angle}")

    def plan_bottom_z(self, angle: float, planned_moves: Dict[str, float]):
        # Example calculation for moving bottom Z (adjust as needed)
        planned_moves['2A'] = planned_moves.get('2A', 0) + angle
        planned_moves['2B'] = planned_moves.get('2B', 0) + angle
        planned_moves['2C'] = planned_moves.get('2C', 0) + angle
        logger.debug(f"Planned move for bottom Z to angle {angle}")

    def execute_moves(self, planned_moves: Dict[str, float]):
        for encoder_name, angle in planned_moves.items():
            try:
                self.encoders[encoder_name].set_angle(angle)
                logger.debug(f"Executing move: {encoder_name} to angle {angle}")
            except Exception as e:
                logger.error(f"Error moving {encoder_name}: {e}")

    def update(self, settings: ELATSettings):
        if self.settings is None or settings != self.settings:
            logger.info(f"Updating settings to {settings}")
            planned_moves = {}
            for attr, value in settings.__dict__.items():
                config = self.config[attr]
                config['move_function'](config['encoder_names'][0], value, planned_moves)
            
            self.execute_moves(planned_moves)
            self.settings = settings

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
        
        if len(angles) == 6:
            settings = ELATSettings(**angles)
            self.update(settings)
        else:
            logger.error("Not all angles specified in the sequence")

    def cmd_seq(self, data):
        self.seq = data
        numChannels = sum(1 for chan in self.seq.allChannels if chan is not None)
        logger.debug(f"Received sequence ({numChannels} channels): {self.seq.name}")
        reply = f"Received sequence ({numChannels} channels): {self.seq.name}"
        self.send_msg(self.ReplyHeader() + reply)

    def queue(self):
        self.parse()
        return 1

    def run(self):
        return 1

    def plotdata(self):
        return [0,], [0,]

if __name__ == '__main__':
    message = """
    ===========================================
    ==           PicoMotor Server 1          ==
    ===========================================
    """
    server = PicoMotorServer("PM1", 60638, message=message)
    server.connect()
    server.main_loop()
    server.close()