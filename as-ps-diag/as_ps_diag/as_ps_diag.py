#!/usr/local/bin/python-sirius
"""AS PS Diagnostic."""

import logging as _log
import os as _os
import signal as _signal
import sys as _sys

import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
from pcaspy import Driver as _Driver
from siriuspy import util as _util
from siriuspy.diagsys.psdiag.csdev import \
    get_ps_diag_propty_database as _get_database
from siriuspy.diagsys.psdiag.main import PSDiagApp as _App
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.search import PSSearch as _PSSearch

_COMMIT_HASH = _util.get_last_commit_hash()

INTERVAL = 0.1
STOP_EVENT = False


def _stop_now(signum, frame):
    _ = frame
    global STOP_EVENT
    sname = _signal.Signals(signum).name
    tstamp = _util.get_timestamp()
    strf = f'{sname} received at {tstamp}'
    _log.warning(strf)
    _sys.stdout.flush()
    _sys.stderr.flush()
    STOP_EVENT = True


def _attribute_access_security_group(server, dbase):
    for k, val in dbase.items():
        if k.endswith(('-RB', '-Sts', '-Cte', '-Mon')):
            val.update({'asg': 'rbpv'})
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    server.initAccessSecurityFile(path_ + '/access_rules.as')


class _PSDiagDriver(_Driver):

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


def run(section='', sub_section='', device='', debug=False):
    """Run IOC."""
    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # configure log
    _util.configure_log_file(debug=debug)

    _log.info("Loading power supplies")
    strf1 = "{:12s}: {}".format('\tSection', section or 'None')
    strf2 = "{:12s}: {}".format('\tSub Section', sub_section or 'None')
    strf3 = "{:12s}: {}".format('\tDevice', device or 'None')
    _log.info(strf1)
    _log.info(strf2)
    _log.info(strf3)

    # create PV database
    device_filter = dict()
    if section:
        device_filter['sec'] = section
    if sub_section:
        device_filter['sub'] = sub_section
    if device:
        device_filter['dev'] = device
    device_filter['dis'] = 'PS'
    psnames = _PSSearch.get_psnames(device_filter)

    if not psnames:
        _log.warning('No devices found. Aborting.')
        _sys.exit(0)

    _version = _util.get_last_commit_hash()
    prefix = _VACA_PREFIX + ('-' if _VACA_PREFIX else '')
    pvdb = dict()
    for psname in psnames:
        strf = f'{psname:32s}'
        _log.debug(strf)
        dbase = _get_database(psname)
        for key, value in dbase.items():
            if key == 'DiagVersion-Cte':
                value['value'] = _COMMIT_HASH
            pvname = psname + ':' + key
            pvdb[pvname] = value

    # check if another IOC is running
    pvname = prefix + next(iter(pvdb))
    if _util.check_pv_online(pvname, use_prefix=False):
        raise ValueError('Another instance of this IOC is already running!')

    # create app
    app = _App(psnames)

    # create a new simple pcaspy server
    _log.info("Creating server with %d devices and '%s' prefix",
              len(psnames), prefix)
    server = _pcaspy.SimpleServer()
    _attribute_access_security_group(server, pvdb)
    server.createPV(prefix, pvdb)

    # create driver
    _log.info('Creating driver')
    try:
        driver = _PSDiagDriver(app)
    except Exception:
        strf = 'Failed to create driver. Aborting'
        _log.error(strf, exc_info=True)  # noqa: G201
        _sys.exit(1)

    _util.print_ioc_banner(
        'AS PS Diagnostic', pvdb,
        'IOC that provides power supplies diagnostics.',
        _version, prefix)

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
