#!/usr/bin/env python-sirius
import logging as _log
import os as _os
import signal as _signal

import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools

from siriuspy import util as _util
from siriuspy import csdev as _csdev
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX

from . import main as _main
from . import pvs as _pvs

INTERVAL = 0.1
stop_event = False
__version__ = _util.get_last_commit_hash()
PREFIX = ''


def _stop_now(signum, frame):
    _, _ = signum, frame
    _log.info('SIGNAL received')
    global stop_event
    stop_event = True


def _attribute_access_security_group(server, db):
    for k, v in db.items():
        if k.endswith(('-RB', '-Sts', '-Cte', '-Mon')):
            v.update({'asg': 'rbpv'})
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    server.initAccessSecurityFile(path_ + '/access_rules.as')


class _PCASDriver(_pcaspy.Driver):

    def __init__(self, apps):
        super().__init__()
        self.apps = apps
        self.apps[0].add_callback(self.update_pv)
        self.apps[1].add_callback(self.update_pv)
        self.apps[0].driver = self
        self.apps[1].driver = self

    def read(self, reason):
        if reason.startswith(self.apps[0].prefix):
            value = self.apps[0].read(reason)
        else:
            value = self.apps[1].read(reason)
        if value is None:
            return super().read(reason)
        else:
            return value

    def write(self, reason, value):
        if reason.startswith(self.apps[0].prefix):
            app_ret = self.apps[0].write(reason, value)
        else:
            app_ret = self.apps[1].write(reason, value)
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
    _util.configure_log_file(debug=False)
    _log.info('Starting...')

    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # create the application model
    _log.debug('Creating App object for IOC.')
    app1 = _main.App(_pvs.IOCPrefixes.CRYO_1)
    app2 = _main.App(_pvs.IOCPrefixes.CRYO_2)
    db1 = app1.get_database()
    db2 = app2.get_database()
    db1.update({'Version-Cte': {'type': 'string', 'value': __version__}})
    db2.update({'Version-Cte': {'type': 'string', 'value': __version__}})
    db = db1 | db2

    ioc_prefix = _VACA_PREFIX + ('-' if _VACA_PREFIX else '')
    ioc_name = 'si-rf-monitor'

    # check if IOC is already running
    running = _util.check_pv_online(
        pvname=ioc_prefix + sorted(db.keys())[0],
        use_prefix=False, timeout=0.5)

    db = _csdev.add_pvslist_cte(db, prefix=_pvs.IOCPrefixes.CRYO_1)

    # add PV Properties-Cte with list of all IOC PVs:
    if running:
        strf = f'Another {ioc_name} is already running!'
        _log.error(strf)
        return

    _util.print_ioc_banner(
        ioc_name, db, 'Monitor Criomodules Temps.', __version__, ioc_prefix
    )

    # create a new simple pcaspy server and driver to respond client's requests
    _log.info('Creating Server.')
    server = _pcaspy.SimpleServer()
    _attribute_access_security_group(server, db)
    _log.info('Setting Server Database.')
    server.createPV(ioc_prefix, db)

    _log.info('Creating Driver.')
    pcas_driver = _PCASDriver([app1, app2])

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    server_thread.daemon = True
    _log.info('Starting Server Thread.')
    server_thread.start()

    # main loop
    # while not stop_event.is_set():
    while not stop_event:
        pcas_driver.app.process(INTERVAL)

    _log.info('Stoping Server Thread...')
    # sends stop signal to server thread
    server_thread.stop()
    server_thread.join()
    _log.info('Server Thread stopped.')
    _log.info('Good Bye.')


if __name__ == '__main__':
    run()
