
import re
import toml, logging
from pydantic import BaseModel
from typing import Optional
import constants, EcoDrive
from utils import *

logger = logging.getLogger('__name__')
logging.basicConfig(filename='/tmp/EpuClass.log', filemode='w', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

class EpuConfig(BaseModel):
    MINIMUN_GAP: float
    MAXIMUM_GAP: float
    MINIMUM_PHASE: float
    MAXIMUM_PHASE: float
    SERIAL_PORT: str
    A_DRIVE_ADDRESS: int
    B_DRIVE_ADDRESS: int
    I_DRIVE_ADDRESS: int
    S_DRIVE_ADDRESS: int
    BAUD_RATE: int
    ECODRIVE_LOG_FILE_PATH: str
    EPU_LOG_FILE_PATH: str

# loads config data
with open('../config/config.toml') as f:
    config = toml.load('../config/config.toml')
epu_config = EpuConfig(**config['EPU2'])
print(epu_config.MINIMUM_PHASE)

class Epu():
    
    BAUD_RATE = epu_config.BAUD_RATE
    MAXIMUM_GAP = epu_config.MAXIMUM_GAP
    MINIMUM_GAP = epu_config.MINIMUN_GAP
    MAXIMUM_PHASE = epu_config.MAXIMUM_PHASE
    MINIMUM_PHASE = epu_config.MINIMUM_PHASE
    A_DRIVE_ADDRESS = epu_config.A_DRIVE_ADDRESS
    B_DRIVE_ADDRESS = epu_config.B_DRIVE_ADDRESS
    I_DRIVE_ADDRESS = epu_config.I_DRIVE_ADDRESS
    S_DRIVE_ADDRESS = epu_config.S_DRIVE_ADDRESS
    SERIAL_PORT = epu_config.SERIAL_PORT

    def __init__(self):

        self.a_drive = EcoDrive(serial_port=self.SERIAL_PORT, address=self.A_DRIVE_ADDRESS,
                    baudrate=self.BAUD_RATE,min_limit=self.MINIMUM_GAP, max_limit=self.MAXIMUM_GAP)
        self.b_drive = EcoDrive(serial_port=self.SERIAL_PORT, address=self.B_DRIVE_ADDRESS,
                    baudrate=self.BAUD_RATE, min_limit=self.MINIMUM_GAP, max_limit=self.MAXIMUM_GAP)
        self.i_drive = EcoDrive(serial_port=self.SERIAL_PORT, address=self.I_DRIVE_ADDRESS,
                    baudrate=self.BAUD_RATE, min_limit=self.MINIMUM_PHASE, max_limit=self.MAXIMUM_PHASE)
        self.s_drive = EcoDrive(serial_port=self.SERIAL_PORT, address=self.S_DRIVE_ADDRESS,
                    baudrate=self.BAUD_RATE, min_limit=self.MINIMUM_PHASE, max_limit=self.MAXIMUM_PHASE)


        self.a_resolver_gap = self.a_drive.get_resolver_position()
        self.a_encoder_gap = self.a_drive.endoder_position
        self.b_resolver_gap = self.b_drive.get_resolver_position()
        self.b_encoder_gap = self.b_drive.endoder_position
        self.i_resolver_phase = self.i_drive.get_resolver_position()
        self.i_resolver_phase = self.i_drive.endoder_position
        self.s_resolver_gap = self.s_drive.get_resolver_position()
        self.s_encoder_gap = self.s_drive.endoder_position

        self.gap = (self.a_encoder_gap + self.b_encoder_gap)/2
        self.gap_halt_status = self.a_drive.get_halten_status()[0] and self.a_drive.get_halten_status()[0]
        self.gap_enable_status = self.a_drive.get_halten_status()[1] and self.a_drive.get_halten_status()[1]
        self.gap_setpoint = self.a_drive.get_target_position()
        self.a_target_position = self.get_target_position()
        self.a_target_position_reached = self.get_target_position_reached()
        self.a_max_velocity = self.get_max_velocity()
        self.soft_drive_message = ''

        self.update()

    @asynch
    @schedule(.05)
    def update(self):      
        self.a_resolver_gap = self.a_drive.get_resolver_position()
        self.a_encoder_gap = self.a_drive.endoder_position
        self.b_resolver_gap = self.b_drive.get_resolver_position()
        self.b_encoder_gap = self.b_drive.endoder_position
        self.i_resolver_phase = self.i_drive.get_resolver_position()
        self.i_resolver_phase = self.i_drive.endoder_position
        self.s_resolver_gap = self.s_drive.get_resolver_position()
        self.s_encoder_gap = self.s_drive.endoder_position

    def set_gap(self, target_gap: float):
        if not (self.MINIMUM_GAP < target_gap < self.MAXIMUM_GAP):
            logger.error(f'Tried to set gap out of the limits ({target_gap}).')
            print('Gap out of the limits.')
            return None
        else:
            try:
                self.a_drive.set_target_position(target_gap)
                self.b_drive.set_target_position(target_gap)
            except Exception:
                logger.exception('Exception raised while trying to set gap.')
                return None
            else:
                try:
                    a_target_pos_read = self.a_drive.get_target_position()
                    b_target_pos_read = self.b_drive.get_target_position()
                except Exception:
                    logger.exception('Exception raised while trying to verify setted gap.')
                    return None
                else:
                    if a_target_pos_read == b_target_pos_read == target_gap:
                        return target_gap
                    else:
                        logger.error('Target position read is different from target position setted!')
                        return None


    def set_phase(self, target_phase: float):
        if not (self.MINIMUM_PHASE < target_phase < self.MAXIMUM_PHASE):
            logger.error(f'Tried to set phase out of the limits ({target_phase}).')
            print('Phase  out of the limits.')
            return None
        else:
            try:
                self.i_drive.set_target_position(target_phase)
                self.s_drive.set_target_position(target_phase)
            except Exception:
                logger.exception('Exception raised while trying to set gap.')
                return None
            else:
                try:
                    i_target_pos_read = self.i_drive.get_target_position()
                    s_target_pos_read = self.s_drive.get_target_position()
                except Exception:
                    logger.exception('Exception raised while trying to verify setted gap.')
                    return None
                else:
                    if i_target_pos_read == s_target_pos_read == target_phase:
                        return target_phase
                    else:
                        logger.error('Target position read is different from target position setted!')
                        return None

    def enable_gap(self):
        return
    def release_gap_halt(self):
        pass
    def start_gap(self):
        pass
    
    def enable_phase(self):
        return
    def release_phase_halt(self):
        pass
    def start_phase(self):
        pass
        

#teste = Epu(a_address=epu_config.drive_a_address, b_address=epu_config.drive_b_address,\
#        min_gap=epu_config.min_gap, max_gap=epu_config.max_gap, min_phase=epu_config.min_phase, max_phase=epu_config.max_phase)


eco_test = EcoDrive(address='21', serial_port="/dev/pts/10")
eco_test.send("BCD:21")
print(eco_test.raw_read())
print(eco_test.get_target_position())
print(eco_test.diagnostic_message())
# status
# resolver
# encoder
# target
# target_reached
# halt
# enable
# start