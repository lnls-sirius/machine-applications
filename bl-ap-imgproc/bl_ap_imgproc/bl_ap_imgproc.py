"""IOC Module."""

import os as _os
import sys as _sys
import signal as _signal
from threading import Event as _Event

import pcaspy as _pcaspy
from pcaspy.tools import ServerThread

from siriuspy import util as _util
from siriuspy.logging import get_logger, LogMonHandler, configure_logging
from siriuspy.dvfimgproc.csdev import Constants
from siriuspy.dvfimgproc.main import App


stop_event = _Event()


def _stop_now(signum, frame):
    _ = frame
    get_logger(_stop_now).warning(
        _signal.Signals(signum).name+' received at '+_util.get_timestamp())
    _sys.stdout.flush()
    _sys.stderr.flush()
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
        self._logger = get_logger(self)
        self.app = app
        self.app.driver = self
        self.app.init_driver()

    def read(self, reason):
        self._logger.debug("Reading {0:s}.".format(reason))
        return super().read(reason)

    def write(self, reason, value):
        if not self._isValid(reason, value):
            return False

        # NOTE: app.write should update driver pv values in database
        ret_val = self.app.write(reason, value)
        if ret_val:
            self._logger.info('YES Write %s: %s', reason, str(value))
        else:
            value = self.getParam(reason)
            self._logger.warning('NO Write %s: %s', reason, str(value))
        return True

    def check_read_only(self, reason):
        is_read_only = reason.endswith(('-Sts', '-RB', '-Mon', '-Cte'))
        if is_read_only:
            self._logger.debug(f'PV {reason:s} is read only.')
        return is_read_only

    def check_value_none(self, val):
        if val is None:
            self._logger.error('client tried to set None value. refusing...')
            return True
        return False

    def check_enums_nok(self, reason, val):
        enums = self.getParamInfo(reason, info_keys=('enums', ))['enums']
        if not enums:
            return False  # not enum
        elif isinstance(val, int) and val < len(enums):
            return False  # enum index in range
        else:
            return True  # enum index out of range

    def _isValid(self, reason, value):
        if self.check_read_only(reason):
            return False
        elif self.check_value_none(value):
            return False
        elif self.check_enums_nok(reason, value):
            return False
        else:
            return True


def define_abort_function():
    """."""
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)


def ioc_is_running(const):
    """."""
    ioc_prefix = const.get_prefix()
    db = const.get_database()
    running = _util.check_pv_online(
        pvname=ioc_prefix + sorted(db.keys())[0],
        use_prefix=False, timeout=0.5)
    return running


def create_server(const):
    """."""
    get_logger(create_server).info('Creating Server.')
    ioc_prefix = const.get_prefix()
    db = const.get_database()

    server = _pcaspy.SimpleServer()
    _attribute_access_security_group(server, db)

    get_logger(create_server).info('Setting Server Database.')
    server.createPV(ioc_prefix, db)
    return server


def initialize_server_thread(server):
    """."""
    server_thread = ServerThread(server)
    server_thread.daemon = True
    get_logger(initialize_server_thread).info('Starting Server Thread.')
    server_thread.start()
    return server_thread


def stop_server_thread(server_thread):
    """."""
    get_logger(stop_server_thread).info('Stoping Server Thread...')
    # send stop signal to server thread
    server_thread.stop()
    server_thread.join()
    get_logger(stop_server_thread).info('Server Thread stopped.')
    return server_thread


def create_driver_app(const):
    """."""
    logger = get_logger(create_driver_app)
    logger.info('Creating Driver.')
    app = App(const=const)
    _Driver(app)  # a handle to Drive object is set within the app object.

    dbase = app._database
    _util.print_ioc_banner(
        ioc_name='BL ImgProc IOC',
        db=dbase,
        description='Image Processing IOC (FAC)',
        version=dbase['ImgVersion-Cte']['value'],
        prefix=const.devname,
        logger=logger)

    # Add handler to update 'Log-Mon' PV to the root logger:
    get_logger().addHandler(LogMonHandler(app.update_log))
    return app


def run(devname, debug=False):
    """Start the IOC."""
    # initial configurations
    configure_logging(debug=debug)
    get_logger(run).info('Starting...')
    define_abort_function()

    # application constants with database
    const = Constants(devname)

    # check whether an instance is already running
    if ioc_is_running(const):
        raise ValueError('Another instance of this IOC is already running !')

    # create server and driver app
    server = create_server(const)
    app = create_driver_app(const)
    server_thread = initialize_server_thread(server)

    # main loop
    interval = 0.5
    while not stop_event.is_set():
        app.process(interval)

    # end of application, stop server thread
    server_thread = stop_server_thread(server_thread)
