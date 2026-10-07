"""IOC for ID Conv."""

import logging as _log
import os as _os
import signal as _signal
import sys as _sys
import traceback as _traceback

import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools

from siriuspy import util as _util
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.pwrsupply.csdev import \
    get_conv_propty_database as _get_conv_propty_database
from siriuspy.search import PSSearch as _PSSearch


from .csdev import get_propty_database as _get_conv_propty_database
from .main import App


STOP_EVENT = False  # _multiprocessing.Event()
PCAS_DRIVER = None

_PREFIX = _VACA_PREFIX + ('-' if _VACA_PREFIX else '')
_COMMIT_HASH = _util.get_last_commit_hash()


def _stop_now(signum, frame):
    _ = frame  # throwaway arguments
    global STOP_EVENT
    sname = _signal.Signals(signum).name
    tstamp = _util.get_timestamp()
    strf = f'{sname} received at {tstamp}'
    _log.warning(strf)
    _sys.stdout.flush()
    _sys.stderr.flush()
    STOP_EVENT = True
    PCAS_DRIVER.app.scan = False


def _attribute_access_security_group(server, dbase):
    for key, value in dbase.items():
        if key.endswith(('-RB', '-Sts', '-Cte', '-Mon')):
            value.update({'asg': 'rbpv'})
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    server.initAccessSecurityFile(path_ + '/access_rules.as')


class _PCASDriver(_pcaspy.Driver):

    def __init__(self, idnames, dbset):
        super().__init__()
        self.app = App(self, idnames, dbset, _PREFIX)

    def read(self, reason):
        value = self.app.read(reason)
        if value is None:
            return super().read(reason)
        return value

    def write(self, reason, value):
        return self.app.write(reason, value)


def init_pcaspy_driver_and_server(idnames):
    """Create PCASpy driver."""
    global PCAS_DRIVER

    dbset = dict()
    for idname in idnames:
        dbase = _get_conv_propty_database(idname)
        dbset.update(dbase)

    # check if another instance of this IOC is already running
    pvname = _PREFIX + next(iter(dbset))
    if _util.check_pv_online(pvname, use_prefix=False):
        raise ValueError('Another instance of this IOC is already running !')

    # Create a new simple pcaspy server and driver to respond client's requests
    server = _pcaspy.SimpleServer()

    # Set security access
    _attribute_access_security_group(server, dbase)

    # Insert PVs db in server
    server.createPV(_PREFIX, dbset)

    # Create driver to handle requests
    PCAS_DRIVER = _PCASDriver(idnames, dbset)

    return server


def run(idnames):
    """Run function."""
    # Define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # Configure log file.
    _util.configure_log_file()

    # Init PCAS_DRIVER and create server
    server = init_pcaspy_driver_and_server(idnames)

    # Create a new thread responsible for listening for client connections
    thread_server = _pcaspy_tools.ServerThread(server)

    # Start threads and processing
    thread_server.start()

    # Main loop - run app.proccess
    while not STOP_EVENT:
        try:
            PCAS_DRIVER.app.process()
        except Exception:
            _log.warning('[!!] - exception while processing main loop')
            _traceback.print_exc()
            break

    # Signal received, exit
    print('exiting...')
    thread_server.stop()
    thread_server.join()
