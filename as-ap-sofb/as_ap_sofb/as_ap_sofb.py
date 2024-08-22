#!/usr/bin/env python-sirius
"""IOC Module."""

import logging as _log
import os as _os
import signal as _signal

import numpy as _np
import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
import siriuspy.util as _util
from siriuspy import csdev as _csdev
from siriuspy.envars import VACA_PREFIX as _VACA_PREFIX
from siriuspy.sofb import EpicsCorrectors as _EpicsCorrectors, \
    EpicsMatrix as _EpicsMatrix, EpicsOrbit as _EpicsOrbit, SOFB as _SOFB
from siriuspy.thread import LoopQueueThread as _LoopQueueThread

stop_event = False
__version__ = _util.get_last_commit_hash()


def _stop_now(signum, frame):
    _, _ = signum, frame
    _log.info('SIGNAL received')
    global stop_event
    stop_event = True


def _attribute_access_security_group(server, db):
    for k, v in db.items():
        if k.endswith(('-RB', '-Sts', '-Cte', '-Mon')):
            v.update({'asg': 'rbpv'})
    path_ = _os.path.abspath(_os.path.dirname(__file__))
    server.initAccessSecurityFile(path_ + '/access_rules.as')


class _PCASDriver(_pcaspy.Driver):

    def __init__(self, app):
        super().__init__()
        self._write_queue = _LoopQueueThread(is_cathread=True)
        self._write_queue.start()
        self.app = app
        self.app.add_callback(self.update_pv)

    def read(self, reason):
        strf = f"Reading {reason:s}."
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

        if isinstance(value, (_np.ndarray, list, tuple)):
            pval = f'{value[0]}...{value[-1]}'
        else:
            pval = f'{value}'
        if isinstance(oldval, (_np.ndarray, list, tuple)):
            opval = f'{oldval[0]}...{oldval[-1]}'
        else:
            opval = f'{oldval}'

        if ret_val:
            _log.info('YES Write %s: %s', reason, pval)
        else:
            _log.warning(
                'NO write %s: %s current value is %s', reason, opval, pval)
            value = oldval
        self.setParam(reason, value)
        self.updatePV(reason)

    def update_pv(self, pvname, value, **kwargs):
        self.setParam(pvname, value)
        if kwargs:
            self.setParamInfo(pvname, kwargs)
        self.updatePV(pvname)

    def _is_valid(self, reason, val):
        if reason.endswith(('-Sts', '-RB', '-Mon', '-Cte')):
            strf = f'PV {reason:s} is read only.'
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


def run(acc='SI', debug=False, tests=False):
    """Start the IOC."""
    _util.configure_log_file(debug=debug)
    _log.info('Starting...')

    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # Creates App object
    _log.debug('Creating SOFB Object.')
    app = _SOFB(acc=acc, tests=tests)
    db = app.csorb.get_ioc_database()
    db.update({'Version-Cte': {'type': 'string', 'value': __version__}})
    ioc_prefix = _VACA_PREFIX + ('-' if _VACA_PREFIX else '')
    ioc_prefix += acc.upper() + '-Glob:AP-SOFB:'
    ioc_name = acc.lower() + '-ap-sofb'
    # check if IOC is already running
    running = _util.check_pv_online(
        pvname=ioc_prefix + sorted(db.keys())[0],
        use_prefix=False, timeout=0.5)
    # add PV Properties-Cte with list of all IOC PVs:
    db = _csdev.add_pvslist_cte(db)
    if running:
        strf = f'Another {ioc_name} is already running!'
        _log.error(strf)
        return
    _util.print_ioc_banner(
        ioc_name, db, 'SOFB for ' + acc, __version__, ioc_prefix)
    # create a new simple pcaspy server and driver to respond client's requests
    _log.info('Creating Server.')
    server = _pcaspy.SimpleServer()
    _attribute_access_security_group(server, db)
    _log.info('Setting Server Database.')
    server.createPV(ioc_prefix, db)
    _log.info('Creating Driver.')
    driver = _PCASDriver(app)

    # initiate a new thread responsible for listening for client connections
    server_thread = _pcaspy_tools.ServerThread(server)
    server_thread.setDaemon(True)
    _log.info('Starting Server Thread.')
    server_thread.start()

    app.orbit = _EpicsOrbit(
        acc=app.acc, prefix=app.prefix, callback=driver.update_pv)
    app.correctors = _EpicsCorrectors(
        acc=app.acc, prefix=app.prefix, callback=driver.update_pv)
    app.matrix = _EpicsMatrix(
        acc=app.acc, prefix=app.prefix, callback=driver.update_pv)

    # main loop
    while not stop_event:
        app.process()

    _log.info('Stoping Server Thread...')
    # sends stop signal to server thread
    server_thread.stop()
    server_thread.join()
    _log.info('Server Thread stopped.')
    app.orbit.shutdown()
    app.correctors.shutdown()
    _log.info('Good Bye.')


if __name__ == '__main__':
    run()
