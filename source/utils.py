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
######################################################################################################

