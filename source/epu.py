import logging, threading, socket
from ecodrive import EcoDrive
from utils import *
from datetime import datetime
import constants as _cte

################## LOGGING #####################
logger = logging.getLogger('__name__')
logging.basicConfig(filename='./epu.log',
                    filemode='a', level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')

logger.info(datetime.now().strftime('%m/%d/%Y, %H:%M:%S'))

class Epu():

    def __init__(self, callback_update=lambda x:1):

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

        # threads
        self.start_event = threading.Event()
        self.stop_event = threading.Event()
        self.stop_event.set()
        self._epu_lock = threading.RLock()
        self.monitor_phase_movement_thread = Thread(
            target=self.monitor_phase_movement,
            daemon=True
            )
        self.standstill_phase_monitoring_thread = Thread(
            target=self.standstill_phase_monitoring,
            daemon=True
            )
        self.standstill_phase_monitoring_thread.setDaemon(True)

        # init functions
        self.init_variables_scope()
        self.standstill_phase_monitoring_thread.start()
        self.monitor_phase_movement_thread.start()

    def update(self):
        try:
            # drive a variables
            self.a_target_position = self.a_drive.get_target_position()
            self.a_resolver_gap = self.a_drive.get_resolver_position()
            self.a_encoder_gap = self.a_drive.get_encoder_position()
            self.a_halt_released, self.a_enable = (
                not self.a_drive.get_halten_status()[0],
                self.a_drive.get_halten_status()[1]
                )
            self.a_diag_code = self.a_drive.get_diagnostic_code()
            self.a_is_moving = False
            # drive b variables
            self.b_target_position = self.b_drive.get_target_position()
            self.b_resolver_gap = self.b_drive.get_resolver_position()
            self.b_encoder_gap = self.b_drive.get_encoder_position()
            self.b_halt_released, self.b_enable = (
                not self.b_drive.get_halten_status()[0],
                self.b_drive.get_halten_status()[1]
                )
            self.b_diag_code = self.b_drive.get_diagnostic_code()
            self.b_is_moving = False
            # drive i variables
            self.i_target_position = self.i_drive.get_target_position()
            self.i_resolver_phase = self.i_drive.get_resolver_position()
            self.i_encoder_phase = self.i_drive.get_encoder_position()
            self.i_halt_released, self.i_enable = (
                not self.i_drive.get_halten_status()[0],
                self.i_drive.get_halten_status()[1]
                )
            self.i_diag_code = self.i_drive.get_diagnostic_code()
            self.i_is_moving = False
            #drive s variables
            self.s_resolver_gap = self.s_drive.get_resolver_position()
            self.s_resolver_phase = self.s_drive.get_resolver_position()
            self.s_encoder_gap = self.s_drive.get_encoder_position()
            self.s_halt_released, self.s_enable = (
                not self.s_drive.get_halten_status()[0],
                self.s_drive.get_halten_status()[1]
                )
            self.s_diag_code = self.s_drive.get_diagnostic_code()
            self.is_moving = (
                self.a_is_moving
                or self.b_is_moving
                or self.i_is_moving
                or self.s_is_moving
                )
            self.gap_is_moving = self.a_drive.get_movement_status()
            self.phase_is_moving = self.i_drive.get_movement_status()
            self.is_moving = self.gap_is_moving or self.phase_is_moving
        except Exception:
            pass

    def init_variables_scope(self):

        # drive a variables
        self.a_target_position = self.a_drive.get_target_position()
        self.a_resolver_gap = self.a_drive.get_resolver_position()
        self.a_encoder_gap = self.a_drive.get_encoder_position()
        self.a_diag_code = self.a_drive.get_diagnostic_code()
        self.a_is_moving = False
        # drive b variables
        self.b_target_position = self.b_drive.get_target_position()
        self.b_resolver_gap = self.b_drive.get_resolver_position()
        self.b_encoder_gap = self.b_drive.get_encoder_position()
        self.b_diag_code = self.b_drive.get_diagnostic_code()
        self.b_is_moving = False
        # drive i variables
        self.i_target_position = self.i_drive.get_target_position()
        self.i_resolver_phase = self.i_drive.get_resolver_position()
        self.i_encoder_phase = self.i_drive.get_encoder_position()
        self.i_diag_code = self.i_drive.get_diagnostic_code()
        self.i_is_moving = False
        #drive s variables
        self.s_resolver_gap = self.s_drive.get_resolver_position()
        self.s_resolver_phase = self.s_drive.get_resolver_position()
        self.s_encoder_gap = self.s_drive.get_encoder_position()
        self.s_diag_code = self.s_drive.get_diagnostic_code()
        self.s_is_moving = False

        ## undulator status variables
        self.is_moving = (
            self.a_is_moving
            or self.b_is_moving
            or self.i_is_moving
            or self.s_is_moving
            )
        self.soft_message = ''
        self.gap_enable = False
        self.phase_enable = False
        self.gap_halt_released = False
        self.phase_halt_released = False
        self.gap_change_allowed = self.gap_halt_released
        self.phase_change_allowed = self.phase_halt_released
        self.gap_is_moving = False
        self.phase_is_moving = False
        self.is_moving = self.gap_is_moving or self.phase_is_moving

        ## undulator gap control variables
        self.gap_target = self.a_target_position
        self.gap = self.a_encoder_gap
        self.gap_enable_and_halt_released = (
            self.gap_enable and self.gap_halt_released
            )
        ### undulator phase control variables
        self.phase_target = self.i_target_position
        self.phase = self.i_encoder_phase
        self.phase_enable_and_halt_released = (
            self.phase_enable and self.phase_halt_released
            )
    
    def monitor_gap_movement(self):
        with self._epu_lock:
            try:
                self.gap_is_moving = 1
                timeout = 25 # faça a conta de quanto tempo leava o maior movimento.
                self.gap = self.a_drive.get_encoder_position(True)
                start = time.time()
                while self.gap_is_moving and timeout:
                    count = 1
                    while count <=10:
                        # get movement status pode ser trocada por target position reached
                        self.gap = self.a_drive.get_encoder_position(False)
                        count +=1
                    self.gap_is_moving = self.a_drive.get_movement_status(False)
                    count = 1    
                    timeout -= 1
                    self.moving_gap_monitoring_update_count +=1
                    end = time.time()
                self.moving_gap_monitoring_update_rate = (
                    self.moving_gap_monitoring_update_count/(end-start)
                )
                self.gap_is_moving = 0
                return self.gap_is_moving
            except Exception as e:
                logger.exception("Could not update encoder.")
                print(e)
    
    def monitor_phase_movement(self):
        while True:
            try:
                self.start_event.wait()
                self.i_drive.connect()
                start = time.time()
                count = 0
                self.start_event.wait()
                while self.start_event.is_set():
                    c = 0
                    while c<15:
                        self.phase = self.i_drive.get_encoder_position(False)
                        velocity = self.i_drive.get_act_velocity(False)
                        c+=1
                        count +=1
                    # print(f'Fase: {self.phase};\
                    #     Velocidade da fase: {velocity}\
                    #         count = {count}')
                    if abs(velocity) < .5 and abs(time.time()-start)>1:
                        end = time.time()
                        self.phase_is_moving = 0
                        self.start_event.clear()
                        print(count, end-start, count/(end-start))
                self.start_event.clear()
                self.stop_event.set()
            except Exception as e:
                logger.exception('Could not moving update')
                print(e)

    def standstill_phase_monitoring(self):
        while True:
            try:
                self.stop_event.wait()
                self.i_resolver_gap = self.i_drive.get_resolver_position()
                self.stop_event.wait()
                self.i_encoder_gap = self.i_drive.get_encoder_position()
                self.stop_event.wait()
                self.i_halt_released, self.i_enable = not self.i_drive.get_halten_status()[0], self.i_drive.get_halten_status()[1]
                self.stop_event.wait()
                self.i_diag_code = self.i_drive.get_diagnostic_code()
                self.stop_event.wait()
                self.s_resolver_gap = self.s_drive.get_resolver_position()
                self.stop_event.wait()
                self.s_encoder_gap = self.s_drive.get_encoder_position()
                self.stop_event.wait()
                self.s_halt_released, self.s_enable = not self.s_drive.get_halten_status()[0], self.s_drive.get_halten_status()[1]
                self.stop_event.wait()
                self.s_diag_code = self.s_drive.get_diagnostic_code()
                self.stop_event.wait()
                self.i_resolver_gap = self.i_drive.get_resolver_position()
                self.stop_event.wait()
                self.i_encoder_gap = self.i_drive.get_encoder_position()
                self.stop_event.wait()
                self.i_halt_released, self.i_enable = not self.i_drive.get_halten_status()[0], self.i_drive.get_halten_status()[1]
                self.stop_event.wait()
                self.i_diag_code = self.i_drive.get_diagnostic_code()
                self.stop_event.wait()
                self.s_resolver_gap = self.s_drive.get_resolver_position()
                self.stop_event.wait()
                self.s_encoder_gap = self.s_drive.get_encoder_position()
                self.stop_event.wait()
                self.s_halt_released, self.s_enable = not self.s_drive.get_halten_status()[0], self.s_drive.get_halten_status()[1]
                self.s_diag_code = self.s_drive.get_diagnostic_code()

            except Exception as e:
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
        ''' Set gap for drives A and B. If all runs ok, returns gap setted, if not, returns None.'''
        previous_gap = self.a_drive.get_target_position()
        if _cte.minimum_gap <= target_gap <= _cte.maximum_gap:
            try:
                self.a_drive.set_target_position(target_gap)
            except:
                logger.exception('Could not set drive A gap.')
                print('Could not set drive A gap.')
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
    
    def gap_set_enable(self, val: bool):
        try:
            assert val==True or val==False
        except Exception:
            logger.error('Enbale argument must be boolean')
            self.soft_drive_message = 'Enbale argument must be boolean'
        else:
            if val:
                with self._epu_lock:
                    a_diagnostic_code = self.a_drive.get_diagnostic_code()
                    b_diagnostic_code = self.b_drive.get_diagnostic_code()
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
                                {self.a_drive.diagnostic_code},\Drive B code:{self.b_drive.diagnostic_code}')
                        self.soft_drive_message = \
                            f'Enable signal not send due to diagnostic code Drive A code:\
                                {self.a_drive.diagnostic_code}, Drive B code:{self.b_drive.diagnostic_code}'
                        return False

            else:
                if not self.gap_halt_release_status():
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
                    logger.error('Release halt before set enable to zero')
                    self.soft_drive_message = 'Release halt before set enable to zero'
            
    def gap_release_halt(self, val: bool):
        try:
            assert val==True or val==False
        except Exception:
            logger.error('Enbale argument must be boolean')
            self.soft_drive_message = 'Enbale argument must be boolean'
        else:
            if val:
                with self._epu_lock:
                    a_diagnostic_code = self.a_drive.get_diagnostic_code()
                    b_diagnostic_code = self.b_drive.get_diagnostic_code()
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

    def gap_enable_and_release_halt(self, val: bool):
        self.gap_set_enable(val)
        self.gap_release_halt(val)

    def gap_start(self, val: bool):
        try:
            assert val==True or val==False
        except AssertionError:
            logger.error('Gap start argument must be boolean.')
            self.soft_drive_message = 'Gap start argument must be boolean.'
            return False
        else:
            with self._epu_lock:
                if self.gap_check_for_move():
                    a_diagnostic_code = self.a_drive.get_diagnostic_code()
                    b_diagnostic_code = self.b_drive.get_diagnostic_code()
                    if a_diagnostic_code == b_diagnostic_code == 'A211':
                        bsmp_enable_message = bsmp_send(
                            _cte.BSMP_WRITE, variableID=_cte.START_CH_AB,
                            value=val).encode()
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.settimeout(.1)
                            s.connect((_cte.beaglebone_addr, _cte.io_port))
                            s.sendall(bsmp_enable_message)
                            self.gap_is_moving = 1
                            self.monitor_gap_movement_thread.start()
                            time.sleep(.01) # magic number
                            while True:
                                data = s.recv(16)
                                if not data: break
                                return data
                    else:
                        logger.error(
                            f'Start signal not send due to diagnostic code Drive A code:\
                                {self.a_drive.diagnostic_code},\Drive B code:{self.b_drive.diagnostic_code}')
                        self.soft_drive_message = \
                            f'Start signal not send due to diagnostic code Drive A code:\
                                {self.a_drive.diagnostic_code}, Drive B code:{self.b_drive.diagnostic_code}'
                        return False
                else:
                    logger.error(
                        "Gap movement not started because one "
                        "or more conditions have not been met. "
                        "Check log for more information."
                        )
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
        if _cte.minimum_phase <= target_phase <= _cte.maximum_phase:
            timeout = 5
            while timeout > 0:
                try:
                    self.i_drive.set_target_position(target_phase)
                    self.s_drive.set_target_position(target_phase)
                except Exception as e:
                    logger.exception('Could not set drive I phase.')
                    print(e)
                else:
                    i = self.i_drive.get_target_position()
                    s = self.s_drive.get_target_position()
                    if i == s == target_phase:
                        return True
                    else:
                        timeout -= 1

        else:
            logger.error(f'Gap valeu given, ({target_phase}), is out of range.')
            print(f'Gap value given, ({target_phase}), is out of range.')
            return previous_gap

    def phase_set_enable(self, val: bool):
        try:
            assert val==True or val==False
        except Exception:
            logger.error('Enbale argument must be boolean')
            self.soft_drive_message = 'Enbale argument must be boolean'
        else:
            if val:
                with self._epu_lock:
                    with self.stop_event.clear():
                        i_diagnostic_code = self.i_drive.get_diagnostic_code()
                        s_diagnostic_code = self.s_drive.get_diagnostic_code()
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
                                    {self.i_drive.diagnostic_code},\Drive S code:{self.s_drive.diagnostic_code}')
                            self.soft_drive_message = \
                                f'Enable signal not send due to diagnostic code Drive I code:\
                                    {self.i_drive.diagnostic_code}, Drive S code:{self.s_drive.diagnostic_code}'
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
    
    def phase_release_halt(self, val: bool):
        try:
            assert val==True or val==False
        except Exception:
            logger.error('Enbale argument must be boolean')
            self.soft_drive_message = 'Enbale argument must be boolean'
        else:
            if val:
                with self._epu_lock:
                    i_diagnostic_code = self.i_drive.get_diagnostic_code()
                    s_diagnostic_code = self.s_drive.get_diagnostic_code()
                    if i_diagnostic_code == s_diagnostic_code == 'A010':
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
                    else:
                        logger.error(
                            f'Relese Halt signal not send due to diagnostic code Drive I code:\
                                {self.i_drive.diagnostic_code},\Drive S code:{self.s_drive.diagnostic_code}')
                        self.soft_drive_message = \
                            f'Relese Halt signal not send due to diagnostic code Drive I code:\
                                {self.i_drive.diagnostic_code}, Drive S code:{self.s_drive.diagnostic_code}'
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

    def phase_start(self, val: bool) -> bool:
        try:
            assert val==True or val==False
        except AssertionError:
            logger.error('Phase start argument must be boolean.')
            self.soft_drive_message = 'Phase start argument must be boolean.'
            return False
        else:
            with self._epu_lock:
                if self.phase_check_for_move():
                    i_diagnostic_code = self.i_drive.get_diagnostic_code()
                    s_diagnostic_code = self.s_drive.get_diagnostic_code()
                    if i_diagnostic_code == s_diagnostic_code == 'A211':
                        bsmp_enable_message = bsmp_send(
                            _cte.BSMP_WRITE, variableID=_cte.START_CH_SI,
                            value=val).encode()
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.settimeout(.1)
                            s.connect((_cte.beaglebone_addr, _cte.io_port))
                            self.stop_event.clear()
                            time.sleep(.1) # waits for the tcp reading in default thread
                            self.start_event.set()
                            s.sendall(bsmp_enable_message)
                            while True:
                                data = s.recv(8)
                                if not data: break
                                return data
                    else:
                        logger.error(
                            f'Start signal not send due to diagnostic code Drive I code:\
                                {self.i_drive.diagnostic_code},\Drive I code:{self.s_drive.diagnostic_code}')
                        self.soft_drive_message = \
                            f'Start signal not send due to diagnostic code Drive S code:\
                                {self.i_drive.diagnostic_code}, Drive S code:{self.s_drive.diagnostic_code}'
                else:
                    logger.error(
                        "Phase movement not started because one or "
                        "more conditions have not been met. "
                        "Check log for more information."
                        )
                    return False

    def allowed_to_change_phase(self) -> bool:
        if not self.phase_enable_status():
            return False
        elif not self.phase_halt_release_status():
            return False
        elif not self.phase_check_for_move():
                return False
        else: return True
    
    def phase_stop(self):
        self.phase_release_halt(0)

epu = Epu()
