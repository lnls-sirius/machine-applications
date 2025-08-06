#!/usr/bin/env python-sirius
import logging as _log
import os as _os
import signal as _signal

import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools

from siriuspy import util as _util
from siriuspy import csdev as _csdev

from . import main as _main
from . import pvs as _pvs

INTERVAL = 0.1
stop_event = False
__version__ = _util.get_last_commit_hash()
PREFIX = ''


def _stop_now(signum, frame):
    print(' - SIGNAL received.')
    global stop_event
    stop_event = True


def _attribute_access_security_group(server, db):
    for k, v in db.items():
        if k.endswith(('-RB', '-Sts', '-Cte', '-Mon')):
            v.update({'asg': 'rbpv'})
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    server.initAccessSecurityFile(path_ + '/access_rules.as')


class _PCASDriver(_pcaspy.Driver):

    def __init__(self, app=None):
        super().__init__()
        self.app = app or _main.App()
        self.app.add_callback(self.update_pv)
        self.app.driver = self

    def read(self, reason):
        value = self.app.read(reason)
        if value is None:
            return super().read(reason)
        else:
            return value

    def write(self, reason, value):
        app_ret = self.app.write(reason, value)
        if app_ret:
            self.setParam(reason, value)
        self.updatePVs()
        return app_ret

    def update_pv(self, pvname, value, **kwargs):
        """Update PV."""
        _ = kwargs
        self.setParam(pvname, value)
        self.updatePV(pvname)


def run():
    """Run the IOC."""
    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    _util.configure_log_file(debug=False)
    _log.info('Starting...')

    # create the application model
    app = _main.App()
    db = app.get_database()
    db.update({'Version-Cte': {'type': 'string', 'value': __version__}})

    ioc_prefix = _pvs.IOC_PREFIX
    ioc_name = 'si-rf-monitor'

    # check if IOC is already running
    running = _util.check_pv_online(
        pvname=ioc_prefix + sorted(db.keys())[0],
        use_prefix=False, timeout=0.5)
    # add PV Properties-Cte with list of all IOC PVs:
    db = _csdev.add_pvslist_cte(db)
    if running:
        strf = f'Another {ioc_name} is already running!'
        _log.error(strf)
        return
    _util.print_ioc_banner(
        ioc_name, db, 'Monitor Criomodule Temps.', __version__, ioc_prefix
    )

    # create a new simple pcaspy server and driver to respond client's requests
    server = _pcaspy.SimpleServer()
    server.createPV(ioc_prefix, db)

    # create the driver
    pcas_driver = _PCASDriver(app)

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    server_thread.start()

    # main loop
    # while not stop_event.is_set():
    while not stop_event:
        pcas_driver.app.process(INTERVAL)

    print('exiting...')
    # send stop signal to server thread
    server_thread.stop()
    server_thread.join()


if __name__ == '__main__':
    run()
