"""IOC for PS."""

import os as _os
import sys as _sys
import signal as _signal
import logging as _log
from threading import Thread as _Thread
import traceback as _traceback
import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools

from siriuspy import util as _util
from siriuspy.envars import vaca_prefix as _VACA_PREFIX
from siriuspy.pwrsupply.beaglebone import BeagleBone as _BeagleBone

from as_ps.main import App

INTERVAL = 0.1/10
stop_event = False  # _multiprocessing.Event()
pcas_driver = None

_PREFIX = _VACA_PREFIX
_COMMIT_HASH = _util.get_last_commit_hash()


def _stop_now(signum, frame):
    global stop_event
    print(_signal.Signals(signum).name + ' received at ' +
          _util.get_timestamp())
    _sys.stdout.flush()
    _sys.stderr.flush()
    stop_event = True
    pcas_driver.app.scan = False


def get_devices(bbbs, simulate=True):
    """Rerturn a controller for each device."""
    pass


def get_database_set(devlist):
    """Return the database set, one for each prefix."""
    db = {}
    for device in devlist:
        dev_db = device.database
        for field in dev_db:
            db[device.psname + ':' + field] = dev_db[field]
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


def run(bbbnames, simulate=True):
    """Main function.

    This is the main function of the IOC:
    1. It first builds a list of all required beaglebone objets
    2. It Builds a list of all power supply devices.
    3. Checks if another instance of the IOC is already running
    4. Initializes epics DB with the set of IOC databases
    5. Creates a Driver to handle requests
    6. Starts a thread (thread_server) that listens to client connections
    6. Creates a thread (thread_scan) to enqueue read requests to update DB

    Three methods in App are running within concurrent threads:
        App.proccess: process all read and write requests in queue
        App.enqueu_scan: enqueue read requests to update DB
        App.write: enqueue write requests.
    """
    global pcas_driver

    # Define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    _util.configure_log_file()

    # Create BBBs
    bbblist = list()
    devlist = list()
    for bbbname in bbbnames:
        bbb = _BeagleBone(bbbname, simulate)
        bbblist.append(bbb)
        for psname in bbb.psnames:
            devlist.append(bbb[psname])
    # What if serial is not running?
    # devlist = get_devices(bbblist, simulate=simulate)
    dbset = get_database_set(devlist)

    # Check if IOC is already running
    if _is_running(dbset):
        print('Another PS IOC is already running!')
        return

    # TODO: discuss with guilherme the need of all these threads

    # Create a new simple pcaspy server and driver to respond client's requests
    server = _pcaspy.SimpleServer()
    for prefix, db in dbset.items():
        server.createPV(prefix, db)

    # Create driver to handle requests
    pcas_driver = _PCASDriver(bbblist, dbset)

    # Create a new thread responsible for listening for client connections
    thread_server = _pcaspy_tools.ServerThread(server)

    # Create scan thread that'll enqueue read request to update DB
    # thread_scan = _Thread(target=pcas_driver.app.enqueue_scan, daemon=True)

    # Start threads and processing
    thread_server.start()
    # thread_scan.start()

    # Main loop - run app.proccess
    while not stop_event:
        try:
            pcas_driver.app.process(INTERVAL)
        except Exception as e:
            _log.warning('[!!] - exception while processing main loop')
            _traceback.print_exc()

    # Signal received, exit
    print('exiting...')
    thread_server.stop()
    # pcas_driver.app.scan = False
    thread_server.join()
    # thread_scan.join()


def _is_running(dbset):
    prefix = tuple(dbset.keys())[0]
    propty = tuple(dbset[prefix].keys())[0]
    pvname = prefix + propty
    # print(pvname)
    running = _util.check_pv_online(
        pvname=pvname, use_prefix=False, timeout=0.5)
    return running


if __name__ == "__main__":
    run(['BO-01:CO-BBB-2'], simulate=True)
