"""CurrInfo Soft IOC."""

import os as _os
import signal as _signal
import sys as _sys

import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
from siriuspy import util as _util
from siriuspy.currinfo import BOCurrInfoApp as _BOCurrInfoApp, \
    LICurrInfoApp as _LICurrInfoApp, SICurrInfoApp as _SICurrInfoApp, \
    TSCurrInfoApp as _TSCurrInfoApp
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.logging import configure_logging, get_logger

INTERVAL = 0.5
STOP_EVENT = False


def _stop_now(signum, frame):
    _ = frame
    get_logger(_stop_now).warning(
        _signal.Signals(signum).name + " received at " + _util.get_timestamp()
    )
    _sys.stdout.flush()
    _sys.stderr.flush()
    global STOP_EVENT
    STOP_EVENT = True


def _attribute_access_security_group(server, dbase):
    for k, val in dbase.items():
        if k.endswith(("-RB", "-Sts", "-Cte", "-Mon")):
            val.update({"asg": "rbpv"})
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    server.initAccessSecurityFile(path_ + "/access_rules.as")


def _get_app(acc):
    acc = acc.lower()
    if acc == "bo":
        return _BOCurrInfoApp()
    elif acc == "si":
        return _SICurrInfoApp()
    elif acc == "li":
        return _LICurrInfoApp()
    elif acc == "ts":
        return _TSCurrInfoApp()
    else:
        raise ValueError(
            "There is no App defined for accelarator " + acc + "."
        )


class _PCASDriver(_pcaspy.Driver):
    def __init__(self, app):
        """Initialize driver."""
        super().__init__()
        self.app = app
        self.app.add_callback(self.update_pv)

    def read(self, reason):
        """Read IOC pvs according to main application."""
        value = self.app.read(reason)
        if value is None:
            return super().read(reason)
        else:
            return value

    def write(self, reason, value):
        """Write IOC pvs according to main application."""
        ret_val = self.app.write(reason, value)
        if reason.endswith("-Cmd"):
            value = self.getParam(reason) + 1
        if ret_val:
            return super().write(reason, value)
        return False

    def update_pv(self, pvname, value, **kwargs):
        """Update PV."""
        _ = kwargs
        self.setParam(pvname, value)
        self.updatePV(pvname)


def run(acc):
    """Main module function."""
    logger = get_logger(run)
    acc = acc.upper()

    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # configure log file
    configure_logging()
    logger.info("Starting...")

    # define IOC, init pvs database and create app object
    _version = _util.get_last_commit_hash()
    _ioc_prefix = _VACA_PREFIX + ("-" if _VACA_PREFIX else "")
    if acc == "BO":
        _ioc_prefix += acc + "-Glob:AP-CurrInfo:"
    logger.debug("Creating App Object.")
    app = _get_app(acc)
    dbase = app.pvs_database
    if acc == "BO":
        dbase["Version-Cte"]["value"] = _version
    else:
        dbase[acc + "-Glob:AP-CurrInfo:Version-Cte"]["value"] = _version

    # check if another IOC is running
    pvname = _ioc_prefix + next(iter(dbase))
    if _util.check_pv_online(pvname, use_prefix=False):
        raise ValueError("Another instance of this IOC is already running!")

    # check if another IOC is running
    _util.print_ioc_banner(
        ioc_name=acc.lower() + "-ap-currinfo",
        db=dbase,
        description=acc.upper() + "-AP-CurrInfo Soft IOC",
        version=_version,
        prefix=_ioc_prefix,
    )

    # create a new simple pcaspy server and driver to respond client's requests
    logger = get_logger(run)
    logger.info("Creating Server.")
    server = _pcaspy.SimpleServer()
    _attribute_access_security_group(server, dbase)
    logger.info("Setting Server Database.")
    server.createPV(_ioc_prefix, dbase)
    logger.info("Creating Driver.")
    _PCASDriver(app)
    app.init_database()

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    logger.info("Starting Server Thread.")
    server_thread.start()

    # main loop
    while not STOP_EVENT:
        app.process(INTERVAL)

    app.close()
    logger.info("Stoping Server Thread...")
    # send stop signal to server thread
    server_thread.stop()
    server_thread.join()
    logger.info("Server Thread stopped.")
    logger.info("Good Bye.")
