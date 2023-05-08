"""EPU module."""

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
from .utils import DriveCOMError

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


def send_bsmp_message(bsmp_enable_message, tcp_client: TCPClient) -> bytes:
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
    if not tcp_client.connected:
        tcp_client.connect()

    tcp_client.send_data(bsmp_enable_message.decode())
    return tcp_client.receive_data(conn='io')


def set_digital_signal(val: bool, bsmp_enable_message: bytes, drive1: EcoDrive,
                       drive2: EcoDrive, right_diagnostic_code: str, tcp_client: TCPClient) -> bool:
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
            response = send_bsmp_message(bsmp_enable_message, tcp_client)
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
        send_bsmp_message(bsmp_enable_message, tcp_client)

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


def read_digital_status(tcp_client, bsmp_id: int) -> bytes:
    bsmp_enable_message = utils.bsmp_send(_cte.BSMP_READ, variableID=bsmp_id, size=0).encode()
    return send_bsmp_message(bsmp_enable_message, tcp_client)


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
            self.args = args
            self._serial_socket = TCPClient(args.beaglebone_addr, args.msg_port)
            self._gpio_socket = TCPClient(args.beaglebone_addr, args.io_port)
            self._serial_socket.connect()
            self._gpio_socket.connect()
            self.callback_update = callback_update
            self.message = None
            self.rs485_connected = self._gpio_socket.connected
            self.gpio_connected = self._serial_socket.connected
            self.tcp_connected = self.rs485_connected and self.gpio_connected

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
            self._epu_lock = threading.RLock()
            self.gap_start_event = threading.Event()
            self.phase_start_event = threading.Event()
            self.monitor_phase_movement_thread = Thread(target=self._monitor_phase_movement, daemon=True)
            self.monitor_gap_movement_thread = Thread(target=self._monitor_gap_movement, daemon=True)

            self._init_variables()

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
        logger.info('Initializing variables.')
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
                    (e, h) = drive.get_halten_status()
                    setattr(self, f'{var}_enable', bool(e))
                    setattr(self, f'{var}_halt_released', bool(h))
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

        self._read_drive_a()
        self._read_drive_b()
        self._read_drive_i()
        self._read_drive_s()

        logger.info('Variables initialized.')

    def _monitor_movement(self, start_event, drive, attribute, logger_message):
        while True:
            start_event.wait()
            setattr(self, f'{attribute}_is_moving', True)
            target = getattr(self, f'{attribute}_target')
            with self._epu_lock:
                logger.info(f'{logger_message} started.')
                drive.connect_to_drive()
                start = time.monotonic()
                update_count = 0
                loop_count = 0
                prev_value = getattr(self, attribute)

                while start_event.is_set():
                    value = drive.read_encoder(False)
                    if isinstance(value, float):
                        setattr(self, attribute, value)
                        self.callback_update()
                        logger.info(f'{attribute}: {value}')
                        update_count += 1

                    if abs(getattr(self, attribute) - target) < .001:
                        try:
                            pos_reached = drive.get_target_position_reached()
                        except Exception as e:
                            logger.debug(f'Falied to read target position reached bit.')
                            logger.debug(e)
                        if True:
                            if not pos_reached:
                                logger.debug(f'Position reached status is FALSE.')
                            else:
                                logger.debug(f'Position reached status is TRUE.')
                            start_event.clear()
                            setattr(self, f'{attribute}_is_moving', False)
                            end = time.monotonic()
                            logger.info(f'{logger_message} finished. Update rate: {int(update_count / (end - start))}')

                    if loop_count >= 10:
                        if getattr(self, attribute) == prev_value:
                            try:
                                pos_reached = drive.get_target_position_reached()
                            except Exception as e:
                                logger.debug(f'Falied to read target position reached bit.')
                                logger.debug(e)
                            if True:
                                if not pos_reached:
                                    logger.debug(f'Position reached status is FALSE.')
                                else:
                                    logger.debug(f'Position reached status is TRUE.')
                                logger.warning(f'{logger_message} stopped because {attribute} has not changed after 10 loops.')
                                start_event.clear()
                                setattr(self, f'{attribute}_is_moving', False)
                        loop_count = 0
                        prev_value = getattr(self, attribute)
                    else:
                        loop_count += 1

    def _monitor_gap_movement(self):
        self._monitor_movement(self.gap_start_event, self.a_drive, 'gap', 'Gap movement')

    def _monitor_phase_movement(self):
        self._monitor_movement(self.phase_start_event, self.i_drive, 'phase', 'Phase movement')

    @utils.run_periodically_in_detached_thread(interval=2)
    def _standstill_monitoring(self):
        """
        Read sensor data and monitor the communications.
        """
        self._check_allowed_to_change()
        self._reconnect_io_serial()

        # read data and save it as attributes
        self._read_drive_a()
        self._read_drive_b()
        self._read_drive_i()
        self._read_drive_s()

        # get gap and phase info from respective encoders and drives
        self.gap_target = self.a_target_position
        self.gap = self.a_encoder_gap
        self.gap_enable_and_halt_released = self.gap_enable and self.gap_halt_released

        self.phase_target = self.i_target_position
        self.phase = self.i_encoder_phase
        self.phase_enable_and_halt_released = self.phase_enable and self.phase_halt_released

    def _check_allowed_to_change(self):
        """
        Check if it is allowed to change the gap and phase.
        """
        self.gap_change_allowed = (self.a_target_position == self.b_target_position) and \
            (self.a_diag_code == self.b_diag_code == 'A211') and \
                (self.a_target_velocity == self.b_target_velocity)

        self.phase_change_allowed = (self.i_target_position == self.s_target_position) and \
            (self.i_diag_code == self.s_diag_code == 'A211') and \
                (self.i_target_velocity == self.s_target_velocity)

    def _reconnect_io_serial(self):
        """
        Check the communication status and reconnect if necessary.
        """
        self.gpio_connected, self.rs485_connected = self._gpio_socket.connected, self._serial_socket.connected
        if not self.gpio_connected:
            self._gpio_socket.connect()

        if not self.rs485_connected:
            self._serial_socket.connect()

        # update class attribute
        self.tcp_connected = self._gpio_socket.connected and self._serial_socket.connected

    def _read_drive(self, drive):
        """
        Read the sensor data from a drive.
        """
        with self._epu_lock:
            try:
                drive_resolver_gap = drive.read_resolver(True)
                drive_encoder_gap = drive.read_encoder(False)
                drive_target_position = drive.get_target_position(False)
                drive_diag_code = drive.get_diagnostic_code(False)
                drive_target_velocity = drive.get_max_velocity(False)

                return (drive_resolver_gap, drive_encoder_gap, drive_target_position, drive_diag_code, drive_target_velocity)

            except (ValueError, TypeError) as e:
                logger.debug(f'Drive {drive} did not respond during standstill monitoring.')
                logger.debug(e)
                raise

    def _read_drive_a(self):
        try:
            self.a_resolver_gap, self.a_encoder_gap, self.a_target_position, self.a_diag_code, self.a_target_velocity = self._read_drive(self.a_drive)
        except (ValueError, TypeError):
            pass

    def _read_drive_b(self):
        try:
            self.b_resolver_gap, self.b_encoder_gap, self.b_target_position, self.b_diag_code, self.b_target_velocity = self._read_drive(self.b_drive)
        except (ValueError, TypeError):
            pass

    def _read_drive_i(self):
        try:
            self.i_encoder_phase, self.i_resolver_phase, self.i_target_position, self.i_diag_code, self.i_target_velocity = self._read_drive(self.i_drive)
        except (ValueError, TypeError):
            pass

    def _read_drive_s(self):
        try:
            self.s_resolver_phase, self.s_encoder_phase, self.s_target_position, self.s_diag_code, self.s_target_velocity = self._read_drive(self.s_drive)
        except (ValueError, TypeError):
            pass

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
        while attempts < 3:
            with self._epu_lock:
                try:
                    return func(value)
                except (DriveCOMError, ValueError):
                    logger.error('Could not set drive value.')
                    time.sleep(0.5)
                    attempts += 1
                    logger.error('Could not set drive value.')
                    raise

    def _set_undulator_property(self, movement_property, value, undulator_property) -> bool:
        with self._epu_lock:
            drive_funcs = {
                ('position', 'gap'): (self.a_drive.set_target_position, self.b_drive.set_target_position),
                ('velocity', 'gap'): (self.a_drive.set_target_velocity, self.b_drive.set_target_velocity),
                ('position', 'phase'): (self.i_drive.set_target_position, self.s_drive.set_target_position),
                ('velocity', 'phase'): (self.i_drive.set_target_velocity, self.s_drive.set_target_velocity),
            }

            func1, func2 = drive_funcs.get((movement_property, undulator_property))
            if func1 is not None:
                try:
                    self._set_drive_values(value, func1)
                except (DriveCOMError, ValueError):
                    logger.error('Could not set drive value.')
                    return False
                else:
                    try:
                        self._set_drive_values(value, func2)
                    except (DriveCOMError, ValueError):
                        logger.warning(
                            f'Could not set {undulator_property} {movement_property} on drive B. \
                            {undulator_property} {movement_property} drives may have different target values.')
                        self.message = f'{undulator_property} {movement_property} drives may have different target values.'
                        self.gap_change_allowed = False
                        return False

    def gap_set(self, target: float) -> bool:
        if _cte.minimum_gap <= target <= _cte.maximum_gap:
            self._set_undulator_property('position', target, 'gap')
        else:
            logger.error(f'Gap value given, ({target}), is out of range.')
            return False

    def gap_set_velocity(self, target: float) -> bool:
        if _cte.minimum_velo_mm_per_min <= target <= _cte.maximum_velo_mm_per_min:
            self._set_undulator_property('velocity', target, 'gap')
        else:
            logger.error(
                f'Velocity ({target}) mm/s is out of range \
                    {_cte.minimum_velo_mm_per_min} < velocity < {_cte.maximum_velo_mm_per_min}')
            return False

    def phase_set(self, target: float) -> bool:
        if _cte.minimum_phase <= target <= _cte.maximum_phase:
            self._set_undulator_property('position', target, 'phase')
        else:
            logger.error(f'Phase value given, ({target}), is out of range.')
            return False

    def phase_set_velocity(self, target: float) -> bool:
        if _cte.minimum_velo_mm_per_min <= target <= _cte.maximum_velo_mm_per_min:
            self._set_undulator_property('velocity', target, 'phase')
        else:
            logger.error(
                f'Velocity ({target}) mm/s is out of range \
                    {_cte.minimum_velo_mm_per_min} < velocity < {_cte.maximum_velo_mm_per_min}')
            return False

    def _gap_check_for_move(self) -> bool:
        retry_count = 3
        with self._epu_lock:
            while retry_count > 0:
                try:
                    drive_a_max_velocity = self.a_drive.get_max_velocity(True)
                    drive_a_target_position = self.a_drive.get_target_position(False)
                    drive_a_diag_code = self.a_drive.get_diagnostic_code(False)
                    drive_b_max_velocity = self.b_drive.get_max_velocity(True)
                    drive_b_target_position = self.b_drive.get_target_position(False)
                    drive_b_diag_code = self.b_drive.get_diagnostic_code(False)

                    if drive_a_max_velocity != drive_b_max_velocity:
                        logger.warning('Gap drives have different maximum velocities.')
                        self.message = 'Gap drives have different maximum velocities.'
                        return False

                    elif drive_a_target_position != drive_b_target_position:
                        logger.warning('Gap drives have different target positions.')
                        self.message = 'Gap drives have different target positions.'
                        return False

                    elif drive_a_diag_code != drive_b_diag_code == 'A211':
                        logger.info('Gap drives diagnostic codes do not allow movement.')
                        self.message = 'Gap drives diagnostic codes do not allow movement.'
                        return False

                    else:
                        return True

                except (ValueError, TypeError) as e:
                    retry_count -= 1
                    if retry_count == 0:
                        logger.error(
                            f'Drive did not respond as expected, probably due to serial \
                                communication problem, after 3 retries')
                        logger.debug(e)
                        return False
                    continue


            logger.info(f'Check for gap movement failed after {retry_count} retries.')
            self.message = 'Check for gap movement failed after retries.'
            return False

    def allowed_to_change_gap(self) -> bool:
        if self.gap_enable_status() and self.gap_halt_status() and self._gap_check_for_move():
            self.gap_change_allowed = True
            return True

        self.gap_change_allowed = False
        return False

    def _phase_check_for_move(self) -> bool:
        retry_count = 3
        with self._epu_lock:
            while retry_count > 0:
                try:
                    drive_i_max_velocity = self.i_drive.get_max_velocity(True)
                    drive_i_target_position = self.i_drive.get_target_position(False)
                    drive_i_diag_code = self.i_drive.get_diagnostic_code(False)
                    drive_s_max_velocity = self.s_drive.get_max_velocity(True)
                    drive_s_target_position = self.s_drive.get_target_position(False)
                    drive_s_diag_code = self.s_drive.get_diagnostic_code(False)

                    if drive_i_max_velocity != drive_s_max_velocity:
                        logger.warning('Phase drives have different maximum velocities.')
                        self.message = 'Phase drives have different maximum velocities.'
                        return False

                    elif drive_i_target_position != drive_s_target_position:
                        logger.warning('Phase drives have different target positions.')
                        self.message = 'Phase drives have different target positions.'
                        return False

                    elif drive_i_diag_code != drive_s_diag_code == 'A211':
                        logger.info('Phase drives diagnostic codes do not allow movement.')
                        self.message = 'Phase drives diagnostic codes do not allow movement.'
                        return False

                    else:
                        return True

                except (ValueError, TypeError) as e:
                    retry_count -= 1
                    if retry_count == 0:
                        logger.error(
                            f'Drive did not respond as expected, probably due to serial \
                                communication problem, after 3 retries')
                        logger.debug(e)
                        return False
                    continue


            logger.info(f'Check for gap movement failed after {retry_count} retries.')
            self.message = 'Check for gap movement failed after retries.'
            return False

    def allowed_to_change_phase(self) -> bool:
        if self.phase_enable_status() and self.phase_halt_status() and self._phase_check_for_move():
            self.phase_change_allowed = True
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
                bsmp_enable_message = utils.bsmp_send(
                    _cte.BSMP_WRITE,
                    variableID=_cte.ENABLE_CH_AB,
                    value=val).encode()

                return set_digital_signal(
                    val, bsmp_enable_message,
                    self.a_drive, self.b_drive, 'A012',
                    self._gpio_socket)

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
                bsmp_enable_message = utils.bsmp_send(
                    _cte.BSMP_WRITE,
                    variableID=_cte.HALT_CH_AB,
                    value=val).encode()

                return set_digital_signal(val, bsmp_enable_message, self.a_drive, self.b_drive, 'A010',
                                          self._gpio_socket)

    gap_release_halt = gap_set_halt

    def gap_start(self, val: bool) -> bool:
        logger.debug('Gap start function called.')
        with self._epu_lock:
            allow_move = self._gap_check_for_move()

        if allow_move:
            logger.debug('Gap is ok to move.')
            bsmp_enable_message = utils.bsmp_send(
                _cte.BSMP_WRITE,
                variableID=_cte.START_CH_AB,
                value=val).encode()
            self.gap_start_event.set()
            response = send_bsmp_message(bsmp_enable_message, self._gpio_socket)
            logger.debug('IO server response to gap start request: {}'.format(response))
            return bool(response)

        else:
            logger.debug('Gap is not ok to move.')
            return False

    def gap_enable_and_release_halt(self, val: bool = True) -> None:
        self.gap_set_halt(False)
        time.sleep(0.1)
        self.gap_set_enable(False)
        time.sleep(0.1)
        if val:
            self.gap_set_enable(True)
            time.sleep(0.1)
            self.gap_set_halt(True)

    def gap_enable_status(self) -> bool:
        with self._epu_lock:
            try:
                status = bool(read_digital_status(
                    self._gpio_socket, _cte.ENABLE_CH_AB)[-2])

            except (IndexError, TypeError):
                status = False

            return status

    def gap_halt_status(self) -> bool:
        with self._epu_lock:
            try:
                status = bool(read_digital_status(
                    self._gpio_socket, _cte.HALT_CH_AB)[-2])

            except (IndexError, TypeError):
                status = False

            return status

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
            bsmp_enable_message = utils.bsmp_send(_cte.BSMP_WRITE,
                                                  variableID=_cte.RESET_CH_AB,
                                                  value=1).encode()
            response = send_bsmp_message(bsmp_enable_message,
                                         self._gpio_socket)
            return True if response else False

    # GPIO phase functions

    def phase_set_enable(self, val: bool):
        """
        Enables or disables phase motors.
        """
        with self._epu_lock:
            if not val and self.phase_halt_status():
                self.message = 'Phase is not halted.'
                return False
            else:
                bsmp_enable_message = utils.bsmp_send(
                    _cte.BSMP_WRITE,
                    variableID=_cte.ENABLE_CH_SI,
                    value=val).encode()

                return set_digital_signal(val, bsmp_enable_message, self.i_drive, self.s_drive, 'A012',
                                          self._gpio_socket)

    def phase_set_halt(self, val: bool):
        """
        Halts or releases phase motors.
        """
        with self._epu_lock:
            if val and not self.phase_enable_status():
                self.message = 'Phase is not halted.'
                return False
            else:
                bsmp_enable_message = utils.bsmp_send(
                    _cte.BSMP_WRITE,
                    variableID=_cte.HALT_CH_SI,
                    value=val).encode()

                return set_digital_signal(val, bsmp_enable_message, self.i_drive, self.s_drive, 'A010',
                                          self._gpio_socket)

    phase_release_halt = phase_set_halt

    def phase_start(self, val: bool) -> bool:
        logger.debug('Phase start function called.')
        with self._epu_lock:
            if self._phase_check_for_move():
                logger.debug('Phase is ok to move.')
                bsmp_enable_message = utils.bsmp_send(
                    _cte.BSMP_WRITE,
                    variableID=_cte.START_CH_SI,
                    value=val).encode()

                self.phase_start_event.set()
                response = send_bsmp_message(bsmp_enable_message, self._gpio_socket)
                logger.debug('IO server response to phase start request: {}'.format(response))
                return bool(response)

    def phase_enable_and_release_halt(self, val) -> None:
        self.phase_set_halt(False)
        time.sleep(0.1)
        self.phase_set_enable(False)
        time.sleep(0.1)
        if val:
            self.phase_set_enable(True)
            time.sleep(0.1)
            self.phase_set_halt(True)

    def phase_enable_status(self):
        with self._epu_lock:
            try:
                status = bool(read_digital_status(
                    self._gpio_socket, _cte.ENABLE_CH_SI)[-2])

            except (IndexError, TypeError):
                status = False

            return status

    def phase_halt_status(self):
        with self._epu_lock:
            try:
                status = bool(read_digital_status(
                    self._gpio_socket, _cte.HALT_CH_SI)[-2])

            except (IndexError, TypeError):
                status = False

            return status

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
            bsmp_enable_message = utils.bsmp_send(_cte.BSMP_WRITE,
                                                  variableID=_cte.RESET_CH_SI,
                                                  value=1).encode()
            response = send_bsmp_message(bsmp_enable_message,
                                         self._gpio_socket)
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

def cycling_test():
    my_epu = Epu(default_args)
    my_epu.turn_on_all()
    my_epu.gap_enable_and_release_halt(True)
    with open('cycling.log', 'w') as f:
        for i in range(10):
            set_and_start_gap(my_epu, 245)
            while my_epu.gap_is_moving:
                time.sleep(1)
            f.write(str(my_epu.gap))

            set_and_start_gap(my_epu, 250)
            time.sleep(.1)
            while my_epu.gap_is_moving:
                time.sleep(1)
            f.write(str(my_epu.gap))

def set_and_start_gap(epu, value):
    epu.gap_set(value)
    epu.gap_start(True)


if __name__ == '__main__':
    pass
