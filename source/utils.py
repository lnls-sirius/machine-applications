import sched
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
