"""Module with main IOC Class."""

import time as _time
from functools import reduce as _reduce
from operator import and_ as _and_
import logging as _log
from siriuspy.csdevice import timesys as _cstime
from siriuspy.timesys import HLTrigger as _HLTrigger

_TIMEOUT = 0.05


class App:
    """Main Class of the IOC Logic."""

    def get_database(self):
        """Get the database."""
        db = dict()
        for obj in self._objects:
            db.update(obj.get_database())
        return db

    def __init__(self, driver=None, trig_list=[]):
        """Initialize the instance.

        driver : is the driver associated with this app;
        triggers_list: is the list of the high level triggers to be managed;
        """
        self.driver = driver
        self._objects = list()
        if trig_list:
            for pref in trig_list:
                self._objects.append(_HLTrigger(pref, self._update_driver))
        self._map2writepvs = self.get_map2writepvs()
        self._map2readpvs = self.get_map2readpvs()

    @property
    def locked(self):
        """Start locking Low Level PVs."""
        return _reduce(_and_, map(lambda x: x.locked, self._objects))

    @locked.setter
    def locked(self, lock):
        """Stop locking Low Level PVs."""
        for obj in self._objects:
            obj.locked = lock

    def process(self, interval):
        """Run continuously in the main thread."""
        t0 = _time.time()
        tf = _time.time()
        dt = interval - (tf-t0)
        if dt > 0:
            _time.sleep(dt)
        else:
            _log.warning('process took {0:f}ms.'.format((tf-t0)*1000))

    def write(self, reason, value):
        """Write value in objects and database."""
        fun_ = self._map2writepvs.get(reason)
        if fun_ is None:
            _log.warning('Not OK: PV %s is not settable.', reason)
            return False
        return fun_(value)

    def read(self, reason, from_db=False):
        """Read PV value from objects or database."""
        if from_db and self.driver is not None:
            value = self.driver.getParam(reason)
        else:
            fun_ = self._map2readpvs.get(reason)
            value = fun_()['value']
        return value

    def get_map2writepvs(self):
        """Get dictionary to write pvs to objects."""
        map2writepvs = dict()
        for obj in self._objects:
            map2writepvs.update(obj.get_map2writepvs())
        return map2writepvs

    def get_map2readpvs(self):
        """Get dictionary to read pvs from objects."""
        map2readpvs = dict()
        for obj in self._objects:
            map2readpvs.update(obj.get_map2readpvs())
        return map2readpvs

    def _update_driver(
            self, pvname, value, alarm=None, severity=None, **kwargs):
        if self.driver is None:
            return
        val = self.driver.getParam(pvname)
        if alarm is not None and severity is not None:
            self.driver.setParamStatus(pvname, alarm=alarm, severity=severity)
            if alarm:
                _log.debug('{0:40s}: alarm'.format(pvname))
        if value is not None and val != value:
            self.driver.setParam(pvname, value)
            _log.debug('{0:40s}: updated'.format(pvname))

        self.driver.updatePV(pvname)
