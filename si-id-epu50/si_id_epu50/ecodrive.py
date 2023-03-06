#!/usr/bin/env python-sirius

import logging
logger = logging.getLogger(__name__)
import socket
import threading
import time

from . import constants as _cte
from .utils import *

class EcoDrive():

    _lock = threading.RLock()
    _TCP_SOCKET_TIMEOUT = 1 # ms

    def __init__(self, socket: socket.socket, address: int, max_limit, min_limit,
                 bbb_hostname, rs458_tcp_port: int = None, drive_name: str = 'EcoDrive') -> None:
        
        """Intramat EcoDirve 03 (controllers DKC**.3-040, -100, -200) class.
           Encaptulate ASCII messages into TCP datagrams.
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
        self.BBB_HOSTNAME = bbb_hostname
        self.RS458_TCP_PORT = rs458_tcp_port
        self.sock = socket
        self.tcp_connected = False
        self.rs485_connected = False
        
        self.tcp_wait_connection()
        self.drive_connect()

        # minimum ecodrive answer delay in ms
        # self.set_rs485_delay(1)

    def tcp_wait_connection(self) -> bool:
        """
        Any time this function is called, it keeps on a loop trying to reach
        the other side of a tcp connection, when it succeed, it returnts True.
        """
        count = 0
        with self._lock:

            while True:

                try:
                    self.sock.sendall(b'')
                except BrokenPipeError:
                    logger.error('BrokenPipeError')
                    self.tcp_connected = False
                    self.rs485_connected = False
                else:
                    self.tcp_connected = True
                    logger.info(f'Drive {self.DRIVE_NAME} connected to {self.BBB_HOSTNAME} on port {self.RS458_TCP_PORT}.')
                    return True
                
                try:
                    self.sock.connect((self.BBB_HOSTNAME, self.RS458_TCP_PORT))
                except Exception as e:
                    self.tcp_connected = False
                    self.rs485_connected = False
                    if not count:
                        print(f'Trying to connect.')
                        logger.info(f'Trying to connect.', e)
                        time.sleep(5)
                    count += 1

                else:
                    self.tcp_connected = True
                    logger.info(f'Drive {self.DRIVE_NAME} connected to {self.BBB_HOSTNAME} on port {self.RS458_TCP_PORT}.')
                    return True

    def drive_connect(self) -> True:
        """Drive connect.
        Keeps trying to connect to drive (SERIAL, NOT TCP CONNECTION) untill it succeed, then returns True.
        Success is accomplished when the drive responds properly.
        """
        with self._lock:

            while True:

                try: byte_message = self.tcp_read_parameter(f'BCD:{self.ADDRESS}', change_drive = False)

                except Exception:

                    logger.exception('Communication error.')
                    self.rs485_connected = False

                else:

                    if not (f'E{self.ADDRESS}' in byte_message.decode()):

                        logger.error(f'Drive {self.DRIVE_NAME}, address {self.ADDRESS}, answer to BCD:{self.ADDRESS}: {byte_message.decode()}')
                        self.rs485_connected = False

                    else:

                        self.rs485_connected = True
                        logger.debug(f'Soft driver {self.DRIVE_NAME} connected do ecodrive address {self.ADDRESS}')
                        return True

    def send_data(self, message: str) -> str:
        '''
        Sends data to drive and returns the drive answer.
        In the future this should be a 'handler class' outside acodrive class.
        '''
                
        with self._lock:
            
            try:
                self.sock.sendall(message.encode())
                
            except BrokenPipeError:
                logger.error(BrokenPipeError)
                
                show_message = True
                while True:
                    if show_message:
                        logger.debug('Disconnected. Trying to reconnect.')
                        show_message = False
                    try:
                        self.sock.connect((self.BBB_HOSTNAME, self.RS458_TCP_PORT))
                        break
                    except Exception as e:
                        logger.debug(e)
                    time.sleep(5)
            
            except Exception as e:
                logger.debug(e)
                time.sleep(5)
            
            else:
                data = ''
                while True:
                    try:
                        chunk = self.sock.recv(32)
                        if not chunk or chunk.decode()[-1]=='>' or chunk.decode()[-1]=='?':
                            data += chunk.decode()
                            break
                        else: data += chunk.decode()

                    except Exception as e:
                        if not data:
                            logger.debug(e)
                            return
                
                return data
                                      
    #@timer # prints the execution time of the function
    def tcp_read_parameter(self, message: str, change_drive: bool = True) -> bytes:

        try:
            if change_drive:
                self.send_data(f'BCD:{self.ADDRESS}\r')

            data = self.send_data(f'{message}\r')

            if change_drive: time.sleep(.007) # makes significant difference
            return data.encode()
        
        except Exception as e:
            logger.debug(e)
                
    def get_resolver_position(self, change_drive = True) -> float:

        try:

            answer = self.read_parameter_data('S-0-0051', change_drive=change_drive)
            fanswer = float(answer)

        except Exception:

            if answer: logger.error('Parameter reading error.', answer)
            else: logger.exception('Parameter reading error.')
            return

        else: return fanswer

    def get_resolver_nominal_position(self, change_drive: bool = True):
        try:
            answer = self.read_parameter_data('S-0-0047', change_drive=change_drive)
            fanswer = float(answer)
        except: return
        else:
            return fanswer

    def get_encoder_nominal_position(self, change_drive: bool = True):
        try:
            answer = self.read_parameter_data('S-0-0048', change_drive=change_drive)
            fanswer = float(answer)
        except: return
        else:
            return fanswer

    def get_upper_limit_position(self, change_drive: bool = True):
        try:
            answer = self.read_parameter_data('S-0-0049', change_drive=change_drive)
            fanswer = float(answer)
        except: return
        else:
            return fanswer

    def get_lower_limit_position(self, change_drive: bool = True) -> float:
        try:
            answer = self.read_parameter_data('S-0-0050', change_drive = change_drive)
            fanswer = float(answer)
        except: return
        else:
            return fanswer

    def get_act_torque(self, change_drive: bool = True) -> float:
        try:
            answer = self.read_parameter_data('S-0-0079', change_drive = change_drive)
            fanswer = float(answer)
        except: return
        else:
            return fanswer

    def get_encoder_position(self, change_drive: bool = True) -> float:

        try:

            answer = self.read_parameter_data('S-0-0053', change_drive = change_drive)
            fanswer = float(answer)

        except Exception:

            if answer: logger.error('Parameter reading error.', answer)
            else: logger.exception('Parameter reading error.')
            return

        else: return fanswer

    def get_diagnostic_code(self, change_drive: bool = True) -> str:

        try:

            answer = self.read_parameter_data('S-0-0390', change_drive = change_drive)
            if type(answer) == str: return answer[:-1]
            else: return

        except Exception:

            logger.exception('Parameter reading error')
            return

    def get_halten_status(self, change_drive = True) -> tuple:

        try: return tuple([int(x) for x in self.read_parameter_data('S-0-0134', change_drive=change_drive)[1:3]])

        except:

            logger.exception('Parameter reading error')
            return

    def get_target_position_reached(self) -> bool:

        try: byte_message = self.tcp_read_parameter('S-0-0013,7,R')

        except Exception:

            logger.exception('Parameter reading error')
            return

        else:

            str_message = byte_message.decode()
            if not 'S-0-0342' in str_message:

                logger.error(f'Parameter reading error: Drive address {self.ADDRESS}; answer: {str_message}')
                return

            else:

                targ_pos_reached_bit = str_message.split('\r\n')[1][1]
                if not (targ_pos_reached_bit == '0' or targ_pos_reached_bit == '1'):
                    logger.error(f'Parameter reading error: Drive address {self.ADDRESS}; answer: {str_message}')
                    return

                return bool(targ_pos_reached_bit)

    def set_target_position(self, target_position: float) -> float:

        if not (self.LOWER_LIMIT <= target_position <= self.UPPER_LIMIT):
            logger.exception('Target position out of limits.')
            raise ValueError('Target position out of limits.')

        else:
            with self._lock:
                try: byte_message = self.tcp_read_parameter('P-0-4006,7,W,>')
                except Exception: logger.exception('Parameter writing error.')
                else:
                    str_message = byte_message.decode()

                    if not 'P-0-4006,7,W,>' in str_message:
                        logger.error(f'Parameter reading error: {str_message}')
                        return

                    else:
                        try: byte_message = self.tcp_read_parameter(f'{target_position}', False)
                        except Exception:
                            logger.exception('Parameter writing error')
                            return

                        else:
                            str_target_position_readback = byte_message.decode()
                            if not f'{target_position}' in str_target_position_readback:
                                logger.error('Target position not setted. Intended target position not found in drive answer.')
                                return

                            else:
                                try: byte_message = self.tcp_read_parameter('<', False)
                                except Exception:
                                    logger.exception('Parameter reading error.')
                                    return

                                else:
                                    str_message = byte_message.decode()
                                    if not f'E{self.ADDRESS}' in str_message:
                                        logger.error(f'Parameter reading error; drive answer to last step of setting target position: {str_message}')
                                        return

                                    else:
                                        target_position = float(str_target_position_readback.split('\r')[0])
                                        return target_position

    def get_target_position(self, change_drive = True):

        try:

            answer = self.read_parameter_data('P-0-4006', change_drive=change_drive)
            fanswer = float(answer)

        except Exception:

            if answer: logger.error('Parameter reading error.', answer)
            else: logger.exception('Parameter reading error.')
            return

        else: return fanswer

    def get_max_velocity(self, change_drive = True):

        try:

            answer = self.read_parameter_data('P-0-4007', change_drive=change_drive)
            fanswer = float(answer)

        except Exception:

            if answer: logger.error('Parameter reading error.', answer)
            else: logger.exception('Parameter reading error.')
            return

        else:
            return fanswer

    def set_target_velocity(self, target: float) -> bool:

        if 30 <= target <= 500:

            with self._lock:

                answer = self.tcp_read_parameter('P-0-4007,7,W,>').decode()

                if '?' in answer:

                    answer = self.tcp_read_parameter( f'{target}', change_drive=False).decode()
                    if str(target) in answer:

                        answer = self.tcp_read_parameter("<", change_drive=False).decode()

                        if f'{self.ADDRESS}' in answer:

                            logger.info(f'Drive {self.DRIVE_NAME} velocity changed to {target}')
                            return True

                        else:
                            logger.info(f'Driver {self.DRIVE_NAME} address not found in last parameter write stage')
                            return False
                    else:
                        logger.info( f'">" character not found in second parameter write stage')
                        return False
                else:
                    logger.info(f'"?" character not found in first parameter write stage')
                    return False

    # Not used yet
    def get_act_velocity(self, change_drive=True):
        try:
            byte_message = self.tcp_read_parameter('S-0-0040,7,R', change_drive=change_drive)
        except Exception as e:
            logger.exception('Communication error in tcp_read_parameter.')
            return None
        else:
            str_message = byte_message.decode().replace('\r', '').split('\n')
            try:
                act_velocity = float(str_message[1])
            except ValueError as e:
                logger.exception('Value error')
            else:
                self.act_velocity = act_velocity
                return act_velocity

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
        answer = self.tcp_read_parameter('P-0-4050,7,R')
        return(answer)

    def set_rs485_delay(self, value):
        answer = self.tcp_read_parameter(f'P-0-4050,7,W,{value}')
        delay = answer.decode().split('\r\n')
        return delay

    def read_parameter_data(self, parameter, change_drive=True, treat_answer = True) -> str:

        try:
            drive_answer = self.tcp_read_parameter(f'{parameter},7,R', change_drive).decode()

        except Exception:
            logger.exception('Tcp reading error')

        else:
            if not f'E{self.ADDRESS}' in drive_answer:
                logger.error(f'Drive {self.DRIVE_NAME} answer to "{parameter},7,R": {drive_answer}')
                return None

            if treat_answer:
                parameter_data = drive_answer.split('\r\n')[1]
                return parameter_data

            else: return drive_answer

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
