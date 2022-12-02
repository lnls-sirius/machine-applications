from urllib.request import install_opener
import serial, time, threading, yaml
from pcaspy import SimpleServer, Driver
import constants

# Quando for implementada a leitura do encoder externo, criar um método para calcular o desvio entre ele e o resolver
# AFTER A E-STOP BECOME DESACTIVATED, THE EXTERNAL ENABLE INPUT MUST RECIEVE A 0-1 EDGE. 

# Passar isso para TOML
port="/dev/ttyUSB0"

with open('drive_messages.yaml', 'r') as f:
    diag_messages = yaml.safe_load(f)['diagnostic_messages']
    '''Indramat ecodrive 3 class for RS232 communication using ASCII protocol,
        based on functional description SMT-02VRS'''

    def __init__(self, serial_port, address, baud_rate, max_limit=300, min_limit=22):
        self.port = serial_port
        self.address = address
        self.baud_rate = baud_rate
        self.max_limit = max_limit
        self.min_limit = min_limit
        self.connected = False
        # Change serial port opening to a method.
        self.ser = serial.Serial(self.port, baudrate=self.baud_rate, timeout=.3,\
            parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)

    def verify_limits(self, set_point) -> bool:
        if self.min_limit <= set_point <= self.max_limit: return True
        else: return False

    def connect(self) -> bool:
        if self.ser.is_open:
            self.send('BCD:{}'.format(self.address)) # treat exceptions (implement exception to send())
            if self.ser.readline() == 'E' + self.address + ':>': # Maybe treat readline() with try/exception was a good idia.
                return(True)
            else:
                return(False)
        else:
            try: 
                self.ser.open()  # Change this: verify if the port is open by self.ser or another object.
            except serial.SerialException:
                print('Serial is open by another object.')
                return(False)
            self.send('BCD:{}'.format(self.address)) # treat exceptions (implement exception to send())
            time.sleep(.1)
            if self.ser.readline() == 'E' + self.address + ':>': # Maybe treat readline() with try/exception was a good idia.
                return(True)
            else:
                return(False)
            
    def disconnect(self) -> bool:
        try:
            if self.ser.is_open:
                self.ser.close()
                return(True)
            else:
                return(-1)
        except serial.SerialException:
            return(-2)

    def send(self, message) -> None:
        self.ser.reset_input_buffer()
        self.ser.write('{}\r\n'.format(message).encode())
        time.sleep(.05)

    def raw_read(self): # If it returns \r, then is necessary to eliminate "\r" to return
        if self.ser.in_waiting:
            tmp = self.ser.read(self.ser.in_waiting)
            self.ser.reset_input_buffer()
            return tmp
        else:
            return False

    def read(self) -> str: # If it returns \r, then is necessary to eliminate "\r" to return
        return self.ser.readline().decode()

    def resolver_position(self) -> str:
        '''Get current position of motor encoder. The initialization of the position feedback happens
        during the execution of S-0-0128, C200 Communication phase 4 transition check; that means, the
        feedback positions are only initialized after successful execution of the command. If an absolute
        encoder is present, the value in S-0-0051, Position Feedback 1 Value then shows the absolute
        position referred to the machine's zero-point, provided that during the initial start-up the
        command P-0-0012, C300 Command 'Set absolute measurement' has been executed once. Otherwise, the
        initialization value depends on whether the parameter P-0- 0019, Position start value has been
        written to during the phase progression or whether the motor feedback is an absolute encoder.'''

        self.send(message='S-0-0051,7,R')
        time.sleep(.1)
        tmp = self.raw_read().decode()
        if f'E{self.address}:>' in tmp and 'S-0-0051,7,R' in tmp: return float(tmp.split('\r\n')[1])
        else: return False
    
    def diagnostic_message(self) -> str:
        '''In the parameter Diagnostic message number (S-0-0390), the same number is 
        stored as can be seen in the seven segment display.'''

        self.send('S-0-0390,7,R')
        time.sleep(.1)
        tmp = self.raw_read().decode()
        if f'E{self.address}:>' in tmp and 'S-0-0390,7,R' in tmp: return tmp.split('\r\n')[1]
        else: return False

    def get_halten_status(self) -> tuple:
        '''Returns a tuple with halt and enable status:
        (halt, enable); 1 for enable, 0 for disable.'''

        self.send('S-0-0134,7,R')
        time.sleep(.1)
        tmp = self.raw_read().decode()
        if f'E{self.address}:>' in tmp and 'S-0-0134,7,R' in tmp: return (tmp.split('\r\n')[1][13], tmp.split('\r\n')[1][14])
        else: return False

    def target_position_reached(self) -> int:
        '''The message 'target position reached' is defined as a bit in the class 3 diagnostics.
        It is set when the position command value S-0-0047 given by the drive internal interpolator
        is equal to the target position S-0-0258.'''

        self.send('S-0-0342,7,R')
        tmp = self.raw_read().decode()
        if 'S-0-0342,7,R' in tmp: return int(tmp.split('\r\n')[1][0])
        else: return False

    def set_target_position(self, target):
        '''List of the target positions for the block operated function (positioning interface).'''

        self.send('P-0-4006,7,W,>')
        if 'P-0-4006,7,W,>' in self.raw_read().decode():
            self.send(f'{target}')
            tmp = self.raw_read().decode()
            if f'{target}' in tmp:
                self.send('<')
                if f'E{self.address}' in self.raw_read().decode():
                    return float(tmp.split('\r')[0])
                else: return(-3)
            else: return(-2)
        else: return(-1)
    
    def get_target_position(self):
        drive_teste.send('P-0-4006,7,R')
        tmp = self.raw_read().decode().replace('\r', '').split('\n')
        if len(tmp) >= 2:
            return float(tmp[1])
        else: return False

