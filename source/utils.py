import sched
import threading
import time
import functools

"""
From stackoverflow answer:
https://stackoverflow.com/questions/2398661/
schedule-a-repeating-event-in-python-3/48758861#48758861"""
def asynch(func):
    @functools.wraps(func)
    def asynch_func(*args, **kwargs):
        # func_hl = threading.Thread(target=func, args=args, kwargs=kwargs)
        func_hl = threading.Thread(
            target=func, args=args, kwargs=kwargs, daemon=True
            )
        func_hl.start()
        return func_hl
    return asynch_func

def schedule(interval):
    def decorator(func):
        def periodic(
            scheduler, interval, action, actionargs=()
            ):
            scheduler.enter(
                interval,
                1, periodic,
                (scheduler, interval, action, actionargs)
                )
            action(*actionargs)
        @functools.wraps(func)
        def wrap(*args, **kwargs):
            scheduler = sched.scheduler(time.time, time.sleep)
            periodic(scheduler, interval, func)
            scheduler.run()
        return wrap
    return decorator

