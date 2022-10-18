'''AFTER AN E-STOP BECOME DESACTIVATED, THE EXTERNAL ENABLE INPUT MUST RECIEVE A 0-1 EDGE. '''
__all__ = ["EcoDrive"]
__author__ = "Rafael Cardoso e Andrei Pereira"
__version__ = "0.0.1"

from ast import Bytes
from concurrent.futures import thread
import threading
import serial, time, yaml, logging
import constants
from functools import wraps
from utils import *

# If desired, the code returned by EcoDrive.get_status() can be used as index to the diag_messages dictionary, which returns the diagnostic message.
with open('../config/drive_messages.yaml', 'r') as f:
    diag_messages = yaml.safe_load(f)['diagnostic_messages']

constants.BAUD_RATE

logger = logging.getLogger('__name__')
logging.basicConfig(filename='/tmp/EcoDrive.log', filemode='w', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

class EcoDrive():
    '''Indramat ecodrive 3 class for RS232 communication using ASCII protocol based on functional description SMT-02VRS'''

    def __init__(self, address, baud_rate, serial_port, max_limit, min_limit, ):
        self.SERIAL_PORT = serial_port
        self.SERIAL_ADDRESS = address
        self.BAUD_RATE = baud_rate
        self.UPPER_LIMIT = max_limit
        self.LOWER_LIMIT = min_limit
        self.MAX_RESOLVER_ENCODER_DIFF = False
        self.connected = False
        self._lock = threading.Lock()

        try:
            self.ser = serial.Serial(self.SERIAL_PORT, baudrate=self.BAUD_RATE, timeout=.3, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
        except ValueError as e:
            print(e)
            logger.exception(f'init(): Could not open serial port: {self.SERIAL_PORT}')
            return
        except serial.SerialException as e:
            print(e)
            logger.exception(f'init(): Could no open serial port: {self.SERIAL_PORT}')
            return


        self.connect()
        self.resolver_position = self.get_resolver_position()
        self.encoder_position = None
        self.diagnostic_code = self.get_diagnostic_code()
        self.halt_status = self.get_halten_status()[0]
        self.enable_status = self.get_halten_status()[1]
        self.target_position = self.get_target_position()
        self.target_position_reached = self.get_target_position_reached()
        self.update()

    @asynch
    @schedule(1)
    def update(self):
        '''Updates class attributes. If used with schedule(x) decorator, updates class attributes once every x seconds. With asynch decorator, runs on a separated thread.'''

        self.get_resolver_position()
        self.get_diagnostic_code()
        self.get_halten_status()
        self.get_halten_status()
        self.get_target_position()
        self.get_target_position_reached()

    def connect(self) -> None:
        if not self.ser.is_open:
            try:
                self.ser.open()
            except serial.SerialException as e:
                logger.exception('Could not open serial port.')
                raise e
        else:
            try:
                byte_message = self.send_and_read('BCD:{}'.format(self.SERIAL_ADDRESS))
            except Exception as e:
                logger.exception('Communication error in send_and_read.')
                raise e
            else:
                str_message = byte_message.decode().split()
                if not (f'E{self.SERIAL_ADDRESS}:>' in str_message[0]):
                    logger.error(f'Drive addres (E{self.SERIAL_ADDRESS}) was expcted in drive answer, but was not found.')
                    raise Exception(f'Drive addres (E{self.SERIAL_ADDRESS}) was expcted in drive answer, but was not found.')
                else:
                    self.connected = True
                    return

    def disconnect(self) -> None:
        self.ser.is_open
        self.ser.close()
        self.connected = False
        return

    def send(self, message: str) -> None:
        'Send message to serial device. Returns None, raises SerialTimeoutException, SerialException or Exception.'
        if self.ser.is_open:
            self.ser.reset_input_buffer()
            try:
                self.ser.write('{}\r\n'.format(message).encode())
            except serial.SerialTimeoutException as e:
                logging.exception('Timeout when sending command to serial port.')
                raise e
            except serial.SerialException() as e:
                logging.exception('An exception ocurrerd while trying to send data to serial port.')
                raise e
            else:
                time.sleep(.5) # magic number!!!!
                return

        else:
            logging.error('Serial closed while trying to send message.')
            raise Exception('Serial port not open.')

    def send_and_read(self, message: str) -> Bytes:
        with self._lock:
            self.send(message)
            byte_encoded_message = self.raw_read()
        return byte_encoded_message

    def raw_read(self) -> Bytes:
        if self.ser.in_waiting:
            try:
                tmp = self.ser.read(self.ser.in_waiting)
            except serial.SerialException:
                logger.exception('raw_read(): serial port is probably closed.')
                raise Exception('Could not read, serial port is probably closed.')
            else:
                self.ser.reset_input_buffer()
                return tmp
        else: return b''

    def get_resolver_position(self) -> float:
        '''Get sresolver reading. Raises AssertError if it answer don't match expected pattern.'''
        try:
            byte_message = self.send_and_read('S-0-0051,7,R')
        except Exception as e:
            logger.exception('Communication error in send_and_read.')
            raise e
        else:
            str_message = byte_message.decode()
            if not (f'E{self.SERIAL_ADDRESS}:>' in str_message and 'S-0-0051,7,R' in str_message):
                logger.error('Drive did not repond as expeted to "S-0-0051,7,R".', f'{str_message}')
                raise Exception('Drive did not repond as expeted to "S-0-0051,7,R".', f'{str_message}')
            resolver_position = str_message.split('\r\n')[1]
            self.resolver_position = resolver_position
            print("get_resolver_position was called")
            return float(resolver_position)

    def get_diagnostic_code(self) -> str:
        '''Gets the diagnostic message code of the drive. the same code can be seen in the seven segment display. Raises AssertError if it answer don't match expected pattern.'''
        try:
            byte_message = self.send_and_read('S-0-0390,7,R')
        except Exception as e:
            logger.exception('Communication error in send_and_read.')
            raise e
        else:
            str_message = byte_message.decode()
            if not (f'E{self.SERIAL_ADDRESS}:>' in str_message and 'S-0-0390,7,R' in str_message):
                logger.error('Drive did not repond as expeted to "S-0-0390,7,R".', f'{str_message}')
                raise Exception('Drive did not repond as expeted to "S-0-0390,7,R".', f'{str_message}')
            else:
                # Crie uma lista com todos os códigos possíveis e então coloque um assert para verificar se o código lido está na lista.
                _d_code = str_message.split('\r\n')[1]
                self.diagnostic_code = _d_code
                return _d_code

    # Uma dúvida (p. 232 func. desc.): para liberar o freio são necessárias duas coisas, bit 13 igual a 1 na master control word & entrada analógica igual alta?
    def get_halten_status(self) -> tuple:
        '''Returns a tuple with Drive Halt and Drive Enable functions status: (halt, enable); 1 for enable, 0 for disable.'''
        try:
            byte_message = self.send_and_read('S-0-0134,7,R')
        except Exception as e:
            logger.exception('Communication error in send_and_read.')
            raise e
        else:
            str_message = byte_message.decode()
            if not (f'E{self.SERIAL_ADDRESS}:>' in str_message and 'S-0-0134,7,R' in str_message):
                logger.error('Drive did not repond as expeted to "S-0-0134,7,R".', f'{str_message}')
                raise Exception('Drive did not repond as expeted to "S-0-0134,7,R".', f'{str_message}')
            else:
                try:
                    drive_halt_status = int(str_message.split('\r\n')[1][13])
                except ValueError as e:
                    logger.exception('Error while evaluating drive halt status bit.')
                    raise e
                else:
                    try:
                        drive_enable_status = int(str_message.split('\r\n')[1][14])
                    except ValueError as e:
                        logger.exception('Error while evaluating drive halt status bit.')
                        raise e
                    else:
                        self.halt_status, self.enable_status = (drive_halt_status, drive_enable_status)
                        return(drive_halt_status, drive_enable_status)

    def get_target_position_reached(self) -> int:
        '''The message 'target position reached' is defined as a bit in the class 3 diagnostics. It is set when the position command value S-0-0047 given by the drive internal interpolator is equal to the target position S-0-0258.'''
        try:
            byte_message = self.send_and_read('S-0-0342,7,R')
        except Exception as e:
            logger.exception('Communication error in send_and_read.')
            raise e
        else:
            str_message = byte_message.decode()
            if not ('S-0-0342,7,R' in str_message):
                logger.error('Drive did not respond as axpected to "S-0-0342,7,R".')
                raise Exception('Drive did not respond as axpected to "S-0-0342,7,R".')
            else:
                targ_pos_reached_bit = str_message.split('\r\n')[1][0]
                if not (targ_pos_reached_bit == '0' or targ_pos_reached_bit == '1'):
                    logger.error('Drive did not respond as axpected: targ_pos_reached bit is not 0 neither 1')
                    raise Exception('Drive did not respond as axpected: targ_pos_reached bit is not 0 neither 1')
                self.target_position_reached = targ_pos_reached_bit
                return int(targ_pos_reached_bit)

    def set_target_position(self, target_position: float) -> float:
        '''Set drive target position.'''
        if not (self.LOWER_LIMIT <= target_position <= self.UPPER_LIMIT): raise ValueError('Target position out of limits.')
        else:
            try:
                byte_message = self.send_and_read('P-0-4006,7,W,>')
            except Exception as e:
                logger.exception('Communication error in send_and_read.')
                raise e
            else:
                str_message = byte_message.decode()
                if not 'P-0-4006,7,W,>' in str_message:
                    logger.error('Drive did not respond as axpected to "P-0-4006,7,W,>" request.')
                    raise Exception('Drive did not respond as axpected to "P-0-4006,7,W,>" request.')
                else:
                    try:
                        byte_message = self.send_and_read(f'{target_position}')
                    except Exception as e:
                        logger.exception('Communication error in send_and_read.')
                        raise e
                    else:
                        str_target_position_readback = byte_message.decode()
                        if not f'{target_position}' in str_target_position_readback:
                            logger.error('Intended target position not found in drive answer.')
                            raise Exception('Intended target position not found in drive answer.')
                        else:
                            try:
                                byte_message = self.send_and_read('<')
                            except Exception as e:
                                logger.exception('Communication error in send_and_read.')
                                raise e
                            else:
                                self.send('<')
                                str_message = self.raw_read().decode()
                                if not f'E{self.SERIAL_ADDRESS}' in str_message:
                                    logger.error(f'Drive addres (E{self.SERIAL_ADDRESS}) was expcted in drive answer, but was not found.')
                                    raise Exception(f'Drive addres (E{self.SERIAL_ADDRESS}) was expcted in drive answer, but was not found.')
                                else:
                                    target_position = float(str_target_position_readback.split('\r')[0])
                                    return target_position

    def get_target_position(self):
        try:
            byte_message = self.send_and_read('P-0-4006,7,R')
        except Exception as e:
            logger.exception('Communication error in send_and_read.')
            raise e
        else:
            str_message = byte_message.decode().replace('\r', '').split('\n')
            try:
                target_position = float(str_message[1])
            except ValueError as e:
                logger.exception('Error while trying to convert target position value received from drive.')
                raise e
            else:
                self.target_position = target_position
                return target_position

    def start(self):
        pass

    def halt(self):
        pass

if __name__ == '__main__':
    eco_test = EcoDrive(address='21', baud_rate=constants.BAUD_RATE, max_limit=constants.MAXIMUM_GAP, min_limit=constants.MINIMUN_GAP, serial_port="/dev/pts/3")
    while True:
        time.sleep(2)
        print(eco_test.diagnostic_code)
        print(eco_test.target_position)
        # print(eco_test.diagnostic_code())