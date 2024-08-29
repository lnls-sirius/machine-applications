"""IOC Module."""

import logging as _log
import os as _os
import signal as _signal
from threading import Event as _Event

import pcaspy as _pcaspy
from pcaspy.tools import ServerThread
from siriuspy import csdev as _csdev, util as _util
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.meas.lienergy.csdev import Const as _csenergy

from .main import App

__version__ = _util.get_last_commit_hash()
INTERVAL = 0.5
stop_event = _Event()


def _stop_now(signum, frame):
    _, _ = signum, frame
    _log.info('SIGINT received')
    global stop_event
    stop_event.set()


def _attribute_access_security_group(server, db):
    for k, v in db.items():
        if k.endswith(('-RB', '-Sts', '-Cte', '-Mon')):
            v.update({'asg': 'rbpv'})
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    server.initAccessSecurityFile(path_ + '/access_rules.as')


class _Driver(_pcaspy.Driver):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.app.driver = self

    def read(self, reason):
        strf = "Reading {0:s}.".format(reason)
        _log.debug(strf)
        return super().read(reason)

    def write(self, reason, value):
        if not self._is_valid(reason, value):
            return False
        ret_val = self.app.write(reason, value)
        if ret_val:
            _log.info('YES Write %s: %s', reason, str(value))
        else:
            value = self.getParam(reason)
            _log.warning('NO Write %s: %s', reason, str(value))
        self.setParam(reason, value)
        self.updatePV(reason)
        return True

    def _is_valid(self, reason, val):
        if reason.endswith(('-Sts', '-RB', '-Mon', '-Cte')):
            strf = 'PV {0:s} is read only.'.format(reason)
            _log.debug(strf)
            return False
        if val is None:
            msg = 'client tried to set None value. refusing...'
            _log.error(msg)
            return False
        enums = self.getParamInfo(reason, info_keys=('enums', ))['enums']
        if enums and isinstance(val, int) and val >= len(enums):
            _log.warning('value %d too large for enum type PV %s', val, reason)
            return False
        return True


def run(debug=False):
    """Start the IOC."""
    _util.configure_log_file(debug=debug)
    _log.info('Starting...')
    ioc_prefix = _VACA_PREFIX + ('-' if _VACA_PREFIX else '')
    ioc_prefix += 'LI-Glob:AP-MeasEnergy:'

    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # Creates App object
    db = _csenergy.get_database()
    db['Version-Cte'] = {'type': 'string', 'value': __version__}
    # add PV Properties-Cte with list of all IOC PVs:
    db = _csdev.add_pvslist_cte(db, prefix='')
    # check if IOC is already running
    running = _util.check_pv_online(
        pvname=ioc_prefix + sorted(db.keys())[0],
        use_prefix=False, timeout=0.5)
    if running:
        strf = 'Another ' + ioc_prefix + ' is already running!'
        _log.error(strf)
        return
    _util.print_ioc_banner(
            '', db, 'LI Energy IOC.', __version__, ioc_prefix)
    # create a new simple pcaspy server and driver to respond client's requests
    _log.info('Creating Server.')
    server = _pcaspy.SimpleServer()
    _attribute_access_security_group(server, db)
    _log.info('Setting Server Database.')
    server.createPV(ioc_prefix, db)
    _log.info('Creating Driver.')
    app = App()
    _Driver(app)

    # initiate a new thread responsible for listening for client connections
    server_thread = ServerThread(server)
    server_thread.daemon = True
    _log.info('Starting Server Thread.')
    server_thread.start()

    # main loop
    while not stop_event.is_set():
        app.process(INTERVAL)

    _log.info('Stoping Server Thread...')
    # send stop signal to server thread
    server_thread.stop()
    server_thread.join()
    _log.info('Server Thread stopped.')
    _log.info('Good Bye.')
