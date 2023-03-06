import threading
import socket
import logging
import logging.handlers

from . import constants as _cte
from .utils import *
from .ecodrive import *

logger = logging.getLogger(__name__)
class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

default_args = Namespace(pv_prefix='SI-10SB:ID-EPU50:', msg_port=5052, io_port=5050, beaglebone_addr='10.128.110.160')

class Epu():

    def __init__(self, args, callback_update=lambda: 1):

        serialStream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.args = args
        self.gpio_connected = False
        self.tcp_wait_connection()

        self.a_drive = EcoDrive(socket=serialStream,
            address=_cte.a_drive_address,
            min_limit=_cte.minimum_gap,
            max_limit=_cte.maximum_gap,
            bbb_hostname=self.args.beaglebone_addr,
            rs458_tcp_port=self.args.msg_port,
            drive_name='A')

        self.b_drive = EcoDrive(socket=serialStream,
            address=_cte.b_drive_address,
            min_limit=_cte.minimum_gap,
            max_limit=_cte.maximum_gap,
            bbb_hostname=self.args.beaglebone_addr,
            rs458_tcp_port=self.args.msg_port,
            drive_name='B')

        self.i_drive = EcoDrive(socket=serialStream,
            address=_cte.i_drive_address,
            min_limit=_cte.minimum_phase,
            max_limit=_cte.maximum_phase,
            bbb_hostname=self.args.beaglebone_addr,
            rs458_tcp_port=self.args.msg_port,
            drive_name='I')

        self.s_drive = EcoDrive(socket=serialStream,
            address=_cte.s_drive_address,
            min_limit=_cte.minimum_phase,
            max_limit=_cte.maximum_phase,
            bbb_hostname=self.args.beaglebone_addr,
            rs458_tcp_port=self.args.msg_port,
            drive_name='S')

        logger.info('The 4 drives were initialized correctly.')

        self.callback_update = callback_update
        self.warnings = [] # not used yet

        # config threads
        self.gap_start_event = threading.Event()
        self.phase_start_event = threading.Event()
        self.stop_event = threading.Event()
        self.stop_event.set()
        self._epu_lock = threading.RLock()
        self.monitor_phase_movement_thread = Thread(target=self.monitor_phase_movement, daemon=True)
        self.monitor_gap_movement_thread = Thread(target=self.monitor_gap_movement, daemon=True)
        self.standstill_monitoring_thread = Thread(target=self.standstill_monitoring, daemon=True)

        logger.info('Initializing variables.')

        # initialize variables
        while True:
            try: self.init_variables_scope()
            except Exception: logger.error('Trying to initialize variables...')
            else: break

        logger.info('Variables initialized correctly.')

        # starts threads
        self.standstill_monitoring_thread.start()
        self.monitor_phase_movement_thread.start()
        self.monitor_gap_movement_thread.start()

    # tests connection with GPIO server (BBB)
    def tcp_wait_connection(self):

        while True:

            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.args.beaglebone_addr, self.args.io_port))

            except socket.timeout as e:
                self.gpio_connected = False
                logger.exception('Trying to connect to GPIO server.')
                print(f'Trying to connect to GPIO server: {e}')

            except socket.error as e:
                self.gpio_connected = False
                print(f'Trying to connect: {e}')
                logger.exception('Trying to connect to GPIO server.')

            except Exception as e:
                self.gpio_connected = False
                logger.exception('Trying to connect to GPIO server.')
                print(f'Trying to connect: {e}')

            else:
                logger.info(f'Connected to GPIO server.')
                self.gpio_connected = True
                s.shutdown(socket.SHUT_RDWR)
                s.close()
                return True

            time.sleep(5)

    # motion monitoring

    def init_variables_scope(self):
        # drive a variables
        self.a_target_position = float(self.a_drive.get_target_position())
        self.a_target_velocity = float(self.a_drive.get_max_velocity())
        self.a_resolver_gap = float(self.a_drive.get_resolver_position())
        self.a_encoder_gap = float(self.a_drive.get_encoder_position())
        self.a_diag_code = self.a_drive.get_diagnostic_code()
        self.a_is_moving = False
        # drive b variables
        self.b_target_position = float(self.b_drive.get_target_position())
        self.b_target_velocity = float(self.b_drive.get_max_velocity())
        self.b_resolver_gap = float(self.b_drive.get_resolver_position())
        self.b_encoder_gap = float(self.b_drive.get_encoder_position())
        self.b_diag_code = self.b_drive.get_diagnostic_code()
        self.b_is_moving = False
        # drive i variables
        self.i_target_position = float(self.i_drive.get_target_position())
        self.i_target_velocity = float(self.i_drive.get_max_velocity())
        self.i_resolver_phase = float(self.i_drive.get_resolver_position())
        self.i_encoder_phase = float(self.i_drive.get_encoder_position())
        self.i_diag_code = self.i_drive.get_diagnostic_code()
        self.i_is_moving = False
        #drive s variables
        self.s_resolver_gap = float(self.s_drive.get_resolver_position())
        self.s_target_velocity = float(self.s_drive.get_max_velocity())
        self.s_resolver_phase = float(self.s_drive.get_resolver_position())
        self.s_encoder_phase = float(self.s_drive.get_encoder_position())
        self.s_diag_code = self.s_drive.get_diagnostic_code()
        self.s_is_moving = False

        ## undulator status variables
        self.soft_message = ''
        gap_drive_enable, gap_drive_halt = self.gap_enable_status(), self.gap_halt_release_status()
        phase_drive_enable, phase_drive_halt = self.phase_enable_status(), self.phase_halt_release_status()
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
        self.gap_enable_and_halt_released = self.gap_enable and self.gap_halt_released
        ### undulator phase control variables
        self.phase_target = self.i_target_position
        self.phase_target_velocity = self.i_target_velocity
        self.phase = self.i_encoder_phase
        self.phase_enable_and_halt_released = self.phase_enable and self.phase_halt_released

    def monitor_gap_movement(self):

        while True:
            try:
                self.gap_start_event.wait()
                
                with self._epu_lock:
                    logger.info('\nGap movement started\n')
                    self.a_drive.drive_connect() # sends BCD:{address} to drive A
                    start = time.time()
                    update_count = 0

                    while self.gap_start_event.is_set():

                        g = self.a_drive.get_encoder_position(False)

                        if type(g) == float:
                            self.gap = g
                            self.callback_update()
                            update_count += 1
                            # logger.info(f'Gap: {self.gap}') # helps to diagnose updating problems

                        if abs(self.gap - self.gap_target) < .001:
                            self.gap_is_moving = 0
                            self.gap_start_event.clear()
                            end = time.time()
                            # logger.info(f'\nGap movement finished. \
                            #     Update rate: {update_count/(end-start)}')
                            logger.info(f'{self.gap}\t{update_count/(end-start)}')

                    self.stop_event.set()

            except Exception:
                logger.exception('Gap fast update error.')

    def monitor_phase_movement(self):

        while True:

            try:

                self.phase_start_event.wait()
                self.i_drive.drive_connect() # sends BCD:{address}

                while self.phase_start_event.is_set():

                    p = self.i_drive.get_encoder_position(False)

                    if type(p) == float:

                        self.phase = p
                        self.callback_update()


                    if abs(self.phase - self.phase_target) < .001:

                        self.phase_is_moving = 0
                        self.phase_start_event.clear()

                self.stop_event.set()

            except Exception:  logger.exception('Phase fast update error.')

    def standstill_monitoring(self):

        while True:

            try:

                self.allowed_to_change_gap()
                self.allowed_to_change_phase()

                # Drive A

                self.stop_event.wait()
                self.a_resolver_gap = self.a_drive.get_resolver_position()

                self.stop_event.wait()
                self.a_encoder_gap = self.a_drive.get_encoder_position()
                self.gap = self.a_encoder_gap

                self.stop_event.wait()
                self.a_diag_code = self.a_drive.get_diagnostic_code()

                self.stop_event.wait()
                e, h = self.a_drive.get_halten_status()
                self.gap_enable, self.gap_halt_released = e, h
                self.gap_enable_and_halt_released = self.gap_enable and self.gap_halt_released

                # Drive B

                self.stop_event.wait()
                self.b_resolver_gap = self.b_drive.get_resolver_position()

                self.stop_event.wait()
                self.b_encoder_gap = self.b_drive.get_encoder_position()

                self.stop_event.wait()
                self.b_diag_code = self.b_drive.get_diagnostic_code()

                # Drive I

                self.stop_event.wait()
                self.i_encoder_phase = self.i_drive.get_encoder_position()
                
                self.stop_event.wait()
                self.i_resolver_phase = self.i_drive.get_resolver_position()
                self.phase = self.i_encoder_phase

                self.stop_event.wait()
                e, h = self.i_drive.get_halten_status()
                self.phase_enable, self.phase_halt_released = e, h
                self.phase_enable_and_halt_released = self.phase_enable and self.phase_halt_released

                self.stop_event.wait()
                self.i_diag_code = self.i_drive.get_diagnostic_code()

                # Drive S

                self.stop_event.wait()
                self.s_resolver_phase = self.s_drive.get_resolver_position()

                self.stop_event.wait()
                self.s_encoder_phase = self.s_drive.get_encoder_position()

                self.stop_event.wait()
                self.s_diag_code = self.s_drive.get_diagnostic_code()

            except Exception:
                logger.error('Standstill monitoring error.')

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
        
        if _cte.minimum_gap <= target_gap <= _cte.maximum_gap:
            while True:
                self.stop_event.wait() # prevents send message to drive while fast gap updating is running
                self.stop_event.clear()
                try:
                    self.a_drive.set_target_position(target_gap)
                    self.b_drive.set_target_position(target_gap)
                    self.a_target_position = self.a_drive.get_target_position()
                    self.b_target_position = self.b_drive.get_target_position()
                except Exception as e:
                    self.stop_event.set()
                    logger.exception('Could not change target gap')
                    if self.a_target_position != self.b_target_position:
                        logger.warning('GC01 warning: correct cause before moving')
                else:
                    if self.a_target_position == self.b_target_position:
                        self.stop_event.set()
                        self.gap_target = target_gap
                        return target_gap
                    else:
                        logger.warning('GC01 warning: correct cause before moving')
                        self.gap_target = None
        else:
            self.stop_event.set()
            logger.error(f'Gap value given, ({target_gap}), is out of range.')
            return self.gap_target

    def gap_set_velocity(self, target_velocity: float):
        self.stop_event.clear()
        if (
            _cte.minimum_velo_mm_per_min
            <= target_velocity
            <= _cte.maximum_velo_mm_per_min
            ):
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
                drive_a_diag_code = self.a_drive.get_diagnostic_code()
                drive_b_diag_code = self.b_drive.get_diagnostic_code()
                if drive_a_diag_code == drive_b_diag_code == 'A211':
                    return True
            else:
                logger.warning('Movement not allowed. Drives A and B have different target positions.')
                return False
        else:
            # Verificar a diferença entre setpoint de velocidade e velocidade máxima
            logger.warning('Movement not allowed. Drives A and B have different target velocities.')
            return False

    def allowed_to_change_gap(self) -> bool:
        with self._epu_lock:
            try:
                if self.gap_enable_status():
                    if self.gap_halt_release_status():
                        self.stop_event.clear()
                        if self.gap_check_for_move():
                            self.stop_event.set()
                            self.gap_change_allowed = True
                            return True
                        else:
                            self.stop_event.set()
                            self.gap_change_allowed = False
                            return False
                    else:
                        self.gap_change_allowed = False
                        return False
                else:
                    self.gap_change_allowed = False
                    return False

            except Exception:
                # Just reinforce the need of stop_event ben set in this point, after validation, it could be removed.
                if not self.stop_event.is_set(): self.stop_event.set()
                logger.debug('Could not complete gap check for move.')

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

        if _cte.minimum_phase <= target_phase <= _cte.maximum_phase:
            while 1:
                self.stop_event.clear()
                try:
                    self.i_drive.set_target_position(target_phase)
                    self.s_drive.set_target_position(target_phase)
                    i_target_position = self.i_drive.get_target_position()
                    s_target_position = self.s_drive.get_target_position()
                except Exception:
                    self.stop_event.set()
                    logger.exception('Could not change target phase')
                    print('Could not change target phase')
                    try:
                        if i_target_position != s_target_position:
                            logger.warning('PC01 warning: correct cause before moving')
                            self.warnings.append('GC01')
                            print('PC01 warning: correct cause before moving')
                    except: pass
                else:
                    if i_target_position == s_target_position:
                        self.stop_event.set()
                        self.phase_target = target_phase
                        return target_phase
                    else:
                        logger.warning('PC01 warning: correct cause before moving')
                        self.warnings.append('GC01')
                        print('PC01 warning: correct cause before moving')
                        self.phase_target = None
        else:
            self.stop_event.set()
            logger.error(f'phase value given, ({target_phase}), is out of range.')
            print(f'phase value given, ({target_phase}), is out of range.')
            return self.phase_target

    def phase_set_velocity(self, target_velocity: float):
        self.stop_event.clear()
        if (
            _cte.minimum_velo_mm_per_min
            <= target_velocity
            <= _cte.maximum_velo_mm_per_min
            ):
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
            logger.info(
                'Velocity must be between {} mm/s and {} mm/s'.format(
                    _cte.minimum_velo_mm_per_min,
                    _cte.maximum_velo_mm_per_min)
                    )

    def phase_check_for_move(self) -> bool:
        drive_i_max_velocity = self.i_drive.get_max_velocity()
        drive_s_max_velocity = self.s_drive.get_max_velocity()
        if drive_i_max_velocity == drive_s_max_velocity:
            drive_i_target_position = self.i_drive.get_target_position()
            drive_s_target_position = self.s_drive.get_target_position()
            if drive_i_target_position == drive_s_target_position:
                drive_i_diag_code = self.i_drive.get_diagnostic_code()
                drive_s_diag_code = self.s_drive.get_diagnostic_code()
                if drive_i_diag_code == drive_s_diag_code:
                    return True
                else: return False
            else:
                logger.info('Movement not allowed. Drives I and S have different target positions.')
                return False
        else:
            # Verificar a diferença entre setpoint de velocidade e velocidade máxima
            logger.info('Movement not allowed. Drives I and S have different target velocities.')
            return False

    def allowed_to_change_phase(self) -> bool:
        with self._epu_lock:
            try:
                if self.phase_enable_status():
                    if self.phase_halt_release_status():
                        self.stop_event.clear()
                        if self.phase_check_for_move():
                            self.stop_event.set()
                            self.phase_change_allowed = True
                            return True
                        else:
                            self.stop_event.set()
                            self.phase_change_allowed = False
                            return False
                    else:
                        self.phase_change_allowed = False
                        return False

                else:
                    self.phase_change_allowed = False
                    return False
            except Exception:
                # Just reinforce the need of stop_event ben set in this point, after validation, it could be removed.
                if not self.stop_event.is_set(): self.stop_event.set()
                logger.debug('Could not complete phase check for move')

    # GPIOs functions

    def gap_set_enable(self, val: bool):

        if val:

            with self._epu_lock:

                try:

                    a_diagnostic_code = self.a_drive.get_diagnostic_code()
                    b_diagnostic_code = self.b_drive.get_diagnostic_code()
                    self.stop_event.set()

                except Exception:

                    self.stop_event.set()
                    logger.exception('Gap enable setting error.')
                    return

                else:
                    if a_diagnostic_code == b_diagnostic_code == 'A012':

                        bsmp_enable_message = bsmp_send(_cte.BSMP_WRITE, variableID=_cte.ENABLE_CH_AB, value=val).encode()

                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

                            s.settimeout(1)
                            s.connect((self.args.beaglebone_addr, self.args.io_port))
                            s.sendall(bsmp_enable_message)
                            time.sleep(.01) # magic number

                            while True:
                                data = s.recv(16)
                                if not data: break
                                logger.info('Gapo enabled')
                                return data

                    else:
                        logger.error(f'Drive A code:  {a_diagnostic_code}, Drive B code:{b_diagnostic_code}')
                        self.soft_drive_message = f'Drive A code: {a_diagnostic_code}, Drive B code:{b_diagnostic_code}'
                        return False

        else:
            if not self.gap_halt_release_status(): # get this information from drive

                bsmp_enable_message = bsmp_send(_cte.BSMP_WRITE, variableID=_cte.ENABLE_CH_AB, value=val).encode()

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

                    s.settimeout(1)
                    s.connect((self.args.beaglebone_addr, self.args.io_port))
                    s.sendall(bsmp_enable_message)
                    time.sleep(.01) # magic number

                    while True:
                        data = s.recv(16)
                        if not data: break
                        return data
            else:
                logger.info('Release halt to disable drive.')
                return False

    def gap_release_halt(self, val: bool):

        if val:
            with self._epu_lock:

                try:
                    a_diagnostic_code = self.a_drive.get_diagnostic_code()
                    b_diagnostic_code = self.b_drive.get_diagnostic_code()
                    self.stop_event.set()

                except Exception:
                    self.stop_event.set()
                    logger.exception('Gap release halt error.')

                else:
                    if a_diagnostic_code == b_diagnostic_code == 'A010':

                        bsmp_enable_message = bsmp_send(_cte.BSMP_WRITE, variableID=_cte.HALT_CH_AB, value=val).encode()

                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.settimeout(.1)
                            s.connect((self.args.beaglebone_addr, self.args.io_port))
                            s.sendall(bsmp_enable_message)
                            time.sleep(.01) # magic number

                            while True:
                                data = s.recv(16)
                                if not data: break
                                return data

                    else:
                        logger.error(
                            f'Relese Halt signal not send due to diagnostic code Drive A code:\
                                {a_diagnostic_code},\Drive B code:{b_diagnostic_code}')
                        self.soft_drive_message = \
                            f'Relese Halt signal not send due to diagnostic code Drive A code:\
                                {a_diagnostic_code}, Drive B code:{b_diagnostic_code}'
                        return False
        else:
            bsmp_enable_message = bsmp_send(_cte.BSMP_WRITE, variableID=_cte.HALT_CH_AB, value=val).encode()

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(.1)
                s.connect((self.args.beaglebone_addr, self.args.io_port))
                s.sendall(bsmp_enable_message)
                time.sleep(.01) # magic number

                while True:
                    data = s.recv(16)
                    if not data: break
                    return data

    def gap_enable_and_release_halt(self, val: bool = True) -> bool:

        try:
            with self._epu_lock:

                if val:

                    timeout_count = 10

                    while not self.gap_enable_status():
                        self.gap_set_enable(1)
                        time.sleep(.1)
                        timeout_count -= 1
                        if not timeout_count: break

                    timeout_count = 10

                    while not self.gap_halt_release_status():
                        self.gap_release_halt(1)
                        time.sleep(.1)
                        timeout_count -= 1
                        if not timeout_count: break

                else:

                    timeout_count = 10

                    while self.gap_halt_release_status():
                        self.gap_release_halt(0)
                        time.sleep(.1)
                        timeout_count -= 1
                        if not timeout_count: break

                    timeout_count = 10

                    while self.gap_enable_status():
                        self.gap_set_enable(0)
                        time.sleep(.1)
                        timeout_count -= 1
                        if not timeout_count: break

        except Exception:
            logger.exception('GPIO comunication error.')
            return False

    def gap_enable_status(self) -> bool:

        bsmp_enable_message = bsmp_send( _cte.BSMP_READ, variableID=_cte.ENABLE_CH_AB, size=0).encode()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            s.settimeout(.1)
            s.connect((self.args.beaglebone_addr, self.args.io_port))
            s.sendall(bsmp_enable_message)
            time.sleep(.01) # magic number

            while True:
                data = s.recv(16)
                if not data: break
                return(bool(data[-2]))

    def gap_halt_release_status(self):

        bsmp_enable_message = bsmp_send(_cte.BSMP_READ, variableID=_cte.HALT_CH_AB, size=0).encode()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            s.settimeout(.1)
            s.connect((self.args.beaglebone_addr, self.args.io_port))
            s.sendall(bsmp_enable_message)
            time.sleep(.01) # magic number

            while True:
                data = s.recv(16)
                if not data: break
                return(bool(data[-2]))

    def gap_start(self, val: bool):

        # while self.phase_is_moving: time.sleep(2)       # with this, gap movement is dependent of self.phase_is_moving right updating.

        with self._epu_lock:
            self.stop_event.clear()

            if self.gap_check_for_move():
                try:
                    a_diagnostic_code = self.a_drive.get_diagnostic_code()
                    b_diagnostic_code = self.b_drive.get_diagnostic_code()

                except:
                    logger.exception('Error while getting diagnostic codes.')
                    self.stop_event.set()

                else:
                    if a_diagnostic_code == b_diagnostic_code == 'A211':
                        bsmp_enable_message = bsmp_send(_cte.BSMP_WRITE, variableID=_cte.START_CH_AB, value=val).encode()

                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.settimeout(1)
                            s.connect((self.args.beaglebone_addr, self.args.io_port))
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

    def gap_stop(self):
        timeout_count = 10
        while self.gap_halt_release_status():
            self.gap_release_halt(0)
            time.sleep(.1)
            timeout_count -= 1
            if not timeout_count: break
        timeout_count = 10
        while self.gap_enable_status():
            self.gap_set_enable(0)
            time.sleep(.1)
            timeout_count -= 1
            if not timeout_count: break

    def phase_set_enable(self, val: bool):

        if val:

            with self._epu_lock:

                try:

                    i_diagnostic_code = self.i_drive.get_diagnostic_code()
                    s_diagnostic_code = self.s_drive.get_diagnostic_code()
                    self.stop_event.set()

                except Exception:

                    self.stop_event.set()
                    logger.exception('Phase enable setting error.')
                    return

                else:
                    if i_diagnostic_code == s_diagnostic_code == 'A012':

                        bsmp_enable_message = bsmp_send(_cte.BSMP_WRITE, variableID=_cte.ENABLE_CH_SI, value=val).encode()

                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

                            s.settimeout(1)
                            s.connect((self.args.beaglebone_addr, self.args.io_port))
                            s.sendall(bsmp_enable_message)
                            time.sleep(.01) # magic number

                            while True:
                                data = s.recv(16)
                                if not data: break
                                logger.info('Phase enabled')
                                return data

                    else:
                        logger.error(f'Drive I  code: {i_diagnostic_code}, Drive S code:{s_diagnostic_code}')
                        self.soft_drive_message = f'Drive I code: {i_diagnostic_code}, Drive S code:{s_diagnostic_code}'
                        return False

        else:
            if not self.phase_halt_release_status(): # get this information from drive

                bsmp_enable_message = bsmp_send(_cte.BSMP_WRITE, variableID=_cte.ENABLE_CH_SI, value=val).encode()

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

                    s.settimeout(1)
                    s.connect((self.args.beaglebone_addr, self.args.io_port))
                    s.sendall(bsmp_enable_message)
                    time.sleep(.01) # magic number

                    while True:
                        data = s.recv(16)
                        if not data: break
                        return data
            else:
                logger.info('Release halt to disable drive.')
                return False

    def phase_release_halt(self, val: bool):

        if val:
            with self._epu_lock:

                try:
                    i_diagnostic_code = self.i_drive.get_diagnostic_code()
                    s_diagnostic_code = self.s_drive.get_diagnostic_code()
                    self.stop_event.set()

                except Exception:
                    self.stop_event.set()
                    logger.exception('Phase release halt error.')

                else:
                    if i_diagnostic_code == s_diagnostic_code == 'A010':

                        bsmp_enable_message = bsmp_send(_cte.BSMP_WRITE, variableID=_cte.HALT_CH_SI, value=val).encode()

                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.settimeout(.1)
                            s.connect((self.args.beaglebone_addr, self.args.io_port))
                            s.sendall(bsmp_enable_message)
                            time.sleep(.01) # magic number

                            while True:
                                data = s.recv(16)
                                if not data: break
                                return data

                    else:
                        logger.error(f'Drive I diagnostic code: {i_diagnostic_code},\
                            Drive S diagnostic code:{s_diagnostic_code}')
                        self.soft_drive_message = f'Drive I diagnostic code: {i_diagnostic_code},\
                            Drive S diagnostic code:{s_diagnostic_code}'
                        return False
        else:
            bsmp_enable_message = bsmp_send(_cte.BSMP_WRITE, variableID=_cte.HALT_CH_SI, value=val).encode()

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(.1)
                s.connect((self.args.beaglebone_addr, self.args.io_port))
                s.sendall(bsmp_enable_message)
                time.sleep(.01) # magic number

                while True:
                    data = s.recv(16)
                    if not data: break
                    return data

    def phase_enable_and_release_halt(self, val) -> bool:

        try:
            with self._epu_lock:

                if val:

                    timeout_count = 10

                    while not self.phase_enable_status():
                        self.phase_set_enable(1)
                        time.sleep(.1)
                        timeout_count -= 1
                        if not timeout_count: break

                    timeout_count = 10

                    while not self.phase_halt_release_status():
                        self.phase_release_halt(1)
                        time.sleep(.1)
                        timeout_count -= 1
                        if not timeout_count: break

                else:

                    timeout_count = 10

                    while self.phase_halt_release_status():
                        self.phase_release_halt(0)
                        time.sleep(.1)
                        timeout_count -= 1
                        if not timeout_count: break

                    timeout_count = 10

                    while self.phase_enable_status():
                        self.phase_set_enable(0)
                        time.sleep(.1)
                        timeout_count -= 1
                        if not timeout_count: break


        except Exception:
            logger.exception('GPIO comunication error.')
            return False

    def phase_enable_status(self):

        bsmp_enable_message = bsmp_send(_cte.BSMP_READ, variableID=_cte.ENABLE_CH_SI, size=0).encode()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            s.settimeout(.1)
            s.connect((self.args.beaglebone_addr, self.args.io_port))
            s.sendall(bsmp_enable_message)
            time.sleep(.01) # magic number

            while True:
                data = s.recv(16)
                if not data: break
                return(bool(data[-2]))

    def phase_halt_release_status(self):

        bsmp_enable_message = bsmp_send(_cte.BSMP_READ, variableID=_cte.HALT_CH_SI, size=0).encode()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            s.settimeout(.1)
            s.connect((self.args.beaglebone_addr, self.args.io_port))
            s.sendall(bsmp_enable_message)
            time.sleep(.01) # magic number

            while True:
                data = s.recv(16)
                if not data: break
                return(bool(data[-2]))

    def phase_start(self, val: bool) -> bool:

        with self._epu_lock:
            self.stop_event.clear()

            if self.phase_check_for_move():

                try:
                    i_diagnostic_code = self.i_drive.get_diagnostic_code()
                    s_diagnostic_code = self.s_drive.get_diagnostic_code()

                except:
                    logger.exception('Error while getting diagnostic codes')
                    self.stop_event.set()

                else:
                    if i_diagnostic_code == s_diagnostic_code == 'A211':

                        bsmp_enable_message = bsmp_send(_cte.BSMP_WRITE, variableID=_cte.START_CH_SI, value=val).encode()

                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

                            s.settimeout(1)
                            s.connect((self.args.beaglebone_addr, self.args.io_port))
                            self.phase_start_event.set()
                            self.phase_is_moving = True
                            time.sleep(.1) # waits for the tcp reading in default thread
                            s.sendall(bsmp_enable_message)

                            while True:
                                data = s.recv(8)
                                if not data: break
                                return data

                    else:
                        self.stop_event.set()
                        logger.error(
                            f'Start signal not send due to diagnostic code Drive I code:\
                                {i_diagnostic_code},\Drive I code:{s_diagnostic_code}')
                        self.soft_drive_message = \
                            f'Start signal not send due to diagnostic code Drive S code:\
                                {i_diagnostic_code}, Drive S code:{s_diagnostic_code}'

            else:
                self.stop_event.set()
                logger.error("Phase movement not started because one or ""more conditions have not been met. ""Check log for more information.")
                return False

    def phase_stop(self):
        timeout_count = 10
        while self.phase_halt_release_status():
            self.phase_release_halt(0)
            time.sleep(.1)
            timeout_count -= 1
            if not timeout_count: break
        timeout_count = 10
        while self.phase_enable_status():
            self.phase_set_enable(0)
            time.sleep(.1)
            timeout_count -= 1
            if not timeout_count: break

    def gap_turn_on(self) -> bool:

        with self._epu_lock:

            bsmp_enable_message = bsmp_send(_cte.BSMP_WRITE, variableID=_cte.RESET_CH_AB, value=1).encode()

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

                s.settimeout(1)
                s.connect((self.args.beaglebone_addr, self.args.io_port))
                time.sleep(.1) # waits for the tcp reading in default thread
                s.sendall(bsmp_enable_message)
                time.sleep(.1)
                while True:
                    data = s.recv(8)
                    if not data: break
                    return data

    def phase_turn_on(self) -> bool:

        with self._epu_lock:

            bsmp_enable_message = bsmp_send(_cte.BSMP_WRITE, variableID=_cte.RESET_CH_SI, value=1).encode()

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

                s.settimeout(1)
                s.connect((self.args.beaglebone_addr, self.args.io_port))
                time.sleep(.1) # waits for the tcp reading in default thread
                s.sendall(bsmp_enable_message)
                time.sleep(.1)
                while True:
                    data = s.recv(8)
                    if not data: break
                    return data

    def turn_on_all(self):
        self.gap_turn_on()
        time.sleep(1)
        self.phase_turn_on()


def get_file_handler(file: str):
    # logger.handlers.clear()
    fh = logging.handlers.RotatingFileHandler(file, maxBytes=10000000, backupCount=10)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s"))
    return fh

def get_logger(file_handler):
    lg = logging.getLogger()
    lg.setLevel(logging.DEBUG)
    lg.addHandler(file_handler)
    return lg

def cycling():
    ''' For future cycling tests'''
    pass
      
logger.handlers.clear()
fh = get_file_handler('testing.log')
root = get_logger(fh)
            
if __name__ == '__main__':
    epu = Epu(default_args)
