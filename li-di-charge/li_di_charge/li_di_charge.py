"""IOC Module."""

import os as _os
import time as _time
from copy import deepcopy as _dcopy
import logging as _log
import signal as _signal
from threading import Event as _Event
import visa
from pcaspy import SimpleServer, Driver
from pcaspy.tools import ServerThread
from siriuspy import util as _util
from siriuspy.csdevice import util as _cutil
from siriuspy.envars import vaca_prefix as _vaca_prefix

__version__ = _util.get_last_commit_hash()
INTERVAL = 0.5
stop_event = _Event()


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


class _Driver(Driver):
    NAME = 0
    CURR = 1
    AVG = 2
    MIN = 3
    MAX = 4
    STD = 6
    COUNT = 7

    def __init__(self, ip):
        super().__init__()
        rm = visa.ResourceManager('@py')
        # open communication with Oscilloscope
        self.osc_socket = rm.open_resource('TCPIP::'+ip+'::inst0::INSTR')

    def read(self, reason):
        _log.debug("Reading {0:s}.".format(reason))
        return super().read(reason)

    def write(self, reason, value):
        if not self._isValid(reason, value):
            return False
        self.setParam(reason, value)
        self.updatePV(reason)
        return True

    def process(self, interval):
        tini = _time.time()
        try:
            self._update()
        except:
            _log.error('Problem reading data!!')
            pass
        dtim = _time.time() - tini
        if dtim <= interval:
            _time.sleep(interval - dtim)

    def _update(self):
        meas = self.osc_socket.query(":MEASure:RESults?")
        meas = meas.split(',')
        idxict1 = [i for i, val in enumerate(meas) if 'ICT1' in val].pop()
        chg1 = float(meas[idxict1 + self.CURR])
        ave1 = float(meas[idxict1 + self.AVG])
        min1 = float(meas[idxict1 + self.MIN])
        max1 = float(meas[idxict1 + self.MAX])
        std1 = float(meas[idxict1 + self.STD])
        cnt1 = float(meas[idxict1 + self.COUNT])
        idxict2 = [i for i, val in enumerate(meas) if 'ICT2' in val].pop()
        chg2 = float(meas[idxict2 + self.CURR])
        ave2 = float(meas[idxict2 + self.AVG])
        min2 = float(meas[idxict2 + self.MIN])
        max2 = float(meas[idxict2 + self.MAX])
        std2 = float(meas[idxict2 + self.STD])
        cnt2 = float(meas[idxict2 + self.COUNT])

        eff = 100 * chg2/chg1
        effave = 100 * ave2/ave1

        self.setParam('LI-01:DI-ICT-1:Charge-Mon', chg1)
        self.setParam('LI-01:DI-ICT-1:ChargeAvg-Mon', ave1)
        self.setParam('LI-01:DI-ICT-1:ChargeMin-Mon', min1)
        self.setParam('LI-01:DI-ICT-1:ChargeMax-Mon', max1)
        self.setParam('LI-01:DI-ICT-1:ChargeStd-Mon', std1)
        self.setParam('LI-01:DI-ICT-1:PulseCount-Mon', cnt1)
        self.setParam('LI-01:DI-ICT-2:Charge-Mon', chg2)
        self.setParam('LI-01:DI-ICT-2:ChargeAvg-Mon', ave2)
        self.setParam('LI-01:DI-ICT-2:ChargeMin-Mon', min2)
        self.setParam('LI-01:DI-ICT-2:ChargeMax-Mon', max2)
        self.setParam('LI-01:DI-ICT-2:ChargeStd-Mon', std2)
        self.setParam('LI-01:DI-ICT-2:PulseCount-Mon', cnt2)
        self.setParam('LI-Glob:AP-TranspEff:Eff-Mon', eff)
        self.setParam('LI-Glob:AP-TranspEff:EffAvg-Mon', effave)
        self.updatePVs()

    @staticmethod
    def get_database():
        def_db = {
                'type': 'float', 'value': 0.0, 'unit': 'nC', 'prec': 3}
        pvs = [
            'LI-01:DI-ICT-1:Charge-Mon',
            'LI-01:DI-ICT-1:ChargeAvg-Mon',
            'LI-01:DI-ICT-1:ChargeMin-Mon',
            'LI-01:DI-ICT-1:ChargeMax-Mon',
            'LI-01:DI-ICT-1:ChargeStd-Mon',
            'LI-01:DI-ICT-2:Charge-Mon',
            'LI-01:DI-ICT-2:ChargeAvg-Mon',
            'LI-01:DI-ICT-2:ChargeMin-Mon',
            'LI-01:DI-ICT-2:ChargeMax-Mon',
            'LI-01:DI-ICT-2:ChargeStd-Mon',
        ]
        db = {pv: _dcopy(def_db) for pv in pvs}
        def_db['unit'] = '%'
        db['LI-01:DI-ICT-1:PulseCount-Mon'] = {'type': 'int', 'value': 0}
        db['LI-01:DI-ICT-2:PulseCount-Mon'] = {'type': 'int', 'value': 0}
        db['LI-Glob:AP-TranspEff:Eff-Mon'] = _dcopy(def_db)
        db['LI-Glob:AP-TranspEff:EffAvg-Mon'] = _dcopy(def_db)
        return db

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


def run(debug=False):
    """Start the IOC."""
    ioc_prefix = 'LI-Fam:DI-ICT'
    osc_ip = 'scope-dig-linac-ict'

    _util.configure_log_file(debug=debug)
    _log.info('Starting...')

    # define abort function
    _signal.signal(_signal.SIGINT, _stop_now)
    _signal.signal(_signal.SIGTERM, _stop_now)

    # Creates App object
    _log.debug('Creating App Object.')
    db = _Driver.get_database()
    db[ioc_prefix + ':Version-Cte'] = {'type': 'string', 'value': __version__}
    # add PV Properties-Cte with list of all IOC PVs:
    db = _cutil.add_pvslist_cte(db, prefix=ioc_prefix)
    # check if IOC is already running
    running = _util.check_pv_online(
        pvname=_vaca_prefix + sorted(db.keys())[0],
        use_prefix=False, timeout=0.5)
    if running:
        _log.error('Another ' + ioc_prefix + ' is already running!')
        return
    _util.print_ioc_banner(
            ioc_prefix, db, 'Linac Charge Reader IOC.', __version__,
            _vaca_prefix)
    # create a new simple pcaspy server and driver to respond client's requests
    _log.info('Creating Server.')
    server = SimpleServer()
    _attribute_access_security_group(server, db)
    _log.info('Setting Server Database.')
    server.createPV(_vaca_prefix, db)
    _log.info('Creating Driver.')
    driver = _Driver(osc_ip)

    # initiate a new thread responsible for listening for client connections
    server_thread = ServerThread(server)
    server_thread.daemon = True
    _log.info('Starting Server Thread.')
    server_thread.start()

    # main loop
    while not stop_event.is_set():
        driver.process(INTERVAL)

    _log.info('Stoping Server Thread...')
    # send stop signal to server thread
    server_thread.stop()
    server_thread.join()
    _log.info('Server Thread stopped.')
    _log.info('Good Bye.')
