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
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s"))
    return fh

def configure_root_logger(file_handler):
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(file_handler)
    return root