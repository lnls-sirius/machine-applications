"""Main IOC module."""

import sys
import os
import traceback
from threading import Thread as _Thread
import pcaspy

from . import constants as _cte
from . import iocDriver as _iocDriver
from . import csdev as _csdev
from . import save_restore as _save_restore


def run(args):
    """."""
    # create CA server
    server = pcaspy.SimpleServer()

    # config access security
    server.initAccessSecurityFile(
        _cte.access_security_filename, PREFIX=args.pv_prefix)

    # instantiate PV database
    idname = args.pv_prefix
    pvdb = _csdev.get_pvdb(idname)
    server.createPV(idname, pvdb)

    # create pcaspy driver
    driver = _iocDriver.EPUSupport(args)

    # restore saved PV values
    restore = _Thread(
        target=_save_restore.restore_after_delay,
        args=(
            args.autosave_request_file,  # request file name
            args.pv_prefix,  # pv prefix
            args.autosave_dir,  # save directory
            5.0,  # delay before restoring
        ),
        daemon=True,
    )
    restore.start()

    # start autosave
    autosave = _Thread(
        target=_save_restore.save_monitor_with_delay,
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
