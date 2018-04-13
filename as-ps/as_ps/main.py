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

    Operation = _namedtuple('Operation', 'function, kwargs')

    def __init__(self, driver, bbblist, database, prefix):
        """Create Power Supply controllers."""
        # self._devices = devices
        self._driver = driver
        # Mapping device to bbb
        self._bbblist = bbblist
        # Map psname to bbb
        self._bbb_devices = dict()
        for bbb in self.bbblist:
            for psname in bbb.psnames:
                self._bbb_devices[psname] = bbb
        self._op_deque = _deque()
        self._scan_interval = 0.1
        self.scan = True

        # Read Constants
        for psname, bbb in self._bbb_devices.items():
            version = bbb[psname].read('Version-Cte')
            reason = psname + ':Version-Cte'
            self.driver.setParam(reason, version)
        self.driver.updatePVs()

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
    def bbblist(self):
        """BBBs."""
        return self._bbblist

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
        print("[{:.2s}] - {:.32s} = {:.50s}".format(
            'R ', reason, str(self.driver.getParam(reason))))
        return None

    def write(self, reason, value):
        """Enqueue write request."""
        split = reason.split(':')
        device = ':'.join(split[:2])
        field = split[-1]
        op = App.Operation(
            self._write,
            {'device_name': device, 'field': field, 'value': value})
        self._op_deque.appendleft(op)
        return

    def _write(self, device_name, field, value):
        """Write value to device field."""
        bbb = self._bbb_devices[device_name]
        reason = device_name + ':' + field
        if bbb.write(device_name, field, value):
            if isinstance(value, _np.ndarray):
                print("[{:.2s}] - {:.32s}".format('W ', reason))
            else:
                print("[{:.2s}] - {:.32s} = {:50s}".format(
                    'W ', reason, str(value)))
            self.driver.setParamStatus(
                reason, _Alarm.NO_ALARM, _Severity.NO_ALARM)
        else:
            print("[{:.2s}] - {:.32s} = {:.50s} - SERIAL ERROR".format(
                'W ', reason, str(value)))
            self.driver.setParamStatus(
                reason, _Alarm.TIMEOUT_ALARM, _Severity.INVALID_ALARM)
        self.driver.setParam(reason, value)
        self.driver.updatePVs()
        return

    def _set_fields(self, device_name, fields_dict):
        """Update fields of db.

        `fields` is a dict with fields as key
        """
        for field, value in fields_dict.items():
            reason = device_name + ':' + field
            self.driver.setParam(reason, value)
            self.driver.setParamStatus(
                reason, _Alarm.NO_ALARM, _Severity.NO_ALARM)

    def _set_fields_invalid(self, device_name, fields_list):
        """Set fields to invalid."""
        for field in fields_list:
            reason = device_name + ':' + field
            self.driver.setParamStatus(
                reason, _Alarm.TIMEOUT_ALARM, _Severity.INVALID_ALARM)

    def _set_device_setpoints(self, device_name, device):
        fields = dict()
        fields.update(device.read_setpoints())
        fields.update(device.read_status())
        self._set_fields(device_name, fields)

    def _set_device_variables(self, device_name, device):
        variables = device.read_ps_variables()
        if not device.connected:
            self._set_fields_invalid(device_name, device.database.keys())
        elif device.connected and variables is not None:
            self._set_fields(device_name, variables)
        else:
            # Log
            pass

    def _scan_pru(self, pru):
        # Scan PRU
        if pru.sync_status == pru._SYNC_ON:
            self._scan_interval = 1
        else:
            self._scan_interval = 0.1

    def scan_bbb(self, bbb):
        """Scan devices and PRU."""
        self._scan_pru(bbb.pru)
        for psname, ps in bbb.power_supplies.items():
            self._set_device_setpoints(psname, ps)
            self._set_device_variables(psname, ps)
        self.driver.updatePVs()
        return

    def enqueue_scan(self):
        """Enqueue read methods run as a thread."""
        while self.scan:
            for bbb in self.bbblist:
                op = App.Operation(self.scan_bbb, {'bbb': bbb})
                self._op_deque.append(op)
            # _time.sleep(1/len(self.devices))
            _time.sleep(self._scan_interval)
