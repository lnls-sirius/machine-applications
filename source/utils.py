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

#import threading
#import time
#import functools
#
#"""
#From stackoverflow answer:
#https://stackoverflow.com/questions/2398661/
#schedule-a-repeating-event-in-python-3/48758861#48758861"""
#def asynch(func):
#    @functools.wraps(func)
#    def asynch_func(*args, **kwargs):
#        # func_hl = threading.Thread(target=func, args=args, kwargs=kwargs)
#        func_hl = threading.Thread(
#            target=func, args=args, kwargs=kwargs, daemon=True
#            )
#        func_hl.start()
#        return func_hl
#    return asynch_func
#
#def schedule(interval):
#    def decorator(func):
#        def periodic(
#            scheduler, interval, action, actionargs=()
#            ):
#            scheduler.enter(
#                interval,
#                1, periodic,
#                (scheduler, interval, action, actionargs)
#                )
#            action(*actionargs)
#        @functools.wraps(func)
#        def wrap(*args, **kwargs):
#            scheduler = sched.scheduler(time.time, time.sleep)
#            periodic(scheduler, interval, func)
