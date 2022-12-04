#!/usr/bin/env python-sirius

import logging
logger = logging.getLogger(__name__)
import logging.handlers as handlers
import socket
import threading
import time

from . import constants as _cte
from .utils import *

logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logHandler = handlers.RotatingFileHandler(filename='ecodrive.log', maxBytes=10*1024*1024)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)


class EcoDrive():

    _lock = threading.RLock()
    _SOCKET_TIMEOUT = 1 # tcp socket timeout

    def __init__(self, address, max_limit=+25, min_limit=-25,
                    bbb_hostname = None, rs458_tcp_port=None, drive_name = 'EcoDrive') -> None:
        """."""
        self.ADDRESS = address
        self.UPPER_LIMIT = max_limit
        self.LOWER_LIMIT = min_limit
        self.DRIVE_NAME = drive_name
        self.soft_drive_message = ''  # holds general information about events

        # connections
        self.BBB_HOSTNAME = bbb_hostname
        self.RS458_TCP_PORT = rs458_tcp_port
        self.tcp_connected = False
        self.rs485_connected = False
        self.tcp_wait_connection()
        self.drive_connect()

        # sets ecodrive answer delay (in ms, minimum is 1)
        # self.set_rs485_delay(1)

    def tcp_wait_connection(self) -> bool:
        """TCP wait connection.
        
        Any time this function is called, it keeps on a loop trying to reach
        the other side of a tcp connection, when it succeed,
        it returnts True.
        """
        with self._lock:
            
            while True:
                
                try:
                    
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((self.BBB_HOSTNAME, self.RS458_TCP_PORT))

                except socket.timeout as e:
                    
                    self.tcp_connected = False
                    self.rs485_connected = False
                    logger.info(f'Trying to connect...', e)
                    print(f'Trying to connect...', e)
                    time.sleep(3)

                except socket.error as e:
                    
                    self.tcp_connected = False
                    self.rs485_connected = False
                    logger.info(f'Trying to connect.', e)

                except Exception:
                    
                    self.tcp_connected = False
                    self.rs485_connected = False
                    logger.info('Trying to connect...', e)

                else:
                    
                    self.tcp_connected = True
                    logger.info(f'Drive {self.DRIVE_NAME} connected to {self.BBB_HOSTNAME} on port {self.RS458_TCP_PORT}.')
                    s.shutdown(socket.SHUT_RDWR)
                    s.close()
                    return True


    def drive_connect(self) -> True:
        """Drive connect.
        Keeps trying to connect to drive (rs485 level with provided
        drive address) untill it succeed, then returns True.
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
                        logger.info(f'Soft driver {self.DRIVE_NAME} connected do ecodrive address {self.ADDRESS}')
                        return True

    #@timer # prints the execution time of the function
    def tcp_read_parameter(self, message: str, change_drive: bool = True) -> str:

        with self._lock:

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                
                s.settimeout(EcoDrive._SOCKET_TIMEOUT)

                while True:
                    try:
                        s.connect((self.BBB_HOSTNAME, self.RS458_TCP_PORT))
                        break

                    except Exception as e:
                        logger.error('Communication error.', e)
                        self.tcp_wait_connection()
                        self.drive_connect()

                if change_drive:
                    
                    s.sendall(f'BCD:{self.ADDRESS}\r'.encode())
                    data: str = ''
                
                    while True:
                        try:
                            chunk = s.recv(16)
                            if not chunk or chunk.decode()[-1]=='>':
                                data += chunk.decode()
                                break
                            else: data += chunk.decode()
                        
                        except Exception:
                            if not data:
                                logger.exception('Communication error.')
                                return
                        
                s.sendall(f'{message}\r'.encode())
                data: str = ''

                while True:
                    try:
                        chunk = s.recv(16)
                        if not chunk or chunk.decode()[-1]=='>' or chunk.decode()[-1]=='?':
                            data += chunk.decode()
                            break
                        else: data += chunk.decode()
                    
                    except Exception:
                        if not data:
                            logger.exception('Communicatio error')
                            return
                            

            if change_drive: time.sleep(.007) # makes significant difference
            return data.encode()
        
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
            #self.tcp_read_parameter('S-0-0099,7,W,00', False)
            self.tcp_read_parameter('S-0-0127,7,W,11', False)
            self.tcp_read_parameter('S-0-0127,7,W,00', False)
            self.tcp_read_parameter('S-0-0128,7,W,11', False)
            self.tcp_read_parameter('S-0-0128,7,W,00', False)


################### MODULE TESTING ##################
if __name__ == '__main__':
    eco_test = EcoDrive(address=21, min_limit=_cte.minimum_gap, max_limit=_cte.maximum_gap, drive_name='Teste')
    for i in range(10):
        print(eco_test.get_resolver_position())
        print(eco_test.get_max_velocity())
        print(eco_test.get_halten_status())
