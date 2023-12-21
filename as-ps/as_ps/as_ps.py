"""IOC for power supplies."""

import os as _os
import sys as _sys
import signal as _signal
import logging as _log
import traceback as _traceback

import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools

from PRUserial485 import EthBridgeClient as _EthBridgeClient

from siriuspy import util as _util
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.pwrsupply.factory import BBBFactory
from siriuspy.logging import configure_logging, get_logger

from .main import App

STOP_EVENT = False  # _multiprocessing.Event()


def _stop_now(signum, frame):
    _ = frame
    get_logger(_stop_now).warning(
        _signal.Signals(signum).name + ' received at ' + _util.get_timestamp()
    )
    _sys.stdout.flush()
    _sys.stderr.flush()
    global STOP_EVENT
    STOP_EVENT = True


def _attribute_access_security_group(server, dbase):
    for key, value in dbase.items():
        if key.endswith(('-RB', '-Sts', '-Cte', '-Mon')):
            value.update({'asg': 'rbpv'})
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    server.initAccessSecurityFile(path_ + '/access_rules.as')


class _PCASDriver(_pcaspy.Driver):

    def __init__(self, bbblist, dbset):
        super().__init__()
        self.app = App(self, bbblist, dbset)

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
    logger = get_logger(run)

    # Define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    configure_logging()
    logger.info('--- PS IOC structures initialization ---\n')

    # Create BBBs
    bbblist = list()
    dbset = dict()
    for bbbname in bbbnames:
        bbbname = bbbname.replace('--', ':')
        bbb, dbase = BBBFactory.create(_EthBridgeClient, bbbname=bbbname)
        bbblist.append(bbb)
        dbset.update(dbase)

    version = _util.get_last_commit_hash()
    ioc_prefix = _VACA_PREFIX + ("-" if _VACA_PREFIX else "")

    # check if another instance of this IOC is already running
    pvname = ioc_prefix + next(iter(dbset))
    if _util.check_pv_online(pvname, use_prefix=False):
        raise ValueError('Another instance of this IOC is already running !')

    # print info about the IOC
    _util.print_ioc_banner(
        ioc_name='PS IOC',
        db=dbset,
        description='Power Supply IOC (FAC)',
        version=version,
        prefix=ioc_prefix)

    # Create a new simple pcaspy server and driver to respond client's requests
    logger.info("Creating Server.")
    server = _pcaspy.SimpleServer()
    # Set security access
    _attribute_access_security_group(server, dbset)
    logger.info("Setting Server Database.")
    server.createPV(ioc_prefix, dbset)
    logger.info("Creating Driver.")
    driver = _PCASDriver(bbblist, dbset)

    # Create a new thread responsible for listening for client connections
    thread_server = _pcaspy_tools.ServerThread(server)
    logger.info("Starting Server Thread.")
    thread_server.start()

    # Main loop - run app.proccess
    while not STOP_EVENT:
        try:
            driver.app.process()
        except Exception:
            _log.exception('[!!] - exception while processing main loop')
            _traceback.print_exc()
            break
    driver.app.scan = False
    logger.info("Stoping Server Thread...")
    # Signal received, exit
    thread_server.stop()
    thread_server.join()
    logger.info("Server Thread stopped.")
    logger.info("Good Bye.")
