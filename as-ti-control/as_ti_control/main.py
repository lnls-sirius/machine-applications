"""Module with main IOC Class."""

import time as _time
import logging as _log
from siriuspy.csdevice import timesys as _cstime
from siriuspy.timesys import HLEvent as _HLEvent, HLTrigger as _HLTrigger

_TIMEOUT = 0.05


class App:
    """Main Class of the IOC Logic."""

    def get_database(self):
        """Get the database."""
        db = dict()
        for obj in self._objects:
            db.update(obj.get_database())
        return db

    def __init__(self, driver=None, trig_list=[], events=True):
        """Initialize the instance.

        driver : is the driver associated with this app;
        triggers_list: is the list of the high level triggers to be managed;
        events: define if this app will manage evg events.
        """
        self.driver = driver
        self._objects = list()
        if events:
            for ev_hl in _cstime.Const.EvtHL2LLMap:
                self._objects.append(_HLEvent(ev_hl, self._update_driver))
        if trig_list:
            for pref in trig_list:
                self._objects.append(_HLTrigger(pref, self._update_driver))
        self._map2write = self.get_map2write()
        self._db = self.get_database()

    @property
    def locked(self):
        """Start locking Low Level PVs."""
        locked = True
        for obj in self._objects:
            locked &= obj.locked
        return locked

    @locked.setter
    def locked(self, lock):
        """Stop locking Low Level PVs."""
        for obj in self._objects:
            if lock:
                vals = obj.readall(is_sp=True)
                for prop, val in vals.items():
                    obj.write(prop, val['value'])
            obj.locked = lock

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
        fun_ = self._map2write.get(reason)
        if fun_ is None:
            _log.warning('Not OK: PV %s is not settable.', reason)
            return False
        ret_val = fun_(value)
        if ret_val:
            _log.info('YES Write %s: %s', reason, str(value))
        else:
            value = self.driver.getParam(reason)
            _log.warning('NO write %s: %s', reason, str(value))
        self._update_driver(reason, value)
        return True

    def get_map2write(self):
        """Get the database."""
        map2write = dict()
        for obj in self._objects:
            map2write.update(obj.get_map2write())
        return map2write

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
        enums = self._db[reason].get('enums')
        if enums is not None and isinstance(val, int) and val >= len(enums):
            _log.warning('value %d too large for enum type PV %s', val, reason)
            return False
        return True
