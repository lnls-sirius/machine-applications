#!/usr/local/bin/python-sirius
"""LI AP Diagnostic."""

import os as _os
import sys as _sys
import signal as _signal
import logging as _log

import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
from pcaspy import Driver as _Driver

from siriuspy import util as _util
from siriuspy.envars import VACA_PREFIX as _vaca_prefix

from siriuspy.diagsys.lidiag.csdev import get_li_diag_propty_database as \
    _get_database, Const as _Const
from siriuspy.diagsys.lidiag.main import LIDiagApp as _App


_COMMIT_HASH = _util.get_last_commit_hash()

INTERVAL = 0.1
STOP_EVENT = False


def _stop_now(signum, frame):
    global STOP_EVENT
    _log.warning(_signal.Signals(signum).name +
                 ' received at ' + _util.get_timestamp())
    _sys.stdout.flush()
    _sys.stderr.flush()
    STOP_EVENT = True


def _attribute_access_security_group(server, dbase):
    for k, val in dbase.items():
        if k.endswith(('-RB', '-Sts', '-Cte', '-Mon')):
            val.update({'asg': 'rbpv'})
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    server.initAccessSecurityFile(path_ + '/access_rules.as')


class _LIDiagDriver(_Driver):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.app.add_callback(self.update_pv)

    def read(self, reason):
        value = self.app.read(reason)
        if value is None:
            return super().read(reason)
        else:
            return value

    def write(self, reason, value):
        if self.app.write(reason, value):
            return super().write(reason, value)
        return False

    def update_pv(
            self, pvname, value=None, alarm=None, severity=None, field='value',
            **kwargs):
        """."""
        _ = kwargs
        if field == 'value':
            self.setParam(pvname, value)
        elif field == 'status':
            if value is not None:
                self.setParam(pvname, value)
            self.setParamStatus(pvname, alarm, severity)
        self.updatePV(pvname)


def run(debug=False):
    """Run IOC."""
    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # configure log
    _util.configure_log_file(debug=debug)

    _log.info("Loading Linac devices")
    # create PV database
    devices = _Const.ALL_DEVICES

    prefix = _vaca_prefix
    pvdb = dict()
    for dev in devices:
        _log.debug('{:32s}'.format(dev))
        dbase = _get_database(dev)
        for key, value in dbase.items():
            if key == 'DiagVersion-Cte':
                value['value'] = _COMMIT_HASH
            pvname = dev + ':' + key
            pvdb[pvname] = value

    # check if another IOC is running
    pvname = prefix + next(iter(pvdb))
    if _util.check_pv_online(pvname, use_prefix=False):
        raise ValueError('Another instance of this IOC is already running!')

    # create app
    app = _App(prefix, devices)

    # create a new simple pcaspy server
    _log.info("Creating server with %d devices and '%s' prefix",
              len(devices), prefix)
    server = _pcaspy.SimpleServer()
    _attribute_access_security_group(server, pvdb)
    server.createPV(prefix, pvdb)

    # create driver
    _log.info('Creating driver')
    try:
        driver = _LIDiagDriver(app)
    except Exception:
        _log.error('Failed to create driver. Aborting', exc_info=True)
        _sys.exit(1)

    _util.print_ioc_banner(
        'Linac Diagnostic', pvdb,
        'IOC that provides diagnostics for Linac devices.',
        _COMMIT_HASH, prefix)

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    server_thread.start()

    # main loop
    driver.app.scanning = True
    while not STOP_EVENT:
        driver.app.process(INTERVAL)

    driver.app.scanning = False
    driver.app.quit = True

    # sends stop signal to server thread
    server_thread.stop()
    server_thread.join()
