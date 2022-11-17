import logging
import socket
import threading
import time

import constants as _cte
from utils import *

logger = logging.getLogger('__name__')
logging.basicConfig(
    filename='./EcoDrive.log', filemode='w', level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S')

class EcoDrive():

    _lock = threading.RLock()
    _SOCKET_TIMEOUT = .8 # tcp socket timeout

    def __init__(self, address, max_limit=+25, min_limit=-25,
                    bbb_hostname = _cte.beaglebone_addr, rs458_tcp_port=_cte.msg_port, drive_name = 'EcoDrive') -> None:

        self.ADDRESS = address
        self.UPPER_LIMIT = max_limit
        self.LOWER_LIMIT = min_limit
        self.DRIVE_NAME = drive_name
        self.soft_drive_message = ''  # holds general information about events 

        # connections
        self.BBB_HOSTNAME = bbb_hostname
        self.RS458_TCP_PORT = rs458_tcp_port
        self.tcp_wait_connection()
        self.drive_connect()

        # sets ecodrive answer delay (in ms, minimum is 1)
        self.set_rs485_delay(1)

    def tcp_wait_connection(self) -> bool:
        '''
        Any time this function is called, it keeps on a loop trying to reach the other side of a tcp connection,
        when it succeed, it returnts True.
        '''
        with self._lock:
            while True:
                try:
                    s =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((self.BBB_HOSTNAME, self.RS458_TCP_PORT))

                except socket.timeout as e:
                    logger.info(f'Trying to connect.', e)
                    print(f'Trying to connect.', e)
                    time.sleep(2)

                except socket.error as e:
                    logger.exception(f'Trying to connect.')
                    print(e)

                except Exception:
                    logger.exception('Trying to connect')

                else:
                    print(f'Connected.')
                    logger.info(f'Connected.')
                    s.shutdown(socket.SHUT_RDWR)
                    s.close()
                    return True

    def drive_connect(self) -> bool:
        while True:
            try:
                byte_message = self.tcp_read_parameter(f'BCD:{self.ADDRESS}', change_drive=False)

            except Exception:
                logger.exception('Communication error.')
                return False

            else:
                if not (f'E{self.ADDRESS}' in byte_message.decode()):
                    logger.error(f'Trying connection to Drive {self.DRIVE_NAME}, address ({self.ADDRESS}).\
                                    Drive address expected in drive answer, but was not found.')

                else:
                    logger.info(f'Soft driver {self.DRIVE_NAME} connected do ecodrive number {self.ADDRESS}')
                    print(f'Soft driver {self.DRIVE_NAME} connected do ecodrive number {self.ADDRESS}')
                    return True

    @timer
    def tcp_read_parameter(self, message: str, change_drive: bool = True) -> bytes:

        with self._lock:

            if change_drive:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    data = ''
                    s.settimeout(EcoDrive._SOCKET_TIMEOUT)

                    while True:
                        try:
                            s.connect((self.BBB_HOSTNAME, self.RS458_TCP_PORT))
                            break

                        except Exception as e:
                            logger.exception('Communication error.')
                            print('Communication error', e)
                            self.tcp_wait_connection()
                            self.drive_connect()
                        
                    s.sendall(f'BCD:{self.ADDRESS}\r'.encode())

                    while True:
                        try:

                            chunk = s.recv(16)
                            if not chunk or chunk.decode()[-1]=='>':
                                data += chunk.decode()
                                break
                            else: data += chunk.decode()

                        except Exception as e:
                            logger.exception('Error while setting address')
                            print(e)
                            if not data: return

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                while True:
                    try:
                        s.connect((self.BBB_HOSTNAME, self.RS458_TCP_PORT))
                        break

                    except Exception as e:
                        logger.exception('Communication error.')
                        print('Communication error', e)
                        self.tcp_wait_connection()
                        self.drive_connect()

                s.sendall(f'{message}\r'.encode())
                data = ''
                
                while True:
                    try:
                        chunk = s.recv(16)
                        if not chunk or chunk.decode()[-1]=='>':
                            data += chunk.decode()
                            break
                        else: data += chunk.decode()

                    except Exception as e:
                        print(e)
                        if data: return data
                        else: return 

                return data.encode()

    def get_resolver_position(self, change_drive = True) -> float:
        return float(self.read_parameter_data('S-0-0051', change_drive=change_drive))
    
    def get_resolver_nominal_position(self):
        return float(self.read_parameter_data('S-0-0047'))

    def get_encoder_nominal_position(self):
        return float(self.read_parameter_data('S-0-0048'))

    def get_upper_limit_position(self):
        return float(self.read_parameter_data('S-0-0049'))

    def get_lower_limit_position(self) -> float:
        return float(self.read_parameter_data('S-0-0050'))

    def get_act_torque(self) -> float:
        return float(self.read_parameter_data('S-0-0079'))

    def get_encoder_position(self, change_drive=True) -> float:
        return float(self.read_parameter_data('S-0-0053', change_drive=change_drive))

    def get_diagnostic_code(self, change_drive: bool = True) -> str:
        return self.read_parameter_data('S-0-0390', change_drive=change_drive)[:-1]

    def get_halten_status(self, change_drive = True) -> tuple:
        return tuple([int(x) for x in eco_test.read_parameter_data('S-0-0134', change_drive=change_drive)[13:15]])

    def get_target_position_reached(self) -> bool:
        try:
            byte_message = self.tcp_read_parameter('S-0-0013,7,R')
        except Exception as e:
            logger.exception('Communication error in tcp_read_parameter.')
        else:
            str_message = byte_message.decode()
            if not ('S-0-0342,7,R' in str_message):
                logger.error('Drive did not respond as axpected to "S-0-0013,7,R".')
                raise Exception('Drive did not respond as axpected to "S-0-0013,7,R".')
            else:
                targ_pos_reached_bit = str_message.split('\r\n')[1][1]
                if not (targ_pos_reached_bit == '0' or targ_pos_reached_bit == '1'):
                    logger.error(
                        "Drive did not respond as axpected: "
                        "targ_pos_reached bit is not 0 neither 1"
                        )
                    raise Exception(
                        "Drive did not respond as axpected: "
                        "targ_pos_reached bit is not 0 neither 1"
                        )
                self.target_position_reached = targ_pos_reached_bit
                return bool(targ_pos_reached_bit)

    def set_target_position(self, target_position: float) -> float:
        if not (
            self.LOWER_LIMIT <= target_position <= self.UPPER_LIMIT):
            logger.exception('Target position out of limits.')
            raise ValueError('Target position out of limits.')
        else:
            try:
                byte_message = self.tcp_read_parameter('P-0-4006,7,W,>')
            except Exception as e:
                logger.exception('Communication error in tcp_read_parameter().')
            else:
                str_message = byte_message.decode()
                if not 'P-0-4006,7,W,>' in str_message:
                    logger.error(
                        '"P-0-4006,7,W,>" not found in drive answer for "P-0-4006,7,W,>" command')
                    print(
                        '"P-0-4006,7,W,>" not found in drive answer to "P-0-4006,7,W,>" command')
                    raise Exception(
                        '"P-0-4006,7,W,>" not found in drive answer to "P-0-4006,7,W,>" command')
                else:
                    try:
                        byte_message = self.tcp_read_parameter(f'{target_position}', False)
                    except Exception as e:
                        logger.exception('Could not set target position.')
                    else:
                        str_target_position_readback = byte_message.decode()
                        if not f'{target_position}' in str_target_position_readback:
                            logger.error(
                                'Target position not setted. Intended target position not found in drive answer.')
                            raise Exception(
                                'Target position not setted. Intended target position not found in drive answer.')
                        else:
                            try:
                                byte_message = self.tcp_read_parameter('<', False)
                            except Exception as e:
                                logger.exception('Communication error in tcp_read_parameter().')
                            else:
                                str_message = byte_message.decode()
                                if not f'E{self.ADDRESS}' in str_message:
                                    logger.error(
                                        f'Drive addres (E{self.ADDRESS}) was expcted in drive answer, but was not found.')
                                    raise Exception(
                                        f'Drive addres (E{self.ADDRESS}) was expcted in drive answer, but was not found.')
                                else:
                                    target_position = float(str_target_position_readback.split('\r')[0])
                                    return target_position

    def get_target_position(self):
        return float(self.read_parameter_data('P-0-4006,7,R'))

    def get_max_velocity(self, chande_drive: bool =True):
        return float(self.read_parameter_data('P-0-4007,7,R', change_drive=chande_drive))

    def set_target_velocity(self, target: float) -> bool:
        if 50 <= target <= 500:
            with self._lock:
                answer = self.tcp_read_parameter('P-0-4007,7,W,>').decode()
                if '?' in answer:
                    answer = self.tcp_read_parameter(
                        f'{target}', change_drive=False).decode()
                    if str(target) in answer:
                        answer = self.tcp_read_parameter("<", change_drive=False).decode()
                        if f'{self.ADDRESS}' in answer:
                            logger.info(
                                f'Drive {self.DRIVE_NAME} velocity changed to {target}')
                            return True
                        else:
                            logger.info(
                                f'Driver {self.DRIVE_NAME} address not found in last parameter write stage')
                            return False
                    else:
                        logger.info(
                                f'">" character not found in second parameter write stage')
                        return False
                else:
                    logger.info(f'"?" character not found in first parameter write stage')
                    return False

    def get_act_velocity(self, change_drive=True):
        try:
            byte_message = self.tcp_read_parameter('S-0-0040,7,R', change_drive=change_drive)
        except Exception as e:
            logger.exception('Communication error in tcp_read_parameter.')
            raise e
        else:
            str_message = byte_message.decode().replace('\r', '').split('\n')
            try:
                act_velocity = float(str_message[1])
            except ValueError as e:
                logger.exception(
                    'Error while trying to convert max velocity value received from drive.')
                raise e
            else:
                self.act_velocity = act_velocity
                return act_velocity

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
        answer = self.tcp_read_parameter('P-0-4050,7,R')
        return(answer)

    def set_rs485_delay(self, value):
        answer = self.tcp_read_parameter(f'P-0-4050,7,W,{value}')
        delay = answer.decode().split('\r\n')
        return delay

    def read_parameter_data(self, parameter, change_drive=True, treat_answer=True) -> str:
        try:
            drive_answer = self.tcp_read_parameter(f'{parameter},7,R', change_drive).decode()
        except Exception:
            logger.exception('Tcp reading error')
        else:
            if not f'E{self.ADDRESS}:>' in drive_answer:
                logger.error(
                    'Corrupt drive answer', f'Drive {self.DRIVE_NAME} answer to "{parameter},7,R" {drive_answer}')
                raise Exception(
                    'Corrupt drive answer', f'Drive {self.DRIVE_NAME} answer to "{parameter},7,R": {drive_answer}')
            if treat_answer:
                parameter_data = drive_answer.split('\r\n')[1]
                return parameter_data
            else: return drive_answer    

    def clear_error(self):
        with self._lock:
            self.tcp_read_parameter('S-0-0099,3,r')
            self.tcp_read_parameter('S-0-0099,7,w,11b', False)
            self.tcp_read_parameter('S-0-0099,1,w,0', False)
            self.tcp_read_parameter('S-0-0099,7,w,0b', False)
            self.tcp_read_parameter('S-0-0099,7,w,0b', False)
            self.tcp_read_parameter('S-0-0099,7,w,0b', False)


################### MODULE TESTING ##################
if __name__ == '__main__':
    eco_test = EcoDrive(address=21, min_limit=_cte.minimum_gap, max_limit=_cte.maximum_gap, drive_name='Teste')
    for i in range(1):
        print(eco_test.get_diagnostic_code())
