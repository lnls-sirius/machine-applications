
import re
import toml, logging
from pydantic import BaseModel
from typing import Optional
import constants, EcoDrive
from utils import *

logger = logging.getLogger('__name__')
logging.basicConfig(
    filename='/tmp/EpuClass.log', filemode='w', level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S')

class Epu():

    def __init__(self):

        self.a_drive = EcoDrive(
            serial_port=constants.SERIAL_PORT,
            address=constants.A_DRIVE_ADDRESS,
            baudrate=constants.BAUD_RATE,
            min_limit=constants.MINIMUM_GAP,
            max_limit=constants.MAXIMUM_GAP)
        self.b_drive = EcoDrive(
            serial_port=constants.SERIAL_PORT,
            address=constants.B_DRIVE_ADDRESS,
            baudrate=constants.BAUD_RATE,
            min_limit=constants.MINIMUM_GAP,
            max_limit=constants.MAXIMUM_GAP)
        self.i_drive = EcoDrive(
            serial_port=constants.SERIAL_PORT,
            address=constants.I_DRIVE_ADDRESS,
            baudrate=constants.BAUD_RATE,
            min_limit=constants.MINIMUM_PHASE,
            max_limit=constants.MAXIMUM_PHASE)
        self.s_drive = EcoDrive(
            serial_port=constants.SERIAL_PORT,
            address=constants.S_DRIVE_ADDRESS,
            baudrate=constants.BAUD_RATE,
            min_limit=constants.MINIMUM_PHASE,
            max_limit=constants.MAXIMUM_PHASE)


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
        if not (constants.MINIMUM_GAP < target_gap < constants.MAXIMUM_GAP):
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
        if not (constants.MINIMUM_PHASE < target_phase < constants.MAXIMUM_PHASE):
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

    def enable_gap(self, option):
        if option:
            # enable
            pass
        else:
            # disable
            pass
        return
    def release_gap_halt(self, option):
        if option:
            # release
            pass
        else:
            # halt
            pass
        pass
    def enable_release_gap(self, option):
        if option:
            # enable and release
            pass
        else:
            # disable and halt
            pass
    def start_gap(self):
        pass
    def enable_phase(self, option):
        if option:
            # enable
            pass
        else:
            # disable
            pass
        return
    def release_phase_halt(self, option):
        if option:
            # release
            pass
        else:
            # halt
            pass
        pass
    def enable_release_phase(self, option):
        if option:
            # enable and release
            pass
        else:
            # disable and halt
            pass
    def start_phase(self):
        pass
    def stop(self):
        pass

#teste = Epu(a_address=constants.drive_a_address, b_address=constants.drive_b_address,\
#        min_gap=constants.min_gap, max_gap=constants.max_gap, min_phase=constants.min_phase, max_phase=constants.max_phase)


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