"""AS-AP-InjCtrl Soft IOC."""

import logging as _log
import os as _os
import signal as _signal
import sys as _sys
import time as _time

import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
from siriuspy import util as _util
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.injctrl.main import App as _App

INTERVAL = 0.1
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
        value = self.app.read(reason)
        if value is None:
            return super().read(reason)
        return value

    def write(self, reason, value):
        """Write IOC pvs according to main application."""
        ret_val = self.app.write(reason, value)
        if reason.endswith('-Cmd'):
            value = self.getParam(reason) + 1
        if ret_val:
            return super().write(reason, value)
        return False

    def update_pv(self, pvname, value, **kwargs):
        """Update PV."""
        _ = kwargs
        self.setParam(pvname, value)
        self.updatePV(pvname)


def run():
    """Run main module function."""
    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # configure log file
    _util.configure_log_file()

    # define IOC, init pvs database and create app object
    _version = _util.get_last_commit_hash()
    _ioc_prefix = _VACA_PREFIX + ('-' if _VACA_PREFIX else '')
    _ioc_prefix += 'AS-Glob:AP-InjCtrl:'
    app = _App()
    dbase = app.pvs_database
    dbase['Version-Cte']['value'] = _version
    dbase['TimestampBoot-Cte']['value'] = _time.time()

    # check if another IOC is running
    pvname = _ioc_prefix + next(iter(dbase))
    if _util.check_pv_online(pvname, use_prefix=False):
        raise ValueError('Another instance of this IOC is already running!')

    # check if another IOC is running
    _util.print_ioc_banner(
        ioc_name='AS-AP-InjCtrl',
        db=dbase,
        description='AS-AP-InjCtrl Soft IOC',
        version=_version,
        prefix=_ioc_prefix)

    # create a new simple pcaspy server and driver to respond client's requests
    server = _pcaspy.SimpleServer()
    _attribute_access_security_group(server, dbase)
    server.createPV(_ioc_prefix, dbase)
    driver = _PCASDriver(app)
    app.init_database()

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
