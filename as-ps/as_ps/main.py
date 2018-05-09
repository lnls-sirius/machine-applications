"""Main application."""

import time as _time
import numpy as _np
import logging as _log
# from collections import deque as _deque
# from collections import namedtuple as _namedtuple
# from threading import Thread as _Thread
# from threading import Lock as _Lock

from pcaspy import Alarm as _Alarm
from pcaspy import Severity as _Severity

# import as_ps.pvs as _pvs
import siriuspy as _siriuspy
import siriuspy.util as _util
from siriuspy.pwrsupply.beaglebone import _E2SController

__version__ = _util.get_last_commit_hash()

# FREQUENCY_SCAN = 10.0  # [Hz]
# FREQUENCY_RAMP = 2.0  # [Hz]


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

        # save file with PVs list
        _siriuspy.util.save_ioc_pv_list('as-ps',
                                        ('',
                                         prefix),
                                        dbset[prefix])

        # map psname to bbb
        self._bbb_devices = dict()
        for bbb in self.bbblist:
            for psname in bbb.psnames:
                self._bbb_devices[psname] = bbb

        # operation queue
        # self._op_deque = _deque()  # TODO: is dequeu thread-safe ?!
        # self._lock = _Lock()

        # scan
        # TODO: there should be one _scan_interval for each BBB !!!
        # rethink IOC duties.
        # self._scan_interval = 1.0/FREQUENCY_SCAN
        # self.scan = True

        # read Constants once and for all
        # self._constants_update = False

        # symbol to threads that execute BSMP blocking operations
        # self._op_thread = None

    # API
    @property
    def driver(self):
        """Pcaspy driver."""
        return self._driver

    @property
    def bbblist(self):
        """Return list of beaglebone objects."""
        return self._bbblist

    def process(self, interval):
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
        _time.sleep(abs(_E2SController.INTERVAL_SCAN-(t1-t0)))

    def read(self, reason):
        """Read from database."""
        _log.info("[{:.2s}] - {:.32s} = {:.50s}".format(
            'R ', reason, str(self.driver.getParam(reason))))
        return None

    def write(self, reason, value):
        """Enqueue write request."""
        # TODO: can we parse reason with SiriusPVName?
        split = reason.split(':')
        device = ':'.join(split[:2])
        field = split[-1]

        _log.info("[{:.2s}] - {:.32s} = {:.50s}".format(
            'W ', reason, str(value)))

        bbb = self._bbb_devices[device]
        bbb.write(device, field, value)

    # Private
    def _check_value_changed(self, reason, new_value):
        return True
        # TODO: Is it necessary to check?
        old_value = self.driver.getParam(reason)
        if isinstance(new_value, _np.ndarray):
            # TODO: check for ndarray
            return True
        else:
            if new_value != old_value:
                return True
        return False

    def _update_ioc_database(self, bbb, device_name):
        # Return dict idexed with reason
        for reason, new_value in bbb.read(device_name).items():
            if self._check_value_changed(reason, new_value):
                if new_value is None:
                    continue
                self.driver.setParam(reason, new_value)
                self.driver.setParamStatus(
                    reason, _Alarm.NO_ALARM, _Severity.NO_ALARM)

    def _set_device_disconnected(self, bbb, device_name):
        for field in bbb.devices_database:
            reason = device_name + ':' + field
            self.driver.setParamStatus(
                reason, _Alarm.TIMEOUT_ALARM, _Severity.INVALID_ALARM)

    def _scan_bbb(self, bbb):
        for device_name in bbb.psnames:
            if bbb.check_connected(device_name):
                self._update_ioc_database(bbb, device_name)
            else:
                self._set_device_disconnected(bbb, device_name)
