"""Main application."""

import time as _time
import logging as _log
import re as _re
import numpy as _np

from pcaspy import Alarm as _Alarm
from pcaspy import Severity as _Severity

import siriuspy as _siriuspy
import siriuspy.util as _util

from siriuspy.thread import DequeThread as _DequeThread

__version__ = _util.get_last_commit_hash()


# Select whether to queue write requests or process them right away.
_USE_WRITE_QUEUE = True


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

    _setpoint_regexp = _re.compile('^.*-(SP|Sel)$')

    def __init__(self, driver, bbblist, dbset, prefix):
        """Create Power Supply controllers."""
        self._driver = driver

        # write operation queue
        self._prucqueue = _DequeThread() if _USE_WRITE_QUEUE else None

        # mapping device to bbb
        self._bbblist = bbblist

        # print info about the IOC
        _siriuspy.util.print_ioc_banner(
            ioc_name='BeagleBone',
            db=dbset[prefix],
            description='BeagleBone Power Supply IOC',
            version=__version__,
            prefix=prefix)

        # build bbb_devices dict (and set _prucqueue)
        self._create_bbb_dev_dict()

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
        """Process all write requests in queue and does a BBB scan."""
        time0 = _time.time()
        if self._prucqueue:  # Not None and not empty
            status = self._prucqueue.process()
            if status:
                txt = ("[{:.2s}] - new thread started for write queue item. "
                       "items left: {}")
                logmsg = txt.format('Q ', len(self._prucqueue))
                _log.info(logmsg)
            # scanning bbb allows for read-only variables to be updated while
            # there are pending write operations in the queue, since setpoint
            # variables will not be updated in the scan, in order not to spoil
            # the received write value.
            for bbb in self.bbblist:
                self.scan_bbb(bbb)
            _time.sleep(0.050)
        else:
            for bbb in self.bbblist:
                self.scan_bbb(bbb)
            time1 = _time.time()
            # TODO: measure this interval for various BBBs...
            # _log.info("process.... {:.3f} ms".format(1000*(time1-time0)))
            _time.sleep(abs(self._interval-(time1-time0)))

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
        if _USE_WRITE_QUEUE:
            # NOTE: This modified behaviour is to allow loading
            # global_config to complete without artificial warning
            # messages or unnecessary delays. Whether we should extend
            # it to all power supplies remains to be checked.
            if App._setpoint_regexp.match(reason):
                # Accept *-SP and *-Sel right away (not *-Cmd !)
                self.driver.setParam(reason, value)
                self.driver.updatePV(reason)
            bbb = self._bbb_devices[pvname.device_name]
            operation = (self._write_operation, (bbb, pvname, value))
            self._prucqueue.append(operation)
            self._prucqueue.process()
        else:
            self.driver.setParam(reason, value)
            self.driver.updatePV(reason)
            bbb = self._bbb_devices[pvname.device_name]
            time0 = _time.time()
            bbb.write(pvname.device_name, pvname.propty, value)
            time1 = _time.time()
            # self.scan_device(bbb, pvname.device_name, force_update=True)
            _log.info("[{:.2s}] - {:.32s} : {:.50s}".format(
                'T ', reason, '{:.3f} ms'.format((time1-time0)*1000)))

    def scan_bbb(self, bbb):
        """Scan BBB devices and update ioc DB."""
        for device_name in bbb.psnames:
            self.scan_device(bbb, device_name)

    def scan_device(self, bbb, device_name, force_update=False):
        """Scan BBB device and update ioc DB."""
        dev_connected = bbb.check_connected(device_name)
        self._update_ioc_database(bbb, device_name, dev_connected,
                                  force_update)

    # --- private methods ---

    def _create_bbb_dev_dict(self):
        # build _bbb_devices dict
        self._bbb_devices = dict()
        self._dev_connected = dict()
        self._interval = float('Inf')
        for bbb in self.bbblist:
            # get minimum time interval for BBB
            self._interval = min(self._interval, bbb.update_interval())
            # create bbb_device dict
            for dev_name in bbb.psnames:
                self._dev_connected[dev_name] = None
                self._bbb_devices[dev_name] = bbb

    def _write_operation(self, bbb, pvname, value):
        time0 = _time.time()
        bbb.write(pvname.device_name, pvname.propty, value)
        # NOTE: This scan_device might be redundent
        # self.scan_device(bbb, pvname.device_name, force_update=True)
        time1 = _time.time()
        _log.info("[{:.2s}] - {:.32s} : {:.50s}".format(
            'T ', pvname,
            'write operation took {:.3f} ms'.format((time1-time0)*1000)))

    def _update_ioc_database(self, bbb, device_name,
                             dev_connected=True,
                             force_update=False):

        # connection state changed?
        if dev_connected == self._dev_connected[device_name]:
            conn_changed = False
        else:
            conn_changed = True

        # Return dict indexed with reason
        data, updated = bbb.read(device_name, force_update=force_update)

        # return if nothing changed at all
        if not updated and not conn_changed:
            return

        for reason, new_value in data.items():

            if self._prucqueue and App._setpoint_regexp.match(reason):
                # While there are pending write operations in the queue we
                # cannot update setpoint variables or we will spoil the
                # accepted value in the write method.
                continue

            # check if specific reason value did change
            if updated:
                value_changed = self._check_value_changed(reason, new_value)
            else:
                value_changed = False

            # if it changed and is not None, update its PV database entry
            if value_changed and new_value is not None:
                self.driver.setParam(reason, new_value)
                self.driver.updatePV(reason)

            # update alarm state
            if conn_changed:
                if dev_connected:
                    self.driver.setParamStatus(
                        reason, _Alarm.NO_ALARM, _Severity.NO_ALARM)
                else:
                    self.driver.setParamStatus(
                        reason, _Alarm.TIMEOUT_ALARM, _Severity.INVALID_ALARM)

        # update device connection state
        self._dev_connected[device_name] = dev_connected

    def _check_value_changed(self, reason, new_value):
        old_value = self.driver.getParam(reason)
        # NOTE: convert all WfmData to numpy from bottom up to here!
        if isinstance(new_value, _np.ndarray):
            if not isinstance(old_value, _np.ndarray):
                # NOTE: this might be necessary only in the initialization.
                old_value = _np.array(old_value)
            if not _np.all(old_value == new_value):
                # NOTE: for a 4000-element numpy array comparison in
                # a standard intel CPU takes:
                # 1) np.all(a == b) -> ~4 us
                # 2) np.allclose(a, b) -> 30 us
                # 3) np.array_equal(a, b) -> ~4 us
                # NOTE: it is not clear if numpy comparisons to avoid updating
                # this PV do improve performance. how long does it take for
                # pcaspy to update the numpy PV?
                return True
            else:
                return False
        else:
            if new_value != old_value:
                return True
        return False
