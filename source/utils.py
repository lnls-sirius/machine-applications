import sched, time, struct
from functools import wraps
from threading import Thread

def schedule(interval):
    def decorator(func):
        def periodic(scheduler, interval, action, actionargs=(), kwargs ={}):
            scheduler.enter(interval, 1, periodic,
                            (scheduler, interval, action, actionargs, kwargs))
            action(*actionargs, **kwargs)
        @wraps(func)
        def wrap(*args, **kwargs):
            scheduler = sched.scheduler()
            periodic(scheduler, interval, func, args, kwargs)
            scheduler.run()
        return wrap
    return decorator

def asynch(func):
    @wraps(func)
    def async_func(*args, **kwargs):
        func_hl = Thread(target=func, args=args, kwargs=kwargs)
        func_hl.start()
        return func_hl
    return async_func

#https://realpython.com/primer-on-python-decorators/
def timer(func):
    """Print the runtime of the decorated function"""
    @wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer

############# BSMP stuff ##################
def verify_checksum(list_values):
    counter = 0
    for data in list_values:
        counter += data 
    counter = (counter & 255)
    return(counter)
# get from https://github.com/cnpem-sei/epu-interface-sw/blob/master/epusocket.py
def include_checksum(list_values):
    counter = 0
    i = 0
    while (i < len(list_values)):
        counter += list_values[i]
        i += 1
    counter = (counter & 0xFF)
    counter = (256 - counter) & 0xFF
    return(list_values + [counter])
def  bsmp_send(command_type, variableID = 0x00, value = 0x00, size = 1):
    send_message = [0x00, command_type] + [c for c in struct.pack("!h", size + 1)] + [variableID]
    print(send_message)
    if size == 1:
        send_message = send_message + [value]
    elif size == 2:
        send_message = send_message + [c for c in struct.pack("!h", value)]
    elif size == 4:
        send_message = send_message + [c for c in struct.pack("!I", value)]
    return("".join(map(chr, include_checksum(send_message))))
############################################




# SERIAL STUFF (ARCHIVE)
#def serial_send_and_read(self, message: str) -> Bytes:
#     with self._lock:
#         self.serial_send(message)
#         byte_encoded_message = self.serial_read()
#     return byte_encoded_message
# def serial_send(self, message: str) -> None:
#     '''Send message to serial device. Returns None,
#     raises SerialTimeoutException, SerialException or Exception.'''
#     if self.ser.is_open:
#         self.ser.reset_input_buffer()
#         try:
#             self.ser.write('{}\r\n'.format(message).encode())
#         except serial.SerialTimeoutException as e:
#             logging.exception(
#                 'Timeout when sending command to serial port.')
#             raise e
#         except serial.SerialException() as e:
#             logging.exception(
#                 'An exception ocurrerd while trying to send data to serial port.')
#             raise e
#         else:
#             time.sleep(.5) # magic number!!!!
#             return
#     else:
#         logging.error('Serial closed while trying to send message.')
#         raise Exception('Serial port not open.')
# def serial_connect(self):
#     while not self.connected:
#         try:
#             self.ser = serial.Serial(
#                 self.SERIAL_PORT, baudrate=self.BAUD_RATE,
#                 timeout=.3, parity=serial.PARITY_NONE,
#                 stopbits=serial.STOPBITS_ONE)
#         except ValueError as e:
#             print(e)
#             logger.exception(
#                 f'init(): Could not open serial port: {self.SERIAL_PORT}')
#             return
#         except serial.SerialException as e:
#             print(e)
#             logger.exception(
#                 f'init(): Could no open serial port: {self.SERIAL_PORT}')
#             return
#         else:
#             try:
#                 self.connect()
#                 logger.log(f'Drive {drive_name} connected!')
#                 print(f'Drive {drive_name} connected!')
#             except Exception:
#                 pass
# def serial_connect_BCD(self) -> None:
#     if not self.ser.is_open:
#         try:
#             self.ser.open()
#         except serial.SerialException as e:
#             logger.exception('Could not open serial port.')
#             raise e
#     else:
#         try:
#             byte_message = self.send_and_read(
#                 'BCD:{}'.format(self.SERIAL_ADDRESS))
#         except Exception as e:
#             logger.exception('Communication error in send_and_read.')
#             raise e
#         else:
#             str_message = byte_message.decode().split()
#             if not (f'E{self.SERIAL_ADDRESS}:>' in str_message[0]):
#                 logger.error(
#                     f'Drive addres (E{self.SERIAL_ADDRESS}) was expcted in drive answer, but was not found.')
#                 raise Exception(
#                     f'Drive addres (E{self.SERIAL_ADDRESS}) was expcted in drive answer, but was not found.')
#             else:
#                 self.connected = True
#                 return
# def serial_read(self) -> Bytes:
#     if self.ser.in_waiting:
#         try:
#             tmp = self.ser.read(self.ser.in_waiting)
#         except serial.SerialException:
#             logger.exception('raw_read(): serial port is probably closed.')
#             raise Exception('Could not read, serial port is probably closed.')
#         else:
#             self.ser.reset_input_buffer()
#             return tmp
#     else: return b''
