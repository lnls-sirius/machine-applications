'''
https://www.toptal.com/python/in-depth-python-logging
'''
import logging
import logging.handlers

FORMATTER = logging.Formatter("%(asctime)s | [%(levelname)s] %(name)s [%(module)s.%(funcName)s:%(lineno)d]: %(message)s")
LOG_FILE = "si_id_epu50.log"

def get_file_handler(file: str):
    # logger.handlers.clear()
    fh = logging.handlers.RotatingFileHandler(file, maxBytes=1000000, backupCount=10)
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s"))
    return fh

def get_logger(name, file_handler):
    lg = logging.getLogger(name)
    lg.setLevel(logging.INFO)
    lg.addHandler(file_handler)
    return lg