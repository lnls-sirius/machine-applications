"""IOC Module."""

import logging as _log
import os as _os
import signal as _signal
from threading import Event as _Event

import pcaspy as _pcaspy
from pcaspy.tools import ServerThread
from siriuspy import csdev as _csdev, util as _util
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.search import HLTimeSearch as _HLTimeSearch
from siriuspy.thread import LoopQueueThread as _LoopQueueThread

from .main import App

__version__ = _util.get_last_commit_hash()
INTERVAL = 0.5
stop_event = _Event()

SPECIAL_TRIGS = {
    'si-bpms': 'SI-Fam:TI-BPM', 'si-skews': 'SI-Glob:TI-Mags-Skews',
    'si-corrs': 'SI-Glob:TI-Mags-Corrs', 'si-qtrims': 'SI-Glob:TI-Mags-QTrims',
    'bo-corrs': 'BO-Glob:TI-Mags-Corrs', 'bo-bpms': 'BO-Fam:TI-BPM'}
TRIG_TYPES = {'as', 'tb', 'ts', 'li', 'si', 'bo', 'ba'}
TRIG_TYPES |= set(SPECIAL_TRIGS.keys())


def _stop_now(signum, frame):
    _, _ = signum, frame
    _log.info('SIGINT received')
    global stop_event
    stop_event.set()


def _attribute_access_security_group(server, db):
    for k, v in db.items():
        if k.endswith(('-RB', '-Sts', '-Cte', '-Mon')):
            v.update({'asg': 'rbpv'})
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    server.initAccessSecurityFile(path_ + '/access_rules.as')


def _get_ioc_name_and_triggers(section):
    if section.lower() not in TRIG_TYPES:
        _log.error("wrong input value for parameter 'section'.")
        raise Exception("wrong input value for parameter 'section'.")

    if section in SPECIAL_TRIGS:
        triglist = [SPECIAL_TRIGS[section], ]
    else:
        triglist = set(
            _HLTimeSearch.get_hl_triggers({'sec': section.upper()[:2]}))
        triglist = triglist - set(SPECIAL_TRIGS.values())
        triglist = list(triglist)

    ioc_name = section.lower()[:2] + '-ti-trig'
    ioc_prefix = section.upper()[:2] + '-Glob:TI-Trig'
    if len(section) > 2:
        ioc_name += '-' + section[3:]
        ioc_prefix = triglist[0]
    ioc_prefix += ':'
    return ioc_name, ioc_prefix, triglist


class _Driver(_pcaspy.Driver):

    def __init__(self, app):
        super().__init__()
        self._write_queue = _LoopQueueThread(is_cathread=True)
        self._write_queue.start()
        self.app = app
        self.app.driver = self

    def read(self, reason):
        strf = "Reading {0:s}.".format(reason)
        _log.debug(strf)
        return super().read(reason)

    def write(self, reason, value):
        if not self._is_valid(reason, value):
            return False
        self._write_queue.put(
            (self._write, (reason, value)), block=False)
        return True

    def _write(self, reason, value):
        ret_val = self.app.write(reason, value)
        oldval = self.getParam(reason)
        if reason.endswith('-Cmd'):
            value = oldval + 1
        if ret_val:
            _log.info('YES Write %s: %s', reason, str(value))
        else:
            _log.warning(
                'NO write %s: %s current value is %s',
                reason, str(oldval), str(value))
            value = oldval
        self.setParam(reason, value)
        self.updatePV(reason)

    def _is_valid(self, reason, val):
        if reason.endswith(('-Sts', '-RB', '-Mon', '-Cte')):
            strf = 'PV {0:s} is read only.'.format(reason)
            _log.debug(strf)
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


def run(section='as', wait=5, debug=False):
    """Start the IOC."""
    _util.configure_log_file(debug=debug)
    _log.info('Starting...')

    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # get IOC name and triggers list
    ioc_name, ioc_prefix, trig_list = _get_ioc_name_and_triggers(section)
    if not trig_list:
        _log.fatal('Must select some triggers to run IOC.')
        return

    # Creates App object
    _log.debug('Creating App Object.')
    app = App(trig_list=trig_list)

    db = app.get_database()
    db[ioc_prefix + 'Version-Cte'] = {'type': 'string', 'value': __version__}
    # add PV Properties-Cte with list of all IOC PVs:
    db = _csdev.add_pvslist_cte(db, prefix=ioc_prefix)
    prefix = _VACA_PREFIX + ('-' if _VACA_PREFIX else '')

    # check if IOC is already running
    running = _util.check_pv_online(
        pvname=prefix + sorted(db.keys())[0],
        use_prefix=False, timeout=0.5)
    if running:
        strf = 'Another ' + ioc_name + ' is already running!'
        _log.error(strf)
        return
    _util.print_ioc_banner(
        ioc_name, db, 'High Level Timing IOC.', __version__, prefix)

    _log.info('Creating Server.')
    server = _pcaspy.SimpleServer()
    _attribute_access_security_group(server, db)
    _log.info('Setting Server Database.')
    server.createPV(prefix, db)

    _log.info('Waiting 5s for PVs to connect...')
    app.wait_for_connection(5)

    _log.info('Creating Driver.')
    _Driver(app)

    _log.info('Starting Server Thread.')
    server_thread = ServerThread(server)
    server_thread.daemon = True
    server_thread.start()

    tm = max(2, wait)
    strf = 'Waiting ' + str(tm) + ' seconds to start locking Low Level.'
    _log.info(strf)
    stop_event.wait(tm)
    _log.info('Start locking now.')
    if not stop_event.is_set():
        # First Set the correct initial state
        db = app.get_database()
        m2w = app.get_map2writepvs()
        for pv, fun in app.get_map2readpvs().items():
            val = fun()
            value = val.pop('value')
            if value is None:
                continue
            if pv.endswith(('-SP', '-Sel')) and not pv.endswith('LvlLock-Sel'):
                m2w[pv](value)
            try:
                app.driver.setParam(pv, value)
            except TypeError as err:
                print(pv, value)
                raise err
            app.driver.setParamStatus(pv, **val)
            app.driver.updatePV(pv)

        # Start locking
        app.locked = True

    # main loop
    while not stop_event.is_set():
        app.process(INTERVAL)

    _log.info('Stoping Server Thread...')
    # send stop signal to server thread
    server_thread.stop()
    server_thread.join()
    _log.info('Server Thread stopped.')
    _log.info('Good Bye.')
