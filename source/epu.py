import logging, threading, socket
from ecodrive import EcoDrive
from utils import *
from datetime import datetime
import constants as _cte

################## LOGGING #####################
logging.basicConfig(filename='epu.txt', filemode='w', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', encoding='utf-8')
logger = logging.getLogger(__name__)
logger.info(datetime.now().strftime('%m/%d/%Y, %H:%M:%S'))

class Epu():

    def __init__(self, callback_update=lambda x:1):

        self.callback_update = callback_update
        self.warnings = []
        #self.callback_update = callback_update
        self.a_drive = EcoDrive(
            address=_cte.a_drive_address,
            min_limit=_cte.minimum_gap,
            max_limit=_cte.maximum_gap, drive_name='A')
        self.b_drive = EcoDrive(
            address=_cte.b_drive_address,
            min_limit=_cte.minimum_gap,
            max_limit=_cte.maximum_gap, drive_name='B')
        self.i_drive = EcoDrive(
            address=_cte.i_drive_address,
            min_limit=_cte.minimum_phase,
            max_limit=_cte.maximum_phase, drive_name='I')
        self.s_drive = EcoDrive(
            address=_cte.s_drive_address,
            min_limit=_cte.minimum_phase,
            max_limit=_cte.maximum_phase, drive_name='S')

        # config threads
        self.gap_start_event = threading.Event()
        self.phase_start_event = threading.Event()
        self.stop_event = threading.Event()
        self.stop_event.set()
        self._epu_lock = threading.RLock()
        self.monitor_phase_movement_thread = Thread(target=self.monitor_phase_movement, daemon=True)
        self.monitor_gap_movement_thread = Thread(target=self.monitor_gap_movement, daemon=True)
        self.standstill_monitoring_thread = Thread(target=self.standstill_monitoring, daemon=True)

        # init functions
        self.init_variables_scope()
        self.standstill_monitoring_thread.start()
        self.monitor_phase_movement_thread.start()
        self.monitor_gap_movement_thread.start()

    def init_variables_scope(self):
        # drive a variables
        self.a_target_position = self.a_drive.get_target_position()
        self.a_target_velocity = self.a_drive.get_max_velocity()
        self.a_resolver_gap = self.a_drive.get_resolver_position()
        self.a_encoder_gap = self.a_drive.get_encoder_position()
        self.a_diag_code = self.a_drive.get_diagnostic_code()
        self.a_is_moving = False
        # drive b variables
        self.b_target_position = self.b_drive.get_target_position()
        self.b_target_velocity = self.b_drive.get_max_velocity()
        self.b_resolver_gap = self.b_drive.get_resolver_position()
        self.b_encoder_gap = self.b_drive.get_encoder_position()
        self.b_diag_code = self.b_drive.get_diagnostic_code()
        self.b_is_moving = False
        # drive i variables
        self.i_target_position = self.i_drive.get_target_position()
        self.i_target_velocity = self.i_drive.get_max_velocity()
        self.i_resolver_phase = self.i_drive.get_resolver_position()
        self.i_encoder_phase = self.i_drive.get_encoder_position()
        self.i_diag_code = self.i_drive.get_diagnostic_code()
        self.i_is_moving = False
        #drive s variables
        self.s_resolver_gap = self.s_drive.get_resolver_position()
        self.s_target_velocity = self.s_drive.get_max_velocity()
        self.s_resolver_phase = self.s_drive.get_resolver_position()
        self.s_encoder_phase = self.s_drive.get_encoder_position()
        self.s_diag_code = self.s_drive.get_diagnostic_code()
        self.s_is_moving = False

        ## undulator status variables
        self.soft_message = ''
        gap_drive_enable, gap_drive_halt = self.a_drive.get_halten_status()
        phase_drive_enable, phase_drive_halt = self.i_drive.get_halten_status()
        self.gap_enable = gap_drive_enable
        self.phase_enable = phase_drive_enable
        self.gap_halt_released = not gap_drive_halt
        self.phase_halt_released = not phase_drive_halt
        self.gap_change_allowed = self.gap_halt_released
        self.phase_change_allowed = self.phase_halt_released
        self.gap_is_moving = False
        self.phase_is_moving = False
        self.is_moving = self.phase_is_moving or self.gap_is_moving

        ## undulator gap control variables
        self.gap_target = self.a_target_position
        self.gap_target_velocity = self.a_target_velocity
        self.gap = self.a_encoder_gap
        self.gap_enable_and_halt_released = (
            self.gap_enable and self.gap_halt_released
            )
        ### undulator phase control variables
        self.phase_target = self.i_target_position
        self.phase_target_velocity = self.i_target_velocity
        self.phase = self.i_encoder_phase
        self.phase_enable_and_halt_released = (
            self.phase_enable and self.phase_halt_released
            )
    
    def monitor_gap_movement(self):
        while True:
            try:
                self.gap_start_event.wait()
                self.a_drive.connect() # sends BCD:{address}
                start = time.time()
                count = 0
                while self.gap_start_event.is_set():
                    c = 0
                    while c<20:
                        self.gap = self.a_drive.get_encoder_position(False)
                        #self.callback_update()
                        print(self.gap, self.gap_is_moving)
                        c+=1
                        count +=1
                    if abs(self.gap - self.gap_target) < .005:
                        end = time.time()
                        self.gap_is_moving = 0
                        self.gap_start_event.clear()
                        print(count, end-start, count/(end-start))
                self.gap_start_event.clear()
                self.stop_event.set()
            except Exception as e:
                logger.exception('Could not moving update')
                print(e)
    
    def monitor_phase_movement(self):
        while True:
            try:
                self.phase_start_event.wait()
                self.i_drive.connect() # sends BCD:{address}
                #timeout = abs(self.phase_target - self.phase)/self.target_velocity
                start = time.time()
                count = 0
                while self.phase_start_event.is_set():
                    c = 0
                    while c<20:
                        self.phase = self.i_drive.get_encoder_position(False)
                        #self.callback_update()
                        c+=1
                        count +=1
                    # print(f'Fase: {self.phase}')
                    if abs(self.phase - self.phase_target) < .005:
                        end = time.time()
                        self.phase_is_moving = 0
                        self.phase_start_event.clear()
                        print(count, end-start, count/(end-start))
                self.phase_start_event.clear()
                self.stop_event.set()
            except Exception as e:
                logger.exception('Could not moving update')
                print(e)

    def standstill_monitoring(self):
        while True:
            try:
                # self.gap_enable_status()
                # self.gap_halt_release_status()
                # self.phase_enable_status()
                # self.phase_halt_release_status()
                self.stop_event.wait()
                self.i_resolver_phase = self.i_drive.get_resolver_position()
                self.stop_event.wait()
                self.i_encoder_phase = self.i_drive.get_encoder_position()
                self.phase = self.i_encoder_phase
                self.stop_event.wait()
                a, b = self.i_drive.get_halten_status()
                self.i_halt_released, self.i_enable = a, b
                self.stop_event.wait()
                self.i_diag_code = self.i_drive.get_diagnostic_code()
                self.stop_event.wait()
                self.s_resolver_phase = self.s_drive.get_resolver_position()
                self.stop_event.wait()
                self.s_encoder_phase = self.s_drive.get_encoder_position()
                self.stop_event.wait()
                a, b = self.s_drive.get_halten_status()
                self.s_halt_released, self.s_enable = a, b
                self.stop_event.wait()
                self.s_diag_code = self.s_drive.get_diagnostic_code()
                self.stop_event.wait()
                self.a_resolver_gap = self.a_drive.get_resolver_position()
                self.stop_event.wait()
                self.a_encoder_gap = self.a_drive.get_encoder_position()
                self.gap = self.a_encoder_gap
                self.stop_event.wait()
                a, b = self.a_drive.get_halten_status()
                self.a_halt_released, self.a_enable = a, b
                self.stop_event.wait()
                self.a_diag_code = self.a_drive.get_diagnostic_code()
                self.stop_event.wait()
                self.b_resolver_gap = self.b_drive.get_resolver_position()
                self.stop_event.wait()
                self.b_encoder_gap = self.b_drive.get_encoder_position()
                self.stop_event.wait()
                a, b = self.b_drive.get_halten_status()
                self.b_halt_released, self.b_enable =  a, b
                self.b_diag_code = self.b_drive.get_diagnostic_code()
            except Exception as e:
                logger.exception('Default monitor thread exception')
                print(e)

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
        self.stop_event.clear()
        if _cte.minimum_gap <= target_gap <= _cte.maximum_gap:
            try:
                self.a_drive.set_target_position(target_gap)
                self.b_drive.set_target_position(target_gap)
                self.a_target_position = self.a_drive.get_target_position()
                self.b_target_position = self.b_drive.get_target_position()
            except Exception as e:
                self.stop_event.set()
                logger.exception('Could not change target gap')
                print('Could not change target gap')
                if self.a_target_position != self.b_target_position:
                    logger.warning('GC01 warning: correct cause before moving')
                    self.warnings.append('GC01')
                    print('GC01 warning: correct cause before moving')
                    raise e
            else:
                if self.a_target_position == self.b_target_position:
                    self.stop_event.set()
                    self.gap_target = target_gap
                    return target_gap
                else:
                    logger.warning('GC01 warning: correct cause before moving')
                    self.warnings.append('GC01')
                    print('GC01 warning: correct cause before moving')
                    self.gap_target = None
                    raise e
        else:
            self.stop_event.set()
            logger.error(f'Gap value given, ({target_gap}), is out of range.')
            print(f'Gap value given, ({target_gap}), is out of range.')
            return self.gap_target

    def gap_set_velocity(self, target_velocity: float):
        self.stop_event.clear()
        if 50 <= target_velocity <= 500:
            try:
                self.a_drive.set_target_velocity(target_velocity)
                self.b_drive.set_target_velocity(target_velocity)
                self.a_target_velocity = self.a_drive.get_max_velocity()
                self.b_target_velocity = self.b_drive.get_max_velocity()
            except Exception as e:
                self.stop_event.set()
                logger.exception('Could not change gap target velocity')
                print('Could not change gap target velocity')
                if self.a_target_position != self.b_target_position:
                    logger.warning('GC02 warning: correct cause before moving')
                    self.warnings.append('GC01')
                    print('GC02 warning: correct cause before moving')
                    raise e
            else:
                if self.a_target_position == self.b_target_position:
                    self.stop_event.set()
                    self.gap_target_velocity = target_velocity
                    return target_velocity
                else:
                    logger.warning('GC02 warning: correct cause before moving')
                    self.warnings.append('GC02')
                    print('GC02 warning: correct cause before moving')
                    self.gap_target = None
                    raise e
        else:
            self.stop_event.set()
            logger.error(f'Velocity value given, ({target_velocity}), is out of range.')
            print(f'Velocity value given, ({target_velocity}), is out of range.')
            return self.gap_target

    def gap_check_for_move(self) -> bool:
        drive_a_max_velocity = self.a_drive.get_max_velocity()
        drive_b_max_velocity = self.b_drive.get_max_velocity()
        if drive_a_max_velocity == drive_b_max_velocity:
            drive_a_target_position = self.a_drive.get_target_position()
            drive_b_target_position = self.b_drive.get_target_position()
            if drive_a_target_position == drive_b_target_position:
                drive_i_diag_code = self.i_drive.get_diagnostic_code()
                drive_s_diag_code = self.s_drive.get_diagnostic_code()
                drive_a_diag_code = self.a_drive.get_diagnostic_code()
                drive_b_diag_code = self.b_drive.get_diagnostic_code()
                if drive_i_diag_code == drive_s_diag_code == drive_a_diag_code == drive_b_diag_code == 'A211':
                    return True
            else:
                logger.warning('Movement not allowed. Drives A and B have different target positions.')
                return False
        else:
            # Verificar a diferença entre setpoint de velocidade e velocidade máxima
            logger.warning('Movement not allowed. Drives A and B have different target velocities.')
            return False
    
    def allowed_to_change_gap(self) -> bool:
            if not self.gap_enable_status():
                return False
            elif not self.gap_halt_release_status():
                return False
            elif not self.gap_check_for_move():
                    return False
            else:
                self.gap_change_allowed = True
                return True

    def gap_set_enable(self, val: bool):
        try:
            assert val==True or val==False
        except Exception:
            logger.error('Enbale argument must be boolean')
            self.soft_drive_message = 'Enbale argument must be boolean'
        else:
            if val:
                with self._epu_lock:
                    self.stop_event.clear()
                    try:
                        a_diagnostic_code = self.a_drive.get_diagnostic_code()
                        b_diagnostic_code = self.b_drive.get_diagnostic_code()
                        self.stop_event.set()
                    except Exception:
                        self.stop_event.set()
                        logger.exception('Could not set enable')
                    else:
                        if a_diagnostic_code == b_diagnostic_code == 'A012':
                            bsmp_enable_message = bsmp_send(
                                _cte.BSMP_WRITE, variableID=_cte.ENABLE_CH_AB,
                                    value=val).encode()
                            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                                s.settimeout(.1)
                                s.connect((_cte.beaglebone_addr, _cte.io_port))
                                s.sendall(bsmp_enable_message)
                                time.sleep(.01) # magic number
                                while True:
                                    data = s.recv(16)
                                    if not data: break
                                    return data
                        else:
                            logger.error(
                                f'Enable signal not send due to diagnostic code Drive A code:\
                                    {a_diagnostic_code},\Drive B code:{b_diagnostic_code}')
                            self.soft_drive_message = \
                                f'Enable signal not send due to diagnostic code Drive A code:\
                                    {a_diagnostic_code}, Drive B code:{b_diagnostic_code}'
                            return False

            else:
                if not self.gap_halt_release_status():
                    bsmp_enable_message = bsmp_send(_cte.BSMP_WRITE, variableID=_cte.ENABLE_CH_AB, value=val).encode()
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(.1)
                        s.connect((_cte.beaglebone_addr, _cte.io_port))
                        s.sendall(bsmp_enable_message)
                        time.sleep(.01) # magic number
                        while True:
                            data = s.recv(16)
                            if not data: break
                            return data
                else:
                    logger.info('Set drive halt before set enable to zero')
                    print('Set drive halt before set enable to zero')
                    return False
            
    def gap_release_halt(self, val: bool):
        try:
            assert val==True or val==False
        except Exception:
            logger.error('Enbale argument must be boolean')
            self.soft_drive_message = 'Enbale argument must be boolean'
        else:
            if val:
                with self._epu_lock:
                    self.stop_event.clear()
                    try:
                        a_diagnostic_code = self.a_drive.get_diagnostic_code()
                        b_diagnostic_code = self.b_drive.get_diagnostic_code()
                        self.stop_event.set()
                    except Exception:
                        self.stop_event.set()
                        logger.exception('Could not relase halt')
                        print('Could not relase halt')
                    else:
                        if a_diagnostic_code == b_diagnostic_code == 'A010':
                            bsmp_enable_message = bsmp_send(
                                _cte.BSMP_WRITE, variableID=_cte.HALT_CH_AB,
                                value=val).encode()
                            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                                s.settimeout(.1)
                                s.connect((_cte.beaglebone_addr, _cte.io_port))
                                s.sendall(bsmp_enable_message)
                                time.sleep(.01) # magic number
                                while True:
                                    data = s.recv(16)
                                    if not data: break
                                    return data
                        else:
                            logger.error(
                                f'Relese Halt signal not send due to diagnostic code Drive A code:\
                                    {self.a_drive.diagnostic_code},\Drive B code:{self.b_drive.diagnostic_code}')
                            self.soft_drive_message = \
                                f'Relese Halt signal not send due to diagnostic code Drive A code:\
                                    {self.a_drive.diagnostic_code}, Drive B code:{self.b_drive.diagnostic_code}'
                            return False
            else:
                bsmp_enable_message = bsmp_send(
                    _cte.BSMP_WRITE, variableID=_cte.HALT_CH_AB,
                    value=val).encode()
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(.1)
                    s.connect((_cte.beaglebone_addr, _cte.io_port))
                    s.sendall(bsmp_enable_message)
                    time.sleep(.01) # magic number
                    while True:
                        data = s.recv(16)
                        if not data: break
                        return data

    def gap_enable_and_release_halt(self, val: bool=True) -> bool: # alterar nome da função
        if val == True:
            a = self.gap_set_enable(val)
            b = self.gap_release_halt(val)
            if a == b: return True
            else: return False
        elif val == False:
            a = self.gap_release_halt(val)
            b = self.gap_set_enable(val)
            if a == b: return True
            else: return False
        else:
            logger.error('gap_enable_and_release_halt() argument must be boolean')
            print('gap_enable_and_release_halt() argument must be boolean')
            return False

    def gap_start(self, val: bool):
        try:
            assert val==True or val==False
        except AssertionError:
            logger.error('Gap start argument must be boolean.')
            self.soft_drive_message = 'Gap start argument must be boolean.'
            return False
        else:
            with self._epu_lock:
                self.stop_event.clear()
                if self.gap_check_for_move():
                    try:
                        a_diagnostic_code = self.a_drive.get_diagnostic_code()
                        b_diagnostic_code = self.b_drive.get_diagnostic_code()
                    except:
                        logger.error('Could not get diagnostic code')
                        self.stop_event.set()
                    else:
                        if a_diagnostic_code == b_diagnostic_code == 'A211':
                            bsmp_enable_message = bsmp_send(_cte.BSMP_WRITE, variableID=_cte.START_CH_AB, value=val).encode()
                            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                                s.settimeout(.1)
                                s.connect((_cte.beaglebone_addr, _cte.io_port))
                                self.gap_start_event.set()
                                self.gap_is_moving = True
                                time.sleep(.1) # waits for the tcp reading in default thread
                                s.sendall(bsmp_enable_message)
                                while True:
                                    data = s.recv(16)
                                    if not data: break
                                    return data
                        else:
                            self.stop_event.set()
                            logger.error(
                                f'Start signal not send due to diagnostic code Drive A code:\
                                    {a_diagnostic_code},\Drive B code:{b_diagnostic_code}')
                            self.soft_drive_message = \
                                f'Start signal not send due to diagnostic code Drive A code:\
                                    {a_diagnostic_code}, Drive B code:{b_diagnostic_code}'
                            return False
                else:
                    self.stop_event.set()
                    logger.error('Gap movement not started because one or more conditions have not been met.\
                                Check log for more information.')
                    return False

    def gap_enable_status(self) -> bool:
        bsmp_enable_message = bsmp_send(
            _cte.BSMP_READ, variableID=_cte.ENABLE_CH_AB,
            size=0).encode()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(.1)
            s.connect((_cte.beaglebone_addr, _cte.io_port))
            s.sendall(bsmp_enable_message)
            time.sleep(.01) # magic number
            while True:
                data = s.recv(8)
                if not data: break
                if bool(data[-2]): self.gap_enable = True
                else: self.gap_enable = False
                if not data: break
                return(bool(data[-2]))
    
    def gap_halt_release_status(self):
        bsmp_enable_message = bsmp_send(
            _cte.BSMP_READ, variableID=_cte.HALT_CH_AB,
            size=0).encode()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(.1)
            s.connect((_cte.beaglebone_addr, _cte.io_port))
            s.sendall(bsmp_enable_message)
            time.sleep(.01) # magic number!!!!
            while True:
                data = s.recv(8)
                if not data: break
                if bool(data[-2]): self.gap_halt_released = True
                else: self.gap_halt_released = False
                return(bool(data[-2]))

    def gap_stop(self):
        self.gap_set_enable(False)
        self.gap_release_halt(False)
    
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
        self.stop_event.clear()
        if _cte.minimum_phase <= target_phase <= _cte.maximum_phase:
            try:
                self.i_drive.set_target_position(target_phase)
                self.s_drive.set_target_position(target_phase)
                self.i_target_position = self.i_drive.get_target_position()
                self.s_target_position = self.s_drive.get_target_position()
            except Exception as e:
                self.stop_event.set()
                logger.exception('Could not change target phase')
                print('Could not change target phase')
                if self.i_target_position != self.s_target_position:
                    logger.warning('PC01 warning: correct cause before moving')
                    self.warnings.append('GC01')
                    print('PC01 warning: correct cause before moving')
                    raise e
            else:
                if self.i_target_position == self.s_target_position:
                    self.stop_event.set()
                    self.phase_target = target_phase
                    return target_phase
                else:
                    logger.warning('PC01 warning: correct cause before moving')
                    self.warnings.append('GC01')
                    print('PC01 warning: correct cause before moving')
                    self.phase_target = None
                    raise e
        else:
            self.stop_event.set()
            logger.error(f'phase value given, ({target_phase}), is out of range.')
            print(f'phase value given, ({target_phase}), is out of range.')
            return self.phase_target

    def phase_set_velocity(self, target_velocity: float):
        self.stop_event.clear()
        if 50 <= target_velocity <= 500:
            try:
                self.i_drive.set_target_velocity(target_velocity)
                self.s_drive.set_target_velocity(target_velocity)
                self.i_target_velocity = self.i_drive.get_max_velocity()
                self.s_target_velocity = self.s_drive.get_max_velocity()
            except Exception as e:
                self.stop_event.set()
                logger.exception('Could not change phase target velocity')
                print('Could not change phase target velocity')
                if self.i_target_position != self.s_target_position:
                    logger.warning('PC02 warning: correct cause before moving')
                    self.warnings.append('PC02')
                    print('PC02 warning: correct cause before moving')
                    raise e
            else:
                if self.i_target_velocity == self.s_target_velocity:
                    self.stop_event.set()
                    self.phase_target_velocity = target_velocity
                    return target_velocity
                else:
                    logger.warning('PC02 warning: correct cause before moving')
                    self.warnings.append('PC02')
                    print('PC02 warning: correct cause before moving')
                    self.phase_target = None
                    raise e
        else:
            logger.info('Veloxity must be between 50 mm/s and 500 mm/s')

    def phase_check_for_move(self) -> bool:
        drive_i_max_velocity = self.i_drive.get_max_velocity()
        drive_s_max_velocity = self.s_drive.get_max_velocity()
        if drive_i_max_velocity == drive_s_max_velocity:
            drive_i_target_position = self.i_drive.get_target_position()
            drive_s_target_position = self.s_drive.get_target_position()
            if drive_i_target_position == drive_s_target_position:
                drive_i_diag_code = self.i_drive.get_diagnostic_code()
                drive_s_diag_code = self.s_drive.get_diagnostic_code()
                drive_a_diag_code = self.a_drive.get_diagnostic_code()
                drive_b_diag_code = self.b_drive.get_diagnostic_code()
                if drive_i_diag_code == drive_s_diag_code == drive_a_diag_code == drive_b_diag_code:
                    return True
                else: return False
            else:
                print('Movement not allowed. Drives I and S have different target positions.')
                return False
        else:
            # Verificar a diferença entre setpoint de velocidade e velocidade máxima
            print('Movement not allowed. Drives I and S have different target velocities.')
            return False

    def allowed_to_change_phase(self) -> bool:
        try:
            if self.phase_enable_status():
                if self.phase_halt_release_status():
                    self.stop_event.clear()
                    if self.phase_check_for_move():
                        self.stop_event.set()
                        return True
                    else:
                        self.stop_event.set()
                        return False
                else: return False
            else: return False
        except:
            if self.stop_event.is_set(): self.stop_event.set()
            logger.exception('Could not complete check')
            print(f'Could not complete check. Check {__name__} log file')
            
    def phase_set_enable(self, val: bool):
        try:
            assert val==True or val==False
        except Exception:
            logger.error('Enbale argument must be boolean')
            self.soft_drive_message = 'Enbale argument must be boolean'
        else:
            if val:
                with self._epu_lock:
                    self.stop_event.clear()
                    try:
                        i_diagnostic_code = self.i_drive.get_diagnostic_code()
                        s_diagnostic_code = self.s_drive.get_diagnostic_code()
                        self.stop_event.set()
                    except Exception:
                        self.stop_event.set()
                        logger.exception('Could not set phase enable.')
                    else:
                        if i_diagnostic_code == s_diagnostic_code == 'A012':
                            bsmp_enable_message = bsmp_send(
                                _cte.BSMP_WRITE, variableID=_cte.ENABLE_CH_SI,
                                value=val).encode()
                            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                                s.settimeout(.1)
                                s.connect((_cte.beaglebone_addr, _cte.io_port))
                                s.sendall(bsmp_enable_message)
                                time.sleep(.01) # magic number
                                while True:
                                    data = s.recv(16)
                                    if not data: break
                                    return data
                        else:
                            logger.error(
                                f'Enable signal not send due to diagnostic code Drive I code:\
                                    {i_diagnostic_code},\Drive S code:{s_diagnostic_code}')
                            self.soft_drive_message = \
                                f'Enable signal not send due to diagnostic code Drive I code:\
                                    {i_diagnostic_code}, Drive S code:{s_diagnostic_code}'
                            return False
            else:
                if not self.phase_halt_release_status():
                    bsmp_enable_message = bsmp_send(
                        _cte.BSMP_WRITE, variableID=_cte.ENABLE_CH_SI,
                        value=val).encode()
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(.1)
                        s.connect((_cte.beaglebone_addr, _cte.io_port))
                        s.sendall(bsmp_enable_message)
                        time.sleep(.01) # magic number
                        while True:
                            data = s.recv(16)
                            if not data: break
                            return data
                else:
                    logger.info('Enable drive halt before set enable signal to zero')
                    print('Set drive halt before set enable to zero')
                    return False
    
    def phase_release_halt(self, val: bool):
        try:
            assert val==True or val==False
        except Exception:
            logger.error('Enbale argument must be boolean')
            self.soft_drive_message = 'Enbale argument must be boolean'
        else:
            if val:
                i_diagnostic_code = self.i_drive.get_diagnostic_code()
                s_diagnostic_code = self.s_drive.get_diagnostic_code()
                if i_diagnostic_code == s_diagnostic_code == 'A010':
                    bsmp_enable_message = bsmp_send(_cte.BSMP_WRITE, variableID=_cte.HALT_CH_SI, value=val).encode()
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(.1)
                        s.connect((_cte.beaglebone_addr, _cte.io_port))
                        s.sendall(bsmp_enable_message)
                        time.sleep(.01) # magic number
                        while True:
                            data = s.recv(16)
                            if not data: break
                            return data
                else:
                    logger.error(
                        f'Relese Halt signal not send due to diagnostic code Drive I code:\
                            {i_diagnostic_code},\Drive S code:{s_diagnostic_code}')
                    self.soft_drive_message = \
                        f'Relese Halt signal not send due to diagnostic code Drive I code:\
                            {i_diagnostic_code}, Drive S code:{s_diagnostic_code}'
                    return False
            else:
                bsmp_enable_message = bsmp_send(
                    _cte.BSMP_WRITE, variableID=_cte.HALT_CH_SI,
                    value=val).encode()
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(.1)
                    s.connect((_cte.beaglebone_addr, _cte.io_port))
                    s.sendall(bsmp_enable_message)
                    time.sleep(.01) # magic number
                    while True:
                        data = s.recv(16)
                        if not data: break
                        return data

    def phase_enable_and_release_halt(self, val):
        self.phase_set_enable(val)
        self.phase_release_halt(val)

    def phase_enable_status(self):
        bsmp_enable_message = bsmp_send(
            _cte.BSMP_READ, variableID=_cte.ENABLE_CH_SI,
            size=0).encode()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(.1)
            s.connect((_cte.beaglebone_addr, _cte.io_port))
            s.sendall(bsmp_enable_message)
            time.sleep(.01) # magic number!!!!
            while True:
                data = s.recv(8)
                if bool(data[-2]): self.phase_enable = True
                else: self.phase_enable = False
                if not data: break
                if bool(data[-2]): self.gap_enable = True
                else: self.gap_enable = False
                return(bool(data[-2]))
    
    def phase_halt_release_status(self):
        bsmp_enable_message = bsmp_send(
            _cte.BSMP_READ, variableID=_cte.HALT_CH_SI,
            size=0).encode()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(.1)
            s.connect((_cte.beaglebone_addr, _cte.io_port))
            s.sendall(bsmp_enable_message)
            time.sleep(.01) # magic number!!!!
            while True:
                data = s.recv(8)
                if bool(data[-2]): self.phase_halt_released = True
                else: self.phase_halt_released = False
                return(bool(data[-2]))

    def phase_start(self, val: bool) -> bool:
        try:
            assert val==True or val==False
        except AssertionError:
            logger.error('Phase start argument must be boolean.')
            self.soft_drive_message = 'Phase start argument must be boolean.'
            return False
        else:
            with self._epu_lock:
                self.stop_event.clear()
                if self.phase_check_for_move():
                    try:
                        i_diagnostic_code = self.i_drive.get_diagnostic_code()
                        s_diagnostic_code = self.s_drive.get_diagnostic_code()
                    except:
                        logger.error('Could not get diagnostic code')
                        self.stop_event.set()
                    else:
                        if i_diagnostic_code == s_diagnostic_code == 'A211':
                            bsmp_enable_message = bsmp_send(
                                _cte.BSMP_WRITE, variableID=_cte.START_CH_SI,
                                value=val).encode()
                            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                                s.settimeout(.1)
                                s.connect((_cte.beaglebone_addr, _cte.io_port))
                                self.phase_start_event.set()
                                self.phase_is_moving = True
                                time.sleep(.1) # waits for the tcp reading in default thread
                                s.sendall(bsmp_enable_message)
                                while True:
                                    data = s.recv(8)
                                    if not data: break
                                    return data
                        else:
                            logger.error(
                                f'Start signal not send due to diagnostic code Drive I code:\
                                    {i_diagnostic_code},\Drive I code:{s_diagnostic_code}')
                            self.soft_drive_message = \
                                f'Start signal not send due to diagnostic code Drive S code:\
                                    {i_diagnostic_code}, Drive S code:{s_diagnostic_code}'
                else:
                    self.stop_event.set()
                    logger.error(
                        "Phase movement not started because one or "
                        "more conditions have not been met. "
                        "Check log for more information."
                        )
                    return False
  
    def phase_stop(self):
        self.phase_release_halt(0)
        self.phase_set_enable(0)

