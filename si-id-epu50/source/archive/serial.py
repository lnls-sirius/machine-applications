
#SERIAL STUFF (ARCHIVE)

def serial_send_and_read(self, message: str) -> Bytes:
    with self._lock:
        self.serial_send(message)
        byte_encoded_message = self.serial_read()
    return byte_encoded_message
def serial_send(self, message: str) -> None:
    '''Send message to serial device. Returns None,
    raises SerialTimeoutException, SerialException or Exception.'''
    if self.ser.is_open:
        self.ser.reset_input_buffer()
        try:
            self.ser.write('{}\r\n'.format(message).encode())
        except serial.SerialTimeoutException as e:
            logging.exception(
                'Timeout when sending command to serial port.')
            raise e
        except serial.SerialException() as e:
            logging.exception(
                'An exception ocurrerd while trying to send data to serial port.')
            raise e
        else:
            time.sleep(.5) # magic number!!!!
            return
    else:
        logging.error('Serial closed while trying to send message.')
        raise Exception('Serial port not open.')

def serial_connect(self):
    while not self.connected:
        try:
            self.ser = serial.Serial(
                self.SERIAL_PORT, baudrate=self.BAUD_RATE,
                timeout=.3, parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE)
        except ValueError as e:
            print(e)
            logger.exception(
                f'init(): Could not open serial port: {self.SERIAL_PORT}')
            return
        except serial.SerialException as e:
            print(e)
            logger.exception(
                f'init(): Could no open serial port: {self.SERIAL_PORT}')
            return
        else:
            try:
                self.connect()
                logger.log(f'Drive {drive_name} connected!')
                print(f'Drive {drive_name} connected!')
            except Exception:
                pass

def serial_connect_BCD(self) -> None:
    if not self.ser.is_open:
        try:
            self.ser.open()
        except serial.SerialException as e:
            logger.exception('Could not open serial port.')
            raise e
    else:
        try:
            byte_message = self.send_and_read(
                'BCD:{}'.format(self.SERIAL_ADDRESS))
        except Exception as e:
            logger.exception('Communication error in send_and_read.')
            raise e
        else:
            str_message = byte_message.decode().split()
            if not (f'E{self.SERIAL_ADDRESS}:>' in str_message[0]):
                logger.error(
                    f'Drive addres (E{self.SERIAL_ADDRESS}) was expcted in drive answer, but was not found.')
                raise Exception(
                    f'Drive addres (E{self.SERIAL_ADDRESS}) was expcted in drive answer, but was not found.')
            else:
                self.connected = True
                return
                
def serial_read(self) -> Bytes:
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