class EcoDrive(Driver):
    '''Indramat ecodrive 3 class for RS232 communication using ASCII protocol,
        based on functional description SMT-02VRS'''

    def __init__(self, address, serial_port="/dev/ttyUSB0", baud_rate=19200, max_limit=300, min_limit=22):
        super(EcoDrive, self).__init__()
        self.port = serial_port
        self.address = address
        self.baud_rate = baud_rate
        self.max_limit = max_limit
        self.min_limit = min_limit
        self.connected = False
        # Change serial port opening to a method.
        self.ser = serial.Serial(self.port, baudrate=self.baud_rate, timeout=.3,\
            parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)

    def verify_limits(self, set_point) -> bool:
        if self.min_limit <= set_point <= self.max_limit: return True
        else: return False

    def connect(self) -> bool:
        if self.ser.is_open:
            self.send('BCD:{}'.format(self.address)) # treat exceptions (implement exception to send())
            if self.ser.readline() == 'E' + self.address + ':>': # Maybe treat readline() with try/exception was a good idia.
                return(True)
            else:
                return(False)
        else:
            try: 
                self.ser.open()  # Change this: verify if the port is open by self.ser or another object.
            except serial.SerialException:
                print('Serial is open by another object.')
                return(False)
            self.send('BCD:{}'.format(self.address)) # treat exceptions (implement exception to send())
            time.sleep(.1)
            if self.ser.readline() == 'E' + self.address + ':>': # Maybe treat readline() with try/exception was a good idia.
                return(True)
            else:
                return(False)
            
    def disconnect(self) -> bool:
        try:
            if self.ser.is_open:
                self.ser.close()
                return(True)
            else:
                return(-1)
        except serial.SerialException:
            return(-2)

    def send(self, message) -> None:
        self.ser.reset_input_buffer()
        self.ser.write('{}\r\n'.format(message).encode())
        time.sleep(.05)

    def raw_read(self): # If it returns \r, then is necessary to eliminate "\r" to return
        if self.ser.in_waiting:
            tmp = self.ser.read(self.ser.in_waiting)
            self.ser.reset_input_buffer()
            return tmp
        else:
            return False

    def read(self) -> str: # If it returns \r, then is necessary to eliminate "\r" to return
        return self.ser.readline().decode()

    def resolver_position(self) -> str:
        '''Get current position of motor encoder. The initialization of the position feedback happens
        during the execution of S-0-0128, C200 Communication phase 4 transition check; that means, the
        feedback positions are only initialized after successful execution of the command. If an absolute
        encoder is present, the value in S-0-0051, Position Feedback 1 Value then shows the absolute
        position referred to the machine's zero-point, provided that during the initial start-up the
        command P-0-0012, C300 Command 'Set absolute measurement' has been executed once. Otherwise, the
        initialization value depends on whether the parameter P-0- 0019, Position start value has been
        written to during the phase progression or whether the motor feedback is an absolute encoder.'''

        self.send(message='S-0-0051,7,R')
        time.sleep(.1)
        tmp = self.raw_read().decode()
        if f'E{self.address}:>' in tmp and 'S-0-0051,7,R' in tmp: return float(tmp.split('\r\n')[1])
        else: return False
    
    def diagnostic_message(self) -> str:
        '''In the parameter Diagnostic message number (S-0-0390), the same number is 
        stored as can be seen in the seven segment display.'''

        self.send('S-0-0390,7,R')
        time.sleep(.1)
        tmp = self.raw_read().decode()
        if f'E{self.address}:>' in tmp and 'S-0-0390,7,R' in tmp: return tmp.split('\r\n')[1]
        else: return False

    def get_halten_status(self) -> tuple:
        '''Returns a tuple with halt and enable status:
        (halt, enable); 1 for enable, 0 for disable.'''

        self.send('S-0-0134,7,R')
        time.sleep(.1)
        tmp = self.raw_read().decode()
        if f'E{self.address}:>' in tmp and 'S-0-0134,7,R' in tmp: return (tmp.split('\r\n')[1][13], tmp.split('\r\n')[1][14])
        else: return False

    def target_position_reached(self) -> int:
        '''The message 'target position reached' is defined as a bit in the class 3 diagnostics.
        It is set when the position command value S-0-0047 given by the drive internal interpolator
        is equal to the target position S-0-0258.'''

        self.send('S-0-0342,7,R')
        tmp = self.raw_read().decode()
        if 'S-0-0342,7,R' in tmp: return int(tmp.split('\r\n')[1][0])
        else: return False

    def set_target_position(self, target):
        '''List of the target positions for the block operated function (positioning interface).'''

        self.send('P-0-4006,7,W,>')
        if 'P-0-4006,7,W,>' in self.raw_read().decode():
            self.send(f'{target}')
            tmp = self.raw_read().decode()
            if f'{target}' in tmp:
                self.send('<')
                if f'E{self.address}' in self.raw_read().decode():
                    return float(tmp.split('\r')[0])
                else: return(-3)
            else: return(-2)
        else: return(-1)
    
    def get_target_position(self):
        drive_teste.send('P-0-4006,7,R')
        tmp = self.raw_read().decode().replace('\r', '').split('\n')
        if len(tmp) >= 2:
            return float(tmp[1])
        else: return False

    def read(self, reason):
        if reason == 'Resolver-Mon': value = self.resolver_position()
        else: value = self.getParam(reason)
        return value

# --------------

prefix = 'Ecodrive:'
pvdb = {
    'Resolver-Mon' : {
        'prec' : 3,
    },
}

if __name__ == '__main__':
    server = SimpleServer()

server.createPV(prefix, pvdb)
driver = EcoDrive(serial_port=port, address=constants.drive_A_address, baud_rate=constants.baud_rate)

while True:
    # process CA transactions
    server.process(0.1)

