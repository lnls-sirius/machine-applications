"""IOC Module."""

import os as _os
import logging as _log
import signal as _signal
from threading import Event as _Event

from .const import Constants
import pcaspy as _pcaspy
from pcaspy.tools import ServerThread
from siriuspy import util as _util

from .main import App


stop_event = _Event()


def _stop_now(signum, frame):
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
        _log.debug("Reading {0:s}.".format(reason))
        return super().read(reason)

    def write(self, reason, value):
        if not self._isValid(reason, value):
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

    def check_read_only(self, reason):
        is_read_only = reason.endswith(('-Sts', '-RB', '-Mon', '-Cte'))
        if is_read_only:
            _log.debug('PV {0:s} is read only.'.format(reason))

        return not is_read_only

    def check_value_none(self, val):
        if val is None:
            msg = 'client tried to set None value. refusing...'
            _log.error(msg)
            return False
        return True

    def check_enums(self, reason, val):
        enums = self.getParamInfo(reason, info_keys=('enums', ))['enums']
        enum_verifier = enums and isinstance(val, int) and val >= len(enums)
        if enum_verifier:
            _log.warning('value %d too large for enum type PV %s', val, reason)
        return not enum_verifier

    def _isValid(self, reason, val):
        is_valid = self.check_read_only(reason)
        is_valid = self.check_value_none(val)
        is_valid = self.check_enums(reason, val)
        return is_valid


def defineAbortFunction():
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)


def ioc_is_running(const):
    ioc_prefix = const.get_prefix()
    db = const.get_database()
    running = _util.check_pv_online(
        pvname=ioc_prefix + sorted(db.keys())[0],
        use_prefix=False, timeout=0.5)

    if running:
        _log.error('Another ' + ioc_prefix + ' is already running!')
        return True

    _util.print_ioc_banner(
        '', db, 'Image Processing IOC.',
        db['Version-Cte']['value'], ioc_prefix)
    return False


def create_server(const):
    _log.info('Creating Server.')
    ioc_prefix = const.get_prefix()
    db = const.get_database()

    server = _pcaspy.SimpleServer()
    _attribute_access_security_group(server, db)

    _log.info('Setting Server Database.')
    server.createPV(ioc_prefix, db)
    return server


def initialize_server_thread(server):
    server_thread = ServerThread(server)
    server_thread.daemon = True
    _log.info('Starting Server Thread.')
    server_thread.start()
    return server_thread


def stop_server_thread(server_thread):
    _log.info('Stoping Server Thread...')
    # send stop signal to server thread
    server_thread.stop()
    server_thread.join()
    _log.info('Server Thread stopped.')
    return server_thread


def create_driver(const):
    _log.info('Creating Driver.')
    app = App(const=const)
    _Driver(app)
    return app


def ioc_main_loop(app):
    interval = 0.5
    while not stop_event.is_set():
        app.process(interval)


def run_imag_proc(devname, debug=False):
    """Start the IOC."""

    _util.configure_log_file(debug=debug)
    _log.info('Starting...')

    defineAbortFunction()

    const = Constants(devname)

    if not ioc_is_running(const):
        server = create_server(const)
        server_thread = initialize_server_thread(server)
        ioc_main_loop(create_driver(const))
        server_thread = stop_server_thread(server_thread)
