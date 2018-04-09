"""Main application."""

import time as _time
import numpy as _np
from collections import deque as _deque
from collections import namedtuple as _namedtuple

from pcaspy import Alarm as _Alarm
from pcaspy import Severity as _Severity

# import as_ps.pvs as _pvs
import siriuspy as _siriuspy
import siriuspy.util as _util

# Coding guidelines:
# =================
# 01 - pay special attention to code readability
# 02 - simplify logic as much as possible
# 03 - unroll expressions in order to simplify code
# 04 - dont be afraid to generate seemingly repetitive flat code
#      (they may be easier to read!)
# 05 - 'copy and paste' is your friend and it allows you to code 'repeatitive'
#      (but clearer) sections fast.
# 06 - be consistent in coding style (variable naming, spacings, prefixes,
#      suffixes, etc)

__version__ = _util.get_last_commit_hash()


class App:
    """Responsible for updating the IOC database.

    Update values and parameters such as alarms.

    Issues 2 threads:
        - thread to queue all request to devices underneath it.
        - thread to enqueue a read request for each device (10 Hz per dev)
    """

    Operation = _namedtuple('Operation', 'device, function, kwargs')

    def __init__(self, driver, devices, database, prefix):
        """Create Power Supply controllers."""
        self._devices = devices
        self._driver = driver
        self._op_deque = _deque()
        self.scan = True
        # Print info about the IOC
        _siriuspy.util.print_ioc_banner(
            ioc_name='BeagleBone',
            # db=App.pvs_database[_pvs._PREFIX],
            db=database[prefix],
            description='BeagleBone Power Supply IOC',
            version=__version__,
            prefix=prefix)
        _siriuspy.util.save_ioc_pv_list('as-ps',
                                        ('',
                                         prefix),
                                        database[prefix])

    @property
    def driver(self):
        """Pcaspy driver."""
        return self._driver

    @property
    def devices(self):
        """Devices."""
        return self._devices

    def process(self, interval):
        """Process method."""
        if self._op_deque:
            op = self._op_deque.popleft()
            if op.kwargs:
                op.function(**op.kwargs)
            else:
                op.function()
        _time.sleep(0.01)

    def read(self, reason):
        """Read from database."""
        print("[{:s}] - {:32s} = {}".format(
            'R', reason, self.driver.getParam(reason)))
        return None

    def write(self, reason, value):
        """Enqueue write request."""
        split = reason.split(':')
        device = ':'.join(split[:2])
        field = split[-1]
        op = App.Operation(device, self._write,
                           {'device': device, 'field': field, 'value': value})
        self._op_deque.appendleft(op)
        return

    def _write(self, device, field, value):
        """Write value to device field."""
        reason = device + ':' + field
        if self.devices[device].write(field, value):
            print("[{:2s}] - {:32s} = {}".format('W', reason, value))
            self.driver.setParamStatus(
                reason, _Alarm.NO_ALARM, _Severity.NO_ALARM)
        else:
            print("[{:2s}] - {:32s} = {} - SERIAL ERROR".format(
                'W', reason, value))
            self.driver.setParamStatus(
                reason, _Alarm.TIMEOUT_ALARM, _Severity.INVALID_ALARM)
        self.driver.setParam(reason, value)
        self.driver.updatePVs()
        return

    def update_db(self, device_name):
        """Read variables and update DB."""
        dev = self.devices[device_name]
        vars = dev.read_all_variables()
        conn = dev.connected
        if not conn:
            for field in dev.database:
                reason = device_name + ':' + field
                print("[{:2s}] - {:32s} - SERIAL ERROR".format(
                    'RA', reason))
                self.driver.setParamStatus(
                    reason, _Alarm.TIMEOUT_ALARM, _Severity.INVALID_ALARM)
        elif conn and vars is not None:
            for field, value in vars.items():
                reason = device_name + ':' + field
                self.driver.setParam(reason, value)
                self.driver.setParamStatus(
                    reason, _Alarm.NO_ALARM, _Severity.NO_ALARM)
        else:
            print("[RA] - Failed to read {} variables.".format(device_name))
        self.driver.updatePVs()
        return

    def enqueue_scan(self):
        """Enqueue read methods run as a thread."""
        while self.scan:
            for psname, device in self.devices.items():
                op = App.Operation(
                    psname, self.update_db, {'device_name': psname})
                self._op_deque.append(op)
            # _time.sleep(1/len(self.devices))
            _time.sleep(0.1)
