"""Module with main IOC Class."""

import time as _time
import logging as _log
from siriuspy.csdevice import timesys as _cstime
from as_ti_control.hl_classes import HL_Event as _HL_Event
from as_ti_control.hl_classes import HL_Clock as _HL_Clock
from as_ti_control.hl_classes import HL_Trigger as _HL_Trigger
from as_ti_control.hl_classes import HL_EVG as _HL_EVG


_TIMEOUT = 0.05


class App:
    """Main Class of the IOC Logic."""

    def get_database(self):
        """Get the database."""
        db = dict()
        if self._evg is not None:
            db.update(self._evg.get_database())
        for cl in self._clocks.values():
            db.update(cl.get_database())
        for ev in self._events.values():
            db.update(ev.get_database())
        for trig in self._triggers.values():
            db.update(trig.get_database())
        return db

    def __init__(self, driver=None, triggers_list=[],
                 evg_params=True):
        """Initialize the instance.

        driver : is the driver associated with this app;
        triggers_list: is the list of the high level triggers to be managed;
        clocks_evg : define if this app will manage evg params such as clocks,
                     events, etc.
        """
        _log.info('Starting App...')
        self.driver = driver
        self._evg = None
        self._clocks = dict()
        self._events = dict()
        self._triggers = dict()
        if evg_params:
            self._evg = _HL_EVG(self._update_driver)
            _log.info('Creating High Level Interface for Clocks and EVG:')
            for cl_hl, cl_ll in _cstime.clocks_hl2ll_map.items():
                clock = _cstime.clocks_hl_pref + cl_hl
                self._clocks[clock] = _HL_Clock(clock, self._update_driver,
                                                cl_ll)
            _log.info('Creating High Level Interface for Events:')
            for ev_hl, ev_ll in _cstime.events_hl2ll_map.items():
                event = _cstime.events_hl_pref + ev_hl
                self._events[event] = _HL_Event(event, self._update_driver,
                                                ev_ll)
        if triggers_list:
            _log.info('Creating High Level Triggers:')
            for pref in triggers_list:
                self._triggers[pref] = _HL_Trigger(pref, self._update_driver)
        self._database = self.get_database()

    def connect(self):
        """Trigger connection to external PVs in other classes."""
        if self._evg is not None:
            self._evg.connect()
        for key, val in self._clocks.items():
            val.connect()
        for key, val in self._events.items():
            val.connect()
        for key, val in self._triggers.items():
            val.connect()

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
        if reason.endswith(('-Sts', '-RB', '-Mon')):
            return False
        enums = (self._database[reason].get('enums') or
                 self._database[reason].get('Enums'))
        if enums is not None:
            if isinstance(value, int):
                len_ = len(enums)
                if value >= len_:
                    _log.warning('value {0:d} too large '.format(value) +
                                 'for PV {0:s} of type enum'.format(reason))
                    return False
            elif isinstance(value, str):
                if value not in enums:
                    _log.warning('Value {0:s} not permited'.format(value))
                    return False
        return True
