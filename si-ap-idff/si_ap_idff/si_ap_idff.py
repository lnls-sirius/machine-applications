"""SI-AP-IDFF Soft IOC."""

import os as _os
import sys as _sys
import signal as _signal
import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools

from siriuspy import util as _util
from siriuspy.envars import VACA_PREFIX as _vaca_prefix

from siriuspy.idff.main import App as _App


INTERVAL = 0.1  # [s]
STOP_EVENT = False


def _stop_now(signum, frame):
    _ = frame
    print(_signal.Signals(signum).name+' received at '+_util.get_timestamp())
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
        """Write IOC pvs acording to main application."""
        if self.app.write(reason, value):
            return super().write(reason, value)
        return False

    def update_pv(self, pvname, value, **kwargs):
        """Update PV."""
        self.setParam(pvname, value)
        self.updatePV(pvname)


def run(idname):
    """Run main module function."""
    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # configure log file
    _util.configure_log_file()

    # define IOC, init pvs database and create app object
    _version = '1.0.0'
    app = _App(idname)
    dbase = app.pvs_database
    dbase['Version-Cte']['value'] = _version
    _ioc_prefix = _vaca_prefix + ('-' if _vaca_prefix else '')
    _ioc_prefix += app.pvs_prefix + ':'

    # check if another IOC is running
    pvname = _ioc_prefix + next(iter(dbase))
    if _util.check_pv_online(pvname, use_prefix=False):
        raise ValueError('Another instance of this IOC is already running!')

    # check if another IOC is running
    _util.print_ioc_banner(
        ioc_name='SI-AP-IDFF',
        db=dbase,
        description='SI-AP-IDFF Soft IOC',
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
    while not STOP_EVENT:
        driver.app.process(INTERVAL)

    driver.app.quit = True

    # sends stop signal to server thread
    server_thread.stop()
    server_thread.join()
