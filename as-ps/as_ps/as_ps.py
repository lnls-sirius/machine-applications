"""IOC for PS."""

import sys as _sys
import signal as _signal
from threading import Thread as _Thread

import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools

import siriuspy.util as _util
# import as_ps.main as _main
# import as_ps.pvs as _pvs
from as_ps.main import App
from siriuspy.envars import vaca_prefix as _VACA_PREFIX
# from siriuspy.search import PSSearch
# from siriuspy.pwrsupply.data import PSData
# from siriuspy.pwrsupply.pru import PRU
# from siriuspy.pwrsupply.model import FBPPowerSupply
# from siriuspy.pwrsupply.controller import FBPController, FBPControllerSim
from siriuspy.pwrsupply.beaglebone import BeagleBone as _BeagleBone

INTERVAL = 0.1/10
stop_event = False  # _multiprocessing.Event()

_PREFIX = _VACA_PREFIX
_COMMIT_HASH = _util.get_last_commit_hash()


def _stop_now(signum, frame):
    global stop_event
    print(_signal.Signals(signum).name + ' received at ' +
          _util.get_timestamp())
    _sys.stdout.flush()
    _sys.stderr.flush()
    stop_event = True


def get_devices(bbbs, simulate=True):
    """Rerturn a controller for each device."""
    pass


def get_database(controllers):
    """Return the database."""
    db = {}
    for psname in controllers:
        dev_db = controllers[psname].database
        for field in dev_db:
            db[psname + ':' + field] = dev_db[field]
    return {_PREFIX: db}


class _PCASDriver(_pcaspy.Driver):

    def __init__(self, bbblist, database):
        super().__init__()
        self.app = App(self, bbblist, database, _PREFIX)

    def read(self, reason):
        value = self.app.read(reason)
        if value is None:
            return super().read(reason)
        else:
            return value

    def write(self, reason, value):
        return self.app.write(reason, value)


def run(bbblist, simulate=True):
    """Main function."""
    # Define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    _util.configure_log_file()

    # Create BBBs
    bbbs = dict()
    devices = dict()
    for bbbname in bbblist:
        bbb = _BeagleBone(bbbname, simulate)
        for psname in bbb.psnames:
            devices[psname] = bbb[psname]
            bbbs[psname] = bbb
    # What if serial is not running?
    # devices = get_devices(bbbs, simulate=simulate)
    database = get_database(devices)

    # Check if IOC is already running
    pvname = \
        _PREFIX + list(devices[list(devices)[0]].database)[0]
    running = _util.check_pv_online(
        pvname=pvname, use_prefix=False, timeout=0.5)
    if running:
        print('Another PS IOC is already running!')
        return

    # Create a new simple pcaspy server and driver to respond client's requests
    server = _pcaspy.SimpleServer()
    server.createPV(_PREFIX, get_database(devices)[_PREFIX])

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)

    # Create driver to handle requests
    pcas_driver = _PCASDriver(bbbs, database)

    # Create scan thread that'll enqueue read request to update DB
    scan_thread = _Thread(target=pcas_driver.app.enqueue_scan, daemon=True)

    # Start threads and processing
    server_thread.start()
    scan_thread.start()
    while not stop_event:
        pcas_driver.app.process(INTERVAL)

    # Signal received, exit
    print('exiting...')
    server_thread.stop()
    pcas_driver.app.scan = False

    server_thread.join()
    scan_thread.join()


if __name__ == "__main__":
    run(['BO-01:CO-BBB-2'], simulate=True)
