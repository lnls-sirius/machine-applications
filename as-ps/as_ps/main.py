"""Main application."""

import time as _time
import numpy as _np
import logging as _log

from pcaspy import Alarm as _Alarm
from pcaspy import Severity as _Severity

import siriuspy as _siriuspy
import siriuspy.util as _util

__version__ = _util.get_last_commit_hash()


# NOTE on current behaviour of PS IOC:
#
# 01. While in RmpWfm, MigWfm or SlowRefSync, the PS_I_LOAD variable read from
#     power supplies after setting the last curve point may not be the
#     final value given by PS_REFERENCE. This is due to the fact that the
#     power supply control loop takes some time to converge and the PRU may
#     block serial comm. before it. This is evident in SlowRefSync mode, where
#     reference values may change considerably between two setpoints.
#     (see identical note in BeagleBone class)

class App:
    """Responsible for updating the IOC database.

    Update values and parameters such as alarms.
    """

    def __init__(self, driver, bbblist, dbset, prefix):
        """Create Power Supply controllers."""
        self._driver = driver

        # mapping device to bbb
        self._bbblist = bbblist

        # print info about the IOC
        _siriuspy.util.print_ioc_banner(
            ioc_name='BeagleBone',
            db=dbset[prefix],
            description='BeagleBone Power Supply IOC',
            version=__version__,
            prefix=prefix)

        # build _bbb_devices dict
        self._bbb_devices = dict()
        self._interval = None
        for bbb in self.bbblist:
            bbb_interval = bbb.update_interval()
            # get minimum time interval for BBB
            self._interval = min(bbb_interval, self._interval) if \
                self._interval else bbb_interval
            for psname in bbb.psnames:
                self._bbb_devices[psname] = bbb

    # --- public interface ---

    @property
    def driver(self):
        """Pcaspy driver."""
        return self._driver

    @property
    def bbblist(self):
        """Return list of beaglebone objects."""
        return self._bbblist

    def process(self):
        """Process all read and write requests in queue."""
        t0 = _time.time()
        for bbb in self.bbblist:
            self._scan_bbb(bbb)
        self.driver.updatePVs()
        t1 = _time.time()
        # TODO: this detailed time keeping was necessary in order to
        # have an update refresh rate at 10 Hz. scan_bbb is taking around
        # 40 ms to complete. We should start optimizing
        # the IOC code. As it is it is taking up 80% of BBB1 cpu time.
        _time.sleep(abs(self._interval-(t1-t0)))

    def read(self, reason):
        """Read from database."""
        _log.info("[{:.2s}] - {:.32s} = {:.50s}".format(
            'R ', reason, str(self.driver.getParam(reason))))
        return None

    def write(self, reason, value):
        """Enqueue write request."""
        pvname = _siriuspy.namesys.SiriusPVName(reason)
        _log.info("[{:.2s}] - {:.32s} = {:.50s}".format(
            'W ', reason, str(value)))
        if pvname.sec == 'TB':
            # NOTE: This modified behaviour is to allow loading global_config
            # to complete without artificial warning messages or unnecessary
            # delays. Whether we should extend it to all power supplies remains
            # to be checked.
            self.driver.setParam(reason, value)
            self.driver.updatePV(reason)
        bbb = self._bbb_devices[pvname.device_name]
        bbb.write(pvname.device_name, pvname.propty, value)
        # return True

    # --- private methods ---

    def _check_value_changed(self, reason, new_value):
        # TODO: check how arrays are being compared
        old_value = self.driver.getParam(reason)
        if isinstance(new_value, _np.ndarray):
            return True
        else:
            if new_value != old_value:
                return True
        return False

    def _update_ioc_database(self, bbb, device_name):
        # Return dict indexed with reason
        data, updated = bbb.read(device_name)
        if not updated:
            return
        for reason, new_value in data.items():
            if self._check_value_changed(reason, new_value):
                if new_value is None:
                    continue
                self.driver.setParam(reason, new_value)
            self.driver.setParamStatus(
                reason, _Alarm.NO_ALARM, _Severity.NO_ALARM)

    def _update_ioc_database_disconnected(self, bbb, device_name):
        # Return dict indexed with reason
        data, updated = bbb.read(device_name)
        if not updated:
            return
        for reason, new_value in data.items():
            if self._check_value_changed(reason, new_value):
                if new_value is None:
                    continue
                self.driver.setParam(reason, new_value)
            self.driver.setParamStatus(
                reason, _Alarm.TIMEOUT_ALARM, _Severity.INVALID_ALARM)

    def _scan_bbb(self, bbb):
        for device_name in bbb.psnames:
            if bbb.check_connected(device_name):
                self._update_ioc_database(bbb, device_name)
            else:
                self._update_ioc_database_disconnected(bbb, device_name)
