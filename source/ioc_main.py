import pcaspy
import sys
import os
import traceback
import constants as _cte
import iocDriver
import epu_db
from threading import Thread as _Thread
import save_restore

if __name__ == '__main__':
    if epu_db.pv_prefix == '':
        raise ValueError('PV prefix is missing')
    # create CA server
    server = pcaspy.SimpleServer()
    # config access security
    server.initAccessSecurityFile(
        _cte.access_security_filename, PREFIX=epu_db.pv_prefix
        )
    # instantiate PV database
    server.createPV(epu_db.pv_prefix, epu_db.pvdb)
    # create pcaspy driver
    driver = iocDriver.EPUSupport()
    # restore saved PV values
    restore = _Thread(
        target=save_restore.restore_after_delay,
        args=(
            _cte.autosave_request_file, # request file name
            epu_db.pv_prefix, # pv prefix
            _cte.autosave_save_location, # save directory
            5.0 # delay before restoring
            ),
        daemon=True
        )
    restore.start()
    # start autosave
    autosave = _Thread(
        target=save_restore.save_monitor_with_delay,
        args=(
            _cte.autosave_request_file, # request file name
            epu_db.pv_prefix, # pv prefix
            _cte.autosave_save_location, # save directory
            _cte.autosave_update_rate, # save update period
            _cte.autosave_num_backup_files, # max number of backup files
            10.0 # delay before monitoring start
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
