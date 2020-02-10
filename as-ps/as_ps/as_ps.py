"""IOC for power supplies."""

import os as _os
import sys as _sys
import signal as _signal
import logging as _log
import traceback as _traceback

from copy import deepcopy as _deepcopy

import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools

from siriuspy import util as _util
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.pwrsupply.beaglebone import BBBFactory

from as_ps.main import App

STOP_EVENT = False  # _multiprocessing.Event()
PCAS_DRIVER = None

_PREFIX = _VACA_PREFIX
_COMMIT_HASH = _util.get_last_commit_hash()


def _stop_now(signum, frame):
    global STOP_EVENT
    print(_signal.Signals(signum).name + ' received at ' +
          _util.get_timestamp())
    _sys.stdout.flush()
    _sys.stderr.flush()
    STOP_EVENT = True
    if PCAS_DRIVER is not None:
        PCAS_DRIVER.app.scan = False


def get_database_set(bbblist):
    """Return the database set, one for each prefix."""
    db = {}
    for bbb in bbblist:
        dev_db = bbb.e2s_controller.database
        for field in dev_db:
            for psname in bbb.psnames:
                db[psname + ':' + field] = _deepcopy(dev_db[field])
    return {_PREFIX: db}


def _attribute_access_security_group(server, db):
    for k, v in db.items():
        if k.endswith(('-RB', '-Sts', '-Cte', '-Mon')):
            v.update({'asg': 'rbpv'})
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    server.initAccessSecurityFile(path_ + '/access_rules.as')


class _PCASDriver(_pcaspy.Driver):

    def __init__(self, bbblist, dbset):
        super().__init__()
        self.app = App(self, bbblist, dbset, _PREFIX)

    def read(self, reason):
        value = self.app.read(reason)
        if value is None:
            return super().read(reason)
        else:
            return value

    def write(self, reason, value):
        return self.app.write(reason, value)


def run(bbbnames):
    """Run function.

    This is the main function of the IOC:
    1. It first builds a list of all required beaglebone objets
    2. Checks if another instance of the IOC is already running
    3. Initializes epics DB with the set of IOC databases
    4. Creates a Driver to handle requests
    5. Starts a thread (thread_server) that listens to client connections
    """
    global PCAS_DRIVER

    # Define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    _util.configure_log_file()

    # Create BBBs
    bbblist = list()
    dbset = dict()
    for bbbname in bbbnames:
        bbbname = bbbname.replace('--', ':')
        bbb, dbase = BBBFactory.create(bbbname=bbbname)
        bbblist.append(bbb)
        dbset.update(dbase)

    dbset = {_PREFIX: dbset}

    # Create a new simple pcaspy server and driver to respond client's requests
    server = _pcaspy.SimpleServer()
    for prefix, dbase in dbset.items():
        server.createPV(prefix, dbase)

    # Create driver to handle requests
    PCAS_DRIVER = _PCASDriver(bbblist, dbset)

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
