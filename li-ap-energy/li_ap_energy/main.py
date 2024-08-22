"""Module with main IOC Class."""

import logging as _log
import time as _time

from siriuspy.epics import PV as _PV
from siriuspy.meas.lienergy import MeasEnergy
from siriuspy.meas.lienergy.csdev import Const as _CEnergy

_TIMEOUT = 0.05


class App:
    """Main Class of the IOC Logic."""

    def __init__(self, driver=None,):
        """Initialize the instance.

        driver : is the driver associated with this app;
        triggers_list: is the list of the high level triggers to be managed;
        """
        self.driver = driver
        self._database = _CEnergy.get_database()
        self.meas = MeasEnergy(callback=self._update_driver)
        self._map2writepvs = self.get_map2writepvs()
        self._map2readpvs = self.get_map2readpvs()
        self._egun_pv = _PV('LI-01:EG-TriggerPS:status')
        self._spect_pv = _PV('LI-01:PS-Spect:Current-Mon')
        self._was_measuring = False

    def process(self, interval):
        """Run continuously in the main thread."""
        t0 = _time.time()
        # self.turnoff_if_no_beam()
        tf = _time.time()
        dt = interval - (tf-t0)
        if dt > 0:
            _time.sleep(dt)
        else:
            strf = 'process took {0:f}ms.'.format((tf-t0)*1000)
            _log.warning(strf)

    def turnoff_if_no_beam(self):
        """."""
        stt = None
        if self.meas.measuring:
            if not self.should_measure():
                stt = self.meas.MeasureState.Stopped
        else:
            if self.should_measure():
                if self._was_measuring:
                    stt = self.meas.MeasureState.Measuring
        if stt is not None:
            self.meas.measuring = stt
            self._update_driver('MeasureCtrl-Sel', stt)
            self._update_driver('MeasureCtrl-Sts', stt)

    def should_measure(self):
        """."""
        return self._egun_pv.value and self._spect_pv.value > 10

    def write(self, reason, value):
        """Write value in objects and database."""
        fun_ = self._map2writepvs.get(reason)
        if reason.endswith('MeasureCtrl-Sel'):
            self._was_measuring = bool(value)
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
            value = fun_()
        return value

    def get_map2writepvs(self):
        """Get dictionary to write pvs to objects."""
        map2writepvs = dict()
        map2writepvs.update(self.meas.get_map2write())
        return {k: v for k, v in map2writepvs.items() if k in self._database}

    def get_map2readpvs(self):
        """Get dictionary to read pvs from objects."""
        map2readpvs = dict()
        map2readpvs.update(self.meas.get_map2read())
        return {k: v for k, v in map2readpvs.items() if k in self._database}

    def _update_driver(
            self, pvname, value, alarm=None, severity=None, **kwargs):
        if pvname not in self._database:
            return
        if self.driver is None:
            return
        if alarm is not None and severity is not None:
            self.driver.setParamStatus(pvname, alarm=alarm, severity=severity)
            if alarm:
                strf = '{0:40s}: alarm'.format(pvname)
                _log.debug(strf)
        if value is not None:
            self.driver.setParam(pvname, value)
            strf = '{0:40s}: updated'.format(pvname)
            _log.debug(strf)

        self.driver.updatePV(pvname)
