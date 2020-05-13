"""CurrInfo Soft IOC."""

import os as _os
import sys as _sys
import signal as _signal
import logging as _log
import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools

from siriuspy import util as _util
from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.currinfo import BOCurrInfoApp as _BOCurrInfoApp, \
    SICurrInfoApp as _SICurrInfoApp, LICurrInfoApp as _LICurrInfoApp, \
    TBCurrInfoApp as _TBCurrInfoApp, TSCurrInfoApp as _TSCurrInfoApp


INTERVAL = 0.5
STOP_EVENT = False


def _stop_now(signum, frame):
    _ = frame
    print(_signal.Signals(signum).name+' received at '+_util.get_timestamp())
    _sys.stdout.flush()
    _sys.stderr.flush()
    global STOP_EVENT
    STOP_EVENT = True


def _attribute_access_security_group(server, db):
    for k, val in db.items():
        if k.endswith(('-RB', '-Sts', '-Cte', '-Mon')):
            val.update({'asg': 'rbpv'})
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    server.initAccessSecurityFile(path_ + '/access_rules.as')


def _get_app_class(acc):
    acc = acc.lower()
    if acc == 'bo':
        return _BOCurrInfoApp
    elif acc == 'si':
        return _SICurrInfoApp
    elif acc == 'li':
        return _LICurrInfoApp
    elif acc == 'tb':
        return _TBCurrInfoApp
    elif acc == 'ts':
        return _TSCurrInfoApp
    else:
        raise ValueError('There is no App defined for accelarator '+acc+'.')


class _PCASDriver(_pcaspy.Driver):

    def __init__(self, app):
        """Initialize driver."""
        super().__init__()
        self.app = app
        self.app.add_callback(self.update_pv)

    def read(self, reason):
        """Read IOC pvs acording to main application."""
        value = self.app.read(reason)
        if value is None:
            return super().read(reason)
        else:
            return value

    def write(self, reason, value):
        """Write IOC pvs acording to main application."""
        if self.app.write(reason, value):
            super().write(reason, value)
        else:
            return False

    def update_pv(self, pvname, value, **kwargs):
        """."""
        self.setParam(pvname, value)
        self.updatePV(pvname)


def run(acc):
    """Main module function."""
    acc = acc.upper()

    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # configure log file
    _util.configure_log_file()
    _log.info('Starting...')

    # define IOC, init pvs database and create app object
    _version = _util.get_last_commit_hash()
    _ioc_prefix = _vaca_prefix
    if acc in {'SI', 'BO'}:
        _ioc_prefix += acc + '-Glob:AP-CurrInfo:'
    _log.debug('Creating App Object.')
    app_class = _get_app_class(acc)
    app = app_class()
    db = app.pvs_database
    if acc in {'SI', 'BO'}:
        db['Version-Cte']['value'] = _version
    else:
        db[acc+'-Glob:AP-CurrInfo:Version-Cte']['value'] = _version

    # check if another IOC is running
    pvname = _ioc_prefix + next(iter(db))
    if _util.check_pv_online(pvname, use_prefix=False):
        raise ValueError('Another instance of this IOC is already running!')

    # check if another IOC is running
    _util.print_ioc_banner(
        ioc_name=acc.lower()+'-ap-currinfo',
        db=db,
        description=acc.upper()+'-AP-CurrInfo Soft IOC',
        version=_version,
        prefix=_ioc_prefix)

    # create a new simple pcaspy server and driver to respond client's requests
    _log.info('Creating Server.')
    server = _pcaspy.SimpleServer()
    _attribute_access_security_group(server, db)
    _log.info('Setting Server Database.')
    server.createPV(_ioc_prefix, db)
    _log.info('Creating Driver.')
    _PCASDriver(app)
    app.init_database()

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    _log.info('Starting Server Thread.')
    server_thread.start()

    # main loop
    while not STOP_EVENT:
        app.process(INTERVAL)

    app.close()
    _log.info('Stoping Server Thread...')
    # send stop signal to server thread
    server_thread.stop()
    server_thread.join()
    _log.info('Server Thread stopped.')
    _log.info('Good Bye.')
