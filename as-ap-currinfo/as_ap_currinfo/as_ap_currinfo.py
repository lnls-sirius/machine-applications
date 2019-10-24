"""SI-AP-CurrInfo-Charge Soft IOC."""

import os as _os
import sys as _sys
import signal as _signal
import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
from siriuspy import util as _util
import as_ap_currinfo.main as _main
import as_ap_currinfo.pvs as _pvs


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


def _get_app_class(acc):
    if acc == 'bo':
        return _main.BOApp
    elif acc == 'si':
        return _main.SIApp
    else:
        raise ValueError('There is no App defined for accelarator '+acc+'.')


class _PCASDriver(_pcaspy.Driver):

    def __init__(self, acc):
        """Initialize driver."""
        super().__init__()
        app_class = _get_app_class(acc)
        self.app = app_class(self)

    def read(self, reason):
        """Read IOC pvs acording to main application."""
        value = self.app.read(reason)
        if value is None:
            return super().read(reason)
        else:
            return value

    def write(self, reason, value):
        """Write IOC pvs acording to main application."""
        if self.app.write(reason, value):
            super().write(reason, value)
        else:
            return False


def run(acc):
    """Main module function."""
    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    _util.configure_log_file()

    # Init pvs database
    _pvs.select_ioc(acc)
    _get_app_class(acc).init_class()

    # create a new simple pcaspy server and driver to respond client's requests
    server = _pcaspy.SimpleServer()
    db = _get_app_class(acc).pvs_database
    _attribute_access_security_group(server, db)
    server.createPV(_pvs.get_pvs_prefix(), db)
    pcas_driver = _PCASDriver(acc)

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    server_thread.start()

    # main loop
    while not stop_event:
        pcas_driver.app.process(INTERVAL)

    # sends stop signal to server thread
    server_thread.stop()
    server_thread.join()
