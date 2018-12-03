"""Module with main IOC Class."""

import time as _time
import logging as _log
from siriuspy.csdevice import timesys as _cstime
from .hl_classes import HLEvent as _HLEvent, HLClock as _HLClock, \
    HLTrigger as _HLTrigger, HLEVG as _HLEVG


_TIMEOUT = 0.05


class App:
    """Main Class of the IOC Logic."""

    def get_database(self):
        """Get the database."""
        db = dict()
        if self._evg is not None:
            db.update(self._evg.get_database())
        for clk in self._clocks:
            db.update(clk.get_database())
        for evt in self._events:
            db.update(evt.get_database())
        for trig in self._triggers:
            db.update(trig.get_database())
        return db

    def __init__(self, driver=None, trig_list=[], evg_params=True):
        """Initialize the instance.

        driver : is the driver associated with this app;
        triggers_list: is the list of the high level triggers to be managed;
        evg_params: define if this app will manage evg params such as clocks,
                     events, etc.
        """
        self.driver = driver
        self._evg = None
        self._clocks = set()
        self._events = set()
        self._triggers = set()
        if evg_params:
            self._evg = _HLEVG(self._update_driver)
            for cl_hl in _cstime.Const.ClkHL2LLMap:
                self._clocks.add(_HLClock(cl_hl, self._update_driver))
            for ev_hl in _cstime.Const.EvtHL2LLMap:
                self._events.add(_HLEvent(ev_hl, self._update_driver))
        if trig_list:
            for pref in trig_list:
                self._triggers.add(_HLTrigger(pref, self._update_driver))
        self._database = self.get_database()

    def connect(self, respect_ll_state=True):
        """Trigger connection to external PVs in other classes.

        respect_ll_state: If False a default initial state will be forced
            on LL IOCs. Else, it will be read from the LL PVs.
        """
        if self._evg is not None:
            self._evg.connect(respect_ll_state)
        for val in self._clocks:
            val.connect(respect_ll_state)
        for val in self._events:
            val.connect(respect_ll_state)
        for val in self._triggers:
            val.connect(respect_ll_state)

    def start_forcing(self):
        """Start locking Low Level PVs."""
        if self._evg is not None:
            self._evg.start_forcing()
        for val in self._clocks:
            val.start_forcing()
        for val in self._events:
            val.start_forcing()
        for val in self._triggers:
            val.start_forcing()

    def stop_forcing(self):
        """Stop locking Low Level PVs."""
        if self._evg is not None:
            self._evg.stop_forcing()
        for val in self._clocks:
            val.stop_forcing()
        for val in self._events:
            val.stop_forcing()
        for val in self._triggers:
            val.stop_forcing()

    def process(self, interval):
        """Run continuously in the main thread."""
        t0 = _time.time()
        tf = _time.time()
        dt = interval - (tf-t0)
        if dt > 0:
            _time.sleep(dt)
        else:
            _log.debug('process took {0:f}ms.'.format((tf-t0)*1000))

    def write(self, reason, value):
        """Write value in database."""
        if not self._isValid(reason, value):
            return False
        fun_ = self._database[reason].get('fun_set_pv')
        if fun_ is None:
            _log.warning('Not OK: PV %s does not have a set function.', reason)
            return False
        ret_val = fun_(value)
        if ret_val:
            _log.info('YES Write %s: %s', reason, str(value))
        else:
            value = self.driver.getParam(reason)
            _log.warning('NO write %s: %s', reason, str(value))
        self._update_driver(reason, value)
        return True

    def _update_driver(self, pvname, value, alarm=None, severity=None):
        if self.driver is None:
            return
        val = self.driver.getParam(pvname)
        update = False
        if value is not None and val != value:
            self.driver.setParam(pvname, value)
            _log.info('{0:40s}: updated'.format(pvname))
            update = True
        if alarm is not None and severity is not None:
            self.driver.setParamStatus(pvname, alarm=alarm, severity=severity)
            if alarm:
                _log.info('{0:40s}: alarm'.format(pvname))
            update = True
        if update:
            self.driver.updatePV(pvname)

    def _isValid(self, reason, val):
        if reason.endswith(('-Sts', '-RB', '-Mon', '-Cte')):
            _log.debug('App: PV {0:s} is read only.'.format(reason))
            return False
        enums = self._database[reason].get('enums')
        if enums is not None and isinstance(val, int) and val >= len(enums):
            _log.warning('value %d too large for enum type PV %s', val, reason)
            return False
        return True
