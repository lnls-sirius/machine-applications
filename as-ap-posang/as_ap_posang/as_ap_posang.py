"""AS-AP-PosAng Soft IOC."""

import os as _os
import sys as _sys
import signal as _signal
import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
from siriuspy import util as _util
import as_ap_posang.pvs as _pvs
import as_ap_posang.main as _main


INTERVAL = 0.1
stop_event = False


def _stop_now(signum, frame):
    global stop_event
    print(_signal.Signals(signum).name+' received at '+_util.get_timestamp())
    _sys.stdout.flush()
    _sys.stderr.flush()
    stop_event = True


def _attribute_access_security_group(server, db):
    for k, v in db.items():
        if k.endswith(('-RB', '-Sts', '-Cte', '-Mon')):
            v.update({'asg': 'rbpv'})
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    server.initAccessSecurityFile(path_ + '/access_rules.as')


class _PCASDriver(_pcaspy.Driver):

    def __init__(self):
        super().__init__()
        self.app = _main.App(self)

    def read(self, reason):
        return super().read(reason)

    def write(self, reason, value):
        if self.app.write(reason, value):
            super().write(reason, value)
        else:
            return False


def run(transport_line, correctors_type):
    """Run main module function."""
    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    _util.configure_log_file()

    # define IOC
    _pvs.select_ioc(transport_line, correctors_type)
    _main.App.init_class()

    # create a new simple pcaspy server and driver to respond client's requests
    server = _pcaspy.SimpleServer()
    db = _main.App.pvs_database
    _attribute_access_security_group(server, db)
    server.createPV(_pvs.get_pvs_prefix(), db)
    pcas_driver = _PCASDriver()

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    server_thread.start()

    # main loop
    while not stop_event:
        pcas_driver.app.process(INTERVAL)

    # sends stop signal to server thread
    server_thread.stop()
    server_thread.join()
