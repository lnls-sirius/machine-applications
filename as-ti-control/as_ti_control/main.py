"""Module with main IOC Class."""

import time as _time
import logging as _log
from siriuspy.csdevice import timesys as _cstime
from .hl_classes import HL_Event as _HL_Event
from .hl_classes import HL_Clock as _HL_Clock
from .hl_classes import HL_Trigger as _HL_Trigger
from .hl_classes import HL_EVG as _HL_EVG


_TIMEOUT = 0.05


class App:
    """Main Class of the IOC Logic."""

    def get_database(self):
        """Get the database."""
        db = dict()
        if self._evg is not None:
            db.update(self._evg.get_database())
        for cl in self._clocks:
            db.update(cl.get_database())
        for ev in self._events:
            db.update(ev.get_database())
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
            self._evg = _HL_EVG(self._update_driver)
            for cl_hl, cl_ll in _cstime.clocks_hl2ll_map.items():
                self._clocks.add(_HL_Clock(cl_hl, self._update_driver))
            for ev_hl, ev_ll in _cstime.events_hl2ll_map.items():
                self._events.add(_HL_Event(ev_hl, self._update_driver))
        if trig_list:
            for pref in trig_list:
                self._triggers.add(_HL_Trigger(pref, self._update_driver))
        self._database = self.get_database()

    def connect(self, get_ll_state=True):
        """Trigger connection to external PVs in other classes.

        get_ll_state: If False a default initial state will be forced
            on LL IOCs. Else, it will be read from the LL PVs.
        """
        if self._evg is not None:
            self._evg.connect(get_ll_state)
        for val in self._clocks:
            val.connect(get_ll_state)
        for val in self._events:
            val.connect(get_ll_state)
        for val in self._triggers:
            val.connect(get_ll_state)

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
        dt = (tf-t0)
        if dt > 2*interval:
            _log.warning('App: check took {0:f}ms.'.format(dt*1000))
        dt = interval - dt
        if dt > 0:
            _time.sleep(dt)

    def write(self, reason, value):
        """Write PV in the model."""
        if not self._isValid(reason, value):
            return False
        fun_ = self._database[reason].get('fun_set_pv')
        if fun_ is None:
            _log.warning('Not OK: PV ' +
                         '{0:s} does not have a set function.'.format(reason))
            return False
        ret_val = fun_(value)
        if not ret_val:
            _log.warning('Not OK: PV {0:s}; value = {1:s}.'
                         .format(reason, str(value)))
        return ret_val

    def _update_driver(self, pvname, value, alarm=None, severity=None):
        val = self.driver.getParam(pvname)
        update = False
        if value is not None and val != value:
            self.driver.setParam(pvname, value)
            _log.info('{0:40s}: updated'.format(pvname))
            self.driver.updatePVs()
            update = True
        if alarm is not None and severity is not None:
            self.driver.setParamStatus(pvname, alarm=alarm, severity=severity)
            if alarm:
                _log.info('{0:40s}: alarm'.format(pvname))
            update = True
        if update:
            self.driver.updatePVs()

    def _isValid(self, reason, value):
        enums = self._database[reason].get('enums')
        if enums is not None:
            if isinstance(value, int):
                len_ = len(enums)
                if value >= len_:
                    _log.warning('value {0:d} too large '.format(value) +
                                 'for PV {0:s} of type enum'.format(reason))
                    return False
        return True
