"""AS-AP-OpticsCorr-Chrom IOC."""

import logging as _log
import os as _os
import signal as _signal
import sys as _sys

import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
from siriuspy import util as _util
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.opticscorr.chrom import ChromCorrApp as _App

INTERVAL = 0.25
STOP_EVENT = False


def _stop_now(signum, frame):
    _ = frame
    sname = _signal.Signals(signum).name
    tstamp = _util.get_timestamp()
    strf = f'{sname} received at {tstamp}'
    _log.warning(strf)
    _sys.stdout.flush()
    _sys.stderr.flush()
    global STOP_EVENT
    STOP_EVENT = True


def _attribute_access_security_group(server, dbase):
    for k, val in dbase.items():
        if k.endswith(('-RB', '-Sts', '-Cte', '-Mon')):
            val.update({'asg': 'rbpv'})
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    server.initAccessSecurityFile(path_ + '/access_rules.as')


class _PCASDriver(_pcaspy.Driver):

    def __init__(self, app):
        """Initialize driver."""
        super().__init__()
        self.app = app
        self.app.add_callback(self.update_pv)

    def read(self, reason):
        """Read IOC pvs according to main application."""
        return super().read(reason)

    def write(self, reason, value):
        """Write IOC pvs according to main application."""
        if self.app.write(reason, value):
            return super().write(reason, value)
        return False

    def update_pv(self, pvname, value=None, info=None, field='value', **kws):
        """Update PV."""
        _ = kws
        if field == 'value':
            self.setParam(pvname, value)
        elif field == 'info':
            self.setParamInfo(pvname, info)
        self.updatePV(pvname)


def run(acc):
    """Main module function."""
    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # configure log file
    _util.configure_log_file()

    # define IOC, init pvs database and create app object
    _version = _util.get_last_commit_hash()
    _ioc_prefix = _VACA_PREFIX + ('-' if _VACA_PREFIX else '')
    _ioc_prefix += acc.upper() + '-Glob:AP-ChromCorr:'
    app = _App(acc)
    dbase = app.pvs_database
    dbase['Version-Cte']['value'] = _version

    # check if another IOC is running
    pvname = _ioc_prefix + next(iter(dbase))
    if _util.check_pv_online(pvname, use_prefix=False):
        raise ValueError('Another instance of this IOC is already running!')

    # check if another IOC is running
    _util.print_ioc_banner(
        ioc_name=acc.upper()+'-AP-ChromCorr',
        db=dbase,
        description=acc.upper()+'-AP-ChromCorr Soft IOC',
        version=_version,
        prefix=_ioc_prefix)

    # create a new simple pcaspy server and driver to respond client's requests
    server = _pcaspy.SimpleServer()
    _attribute_access_security_group(server, dbase)
    server.createPV(_ioc_prefix, dbase)
    pcas_driver = _PCASDriver(app)
    app.init_database()

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    server_thread.start()

    # main loop
    while not STOP_EVENT:
        pcas_driver.app.process(INTERVAL)

    # sends stop signal to server thread
    server_thread.stop()
    server_thread.join()
