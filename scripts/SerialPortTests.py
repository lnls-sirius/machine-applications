from urllib.request import install_opener
import serial
import time

#Pertinent parameters:
#P-0-4021, Baud rate RS-232/485
#P-0-4022, Drive address - 256 for use the address set via the address switch. Not necessary for RS232
#P-0-4050, Delay answer RS-232/485
#Aguardar 40 ms para uma leitura após solicitado.

drive_address='21'
baude_rate = 19200
port="/dev/ttyUSB0"

class EcoDrive:
    '''Indramat ecodrive 3 class for RS232 communication using ASCII protocol,
        based on functional description SMT-02VRS'''

    def __init__(self, port, address, brate):
        self.port = port
        self.address = address
        self.brate = brate
        self.connected = False
        self.ser = serial.Serial(self.port, baudrate=self.brate, timeout=1,\
            parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)


    def connect(self):
        if not self.ser.is_open:
            try: 
                self.ser.open()  # Change this: verify if the port is open by self.ser or another object.
            except serial.SerialException:
                print('Serial is open by another object.')
                return(False)
        else:
            self.send('BCD:{}'.format(self.address))
            time.sleep(.4)
            if self.ser.readline() == 'E' + self.address + ':>': # Maybe treat readline() with try/exception was a good idia.
                return(True)
            else:
                return(False)
    
    def disconnect(self):
        try:
            if self.ser.is_open():
                self.ser.close()
                return(0)
            else:
                print("Already disconnected.")
                return(None)
        except:
            print("Error on disconnect.")
            return(None)

    def send(self, message):
        self.ser.write('{}\r\n'.format(message).encode())

    def read(self): # If it returns \r, then is necessary to eliminate "\r" to return
        return self.ser.readline()

    def get_position(self):
        '''Get current position of motor encoder. The initialization of the position feedback happens
        during the execution of S-0-0128, C200 Communication phase 4 transition check; that means, the
        feedback positions are only initialized after successful execution of the command. If an absolute
        encoder is present, the value in S-0-0051, Position Feedback 1 Value then shows the absolute
        position referred to the machine's zero-point, provided that during the initial start-up the
        command P-0-0012, C300 Command 'Set absolute measurement' has been executed once. Otherwise, the
        initialization value depends on whether the parameter P-0- 0019, Position start value has been
        written to during the phase progression or whether the motor feedback is an absolute encoder.'''
        self.ser.write(message='S-0-0051,7,R')
    
    def get_drive_status(self):
        '''In the parameter Diagnostic message number (S-0-0390), the same number is 
        stored as can be seen in the seven segment display.'''

        messages = {0: 'P0', 1: 'P1', 2: 'P2', 3: 'P3', 10: 'AH', 12: 'Ab', \
            13: 'bb', 18: 'Jb', 208: 'JF', 211: 'AF', 400: 'AC', }

        self.send('S-0-0390,7,R')
        time.sleep(.6)
        tmp = self.read()
        if tmp != 'E22:>S-0-0390,7,R':
            return(tmp)
        else:
            
        




drive_teste = EcoDrive(brate=baude_rate, address=drive_address, port="/dev/ttyUSB0")
drive_teste.connect()
drive_teste.send("S-0-0051,7,R")
# print(drive_teste.read(40))


print('end of file')