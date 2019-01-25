"""IOC Module."""

import os as _os
import logging as _log
import signal as _signal
from threading import Event as _Event
import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
from as_ti_control import App
from siriuspy import util as _util
from siriuspy.csdevice import util as _cutil
from siriuspy.envars import vaca_prefix as _vaca_prefix
from siriuspy.search import HLTimeSearch as _HLTimeSearch

__version__ = _util.get_last_commit_hash()
INTERVAL = 0.1
stop_event = _Event()

_hl_trig = _HLTimeSearch.get_hl_triggers()
TRIG_TYPES = {
    'trig-as', 'trig-si', 'trig-bo', 'trig-tb', 'trig-ts', 'trig-li',
    'trig-all', 'evts'}


def _stop_now(signum, frame):
    _log.info('SIGINT received')
    global stop_event
    stop_event.set()


def _attribute_access_security_group(server, db):
    for k, v in db.items():
        if k.endswith(('-RB', '-Sts', '-Cte', '-Mon')):
            v.update({'asg': 'rbpv'})
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    server.initAccessSecurityFile(path_ + '/access_rules.as')


def _get_ioc_name_and_triggers(timing):
    if timing.lower() not in TRIG_TYPES:
        _log.error("wrong input value for parameter 'triggers'.")
        raise Exception("wrong input value for parameter 'triggers'.")

    trig_list = _HLTimeSearch.get_hl_triggers()
    events = False
    sec = 'as'
    suf = 'trig'
    if timing.endswith(('as', 'li', 'tb', 'bo', 'ts', 'si')):
        trig_list = _HLTimeSearch.get_hl_triggers({'sec': timing[-2:].upper()})
        sec = timing[-2:]
    elif timing.endswith('evts'):
        trig_list = []
        events = True
        suf = 'evts'
    ioc_name = sec + '-ti-' + suf
    ioc_prefix = sec.upper() + '-Glob:TI-HighLvl' + suf.title()
    return ioc_name, ioc_prefix, events, trig_list


class _Driver(_pcaspy.Driver):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.app.driver = self

    def read(self, reason):
        _log.debug("Reading {0:s}.".format(reason))
        return super().read(reason)

    def write(self, reason, value):
        return self.app.write(reason, value)


def run(timing='evts', lock=False, wait=10, debug=False):
    """Start the IOC."""
    _util.configure_log_file(debug=debug)
    _log.info('Starting...')

    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # get IOC name and triggers list
    ioc_name, ioc_prefix, evts, trig_list = _get_ioc_name_and_triggers(timing)
    if not evts and not trig_list:
        _log.fatal('Must select evts or some triggers to run IOC.')
        return
    # Creates App object
    _log.debug('Creating App Object.')
    app = App(events=evts, trig_list=trig_list)
    db = app.get_database()
    db[ioc_prefix + ':Version-Cte'] = {'type': 'string', 'value': __version__}
    # add PV Properties-Cte with list of all IOC PVs:
    db = _cutil.add_pvslist_cte(db, prefix=ioc_prefix)
    # check if IOC is already running
    running = _util.check_pv_online(
        pvname=_vaca_prefix + sorted(db.keys())[0],
        use_prefix=False, timeout=0.5)
    if running:
        _log.error('Another ' + ioc_name + ' is already running!')
        return
    _util.print_ioc_banner(
            ioc_name, db, 'High Level Timing IOC.', __version__, _vaca_prefix)
    # create a new simple pcaspy server and driver to respond client's requests
    _log.info('Creating Server.')
    server = _pcaspy.SimpleServer()
    _attribute_access_security_group(server, db)
    _log.info('Setting Server Database.')
    server.createPV(_vaca_prefix, db)
    _log.info('Creating Driver.')
    _Driver(app)

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    server_thread.daemon = True
    _log.info('Starting Server Thread.')
    server_thread.start()

    # Connects to low level PVs
    _log.info('Openning connections with Low Level IOCs.')

    if not lock:
        tm = max(5, wait)
        _log.info(
            'Waiting ' + str(tm) + ' seconds to start locking Low Level.')
        stop_event.wait(tm)
        _log.info('Start locking now.')

    if not stop_event.is_set():
        app.locked = True

    # set state
    if lock:
        db = app.get_database()
        for pv, fun in app.get_map2writepvs().items():
            if pv.endswith('-Cmd'):
                continue
            val = db[pv]['value']
            fun(val)
    else:  # or update driver state
        for pvname, fun in app.get_map2readpvs().items():
            val = fun()
            value = val.pop('value')
            app.driver.setParam(pvname, value)
            app.driver.setParamStatus(pvname, **val)
            app.driver.updatePV(pvname)

    # main loop
    while not stop_event.is_set():
        app.process(INTERVAL)

    _log.info('Stoping Server Thread...')
    # send stop signal to server thread
    server_thread.stop()
    server_thread.join()
    _log.info('Server Thread stopped.')
    _log.info('Good Bye.')
