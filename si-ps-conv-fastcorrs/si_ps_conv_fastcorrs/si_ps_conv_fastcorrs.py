"""IOC for fast corrector current-strength convertion."""

import logging as _log
import os as _os
import signal as _signal
import sys as _sys
import traceback as _traceback

import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
from si_ps_conv_fastcorrs.main import App
from siriuspy import util as _util
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.pwrsupply.csdev import \
    get_conv_propty_database as _get_conv_propty_database
from siriuspy.search import PSSearch as _PSSearch

STOP_EVENT = False  # _multiprocessing.Event()
PCAS_DRIVER = None

_PREFIX = _VACA_PREFIX + ('-' if _VACA_PREFIX else '')
_COMMIT_HASH = _util.get_last_commit_hash()


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
    PCAS_DRIVER.app.scan = False


def get_database_set(psname):
    """Return the database set, one for each prefix."""
    dbase = {}
    pstype = _PSSearch.conv_psname_2_pstype(psname)
    propties = _get_conv_propty_database(pstype)
    for key, value in propties.items():
        pvname = psname + ':' + key
        dbase[pvname] = value
    return dbase


def _attribute_access_security_group(server, dbase):
    for key, value in dbase.items():
        if key.endswith(('-RB', '-Sts', '-Cte', '-Mon')):
            value.update({'asg': 'rbpv'})
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    server.initAccessSecurityFile(path_ + '/access_rules.as')


class _PCASDriver(_pcaspy.Driver):

    def __init__(self, psnames, dbset):
        super().__init__()
        self.app = App(self, psnames, dbset, _PREFIX)

    def read(self, reason):
        value = self.app.read(reason)
        if value is None:
            return super().read(reason)
        return value

    def write(self, reason, value):
        return self.app.write(reason, value)


def run(psnames):
    """Run function."""
    global PCAS_DRIVER

    # Define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    _util.configure_log_file()

    dbset = dict()
    for psname in psnames:
        dbase = get_database_set(psname)
        dbset.update(dbase)

    # check if another IOC is running
    pvname = _PREFIX + next(iter(dbset))
    if _util.check_pv_online(pvname):
        raise ValueError('Another IOC is already running !')

    # Create a new simple pcaspy server
    server = _pcaspy.SimpleServer()

    # Set security access
    _attribute_access_security_group(server, dbase)

    # Insert PVs db in server
    server.createPV(_PREFIX, dbset)

    # Create driver to handle requests
    PCAS_DRIVER = _PCASDriver(psnames, dbset)

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
