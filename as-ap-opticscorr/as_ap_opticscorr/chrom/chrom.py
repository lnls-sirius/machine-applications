"""AS-AP-OpticsCorr-Chrom IOC."""

import os as _os
import sys as _sys
import signal as _signal
import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools

from siriuspy import util as _util
from siriuspy.envars import VACA_PREFIX as _vaca_prefix

from siriuspy.opticscorr.chrom import ChromCorrApp as _App


INTERVAL = 0.25
stop_event = False


def _stop_now(signum, frame):
    global stop_event
    print(_signal.Signals(signum).name+' received at '+_util.get_timestamp())
    _sys.stdout.flush()
    _sys.stderr.flush()
    stop_event = True


def _attribute_access_security_group(server, db):
    for k, v in db.items():
        if k.endswith(('-RB', '-Sts', '-Cte', '-Mon')):
            v.update({'asg': 'rbpv'})
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    server.initAccessSecurityFile(path_ + '/access_rules.as')


class _PCASDriver(_pcaspy.Driver):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.app.add_callback(self.update_pv)

    def read(self, reason):
        return super().read(reason)

    def write(self, reason, value):
        if self.app.write(reason, value):
            super().write(reason, value)
        else:
            return False

    def update_pv(self, pvname, value=None, info=None, field='value', **kws):
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
    _ioc_prefix = _vaca_prefix + acc.upper() + '-Glob:AP-ChromCorr:'
    app = _App(acc)
    db = app.pvs_database
    db['Version-Cte']['value'] = _version

    # check if another IOC is running
    pvname = _ioc_prefix + next(iter(db))
    if _util.check_pv_online(pvname, use_prefix=False):
        raise ValueError('Another instance of this IOC is already running!')

    # check if another IOC is running
    _util.print_ioc_banner(
        ioc_name=acc.upper()+'-AP-ChromCorr',
        db=db,
        description=acc.upper()+'-AP-ChromCorr Soft IOC',
        version=_version,
        prefix=_ioc_prefix)

    # create a new simple pcaspy server and driver to respond client's requests
    server = _pcaspy.SimpleServer()
    _attribute_access_security_group(server, db)
    server.createPV(_ioc_prefix, db)
    pcas_driver = _PCASDriver(app)
    app.init_database()

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    server_thread.start()

    # main loop
    while not stop_event:
        pcas_driver.app.process(INTERVAL)

    # sends stop signal to server thread
    server_thread.stop()
    server_thread.join()
