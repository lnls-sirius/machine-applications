#!/usr/bin/env python-sirius
import logging
import threading
import time

from .connection_handler import TCPClient

logger = logging.getLogger(__name__)


class EcoDrive:
    _lock = threading.RLock()

    def __init__(self, tcp_client: TCPClient, address: int, max_limit, min_limit,
                 drive_name: str = 'EcoDrive') -> None:

        """Indramat EcoDrive 03 (controllers DKC**.3-040, -100, -200) class.
           Encapsulate ASCII messages into TCP datagrams.
           Makes available a subset of possible readings and
           writes from/to EcoDrive 03 controllers. It is required that on the
           other side of communication, there is some software
           unwrapping tcp messages and delivering it to a RS485 interface; on CNPEM
           this is typically done with a beagle bone black configured properly.
        """

        self.ADDRESS = address
        self.UPPER_LIMIT = max_limit
        self.LOWER_LIMIT = min_limit
        self.DRIVE_NAME = drive_name
        self.sock = tcp_client
        self.tcp_connected = False
        self.rs485_connected = False

        if not self.sock.connected:
            self.sock.connect()
        self.connect_to_drive()

        # minimum ecodrive answer delay in ms
        self.set_rs485_delay(1)

    # Communication functions

    def connect_to_drive(self) -> bool:
        """
        Try to connect to drive (SERIAL, NOT TCP CONNECTION).
        Keeps trying to connect to drive until it succeeds.
        Success is achieved when the drive responds correctly.
        """
        with self._lock:
            while True:
                time.sleep(1)
                answer = self.tcp_read_parameter(f'BCD:{self.ADDRESS}', change_drive=False)
                if not answer:
                    continue
                elif f'E{self.ADDRESS}' in answer.decode():
                    logger.debug(f'{self.DRIVE_NAME} connected to ecodrive address {self.ADDRESS}')
                    return True
                else:
                    logger.error(f'Drive {self.DRIVE_NAME} failed to connect with \
                                 BCD:{self.ADDRESS}. Response was: {answer.decode()}')
                    self.rs485_connected = False
                    self.sock.clean_socket_buffer()
                    return False

    # @utils.timer # prints the execution time of the function
    def tcp_read_parameter(self, message: str, change_drive: bool = True) -> bytes:
        with EcoDrive._lock:
            if change_drive:
                self.sock.send_data(f'BCD:{self.ADDRESS}\r')
                self.sock.receive_data()  # TODO: verify the coherence of the answer

            self.sock.send_data(f'{message}\r')
            data = self.sock.receive_data()

            if change_drive:
                time.sleep(.01)  # makes significant difference
            return data.encode() if data else b''

    def read_parameter_data(self, parameter: str, change_drive: bool = True, treat_answer: bool = True) -> str:
        response = self.tcp_read_parameter(f"{parameter},7,R", change_drive)
        response = response.decode() if response else None

        if not response:
            logger.error(f"No response received from {self.DRIVE_NAME}.")
            return None

        if f'E{self.ADDRESS}' not in response:
            logger.error(f"Address not found in response from {self.DRIVE_NAME}.")
            return None

        if treat_answer:
            try:
                parameter_data = response.split('\r\n')[1]
                return parameter_data
            except IndexError:
                logger.error(f"IndexError in response from {self.DRIVE_NAME}.")
                logger.debug(f"Response: {response}")
                return None
        else:
            return response

    # Position and velocity functions

    def read_resolver(self, change_drive=True) -> float:
        try:
            answer = self.read_parameter_data('S-0-0051', change_drive=change_drive)
            pos = float(answer)
            return pos

        except (ValueError, TypeError) as e:
            raise e

    def read_encoder(self, change_drive: bool = True) -> float:
        try:
            answer = self.read_parameter_data('S-0-0053', change_drive=change_drive)
            pos = float(answer)
            return pos

        except (ValueError, TypeError) as e:
            raise e

    def get_target_position(self, change_drive: bool = True) -> float:
        try:
            answer = self.read_parameter_data('P-0-4006', change_drive=change_drive)
            pos = float(answer)
            return pos

        except (ValueError, TypeError) as e:
            raise e

    def set_target_position(self, target: float) -> bool:
        try:
            if not (self.LOWER_LIMIT <= target <= self.UPPER_LIMIT):
                raise ValueError('Target position out of limits.')

            with self._lock:
                response = self.tcp_read_parameter('P-0-4006,7,W,>')
                if b'?' not in response:
                    logger.error(f'Error: {response}')
                    return False

                response = self.tcp_read_parameter(f'{target}', change_drive=False)
                if str(target).encode() not in response:
                    logger.error('Target position not set. Intended target velocity not found in drive answer.')
                    return False

                response = self.tcp_read_parameter('<', change_drive=False)
                if f'{self.ADDRESS}'.encode() not in response:
                    logger.error(
                        f'Parameter reading error; drive answer to last step of setting target position: {response}')
                    return False

                logger.info(f'Drive {self.DRIVE_NAME} target position changed to {target} mm.')
                return True

        except Exception as e:
            logger.error(f'Error setting target position: {e}')
            return False

    def get_max_velocity(self, change_drive: bool = True) -> float:
        try:
            answer = self.read_parameter_data('P-0-4007', change_drive=change_drive)
            pos = float(answer)
            return pos

        except (ValueError, TypeError) as e:
            raise e

    # TODO: put limits outside the function
    def set_target_velocity(self, target: float) -> bool:
        try:
            if not (30 <= target <= 500):
                raise ValueError('Target velocity out of limits.')

            with self._lock:
                response = self.tcp_read_parameter('P-0-4007,7,W,>')
                if b'?' not in response:
                    logger.error(f'Error: {response}')
                    return False

                response = self.tcp_read_parameter(f'{target}', change_drive=False)
                if str(target).encode() not in response:
                    logger.error('Target velocity not set. Intended target velocity not found in drive answer.')
                    return False

                response = self.tcp_read_parameter('<', change_drive=False)
                if f'{self.ADDRESS}'.encode() not in response:
                    logger.error(
                        f'Parameter reading error; drive answer to last step of setting target velocity: {response}')
                    return False

                logger.info(f'Drive {self.DRIVE_NAME} velocity changed to {target} mm/s ({target * .001} m/s).')
                return True

        except Exception as e:
            logger.error(f'Error setting target velocity: {e}')
            return False

    # Status functions

    def get_diagnostic_code(self, change_drive: bool = True) -> str:
        answer = self.read_parameter_data('S-0-0390', change_drive=change_drive)
        if isinstance(answer, str):
            return answer[:-1]
        else:
            return ''

    def get_halten_status(self, change_drive: bool = True) -> tuple:
        try:
            return tuple([int(x) for x in self.read_parameter_data('S-0-0134', change_drive=change_drive)[1:3]])

        except Exception as e:
            raise e

    def get_target_position_reached(self) -> bool:
        byte_message = self.tcp_read_parameter('S-0-0013,7,R')
        str_message = byte_message.decode()

        if 'S-0-0342' not in str_message:
            logger.error(f'Parameter reading error: Drive address {self.ADDRESS}; answer: {str_message}')
            raise RuntimeError('Parameter reading error.')

        targ_pos_reached_bit = str_message.split('\r\n')[1][1]
        if targ_pos_reached_bit not in ('0', '1'):
            logger.error(f'Parameter reading error: Drive address {self.ADDRESS}; answer: {str_message}')
            raise RuntimeError('Parameter reading error.')

        return bool(int(targ_pos_reached_bit))

    # Do not use it yet
    def get_movement_status(self, change_drive=True) -> bool:
        try:
            byte_message = self.tcp_read_parameter('S-0-0013,7,R', change_drive=change_drive)
        except Exception as e:
            logger.exception('Communication error in tcp_read_parameter().')
            raise e
        else:
            str_message = byte_message.decode().replace('\r', '').split('\n')
            try:
                is_moving = bool(str_message[1][1])
            except ValueError as e:
                logger.exception(
                    'Error while trying to convert max velocity value received from drive.')
                raise e
            else:
                return is_moving

    def get_rs485_delay(self):
        return self.tcp_read_parameter('P-0-4050,7,R')

    def set_rs485_delay(self, value):
        answer = self.tcp_read_parameter(f'P-0-4050,7,W,{value}')
        delay = answer.decode().split('\r\n')
        return delay

    def clear_error(self):
        with self._lock:
            self.tcp_read_parameter(f'BCD:{self.ADDRESS}', False)
            self.tcp_read_parameter("S-0-0099,3,r", False)
            self.tcp_read_parameter("S-0-0099,7,w,11", False)
            self.tcp_read_parameter("S-0-0099,1,w,0", False)
            self.tcp_read_parameter("S-0-0099,2,r", False)
            self.tcp_read_parameter("S-0-0099,3,r", False)
            self.tcp_read_parameter("S-0-0099,7,w,0", False)
            self.tcp_read_parameter("S-0-0095,3,r", False)
            self.tcp_read_parameter("S-0-0095,7,r", False)
            self.tcp_read_parameter("S-0-0099,1,w,0", False)
            self.tcp_read_parameter("S-0-0099,2,r", False)
            self.tcp_read_parameter("S-0-0099,3,r", False)
            self.tcp_read_parameter("S-0-0099,7,w,0", False)
            self.tcp_read_parameter("S-0-0014,7,r", False)
            self.tcp_read_parameter('S-0-0099,3,r', False)
            self.tcp_read_parameter('S-0-0099,7,w,11', False)
            self.tcp_read_parameter('P-0-4023,7,W,11', False)
            self.tcp_read_parameter('S-0-0099,7,W,11', False)
            self.tcp_read_parameter('P-0-4023,7,W,10', False)
            self.tcp_read_parameter('S-0-0099,7,W,00', False)
            self.tcp_read_parameter('S-0-0127,7,W,11', False)
            self.tcp_read_parameter('S-0-0127,7,W,00', False)
            self.tcp_read_parameter('S-0-0128,7,W,11', False)
            self.tcp_read_parameter('S-0-0128,7,W,00', False)


if __name__ == '__main__':
    pass
