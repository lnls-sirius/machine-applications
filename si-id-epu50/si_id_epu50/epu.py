import logging
import logging.handlers
import threading
from threading import Thread
import time
import socket

from . import constants as _cte
from . import utils
from .connection_handler import TCPClient
from .ecodrive import EcoDrive

logger = logging.getLogger(__name__)


class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


default_args = Namespace(pv_prefix='SI-10SB:ID-EPU50:',
                         msg_port=5052, io_port=5050,
                         beaglebone_addr='10.128.110.160')


# TODO: Check the case where the drives are not in the same state
def get_setpoint(drive_1, drive_2) -> float:
    """
    Returns the target position of the drives of a given operation.
    If the target positions are equal, return the target position for drive A.
    Otherwise, set the target position of drive B to the target position of drive A and return the new target position.
    """
    try:
        target_pos_drive_1 = drive_1.get_target_position()
        target_pos_drive_2 = drive_2.get_target_position()

        if target_pos_drive_1 == target_pos_drive_2:
            return target_pos_drive_1

        else:
            logger.warning('Target positions of drives A and B do not match.')
            return drive_2.set_target_position(target_pos_drive_1)

    except ValueError:
        logger.exception('Drive did not respond as expected.')
        raise RuntimeError('Failed to get/set setpoint for operation.')

    except TypeError:
        logger.exception('Drive did not respond as expected.')
        raise RuntimeError('Failed to get/set setpoint for operation.')


def send_bsmp_message(bsmp_enable_message, host, port) -> bytes:
    """
    Sends a BSMPmessage to the specified host and port and receives response.

    This function establishes a socket connection to the specified host and port, sends the provided BSMP message,
    and waits for a response. It retries the connection and handles various socket-related exceptions.

    Args:
        bsmp_enable_message (bytes): The BSMP enable message to send.
        host (str): The hostname or IP address of the target host.
        port (int): The port number of the target host.

    Returns:
        bytes: The response data received from the host.

    Raises:
        ConnectionRefusedError: If the connection to the host is refused.
        socket.timeout: If the connection times out.
        ConnectionResetError: If the connection is reset by the host.
        BrokenPipeError: If a broken pipe error occurs during communication.
        OSError: If a general connection error occurs.

    Note:
        The function uses a 16-byte buffer to receive response data from the host. If the response data is longer
        than 16 bytes, only the first 16 bytes will be returned.
    """
    attempt = 0
    try:
        with socket.create_connection((host, port)) as s:
            s.sendall(bsmp_enable_message)
            time.sleep(.01)  # magic number

            while True:
                data = s.recv(16)
                if not data:
                    break
                return data

    except ConnectionRefusedError:
        logger.error(f'Connection refused by {host}:{port}')
        return b''

    except socket.timeout:
        logger.error(f'Connection timeout to {host}:{port}')
        return b''

    except ConnectionResetError:
        if not attempt:
            attempt += 1
            return send_bsmp_message(bsmp_enable_message, host, port)
        else:
            logger.warning(f'Connection reset by {host}:{port}')
            return b''

    except BrokenPipeError:
        logger.error(f'Broken pipe to {host}:{port}')
        return b''

    except OSError:
        logger.error(f'Connection error to {host}:{port}')
        return b''


