import sched, time
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
