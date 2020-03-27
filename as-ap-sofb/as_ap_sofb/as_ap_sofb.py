#!/usr/bin/env python-sirius
"""IOC Module."""

import os as _os
import logging as _log
import signal as _signal
import pcaspy as _pcaspy
import pcaspy.tools as _pcaspy_tools
import siriuspy.util as _util
from siriuspy import csdev as _csdev
from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy.sofb import SOFB as _SOFB, EpicsMatrix as _EpicsMatrix, \
    EpicsOrbit as _EpicsOrbit, EpicsCorrectors as _EpicsCorrectors

stop_event = False
__version__ = _util.get_last_commit_hash()


def _stop_now(signum, frame):
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
        self.app = app
        self.app.add_callback(self.update_pv)

    def read(self, reason):
        _log.debug("Reading {0:s}.".format(reason))
        return super().read(reason)

    def write(self, reason, value):
        if not self._isValid(reason, value):
            return False
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
        return True

    def update_pv(self, pvname, value, **kwargs):
        self.setParam(pvname, value)
        self.updatePV(pvname)

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


def run(acc='SI', debug=False):
    """Start the IOC."""
    _util.configure_log_file(debug=debug)
    _log.info('Starting...')

    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # Creates App object
    _log.debug('Creating SOFB Object.')
    app = _SOFB(acc=acc)
    db = app.csorb.get_ioc_database()
    db.update({'Version-Cte': {'type': 'string', 'value': __version__}})
    ioc_prefix = acc.upper() + '-Glob:AP-SOFB:'
    ioc_name = acc.lower() + '-ap-sofb'
    # check if IOC is already running
    running = _util.check_pv_online(
        pvname=_vaca_prefix + ioc_prefix + sorted(db.keys())[0],
        use_prefix=False, timeout=0.5)
    # add PV Properties-Cte with list of all IOC PVs:
    db = _csdev.add_pvslist_cte(db)
    if running:
        _log.error('Another ' + ioc_name + ' is already running!')
        return
    _util.print_ioc_banner(
        ioc_name, db, 'SOFB for ' + acc, __version__,
        _vaca_prefix + ioc_prefix)
    # create a new simple pcaspy server and driver to respond client's requests
    _log.info('Creating Server.')
    server = _pcaspy.SimpleServer()
    _attribute_access_security_group(server, db)
    _log.info('Setting Server Database.')
    server.createPV(_vaca_prefix + ioc_prefix, db)
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
    _log.info('Good Bye.')


if __name__ == '__main__':
    run()