def set_digital_signal(val: bool, bsmp_enable_message: bytes, drive1: EcoDrive,
                       drive2: EcoDrive, right_diagnostic_code: str, host: str, port: int) -> bool:
    """
    Sets a digital signal by sending a BSMP message to the specified host and port.

    This function sets a digital signal by sending a BSMP message to the specified host and port. It checks
    the diagnostic codes of two EcoDrive objects (drive1 and drive2) against a given right_diagnostic_code, and if
    they match, the BSMP message is sent. The response from the host is logged and the function returns True if the
    message is sent successfully, otherwise False.

    Args:
        val (bool): The value of the digital signal to set (True or False).
        bsmp_enable_message (bytes): The BSMP enable message to send.
        drive1 (EcoDrive): The first EcoDrive object.
        drive2 (EcoDrive): The second EcoDrive object.
        right_diagnostic_code (str): The correct diagnostic code to check against.
        host (str): The hostname or IP address of the target host.
        port (int): The port number of the target host.

    Returns:
        bool: True if the BSMP message is sent successfully, otherwise False.

    Note:
        - If val is True, the diagnostic codes of drive1 and drive2 must both match the right_diagnostic_code in
          order for the BSMP message to be sent.
        - If val is False, the BSMP message will be sent unconditionally without checking diagnostic codes.
        - If an error occurs during communication, the function returns False.

    """
    if val:
        diagnostic_code_1 = drive1.get_diagnostic_code()
        diagnostic_code_2 = drive2.get_diagnostic_code()

        if diagnostic_code_1 == diagnostic_code_2 == right_diagnostic_code:
            response = send_bsmp_message(bsmp_enable_message, host, port)
            if response:
                logger.debug('BSMP message sent successfully.')
                return True
            else:
                logger.error('Failed to send BSMP message.')
                return False

        elif diagnostic_code_1 == diagnostic_code_2:
            logger.info('Wrong diagnostic code.')
        else:
            logger.error('Diagnosis code mismatch.')
            return False

    else:
        send_bsmp_message(
            bsmp_enable_message,
            host,
            port)
    return True


def gpio_server_connection_test(addr, port) -> bool:
    """
    Tests the connection to a GPIO server by attempting to create a TCP connection.

    This function attempts to create a TCP connection to a GPIO server with the specified address (hostname or IP
    address) and port number. It uses a timeout of 5 seconds for the connection attempt. If the connection is
    successful, a log message is generated, the connection is closed, and True is returned. If the connection fails,
    an appropriate error message is logged and False is returned.

    Args:
        addr (str): The address (hostname or IP address) of the GPIO server.
        port (int): The port number of the GPIO server.

    Returns:
        bool: True if the connection is successful, otherwise False.

    Note:
        - The timeout for the connection attempt is set to 5 seconds.
        - If an error occurs during the connection attempt, the function logs an error message and returns False.

    """
    try:
        with socket.create_connection((addr, port), timeout=5) as s:
            logger.info(f'Connected to GPIO server.')
            s.close()
        return True

    except socket.timeout:
        logger.exception('Connection timed out while trying to connect to GPIO server.')

    except ConnectionRefusedError as e:
        logger.exception(f'Connection refused by GPIO server: {e}')

    except socket.gaierror as e:
        logger.exception(f'Failed to resolve GPIO server address: {e}')

    except OSError as e:
        logger.exception(f'Error while trying to connect to GPIO server: {e}')

    return False


def read_digital_status(host, port, bsmp_id: int) -> bytes:
    bsmp_enable_message = utils.bsmp_send(_cte.BSMP_READ, variableID=bsmp_id, size=0).encode()
    return send_bsmp_message(bsmp_enable_message, host, port)


