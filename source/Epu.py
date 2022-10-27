import toml, logging, threading, socket
from EcoDrive import EcoDrive
from pydantic import BaseModel
from utils import *
from constants import TCP_IP, GPIO_TCP_PORT, bsmp_send

logger = logging.getLogger('__name__')
logging.basicConfig(filename='/tmp/EpuClass.log',
    filemode='w', level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S')

class EpuConfig(BaseModel):
    MINIMUM_GAP: float
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

with open('../config/config.toml') as f:
    config = toml.load('../config/config.toml')
epu_config = EpuConfig(**config['EPU2'])

BSMP_WRITE = 0X20
BSMP_READ = 0X10

HALT_CH_AB =   0x10
START_CH_AB =  0x20
ENABLE_CH_AB = 0x30

HALT_CH_SI =   0x11
START_CH_SI =  0x21
ENABLE_CH_SI = 0x31

class Epu():

    def __init__(self):

        self.a_drive = EcoDrive(
            serial_port=epu_config.SERIAL_PORT,
            address=epu_config.A_DRIVE_ADDRESS,
            baud_rate=epu_config.BAUD_RATE,
            min_limit=epu_config.MINIMUM_GAP,
            max_limit=epu_config.MAXIMUM_GAP)
        self.b_drive = EcoDrive(
            serial_port=epu_config.SERIAL_PORT,
            address=epu_config.B_DRIVE_ADDRESS,
            baud_rate=epu_config.BAUD_RATE,
            min_limit=epu_config.MINIMUM_GAP,
            max_limit=epu_config.MAXIMUM_GAP)
        self.i_drive = EcoDrive(
            serial_port=epu_config.SERIAL_PORT,
            address=epu_config.I_DRIVE_ADDRESS,
            baud_rate=epu_config.BAUD_RATE,
            min_limit=epu_config.MINIMUM_PHASE,
            max_limit=epu_config.MAXIMUM_PHASE)
        self.s_drive = EcoDrive(
            serial_port=epu_config.SERIAL_PORT,
            address=epu_config.S_DRIVE_ADDRESS,
            baud_rate=epu_config.BAUD_RATE,
            min_limit=epu_config.MINIMUM_PHASE,
            max_limit=epu_config.MAXIMUM_PHASE)

        self._epu_lock = threading.RLock()
        self.MAX_POSITION_DIFF = 1

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
        self.is_moving = self.a_is_moving or self.b_is_moving or self.i_is_moving or self.s_is_moving
        self.soft_message = ''

        ### undulator gap variables
        self.gap_target = self.a_target_position
        self.gap = (self.a_encoder_gap + self.b_encoder_gap)*.5
        # self.gap_velocity = (self.a_act_velocity + self.b_act_velocity)*.5
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
        #self.phase_velocity = (self.i_act_velocity + self.s_act_velocity)*.5
        self.phase_enable = 0
        self.phase_halt_released = 0
        self.phase_enable_and_halt_released = self.phase_enable and self.phase_halt_released
        self.phase_res_position_diff = self.i_resolver_phase - self.s_resolver_phase
        self.phase_enc_position_diff = self.i_encoder_phase - self.s_encoder_phase
        self.phase_change_allowed = self.allowed_phase_change()

        self.update_1()
        self.update_2()


    @asynch
    @schedule(4)
    @timer
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

            # # gap
            self.gap_enable = self.a_enable and self.b_enable
            self.gap_halt_released = self.a_halt_released and self.b_halt_released
            self.gap_enable_and_halt_released = self.gap_enable and self.gap_halt_released
            self.gap_target = self.a_target_position
            self.gap = (self.a_encoder_gap + self.b_encoder_gap)*.5
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
            self.phase_enable = self.i_enable and self.s_enable
            self.phase_halt_released = self.i_halt_released and self.s_halt_released
            self.phase_enable_and_halt_released = self.phase_enable and self.phase_halt_released
        except Exception:
            logger.exception('Could not update_1.')
            print('Exception raised.')

    @asynch
    @schedule(.5)
    @timer
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
        if not (epu_config.MINIMUM_GAP < target_gap < epu_config.MAXIMUM_GAP):
            logger.error(f'Gap valeu given, ({target_gap}), is out of range.')
            print(f'Gap value given, ({target_gap}), is out of range.')
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

    def gap_set_enable(self, value: int):
        if not (self.a_drive.enable_status and self.b_drive.enable_status):
            if self.a_drive.diagnostic_code == self.b_drive.diagnostic_code =='A012':
                bsmp_enable_message = bsmp_send(BSMP_WRITE, command=ENABLE_CH_AB).encode()
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(.1)
                    s.connect((TCP_IP, GPIO_TCP_PORT))
                    s.sendall(bsmp_enable_message)
                    time.sleep(.01) # magic number!!!!
                    while True:
                        data = s.recv(16)
                        if not data: break
                        if data[1] == 224: return True
            else:
                logger.log(f'Enable signal not send due to diagnostic code Drive A code:{self.a_drive.diagnostic_code}, Drive B code:{self.b_drive.diagnostic_code}')
                self.soft_drive_message = f'Enable signal not send due to diagnostic code Drive A code:{self.a_drive.diagnostic_code}, Drive B code:{self.b_drive.diagnostic_code}'
        else:
            logger.log('Enable signal because it was aready present.')
            self.soft_drive_message = 'Enable signal because it was aready present.'
    
    def gap_release_halt(self, value: int):
        if not (self.a_drive.enable_status and self.b_drive.enable_status):
            if self.a_drive.diagnostic_code == self.b_drive.diagnostic_code =='A010':
                # send enable signal logic
                self.gap_halt_released = value
                return value
            else:
                logger.log(f'Enable signal not send due to diagnostic code Drive A code:{self.a_drive.diagnostic_code}, Drive B code:{self.b_drive.diagnostic_code}')
                self.soft_drive_message = f'Enable signal not send due to diagnostic code Drive A code:{self.a_drive.diagnostic_code}, Drive B code:{self.b_drive.diagnostic_code}'
        else:
            logger.log('Enable signal because it was aready present.')
            self.soft_drive_message = 'Enable signal because it was aready present.'

    def gap_enable_and_release_halt(self, value: int):
        self.gap_enable(value)
        self.gap_release_halt(value)

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

    def gap_start(self, value: int) -> bool:
        if self.gap_check_for_move():
            # start
            return True
        else:
            logger.error('Gap movement not started because one or more conditions have not been met. Check log for more information.')
            return False

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
        if not (epu_config.MINIMUM_phase < target_phase < epu_config.MAXIMUM_phase):
            logger.error(f'phase valeu given, ({target_phase}), is out of range.')
            print(f'phase valeu given, ({target_phase}), is out of range.')
            return None
        else:
            try:
                self.i_drive.set_target_position(target_phase)
                self.s_drive.set_target_position(target_phase)
            except Exception:
                logger.exception('Exception raised while trying to set phase.')
                return None
            else:
                try:
                    a_target_pos_read = self.i_drive.get_target_position()
                    b_target_pos_read = self.s_drive.get_target_position()
                except Exception:
                    logger.exception('Exception raised while trying to verify setted phase.')
                    return None
                else:
                    if a_target_pos_read == b_target_pos_read == target_phase:
                        return target_phase
                    else:
                        logger.error('Target position read is different from target position setted!')
                        return None

    def phase_set_enable(self, value: int):
        if not (self.i_drive.enable_status and self.s_drive.enable_status):
            if self.i_drive.diagnostic_code == self.s_drive.diagnostic_code =='A012':
                # send enable signal logic
                self.phase_enable = value
                return True
            else:
                logger.log(f'Enable signal not send due to diagnostic code Drive A code:{self.i_drive.diagnostic_code}, Drive B code:{self.s_drive.diagnostic_code}')
                self.soft_drive_message = f'Enable signal not send due to diagnostic code Drive A code:{self.i_drive.diagnostic_code}, Drive B code:{self.s_drive.diagnostic_code}'
        else:
            logger.log('Enable signal because it was aready present.')
            self.soft_drive_message = 'Enable signal because it was aready present.'
    
    def phase_release_halt(self, value: int):
        if not (self.i_drive.enable_status and self.s_drive.enable_status):
            if self.i_drive.diagnostic_code == self.s_drive.diagnostic_code =='A010':
                # send enable signal logic
                self.gap_halt_released = value
                return
            else:
                logger.log(f'Enable signal not send due to diagnostic code Drive A code:{self.i_drive.diagnostic_code}, Drive B code:{self.s_drive.diagnostic_code}')
                self.soft_drive_message = f'Enable signal not send due to diagnostic code Drive A code:{self.i_drive.diagnostic_code}, Drive B code:{self.s_drive.diagnostic_code}'
        else:
            logger.log('Enable signal because it was aready present.')
            self.soft_drive_message = 'Enable signal because it was aready present.'

    def phase_enable_and_release_halt(self, value: int):
        self.phase_enable(value)
        self.phase_release_halt(value)

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

    def phase_start(self, value: int) -> bool:
        if self.phase_check_for_move():
            # start
            return True
        else:
            logger.error('Phase movement not started because one or more conditions have not been met. Check log for more information.')
            return False

    def allowed_phase_change(self) -> bool:
        if self.i_target_position != self.s_target_position:
            return False
        else: return True
    
    def phase_stop(self):
        self.phase_release_halt(0)



epu = Epu()