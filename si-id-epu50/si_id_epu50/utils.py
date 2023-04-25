import sched
import time
import struct
from functools import wraps
from threading import Thread
import socket
import logging
import logging.handlers

from . import constants as _cte

class DriveCOMError(Exception):
    "Raised when the drive does not respond as expected to a command."
    pass

def run_periodically_in_detached_thread(interval):
    """
    Decorator to run a function periodically in a separate thread detached from terminal.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Define the target function to be executed in a thread
            def target():
                while True:
                    func(*args, **kwargs)
                    time.sleep(interval)

            # Create a new daemon thread without a terminal
            daemon_thread = Thread(target=target, daemon=True)
            daemon_thread.start()

        return wrapper

    return decorator

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
        func_hl = Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        func_hl.start()
        return func_hl
    return async_func


#######################https://realpython.com/primer-on-python-decorators/ ##########################


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


############################################ BSMP stuff ############################################


def verify_checksum(list_values):
    counter = 0
    for data in list_values:
        counter += data 
    counter = (counter & 255)
    return(counter)


########## get from https://github.com/cnpem-sei/epu-interface-sw/blob/master/epusocket.py ##########


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
    if size == 1:
        send_message = send_message + [value]
    elif size == 2:
        send_message = send_message + [c for c in struct.pack("!h", value)]
    elif size == 4:
        send_message = send_message + [c for c in struct.pack("!I", value)]
    return("".join(map(chr, include_checksum(send_message))))


################################## Functions to control BBB GPIOs ####################################


def set_gap_en(val):

    bsmp_enable_message = bsmp_send(_cte.BSMP_WRITE, variableID=_cte.ENABLE_CH_AB, value=val).encode()
                        
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(.1)
        s.connect(('10.128.110.160', 5050))
        s.sendall(bsmp_enable_message)
        time.sleep(.01) # magic number

        while True:
            data = s.recv(16)
            if not data: break
            return data


def set_phase_en(val):
    
    bsmp_enable_message = bsmp_send(_cte.BSMP_WRITE, variableID=_cte.ENABLE_CH_SI, value=val).encode()
                        
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(.1)
        s.connect(('10.128.110.160', 5050))
        s.sendall(bsmp_enable_message)
        time.sleep(.01) # magic number

        while True:
            data = s.recv(16)
            if not data: break
            return data


def set_gap_start(val):
    
    bsmp_enable_message = bsmp_send(_cte.BSMP_WRITE, variableID=_cte.START_CH_AB, value=val).encode()
                        
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(.1)
        s.connect(('10.128.110.160', 5050))
        s.sendall(bsmp_enable_message)
        time.sleep(.01) # magic number

        while True:
            data = s.recv(16)
            if not data: break
            return data


def set_gap_hal(val):
    
    bsmp_enable_message = bsmp_send(_cte.BSMP_WRITE, variableID=_cte.HALT_CH_AB, value=val).encode()
                        
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(.1)
        s.connect(('10.128.110.160', 5050))
        s.sendall(bsmp_enable_message)
        time.sleep(.01) # magic number

        while True:
            data = s.recv(16)
            if not data: break
            return data


def get_phase_hal(val):
    
    bsmp_enable_message = bsmp_send(_cte.BSMP_READ, variableID=_cte.HALT_CH_SI, value=val).encode()
                        
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(.1)
        s.connect(('10.128.110.160', 5050))
        s.sendall(bsmp_enable_message)
        time.sleep(.001) # magic number

        while True:
            data = s.recv(16)
            if not data: break
            return data


def set_phase_start(val):
    
    bsmp_enable_message = bsmp_send(_cte.BSMP_WRITE, variableID=_cte.START_CH_SI, value=val).encode()
                        
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(.1)
        s.connect(('10.128.110.160', 5050))
        s.sendall(bsmp_enable_message)
        time.sleep(.01) # magic number

        while True:
            data = s.recv(16)
            if not data: break
            return data

FORMATTER = logging.Formatter(
    "%(asctime)s | [%(levelname)s] %(name)s [%(module)s.%(funcName)s:%(lineno)d]: %(message)s")
LOG_FILE = "si_id_epu50.log"


def get_file_handler(file: str):
    # logger.handlers.clear()
    fh = logging.handlers.RotatingFileHandler(
        file, maxBytes=1000000, backupCount=10)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s"))
    return fh


def get_logger(name, file_handler):
    lg = logging.getLogger(name)
    lg.setLevel(logging.INFO)
    lg.addHandler(file_handler)
    return lg