class Epu:
    """
    Creates a singleton instance of the EPU class. This class is used to communicate with the EPU. Four EcoDrive
    objects are created, one for each drive in the EPU. The EPU class also creates a TCPClient object, that is passed
    to the EcoDrive objects, to communicate with beaglebone RS485 server. The server receives the messages,
    converts them to RS485 and sends them to the drives. This docstring is being written yet.

    Returns:
        Epu object that can be used to communicate with the EPU.
        
    Note:
        target velocity or position values None indicates that the drives have different values, need to be checked.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Epu, cls).__new__(cls)
        return cls._instance

    def __init__(self, args, callback_update=lambda: 1):

        # Ensure that the instance has not been initialized before
        if not hasattr(self, 'initialized'):
            self._serial_socket = TCPClient(args.beaglebone_addr, args.msg_port)
            self._serial_socket.connect()
            self.args = args
            self.callback_update = callback_update
            self.epu_message = None
            self.tcp_

            # Try to reach the GPIO server
            while not gpio_server_connection_test(self.args.beaglebone_addr, self.args.msg_port):
                time.sleep(5)

            self.a_drive = EcoDrive(tcp_client=self._serial_socket,
                                    address=_cte.a_drive_address,
                                    min_limit=_cte.minimum_gap,
                                    max_limit=_cte.maximum_gap,
                                    drive_name='A')

            self.b_drive = EcoDrive(tcp_client=self._serial_socket,
                                    address=_cte.b_drive_address,
                                    min_limit=_cte.minimum_gap,
                                    max_limit=_cte.maximum_gap,
                                    drive_name='B')

            self.i_drive = EcoDrive(tcp_client=self._serial_socket,
                                    address=_cte.i_drive_address,
                                    min_limit=_cte.minimum_phase,
                                    max_limit=_cte.maximum_phase,
                                    drive_name='I')

            self.s_drive = EcoDrive(tcp_client=self._serial_socket,
                                    address=_cte.s_drive_address,
                                    min_limit=_cte.minimum_phase,
                                    max_limit=_cte.maximum_phase,
                                    drive_name='S')

            logger.info('All drives initialized.')

            # Threads and events
            self.gap_start_event = threading.Event()
            self.phase_start_event = threading.Event()
            self._epu_lock = threading.RLock()
            self.monitor_phase_movement_thread = Thread(target=self._monitor_phase_movement, daemon=True)
            self.monitor_gap_movement_thread = Thread(target=self._monitor_gap_movement, daemon=True)

            logger.info('Initializing variables.')
            self._init_variables()
            logger.info('Variables initialized.')

            # Starts threads
            self._standstill_monitoring()
            self.monitor_phase_movement_thread.start()
            self.monitor_gap_movement_thread.start()

            self.initialized = True

    # Motion monitoring

    def _init_variables(self):
        """
        Initializes variables that will be used in the monitoring threads.
        The several attempts are necessary because the drives may not respond correctly.
        The initialization is separated in several while loops to avoid initializing of all variables if one fails.
        """
        drives = [self.a_drive, self.b_drive, self.i_drive, self.s_drive]
        variables = ['a', 'b', 'i', 's']

        for drive, var in zip(drives, variables):
            while True:
                try:
                    setattr(self, f'{var}_target_position', float(drive.get_target_position()))
                    setattr(self, f'{var}_target_velocity', float(drive.get_max_velocity()))
                    setattr(self, f'{var}_encoder_gap', float(drive.read_encoder()))
                    setattr(self, f'{var}_resolver_phase', float(drive.read_resolver()))
                    setattr(self, f'{var}_encoder_phase', float(drive.read_encoder()))
                    setattr(self, f'{var}_diag_code', drive.get_diagnostic_code())
                    setattr(self, f'{var}_is_moving', False)
                    break
                except (ValueError, TypeError):
                    logger.exception('Trying to initialize variables.')
                    time.sleep(0.5)
                    continue

        # undulator status variables
        self.gap_enable = self.gap_enable_status()
        self.phase_enable = self.phase_enable_status()
        self.gap_halt_released = not self.gap_halt_release_status()
        self.phase_halt_released = not self.phase_halt_release_status()
        self.gap_change_allowed = self.allowed_to_change_gap()
        self.phase_change_allowed = self.allowed_to_change_phase()
        self.gap_is_moving = False
        self.phase_is_moving = False
        self.is_moving = False
        # undulator gap control variables
        self.gap_target = self.a_target_position
        self.gap_target_velocity = self.a_target_velocity
        self.gap = self.a_encoder_gap
        self.gap_enable_and_halt_released = self.gap_enable and self.gap_halt_released
        # undulator phase control variables
        self.phase_target = self.i_target_position
        self.phase_target_velocity = self.i_target_velocity
        self.phase = self.i_encoder_phase
        self.phase_enable_and_halt_released = self.phase_enable and self.phase_halt_released

    def _monitor_movement(self, start_event, drive, attribute, logger_message):
        while True:
            start_event.wait()
            with self._epu_lock:
                logger.info(f'{logger_message} started.')
                drive.connect_to_drive()
                start = time.monotonic()
                update_count = 0

                while start_event.is_set():
                    value = drive.read_encoder(False)
                    if isinstance(value, float):
                        setattr(self, attribute, value)
                        self.callback_update()
                        update_count += 1
                        logger.debug(f'{attribute.capitalize()}: {round(getattr(self, attribute), 3)}')
                        logger.debug(abs(getattr(self, attribute) - getattr(self, f'{attribute}_target')))

                    if abs(getattr(self, attribute) - getattr(self, f'{attribute}_target')) < .001:
                        print(getattr(self, attribute))
                        setattr(self, f'{attribute}_is_moving', False)
                        start_event.clear()
                        end = time.monotonic()
                        logger.info(f'{logger_message.capitalize()} finished. \
                                    Update rate: {int(update_count / (end - start))}')

    def _monitor_gap_movement(self):
        self._monitor_movement(self.gap_start_event, self.a_drive, 'gap', 'Gap movement')

    def _monitor_phase_movement(self):
        self._monitor_movement(self.phase_start_event, self.i_drive, 'phase', 'Phase movement')

    @utils.run_periodically_in_detached_thread(interval=2)
    def _standstill_monitoring(self):
        while self.gap_is_moving:
            time.sleep(1)

        # Check TODO of this functions
        self.allowed_to_change_gap()
        self.allowed_to_change_phase()

        self._read_drive_a()
        self._read_drive_b()
        self._read_drive_i()
        self._read_drive_s()

    def _read_drive_a(self):
        with self._epu_lock:
            try:
                self.a_resolver_gap = self.a_drive.read_resolver(True)
                self.a_encoder_gap = self.a_drive.read_encoder(False)
                self.a_target_position = self.a_drive.get_target_position(False)
                self.gap_target = self.a_target_position
                self.gap = self.a_encoder_gap
                self.a_diag_code = self.a_drive.get_diagnostic_code(False)
                e, h = self.a_drive.get_halten_status(False)
                self.gap_enable, self.gap_halt_released = e, h
                self.gap_enable_and_halt_released = self.gap_enable and self.gap_halt_released

            except ValueError as e:
                logger.info('Drive A did not respond as expected, trying again.')
                logger.debug(e)

            except TypeError as e:
                logger.info('Drive A did not respond during standstill monitoring.')
                logger.debug(e)

    def _read_drive_b(self):
        with self._epu_lock:
            try:
                self.b_resolver_gap = self.b_drive.read_resolver(change_drive=True)
                self.b_encoder_gap = self.b_drive.read_encoder(change_drive=False)
                self.b_diag_code = self.b_drive.get_diagnostic_code(change_drive=False)
                self.b_target_position = self.b_drive.get_target_position(False)

            except ValueError as e:
                logger.info('Drive B did not respond as expected, trying again.')
                logger.debug(e)

            except TypeError as e:
                logger.info('Drive B did not respond during standstill monitoring.')
                logger.debug(e)

    def _read_drive_i(self):
        with self._epu_lock:
            try:
                self.i_encoder_phase = self.i_drive.read_encoder()
                self.i_resolver_phase = self.i_drive.read_resolver(False)
                self.i_target_position = self.i_drive.get_target_position(False)
                self.phase_target = self.i_target_position
                self.phase = self.i_encoder_phase
                e, h = self.i_drive.get_halten_status(False)
                self.phase_enable, self.phase_halt_released = e, h
                self.phase_enable_and_halt_released = self.phase_enable and self.phase_halt_released
                self.i_diag_code = self.i_drive.get_diagnostic_code(False)

            except ValueError as e:
                logger.info('Drive I did not respond as expected, trying again.')
                logger.debug(e)

            except TypeError as e:
                logger.info('Drive I did not respond during standstill monitoring.')
                logger.debug(e)

    def _read_drive_s(self):
        with self._epu_lock:
            try:
                self.s_resolver_phase = self.s_drive.read_resolver()
                self.s_encoder_phase = self.s_drive.read_encoder(False)
                self.s_diag_code = self.s_drive.get_diagnostic_code(False)
                self.s_target_position = self.s_drive.get_target_position(False)

            except ValueError as e:
                logger.info('Drive S did not respond as expected, trying again.')
                logger.debug(e)

            except TypeError as e:
                logger.info('Drive S did not respond during standstill monitoring.')
                logger.debug(e)

                # Gap stuff

    # TODO: This function is not used anywhere, check if it is worth change
    # the gap update to use this instead of a_drive directly. Same to phase.
    @property
    def gap_setpoint(self):
        """
        Returns the target position of the drives for a gap operation.
        """
        with self._epu_lock:
            try:
                return get_setpoint(self.a_drive, self.b_drive)
            except RuntimeError:
                logger.error('Could not get gap setpoint.')
                return None

    @property
    def phase_setpoint(self):
        """
        Returns the target position of the drives for a phase operation.
        """
        with self._epu_lock:
            try:
                return get_setpoint(self.i_drive, self.s_drive)
            except RuntimeError:
                logger.error('Could not get phase setpoint.')
                return None

    def _set_drive_values(self, value: float, func: callable) -> bool:
        attempts = 0
        with self._epu_lock:
            while not func(value):
                time.sleep(.5)
                attempts += 1
                if attempts == 3:
                    return False
            return True

    def gap_set(self, gap: float) -> bool:
        if _cte.minimum_gap <= gap <= _cte.maximum_gap:
            return self._set_drive_values(gap, self.a_drive.set_target_position) and \
                self._set_drive_values(gap, self.b_drive.set_target_position)
        else:
            logger.error(f'Gap value given, ({gap}), is out of range.')
            return False

    def gap_set_velocity(self, velocity: float) -> bool:
        if _cte.minimum_velo_mm_per_min <= velocity <= _cte.maximum_velo_mm_per_min:
            return self._set_drive_values(velocity, self.a_drive.set_target_velocity) and \
                self._set_drive_values(velocity, self.b_drive.set_target_velocity)
        else:
            logger.error(f'Velocity value given, ({velocity}), is out of range.')
            return False

    def phase_set(self, phase: float) -> bool:
        if _cte.minimum_phase <= phase <= _cte.maximum_phase:
            return self._set_drive_values(phase, self.i_drive.set_target_position) and \
                self._set_drive_values(phase, self.s_drive.set_target_position)
        else:
            logger.error(f'Phase value given, ({phase}), is out of range.')
            return False

    def phase_set_velocity(self, velocity: float) -> bool:
        if _cte.minimum_velo_mm_per_min <= velocity <= _cte.maximum_velo_mm_per_min:
            return self._set_drive_values(velocity, self.i_drive.set_target_velocity) and \
                self._set_drive_values(velocity, self.s_drive.set_target_velocity)
        else:
            logger.error(f'Velocity value given, ({velocity}), is out of range.')
            return False

    # TODO: catch exceptions
    def _gap_check_for_move(self) -> bool:
        with self._epu_lock:
            drive_a_max_velocity = self.a_drive.get_max_velocity()
            drive_b_max_velocity = self.b_drive.get_max_velocity()

            if drive_a_max_velocity != drive_b_max_velocity:
                logger.info('Gap drives have different maximum velocities.')
                self.message = 'Gap drives have different maximum velocities.'
                return False

            drive_a_target_position = self.a_drive.get_target_position()
            drive_b_target_position = self.b_drive.get_target_position()

            if drive_a_target_position != drive_b_target_position:
                logger.info('Gap drives have different target positions.')
                self.message = 'Gap drives have different target positions.'
                return False

            drive_a_diag_code = self.a_drive.get_diagnostic_code()
            drive_b_diag_code = self.b_drive.get_diagnostic_code()

            if drive_a_diag_code == drive_b_diag_code == 'A211':
                return True

            else:
                logger.info('Gap drives diagnostic codes do not allow movement.')
                self.message = 'Gap drives diagnostic codes do not allow movement.'
            return False

    # TODO: check if it is necessary to treat exceptions.
    # TODO: write another function just to update the status of the gap in which there is no serial communication
    def allowed_to_change_gap(self) -> bool:
        if self.gap_enable_status() and self.gap_halt_status() and self._gap_check_for_move():
            self.gap_change_allowed = True
            return True

        self.gap_change_allowed = False
        return False

    # TODO: Change to gap standard
    def _phase_check_for_move(self) -> bool:
        with self._epu_lock:
            drive_i_max_velocity = self.i_drive.get_max_velocity()
            drive_s_max_velocity = self.s_drive.get_max_velocity()

            if drive_i_max_velocity != drive_s_max_velocity:
                logger.info('Phase drives have different maximum velocities.')
                self.message = 'Phase drives have different maximum velocities.'
                return False

            drive_i_target_position = self.i_drive.get_target_position()
            drive_s_target_position = self.s_drive.get_target_position()

            if drive_i_target_position != drive_s_target_position:
                logger.info('Phase drives have different target positions.')
                self.message = 'Phase drives have different target positions.'
                return False

            drive_i_diag_code = self.i_drive.get_diagnostic_code()
            drive_s_diag_code = self.s_drive.get_diagnostic_code()

            if drive_i_diag_code == drive_s_diag_code == 'A211':
                return True

            else:
                logger.info('Phase drives diagnostic codes do not allow movement.')
                self.message = 'Phase drives diagnostic codes do not allow movement.'
            return False

    def allowed_to_change_phase(self) -> bool:
        if self.phase_enable_status() and self.phase_halt_status() and self._phase_check_for_move():
            self.gaphase_change_allowed = True
            return True

        self.phase_change_allowed = False
        return False

    # GPIO gap functions

    def gap_set_enable(self, val: bool):
        """
        Enables or disables gap motors.
        """
        with self._epu_lock:
            if not val and self.gap_halt_status():
                self.message = 'Gap is not halted.'
                logger.info('To disable the gap, it must be halted first.')
                return False
            else:
                bsmp_enable_message = utils.bsmp_send(_cte.BSMP_WRITE, variableID=_cte.ENABLE_CH_AB, value=val).encode()
                return set_digital_signal(val, bsmp_enable_message, self.a_drive, self.b_drive, 'A012',
                                          self.args.beaglebone_addr, self.args.io_port)

    def gap_set_halt(self, val: bool):
        """
        Halts or releases gap motors.
        """
        with self._epu_lock:
            if val and not self.gap_enable_status():
                self.message = 'Gap is not enabled.'
                logger.info('To halt the gap, it must be enabled.')
                return False
            else:
                bsmp_enable_message = utils.bsmp_send(_cte.BSMP_WRITE, variableID=_cte.HALT_CH_AB, value=val).encode()
                return set_digital_signal(val, bsmp_enable_message, self.a_drive, self.b_drive, 'A010',
                                          self.args.beaglebone_addr, self.args.io_port)

    gap_release_halt = gap_set_halt

    def gap_start(self, val: bool) -> bool:
        logger.debug('Gap start function called.')
        if self._gap_check_for_move():
            logger.debug('Gap is ok to move.')
            bsmp_enable_message = utils.bsmp_send(_cte.BSMP_WRITE,
                                            variableID=_cte.START_CH_AB,
                                            value=val).encode()
            self.gap_start_event.set()
            response = send_bsmp_message(bsmp_enable_message,
                                         self.args.beaglebone_addr,
                                         self.args.io_port)
            logger.debug('Gap start response: {}'.format(response))
            return bool(response[-2])

    def gap_enable_and_release_halt(self, val: bool = True) -> None:
        self.gap_set_halt(False)
        self.gap_set_enable(False)
        if val:
            self.gap_set_enable(True)
            self.gap_set_halt(True)

    def gap_enable_status(self) -> bool:
        return bool(read_digital_status(self.args.beaglebone_addr,
                                        self.args.io_port,
                                        _cte.ENABLE_CH_AB)[-2])

    def gap_halt_status(self) -> bool:
        return bool(read_digital_status(self.args.beaglebone_addr,
                                        self.args.io_port,
                                        _cte.HALT_CH_AB)[-2])

    gap_halt_release_status = gap_halt_status

    def gap_stop(self) -> None:
        timeout_count = 10
        while self.gap_halt_release_status():
            self.gap_release_halt(False)
            timeout_count -= 1
            if not timeout_count:
                break

        timeout_count = 10
        while self.gap_enable_status():
            self.gap_set_enable(False)
            timeout_count -= 1
            if not timeout_count:
                break

    def gap_turn_on(self) -> bool:
        with self._epu_lock:
            bsmp_enable_message = utils.bsmp_send(_cte.BSMP_WRITE, variableID=_cte.RESET_CH_AB, value=1).encode()
            response = send_bsmp_message(bsmp_enable_message, self.args.beaglebone_addr, self.args.io_port)
            return True if response else False

    # GPIO phase functions

    def phase_set_enable(self, val: bool):
        """
        Enables or disables phase motors.
        """
        with self._epu_lock:
            if not val and self.gap_halt_status():
                epu.message = 'Phase is not halted.'
                return False
            else:
                bsmp_enable_message = utils.bsmp_send(_cte.BSMP_WRITE, variableID=_cte.ENABLE_CH_SI, value=val).encode()
                return set_digital_signal(val, bsmp_enable_message, self.i_drive, self.s_drive, 'A012',
                                          self.args.beaglebone_addr, self.args.io_port)

    def phase_set_halt(self, val: bool):
        """
        Halts or releases phase motors.
        """
        with self._epu_lock:
            if val and not self.phase_enable_status():
                epu.message = 'Phase is not halted.'
                return False
            else:
                bsmp_enable_message = utils.bsmp_send(_cte.BSMP_WRITE, variableID=_cte.HALT_CH_SI, value=val).encode()
                return self._send_digital_signal(val, bsmp_enable_message, self.i_drive, self.s_drive, 'A010')

    phase_release_halt = phase_set_halt

    def phase_start(self, val: bool) -> bool:
        if self._phase_check_for_move():
            bsmp_enable_message = utils.bsmp_send(_cte.BSMP_WRITE, variableID=_cte.START_CH_SI, value=val).encode()
            self.phase_start_event.set()
            return bool(send_bsmp_message(
                        bsmp_enable_message,
                        self.args.beaglebone_addr,
                        self.args.io_port)[-2])

    def phase_enable_and_release_halt(self, val) -> None:
        self.phase_set_halt(False)
        self.phase_set_enable(False)
        if val:
            self.phase_set_enable(True)
            self.phase_set_halt(True)

    def phase_enable_status(self):
        return bool(read_digital_status(self.args.beaglebone_addr,
                                        self.args.io_port,
                                        _cte.ENABLE_CH_SI)[-2])
        
    def phase_halt_status(self):
        return bool(read_digital_status(self.args.beaglebone_addr,
                                        self.args.io_port,
                                        _cte.HALT_CH_SI)[-2])
    
    phase_halt_release_status = phase_halt_status

    def phase_stop(self):
        timeout_count = 10
        while self.phase_halt_release_status():
            self.phase_release_halt(False)
            time.sleep(.1)
            timeout_count -= 1
            if not timeout_count:
                break
        timeout_count = 10
        
        while self.phase_enable_status():
            self.phase_set_enable(False)
            time.sleep(.1)
            timeout_count -= 1
            if not timeout_count:
                break

    def phase_turn_on(self) -> bool:
        with self._epu_lock:
            bsmp_enable_message = utils.bsmp_send(_cte.BSMP_WRITE, variableID=_cte.RESET_CH_SI, value=1).encode()
            response = send_bsmp_message(bsmp_enable_message, self.args.beaglebone_addr, self.args.io_port)
            return True if response else False
    
    # GPIO functions for both gap and phase
    
    def turn_on_all(self):
        self.gap_turn_on()
        time.sleep(1)
        self.phase_turn_on()

    def stop_all(self):
        self.gap_stop()
        self.phase_stop()


def get_file_handler(file: str):
    # logger.handlers.clear()
    file_handler = logging.handlers.RotatingFileHandler(file, maxBytes=10000000, backupCount=10)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s"))
    return file_handler


def get_logger(file_handler):
    lg = logging.getLogger()
    lg.setLevel(logging.DEBUG)
    lg.addHandler(file_handler)
    return lg


logger.handlers.clear()
fh = get_file_handler('testing.log')
root = get_logger(fh)

if __name__ == '__main__':
    epu = Epu(default_args)
    with open('testing.txt', 'w') as f:
        for i in range(10):
            epu.gap_set(245)
            epu.gap_start(True)
            while epu.gap_is_moving:
                time.sleep(1)
            f.write(str(epu.gap))
            epu.gap_set(250)
            epu.gap_start(True)
            time.sleep(.1)
            while epu.gap_is_moving:
                time.sleep(1)
            f.write(str(epu.gap))
