from audioop import add
from curses import baudrate
import serial
#Pertinent parameters:
#P-0-4021, Baud rate RS-232/485
#P-0-4022, Drive address - 256 for use the address set via the address switch. Not necessary for RS232
#P-0-4050, Delay answer RS-232/485

drive_address=21
baude_rate = 19200
port="COM1"

class EcoDrive:
    '''Indramat ecodrive 3 class for RS232 communication using ASCII protocol, based on functional description SMT-02VRS'''

    def __init__(self, port, address, brate):
        self.port = port
        self.address = address
        self.brate = brate

    def connect(self):
        self.ser = serial.Serial(self.port, baudrate=self.brate, \
            parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
        self.write('BCD:{}'.format(self.address))

    def write(self, message):
        self.ser.write(b'{}\r\n'.format(message))

    def read(self, port):
        self.ser.read(10) # How many bytes?


drive_teste = EcoDrive(brate=baude_rate, address=drive_address)
drive_teste.write("")