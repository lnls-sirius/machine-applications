"""IOC Module."""

import os as _os
import time as _time
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
INTERVAL = 0.5
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

    trig_list = []
    events = False
    sec = 'as'
    if timing.endswith('all'):
        trig_list = _HLTimeSearch.get_hl_triggers()
        suf = 'AllTrigs'
    if timing.endswith(('-as', '-li', '-tb', '-bo', '-ts', '-si')):
        trig_list = _HLTimeSearch.get_hl_triggers({'sec': timing[-2:].upper()})
        sec = timing[-2:]
        suf = sec.upper() + 'Trigs'
    elif timing.endswith('evts'):
        events = True
        suf = 'Evts'
    ioc_name = sec + '-ti-' + suf.lower()
    ioc_prefix = sec.upper() + '-Glob:TI-HighLvl-' + suf
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
        if not self._isValid(reason, value):
            return False
        ret_val = self.app.write(reason, value)
        if ret_val:
            _log.info('YES Write %s: %s', reason, str(value))
        else:
            value = self.getParam(reason)
            _log.warning('NO Write %s: %s', reason, str(value))
        self.setParam(reason, value)
        self.updatePV(reason)
        return True

    def _isValid(self, reason, val):
        if reason.endswith(('-Sts', '-RB', '-Mon', '-Cte')):
            _log.debug('PV {0:s} is read only.'.format(reason))
            return False
        if val is None:
            msg = 'client tried to set None value. refusing...'
            _log.error(msg)
            return False
        enums = self.getParamInfo(reason, info_keys=('enums', ))['enums']
        if enums and isinstance(val, int) and val >= len(enums):
            _log.warning('value %d too large for enum type PV %s', val, reason)
            return False
        return True


class _ServerThread(_pcaspy_tools.ServerThread):

    def __init__(self, server, interval=0.1):
        super().__init__(server)
        self.interval = interval

    def run(self):
        """
        Start the server processing
        """
        while self.running:
            t0 = _time.time()
            self.server.process(self.interval)
            dt = _time.time() - t0
            if dt > self.interval*1.1:
                _log.info('Process took: {0:.4f} s'.format(dt))


def run(timing='evts', lock=False, wait=5, debug=False, interval=0.1):
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

    if not lock:
        tm = max(2, wait)
        _log.info(
            'Waiting ' + str(tm) + ' seconds to start locking Low Level.')
        stop_event.wait(tm)
        _log.info('Start locking now.')

    if not stop_event.is_set():
        app.locked = True

    # initiate a new thread responsible for listening for client connections
    server_thread = _ServerThread(server, interval)
    server_thread.daemon = True
    _log.info('Starting Server Thread.')
    server_thread.start()

    # set state
    db = app.get_database()
    m2w = app.get_map2writepvs()
    if lock:
        for pv, fun in m2w.items():
            if pv.endswith('-Cmd'):
                continue
            val = db[pv]['value']
            fun(val)
    else:  # or update driver state
        for pvname, fun in app.get_map2readpvs().items():
            val = fun()
            value = val.pop('value')
            if value is None:
                value = db[pvname]['value']
            if pvname.endswith(('-SP', '-Sel')):
                m2w[pvname](value)
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
