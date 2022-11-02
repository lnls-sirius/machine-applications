import toml, logging, threading, socket
from ecodrive import EcoDrive
from pydantic import BaseModel
from utils import *
from datetime import datetime

################## LOGGING #####################
logger = logging.getLogger('__name__')
logging.basicConfig(filename='./epu.log',
                    filemode='w', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')

logger.info(datetime.now().strftime('%m/%d/%Y, %H:%M:%S'))
  
################# ETHERNET #####################
GPIO_TCP_PORT=5050
RS485_TCP_PORT=9993
BBB_HOSTNAME = 'BBB-DRIVERS-EPU-2022'

############### GPIO COMMANDS ##################
BSMP_WRITE = 0X20
BSMP_READ = 0X10

HALT_CH_AB =   0x10
START_CH_AB =  0x20
ENABLE_CH_AB = 0x30

HALT_CH_SI =   0x11
START_CH_SI =  0x21
ENABLE_CH_SI = 0x31

#################################################

class Epu():

    def __init__(self, callback_update=lambda x:1):

        self.a_drive = EcoDrive(
            address=epu_config.A_DRIVE_ADDRESS,
            min_limit=epu_config.MINIMUM_GAP,
            max_limit=epu_config.MAXIMUM_GAP, drive_name='A')
        self.b_drive = EcoDrive(
            address=epu_config.B_DRIVE_ADDRESS,
            min_limit=epu_config.MINIMUM_GAP,
            max_limit=epu_config.MAXIMUM_GAP, drive_name='B')
        self.i_drive = EcoDrive(
            address=epu_config.I_DRIVE_ADDRESS,
            min_limit=epu_config.MINIMUM_PHASE,
            max_limit=epu_config.MAXIMUM_PHASE, drive_name='I')
        self.s_drive = EcoDrive(
            address=epu_config.S_DRIVE_ADDRESS,
            min_limit=epu_config.MINIMUM_PHASE,
            max_limit=epu_config.MAXIMUM_PHASE, drive_name='S')

        self._epu_lock = threading.RLock()
        self.MAX_POSITION_DIFF = .01

        # drive a variables
        self.a_resolver_gap = self.a_drive.get_resolver_position()
        self.a_encoder_gap = self.a_drive.get_encoder_position()
        self.a_halt_released = not self.a_drive.get_halten_status()[0]
        self.a_enable = not self.a_drive.get_halten_status()[1]
        self.a_target_position = self.a_drive.get_target_position()
        self.a_target_position_reached = self.a_drive.get_target_position_reached()
        self.a_max_velocity = self.a_drive.get_max_velocity()
        self.a_act_velocity = self.a_drive.get_act_velocity()
        self.a_diag_code = self.a_drive.get_diagnostic_code()
        self.a_is_moving = self.a_drive.get_movement_status()
        # drive b variables
        self.b_resolver_gap = self.b_drive.get_resolver_position()
        self.b_encoder_gap = self.b_drive.get_encoder_position()
        self.b_halt_released = not self.b_drive.get_halten_status()[0]
        self.b_enable = not self.b_drive.get_halten_status()[1]
        self.b_target_position = self.b_drive.get_target_position()
        self.b_target_position_reached = self.b_drive.get_target_position_reached()
        self.b_max_velocity = self.b_drive.get_max_velocity()
        self.b_act_velocity = self.a_drive.get_act_velocity()
        self.b_diag_code = self.b_drive.get_diagnostic_code()
        self.b_is_moving = self.b_drive.get_movement_status()
        # drive i variables
        self.i_resolver_phase = self.i_drive.get_resolver_position()
        self.i_encoder_phase = self.i_drive.get_encoder_position()
        self.i_halt_released = not self.i_drive.get_halten_status()[0]
        self.i_enable = not self.i_drive.get_halten_status()[1]
        self.i_target_position = self.i_drive.get_target_position()
        self.i_target_position_reached = self.i_drive.get_target_position_reached()
        self.i_max_velocity = self.i_drive.get_max_velocity()
        self.i_act_velocity = self.a_drive.get_act_velocity()
        self.i_diag_code = self.i_drive.get_diagnostic_code()
        self.i_is_moving = self.i_drive.get_movement_status()
        # drive s variables
        self.s_resolver_phase = self.s_drive.get_resolver_position()
        self.s_encoder_phase = self.s_drive.get_encoder_position()
        self.s_halt_released = not self.s_drive.get_halten_status()[0]
        self.s_enable = not self.s_drive.get_halten_status()[1]
        self.s_target_position = self.s_drive.get_target_position()
        self.s_target_position_reached = self.s_drive.get_target_position_reached()
        self.s_max_velocity = self.s_drive.get_max_velocity()
        self.s_act_velocity = self.a_drive.get_act_velocity()
        self.s_diag_code = self.s_drive.get_diagnostic_code()
        self.s_is_moving = self.s_drive.get_movement_status()

        ##undulator status
        self.is_moving = (
            self.a_is_moving
            or self.b_is_moving
            or self.i_is_moving
            or self.s_is_moving
            )
        self.soft_message = ''

        ## undulator gap variables
        self.gap_target = self.a_target_position
        self.gap = (self.a_encoder_gap + self.b_encoder_gap)*.5
        self.gap_velocity = (self.a_act_velocity + self.b_act_velocity)*.5
        self.gap_enable = 0
        self.phase = (self.i_encoder_phase + self.s_encoder_phase)*.5
        self.gap_halt_released = 0
        self.gap_enable_and_halt_released = self.gap_enable and self.gap_halt_released
        self.gap_res_position_diff = self.a_resolver_gap - self.b_resolver_gap
        self.gap_enc_position_diff = self.a_encoder_gap - self.b_encoder_gap
        self.gap_change_allowed = self.allowed_gap_change()
        self.gap_is_moving = self.a_is_moving or self.b_is_moving
        ### undulator phase variables
        self.phase_target = self.i_target_position
        self.phase = (self.i_encoder_phase + self.s_encoder_phase)*.5
        self.phase_velocity = (self.i_act_velocity + self.s_act_velocity)*.5
        self.phase_enable = 0
        self.phase_halt_released = 0
        self.phase_enable_and_halt_released = self.phase_enable and self.phase_halt_released
        self.phase_res_position_diff = self.i_resolver_phase - self.s_resolver_phase
        self.phase_enc_position_diff = self.i_encoder_phase - self.s_encoder_phase
        self.phase_change_allowed = self.allowed_phase_change()

        #self.update_1()
        #self.update_2()

    @asynch
    @schedule(5)
    #@timer
    def update_1(self):
        try:
            # drive a
            self.a_resolver_gap = self.a_drive.get_resolver_position()
            # self.a_encoder_gap = self.a_drive.get_encoder_position()
            self.a_halt_released = not self.a_drive.get_halten_status()[0]
            self.a_enable = not self.a_drive.get_halten_status()[1]
            self.a_target_position = self.a_drive.get_target_position()
            self.a_target_position_reached = self.a_drive.get_target_position_reached()
            # self.a_max_velocity = self.a_drive.get_max_velocity()
            self.a_act_velocity = self.a_drive.get_act_velocity()
            # self.a_diag_code = self.a_drive.get_diagnostic_code()
            self.a_is_moving = self.a_drive.get_movement_status()

            # drive b
            self.b_resolver_gap = self.b_drive.get_resolver_position()
            # self.b_encoder_gap = self.b_drive.get_encoder_position()
            self.b_halt_released = not self.b_drive.get_halten_status()[0]
            self.b_enable = not self.b_drive.get_halten_status()[1]
            self.b_target_position = self.b_drive.get_target_position()
            self.b_target_position_reached = self.b_drive.get_target_position_reached()
            # self.b_max_velocity = self.b_drive.get_max_velocity()
            self.b_act_velocity = self.a_drive.get_act_velocity()
            # self.b_diag_code = self.b_drive.get_diagnostic_code()
            self.b_is_moving = self.b_drive.get_movement_status()

            # drive i
            self.i_resolver_phase = self.i_drive.get_resolver_position()
            # self.i_encoder_phase = self.i_drive.get_encoder_position()
            self.i_halt_released = not self.i_drive.get_halten_status()[0]
            self.i_enable = not self.i_drive.get_halten_status()[1]
            self.i_target_position = self.i_drive.get_target_position()
            self.i_target_position_reached = self.i_drive.get_target_position_reached()
            # self.i_max_velocity = self.i_drive.get_max_velocity()
            self.i_act_velocity = self.a_drive.get_act_velocity()
            # self.i_diag_code = self.i_drive.get_diagnostic_code()
            self.i_is_moving = self.i_drive.get_movement_status()

            # drive s
            self.s_resolver_phase = self.s_drive.get_resolver_position()
            # self.s_encoder_phase = self.s_drive.get_encoder_position()
            self.s_halt_released = not self.s_drive.get_halten_status()[0]
            self.s_enable = not self.s_drive.get_halten_status()[1]
            self.s_target_position = self.s_drive.get_target_position()
            self.s_target_position_reached = self.s_drive.get_target_position_reached()
            # self.s_max_velocity = self.s_drive.get_max_velocity()
            self.s_act_velocity = self.a_drive.get_act_velocity()
            # self.s_diag_code = self.s_drive.get_diagnostic_code()
            self.s_is_moving = self.s_drive.get_movement_status()

            # undulator status
            self.is_moving = (
                self.a_is_moving
                or self.b_is_moving
                or self.i_is_moving
                or self.s_is_moving
                )

            # gap
            self.gap_enable = self.a_enable and self.b_enable
            self.gap_halt_released = self.a_halt_released and self.b_halt_released
            self.gap_enable_and_halt_released = self.gap_enable and self.gap_halt_released
            self.gap_target = self.a_target_position
            self.gap = (self.a_encoder_gap + self.b_encoder_gap)*.5
            self.gap_velocity = (self.a_act_velocity + self.b_act_velocity)*.5
            self.gap_enable = 0
            self.phase = (self.i_encoder_phase + self.s_encoder_phase)*.5
            self.gap_halt_released = 0
            self.gap_enable_and_halt_released = self.gap_enable and self.gap_halt_released
            self.gap_res_position_diff = self.a_resolver_gap - self.b_resolver_gap
            self.gap_enc_position_diff = self.a_encoder_gap - self.b_encoder_gap
            self.gap_change_allowed = self.allowed_gap_change()
            self.a_is_moving = self.a_drive.get_movement_status()
            self.b_is_moving = self.b_drive.get_movement_status()
            self.gap_is_moving = self.a_is_moving or self.b_is_moving
            # # phase
            self.phase_velocity = (self.s_act_velocity + self.i_act_velocity)*.5
            self.phase_enable = self.i_enable and self.s_enable
            self.phase_halt_released = self.i_halt_released and self.s_halt_released
            self.phase_enable_and_halt_released = self.phase_enable and self.phase_halt_released
        except Exception:
            logger.exception('Could not update_1.')
            print('Exception raised.')


    @asynch
    @schedule(.6)
    #@timer
    def update_2(self):
        with self._epu_lock:
            try:    
                self.a_encoder_gap = self.a_drive.get_encoder_position()
                self.b_encoder_gap = self.b_drive.get_encoder_position()
                self.gap = (self.a_encoder_gap + self.b_encoder_gap)*.5
                self.i_encoder_phase = self.i_drive.get_encoder_position()
                self.s_encoder_phase = self.s_drive.get_encoder_position()
                self.phase = (self.i_encoder_phase + self.s_encoder_phase)*.5
            except:
                logger.exception('Could not update encoder variables.')
                print('Exception raised.')

    # General

    def stop_all(self):
        self.gap_stop()
        self.phase_stop()

    # Gap stuff

    def gap_get_setpoint(self) -> float:
        try:
            a_target = self.a_drive.get_target_position()
            b_target = self.b_drive.get_target_position()
        except:
            logger.exception()
        else:
            if a_target == b_target:
                return a_target
            else:
                self.b_drive.set_target_position(a_target)

    def gap_set(self, target_gap: float) -> float:
        ''' Set gap for drives A and B. If all runs ok, returns gap setted, if not, returns None.'''
        previous_gap = self.a_drive.get_target_position()
        if epu_config.MINIMUM_GAP <= target_gap <= epu_config.MAXIMUM_GAP:
            try:
                self.a_drive.set_target_position(target_gap)
            except:
                logger.exception('Could not set drive A gap.')
                print('Could not set drive A gap.')
                self.a_drive.set_target_position(previous_gap) # Dependendo do lugar que a axceção tiver ocorrido, o setpoint de posição pode já ter sido alterado. Otimize isso tratando melhor a exceção.
                return previous_gap
            else:
                try:
                    self.b_drive.set_target_position(target_gap)
                except Exception as e:
                    logger.exception('Could not set drive B gap.')
                    print('Could not set drive B gap.', e)
                    self.a_drive.set_target_position(previous_gap)  # Optimize this, treating exceptions better
                    self.b_drive.set_target_position(previous_gap)  # Optimize this, treating exceptions better.
                    return previous_gap
                else:
                    return target_gap
        else:
            logger.error(f'Gap valeu given, ({target_gap}), is out of range.')
            print(f'Gap value given, ({target_gap}), is out of range.')
            return previous_gap

    def gap_set_enable(self, val: bool):
        assert val==True or val==False
        bsmp_enable_message = bsmp_send(BSMP_WRITE, variableID=ENABLE_CH_AB, value=val).encode()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(.1)
            s.connect((BBB_HOSTNAME, GPIO_TCP_PORT))
            s.sendall(bsmp_enable_message)
            time.sleep(.01) # magic number!!!!
            while True:
                data = s.recv(16)
                if not data: break
                return data
    
    def gap_release_halt(self, val: bool):
        assert val==True or val==False
        bsmp_enable_message = bsmp_send(BSMP_WRITE, variableID=HALT_CH_AB, value=val).encode()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(.1)
            s.connect((BBB_HOSTNAME, GPIO_TCP_PORT))
            s.sendall(bsmp_enable_message)
            time.sleep(.01) # magic number!!!!
            while True:
                data = s.recv(8)
                if not data: break
                return data

    def gap_enable_and_release_halt(self, val: bool):
        assert val==True or val==False
        self.gap_set_enable(val)
        self.gap_release_halt(val)

    def gap_check_for_move(self) -> bool:
        drive_a_max_velocity = self.a_drive.get_max_velocity()
        drive_b_max_velocity = self.b_drive.get_max_velocity()
        if drive_a_max_velocity == drive_b_max_velocity:
            drive_a_target_position = self.a_drive.get_encoder_position()
            drive_b_target_position = self.b_drive.get_encoder_position()
            if drive_a_target_position == drive_b_target_position:
                return True
            else:
                logger.warning('Movement not allowed. Drives A and B have different target positions.')
                return False
        else:
            logger.warning('Movement not allowed. Drives A and B have different maximum velocities.')
            return False

    def gap_start(self, val: bool) -> bool:
        bsmp_enable_message = bsmp_send(BSMP_WRITE, variableID=START_CH_AB, value=val).encode()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(.1)
            s.connect((BBB_HOSTNAME, GPIO_TCP_PORT))
            s.sendall(bsmp_enable_message)
            time.sleep(.01) # magic number!!!!
            while True:
                data = s.recv(8)
                if not data: break
                return data

    def gap_enable_status(self):
        bsmp_enable_message = bsmp_send(BSMP_READ, variableID=ENABLE_CH_AB, size=0).encode()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(.1)
            s.connect((BBB_HOSTNAME, GPIO_TCP_PORT))
            s.sendall(bsmp_enable_message)
            time.sleep(.01) # magic number!!!!
            while True:
                data = s.recv(8)
                if not data: break
                return(bool(data[-2]))
    
    def gap_halt_release_status(self):
        bsmp_enable_message = bsmp_send(BSMP_READ, variableID=HALT_CH_AB, size=0).encode()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(.1)
            s.connect((BBB_HOSTNAME, GPIO_TCP_PORT))
            s.sendall(bsmp_enable_message)
            time.sleep(.01) # magic number!!!!
            while True:
                data = s.recv(8)
                if not data: break
                return(bool(data[-2]))

    def allowed_gap_change(self) -> bool:
        if self.a_target_position != self.b_target_position:
            return False
        else: return True
    
    def gap_stop(self):
        self.gap_release_halt(0)
    
    # Phase stuff

    def phase_get_setpoint(self) -> float:
        try:
            a_target = self.i_drive.get_target_position()
            b_target = self.s_drive.get_target_position()
        except:
            logger.exception()
        else:
            if a_target == b_target:
                return a_target
            else:
                self.s_drive.set_target_position(a_target)

    def phase_set(self, target_phase: float) -> float:
        previous_gap = self.i_drive.get_target_position()
        if epu_config.MINIMUM_PHASE < target_phase < epu_config.MAXIMUM_PHASE:
            try:
                self.i_drive.set_target_position(target_phase)
            except:
                logger.exception('Could not set drive A gap.')
                print('Could not set drive A gap.')
                self.i_drive.set_target_position(previous_gap) # Dependendo do lugar que a axceção tiver ocorrido, o setpoint de posição pode já ter sido alterado. Otimize isso tratando melhor a exceção.
                return previous_gap
            else:
                try:
                    self.s_drive.set_target_position(target_phase)
                except Exception as e:
                    logger.exception('Could not set drive B gap.')
                    print('Could not set drive B gap.', e)
                    self.i_drive.set_target_position(previous_gap)  # Optimize this, treating exceptions better
                    self.s_drive.set_target_position(previous_gap)  # Optimize this, treating exceptions better.
                    return previous_gap
                else:
                    return target_phase
        else:
            logger.error(f'Gap valeu given, ({target_phase}), is out of range.')
            print(f'Gap value given, ({target_phase}), is out of range.')
            return previous_gap

    def phase_set_enable(self, val: bool):
        assert val==True or val==False
        if self.a_drive.diagnostic_code == self.b_drive.diagnostic_code =='A012':
            bsmp_enable_message = bsmp_send(BSMP_WRITE, variableID=ENABLE_CH_SI, value=val).encode()
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(.1)
                s.connect((BBB_HOSTNAME, GPIO_TCP_PORT))
                s.sendall(bsmp_enable_message)
                time.sleep(.01) # magic number!!!!
                while True:
                    data = s.recv(8)
                    if not data: break
                    return data
        else:
            logger.log(
                f'Enable signal not send due to diagnostic code Drive I code:\
                    {self.a_drive.diagnostic_code},\Drive B code:{self.b_drive.diagnostic_code}')
            self.soft_drive_message = \
                f'Enable signal not send due to diagnostic code Drive S code:\
                    {self.a_drive.diagnostic_code}, Drive B code:{self.b_drive.diagnostic_code}'
    
    def phase_release_halt(self, val: bool):
        assert val==True or val==False
        if self.a_drive.diagnostic_code == self.b_drive.diagnostic_code =='A010':
            bsmp_enable_message = bsmp_send(BSMP_WRITE, variableID=HALT_CH_SI, value=val).encode()
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(.1)
                s.connect((BBB_HOSTNAME, GPIO_TCP_PORT))
                s.sendall(bsmp_enable_message)
                time.sleep(.01) # magic number!!!!
                while True:
                    data = s.recv(8)
                    if not data: break
                    return data
        else:
            logger.warning(
                f'Halt signal not send due to diagnostic code Drive I code:\
                    {self.i_drive.diagnostic_code},\Drive S code:{self.s_drive.diagnostic_code}')
            self.soft_drive_message = \
                f'Halt signal not send due to diagnostic code Drive I code:\
                    {self.i_drive.diagnostic_code}, Drive S code:{self.s_drive.diagnostic_code}'

    def phase_enable_status(self):
        bsmp_enable_message = bsmp_send(BSMP_READ, variableID=ENABLE_CH_SI, size=0).encode()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(.1)
            s.connect((BBB_HOSTNAME, GPIO_TCP_PORT))
            s.sendall(bsmp_enable_message)
            time.sleep(.01) # magic number!!!!
            while True:
                data = s.recv(8)
                if not data: break
                return(bool(data[-2]))
    
    def phase_halt_release_status(self):
        bsmp_enable_message = bsmp_send(BSMP_READ, variableID=HALT_CH_SI, size=0).encode()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(.1)
            s.connect((BBB_HOSTNAME, GPIO_TCP_PORT))
            s.sendall(bsmp_enable_message)
            time.sleep(.01) # magic number!!!!
            while True:
                data = s.recv(8)
                if not data: break
                return(bool(data[-2]))

    def phase_enable_and_release_halt(self, val: bool):
        assert val==True or val==False
        self.phase_set_enable(val)
        self.phase_release_halt(val)

    def phase_check_for_move(self) -> bool:
        drive_i_max_velocity = self.i_drive.get_max_velocity()
        drive_s_max_velocity = self.s_drive.get_max_velocity()
        if drive_i_max_velocity == drive_s_max_velocity:
            drive_i_target_position = self.s_drive.get_encoder_position()
            drive_s_target_position = self.s_drive.get_encoder_position()
            if drive_i_target_position == drive_s_target_position:
                return True
            else:
                logger.warning('Movement not allowed. Drives I and S have different target positions.')
                return False
        else:
            logger.warning('Movement not allowed. Drives I and S have different maximum velocities.')
            return False

    def phase_start(self, val: bool) -> bool:
        if self.phase_check_for_move():
            assert val==True or val==False
            if self.i_drive.diagnostic_code == self.s_drive.diagnostic_code =='A010':
                bsmp_enable_message = bsmp_send(BSMP_WRITE, variableID=START_CH_SI, value=val).encode()
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(.1)
                    s.connect((BBB_HOSTNAME, GPIO_TCP_PORT))
                    s.sendall(bsmp_enable_message)
                    time.sleep(.01) # magic number!!!!
                    while True:
                        data = s.recv(16)
                        if not data: break
                        return data
            else:
                logger.log(
                    f'Start signal not send due to diagnostic code Drive I code:\
                        {self.i_drive.diagnostic_code},\Drive S code:{self.s_drive.diagnostic_code}')
                self.soft_drive_message = \
                    f'Start signal not send due to diagnostic code Drive I code:\
                        {self.i_drive.diagnostic_code}, Drive S code:{self.s_drive.diagnostic_code}'
        else:
            logger.error('Gap movement not started because one or more conditions have not been met. Check log for more information.')
            return False

    def allowed_phase_change(self) -> bool:
        if self.i_target_position != self.s_target_position:
            return False
        else: return True
    
    def phase_stop(self):
        self.phase_release_halt(0)



###------------main------------###
class EpuConfig(BaseModel):
    MINIMUM_GAP: float
    MAXIMUM_GAP: float
    MINIMUM_PHASE: float
    MAXIMUM_PHASE: float
    A_DRIVE_ADDRESS: int
    B_DRIVE_ADDRESS: int
    I_DRIVE_ADDRESS: int
    S_DRIVE_ADDRESS: int
    EPU_LOG_FILE_PATH: str

with open('../config/config.toml') as f:
    config = toml.load('../config/config.toml')
epu_config = EpuConfig(**config['EPU2'])

epu = Epu()
