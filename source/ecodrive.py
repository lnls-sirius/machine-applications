import time, yaml, logging, threading, socket
from utils import *
import constants as _cte

logger = logging.getLogger('__name__')
logging.basicConfig(
    filename='./EcoDrive.log', filemode='w', level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S')

class EcoDrive():
    
    _SOCKET_TIMEOUT = .1
    _RS485_DELAY = 0.058
    _lock = threading.RLock()

    def __init__(
        self, address, max_limit=+25, min_limit=-25,
        bbb_hostname = _cte.beaglebone_addr, rs458_tcp_port=_cte.msg_port,
        drive_name = 'EcoDrive'
        ):
        self.ADDRESS = address
        self.UPPER_LIMIT = max_limit
        self.LOWER_LIMIT = min_limit
        self.DRIVE_NAME = drive_name
        self.soft_drive_message = ''
        self.BBB_HOSTNAME = bbb_hostname
        self.RS458_TCP_PORT = rs458_tcp_port
        self.test_connection()
        self.set_rs485_delay(1)

    def test_connection(self):
        found_bbb = False
        with self._lock:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                while not found_bbb:
                    try:
                        s.connect((self.BBB_HOSTNAME, self.RS458_TCP_PORT))
                    except ConnectionRefusedError:
                        logger.exception('ConnectionRefusedError')
                        self.soft_drive_message = f'Drive {self.DRIVE_NAME} ConnectionRefusedError'
                        #print(self.soft_drive_message)
                        time.sleep(.1)
                    except TimeoutError:
                        logger.exception('Could not connect to beagle bone: socket timeout.')
                        print('Could not connect to beagle bone: socket timeout.')
                    else:
                        self.soft_drive_message = f'Drive {self.DRIVE_NAME} connected.'
                        print(f'Drive {self.DRIVE_NAME} connected.')
                        found_bbb = True

    def connect(self) -> bool:
        with self._lock:
            try:
                byte_message = self.tcp_read_parameter(f'BCD:{self.ADDRESS}')
            except Exception:
                logger.exception('Communication error in tcp_read_parameter.')
            else:
                str_message = byte_message.decode().split()
                if not (f'E{self.ADDRESS}:>' in str_message[0]):
                    logger.error(
                            f'Drive addres (E{self.ADDRESS}) expected in drive answer, but was not found.')
                    return False
                else:
                    return True

    #@timer
    def tcp_read_parameter(self, message, change_drive=True) -> bytes:
        ''' change_drive parameter: change target rs485 drive.'''
        with self._lock:
            if change_drive:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(self._SOCKET_TIMEOUT)
                    s.connect((self.BBB_HOSTNAME, self.RS458_TCP_PORT))
                    s.sendall(f'BCD:{self.ADDRESS}\r\n'.encode())
                    time.sleep(.03) # .015
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self._SOCKET_TIMEOUT)
                s.connect((self.BBB_HOSTNAME, self.RS458_TCP_PORT))
                byte_message = f'{message}\r'.encode()
                s.sendall(byte_message)
                time.sleep(self._RS485_DELAY) # .047
                data = s.recv(64)
                # if not data: break
                return data

    def tcp_write_parameter(self, value):
        with self._lock:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self._SOCKET_TIMEOUT)
                s.connect((self.BBB_HOSTNAME, self.RS458_TCP_PORT))
                byte_message = f'{value}\r\n'.encode()
                s.sendall(byte_message)
                time.sleep(.05) # magic number!!!!
                while True:
                    data = s.recv(32)
                    if not data: break
                    return(data)

    def get_resolver_position(self, change_drive = True) -> float:
        return float(
            self.read_parameter_data('S-0-0051', change_drive=change_drive)
            )
    
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
        return float(
            self.read_parameter_data('S-0-0053', change_drive=change_drive)
            )

    def get_diagnostic_code(self) -> str:
        try:
            byte_message = self.tcp_read_parameter('S-0-0390,7,R')
        except Exception as e:
            logger.exception('Communication error in tcp_read_parameter().')
        else:
            str_message = byte_message.decode()
            if not f'E{self.ADDRESS}:>' in str_message:
                logger.error('Drive did not repond as expeted to "S-0-0390,7,R".', f'{str_message}')
                raise Exception('Drive did not repond as expeted to "S-0-0390,7,R".', f'{str_message}')
            else:
                _d_code = str_message.split('\r\n')[1][:-1]
                return _d_code

    def get_halten_status(self) -> tuple:
        try:
            byte_message = self.tcp_read_parameter('S-0-0134,7,R')
        except Exception as e:
            logger.exception('Communication error in tcp_read_parameter().')
        else:
            str_message = byte_message.decode()
            if not f'E{self.ADDRESS}:>' in str_message:
                logger.error(
                    'Drive did not repond as expeted to "S-0-0134,7,R".',
                    f'{str_message}'
                    )
                raise Exception(
                    'Drive did not repond as expeted to "S-0-0134,7,R".',
                    f'{str_message}'
                    )
            else:
                try:
                    drive_halt_status = int(str_message.split('\r\n')[1][13])
                except ValueError as e:
                    logger.exception('Error while evaluating drive halt status bit.')
                else:
                    try:
                        drive_enable_status = int(str_message.split('\r\n')[1][14])
                    except ValueError as e:
                        logger.exception('Error while evaluating drive halt status bit.')
                        raise e
                    else:
                        self.halt_status, self.enable_status = (drive_halt_status, drive_enable_status)
                        
                        return(drive_halt_status, drive_enable_status)

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
                        byte_message = self.tcp_write_parameter(f'{target_position}')
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
                                byte_message = self.tcp_write_parameter('<')
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
    eco_test = EcoDrive(
            address=21,
            min_limit=_cte.minimum_gap,
            max_limit=_cte.maximum_gap,
            drive_name='Teste')

#     time.sleep(1)
#     while True:
#         m = input(str("Mensagem: "))
#         #time.sleep(1)
#         print(eco_test.tcp_read_parameter(m))
