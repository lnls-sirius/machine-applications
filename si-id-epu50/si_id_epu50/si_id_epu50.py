import pcaspy
import sys
import os
import traceback
from threading import Thread as _Thread
import logging
import logging.handlers
logger = logging.getLogger(__name__)

import constants as _cte
import iocDriver
import epu_db
import save_restore


def run(args):
    """."""
    # create CA server
    server = pcaspy.SimpleServer()

    # config access security
    server.initAccessSecurityFile(
        _cte.access_security_filename, PREFIX=args.pv_prefix
        )

    # instantiate PV database
    server.createPV(args.pv_prefix, epu_db.pvdb)

    # create pcaspy driver
    driver = iocDriver.EPUSupport(args)

    # restore saved PV values
    restore = _Thread(
        target=save_restore.restore_after_delay,
        args=(
            args.autosave_request_file,  # request file name
            args.pv_prefix,  # pv prefix
            args.autosave_dir,  # save directory
            5.0,  # delay before restoring
            ),
        daemon=True
        )
    restore.start()

    # start autosave
    autosave = _Thread(
        target=save_restore.save_monitor_with_delay,
        args=(
            args.autosave_request_file,  # request file name
            args.pv_prefix,  # pv prefix
            args.autosave_dir,  # save directory
            _cte.autosave_update_rate,  # save update period
            _cte.autosave_num_backup_files,  # max number of backup files
            10.0,  # delay before monitoring start
            ),
        daemon=True,
        )
    autosave.start()

    while True:
        try:
            # process CA transactions
            server.process(_cte.ca_process_rate)
        except Exception:
            traceback.print_exc(file=sys.stdout)
            os._exit(0)

def get_file_handler(file: str):
    # logger.handlers.clear()
    file_handler = logging.handlers.RotatingFileHandler(file, maxBytes=10000000, backupCount=10)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s"))
    return file_handler


def get_logger(file_handler):
    lg = logging.getLogger()
    lg.setLevel(logging.DEBUG)
    lg.addHandler(file_handler)
    return lg

if __name__ == '__main__':
    logger.handlers.clear()
    fh = get_file_handler('testing.log')
    root = get_logger(fh)
    run()