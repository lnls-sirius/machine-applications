"""PS Test IOC."""

import sys as _sys
import signal as _signal
from threading import Thread as _Thread

import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools

import siriuspy.util as _util
# import as_ps.main as _main
# import as_ps.pvs as _pvs
from main import App
from siriuspy.envars import vaca_prefix as _VACA_PREFIX
from siriuspy.search import PSSearch
from siriuspy.pwrsupply.data import PSData
from siriuspy.pwrsupply.pru import PRU
from siriuspy.pwrsupply.model import PowerSupply, PowerSupplySim
from siriuspy.pwrsupply.controller import PSController

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


def get_controllers(bbblist, simulate=True):
    controllers = {}
    if not simulate:
        serial = PRU()
        for bbbname in bbblist:
            psnames = PSSearch.conv_bbbname_2_psnames(bbbname)
            for i, psname in enumerate(psnames):
                db = PSData(psname).propty_database
                device = PowerSupply(serial, i + 1, db)
                controllers[psname] = PSController(device)
    else:
        for bbbname in bbblist:
            psnames = PSSearch.conv_bbbname_2_psnames(bbbname)
            for i, psname in enumerate(psnames):
                db = PSData(psname).propty_database
                device = PowerSupplySim(db)
                controllers[psname] = PSController(device)
    return controllers


def get_database(controllers):
    db = {}
    for psname in controllers:
        dev_db = controllers[psname].device.database
        for field in dev_db:
            db[psname + ':' + field] = dev_db[field]
    return {_PREFIX: db}


class _PCASDriver(_pcaspy.Driver):

    def __init__(self, controllers, database):
        super().__init__()
        self.app = App(self, controllers, database, _PREFIX)

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
    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    controllers = get_controllers(bbblist, simulate=simulate)
    database = get_database(controllers)

    # define IOC and initializes it
    # _main.App.init_class(bbblist, simulate=simulate)

    # check if IOC is already running
    pvname = \
        _PREFIX + list(controllers[list(controllers)[0]].device.database)[0]
    running = _util.check_pv_online(
        pvname=pvname, use_prefix=False, timeout=0.5)
    if running:
        print('Another PS IOC is already running!')
        return

    # create a new simple pcaspy server and driver to respond client's requests
    server = _pcaspy.SimpleServer()
    # for prefix, database in _main.App.get_pvs_database().items():
    server.createPV(_PREFIX, get_database(controllers)[_PREFIX])
    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    pcas_driver = _PCASDriver(controllers, database)
    scan_thread = _Thread(target=pcas_driver.app.enqueue_scan)
    server_thread.start()
    scan_thread.start()
    # main loop
    while not stop_event:
        pcas_driver.app.process(INTERVAL)
    print('exiting...')
    # sends stop signal to server thread
    server_thread.stop()
    pcas_driver.app.scan = False
    server_thread.join()
    scan_thread.join()


if __name__ == "__main__":
    run(['BO-01:CO-BBB-2'])
