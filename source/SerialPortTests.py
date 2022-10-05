from urllib.request import install_opener
import serial, time, threading, yaml, socket
import threading
import globals

# Quando for implementada a leitura do encoder externo, criar um método para calcular o desvio entre ele e o resolver
# AFTER A E-STOP BECOME DESACTIVATED, THE EXTERNAL ENABLE INPUT MUST RECIEVE A 0-1 EDGE. 

print(globals.min_gap)

class EcoDrive:
    '''Indramat ecodrive 3 class for RS232 communication using ASCII protocol,
        based on functional description SMT-02VRS'''

    def __init__(self, address, serial_port="/dev/ttyUSB0", baud_rate=19200, max_limit=0, min_limit=10):
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
                self.ser.connect = True
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
        with open('drive_messages.yaml', 'r') as f:
            diag_messages = yaml.safe_load(f)['diagnostic_messages']
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
        '''Set drive target position. Returned values:
        0 -> target position out of limits
        -1 -> erro no envio do comando de escrita;
        -2 -> erro na resposta de confirmação de escrita - target position not in answer message;
        -3 -> erro na confirmação do endereço -> drive address not in answer message.
        -4 -> serial port is closed
        -5 -> drive not connected, use connect() to solve this.'''

        if not self.ser.is_open: return -4
        if not self.ser.connect: return -5

        if self.verify_limits(target):
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
        else: return(0)
    
    def get_target_position(self):
        drive_teste.send('P-0-4006,7,R')
        tmp = self.raw_read().decode().replace('\r', '').split('\n')
        if len(tmp) >= 2:
            return float(tmp[1])
        else: return False



class Epu():
    def __init__(self, a_address, b_address, min_gap, max_gap, min_phase, max_phase):
        self.a_drive = EcoDrive(address=a_address, min_limit=min_gap,\
            max_limit=max_gap)
        self.b_drive = EcoDrive(address=b_address, min_limit=min_gap,\
            max_limit=max_gap)
        self.i_drive = EcoDrive(address=a_address, min_limit=min_phase,\
            max_limit=max_gap)
        self.s_drive = EcoDrive(address=b_address, min_limit=min_phase,\
            max_limit=max_gap)
        
        self.min_gap = min_gap
        self.max_gap = max_gap
        self.min_phase = min_phase
        self.max_phase = max_phase

    def verify_gap_limits(self, t_gap) -> bool:
        if self.min_gap <= t_gap <= self.max_gap: return True
        else: return False
    
    def verify_phase_limits(self, t_phase) -> bool:
        if self.min_phase <= t_phase <= self.max_phase: return True
        else: return False

    def set_gap(self, target_gap):
        if self.verify_gap_limits(target_gap):
            self.a_drive.set_target_position(target_gap)
            self.b_drive.set_target_position(target_gap)
            if target_gap == self.a_drive.get_target_position():
                if target_gap == self.b_drive.get_target_position(): # Put a nested if insted of a logic and for easier debugging.
                    return 1
                else: return -1
            else: return -2
        else: return -3

    def set_phase(self, target_phase):
        if self.verify_phase_limits(target_phase):
            self.i_drive.set_target_position(target_phase)
            self.s_drive.set_target_position(target_phase)
            if target_phase == self.i_drive.get_target_position():
                if target_phase == self.s_drive.get_target_position(): # Put a nested if insted of a logic and for easier debugging.
                    return 1
                else: return -1
            else: return -2
        else: return -3

    def set_counter_phase(self, target_phase):
        if self.verify_phase_limits(target_phase):
            self.i_drive.set_target_position(-target_phase)  # see pacmon source code line 1124
            self.s_drive.set_target_position(target_phase)
            if (target_phase * (-1)) == self.i_drive.get_target_position():
                if target_phase == self.s_drive.get_target_position(): # Put a nested if insted of a logic and for easier debugging.
                    return 1
                else: return -1
            else: return -2
        else: return -3

    def start(self):
        pass
    def free_halt(self):
        pass
    def enable(self):
        pass


#teste = Epu(a_address=globals.drive_A_address, b_address=globals.drive_B_address,\
#        min_gap=globals.min_gap, max_gap=globals.max_gap, min_phase=globals.min_phase, max_phase=globals.max_phase)


eco_test = EcoDrive(address=21, serial_port="/dev/tty0")
eco_test.send('BCD:21')
print(eco_test.raw_read())


# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.connect(('10.1.2.156', 54321))
# sock.send(b'BCD:21')

# MSGLEN=10
# chunks = []
# bytes_recd = 0
# while bytes_recd < MSGLEN:
#     chunk = sock.recv(min(MSGLEN - bytes_recd, 2048))
#     if chunk == b'':
#         raise RuntimeError("socket connection broken")
#     chunks.append(chunk)
#     bytes_recd = bytes_recd + len(chunk)
#     print(b''.join(chunks))