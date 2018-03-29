"""Main application."""

import time as _time
import numpy as _np
from collections import deque as _deque
from collections import namedtuple as _namedtuple

from pcaspy import Alarm as _Alarm
from pcaspy import Severity as _Severity

# import as_ps.pvs as _pvs
import siriuspy as _siriuspy
from siriuspy.bsmp import SerialError as _SerialError
from siriuspy.pwrsupply.controller import InvalidValue as _InvalidValue
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
        # if not self._simulate:
        #     self._serial = PRU()
        #     # Temporary fix for test benches
        #     if self.bbbname == 'BO-Glob:CO-BBB-T1':
        #         addresses = (1, 2)
        #     elif self.bbbname == 'BO-Glob:CO-BBB-T2':
        #         addresses = (5, 6)
        #     for i, address in enumerate(addresses):
        #         self.devices[self._psnames[i]] = \
        #             PowerSupply(self._serial, address)
        # else:
        #     raise NotImplementedError()

    @property
    def driver(self):
        """Pcaspy driver."""
        return self._driver

    @property
    def devices(self):
        """Devices."""
        return self._devices

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
            self.driver.setParam(reason, value)
        else:
            print("[{:2s}] - {:32s} = {} - SERIAL ERROR".format(
                'W', reason, value))
            self.driver.setParamStatus(
                reason, _Alarm.TIMEOUT_ALARM, _Severity.INVALID_ALARM)
        # try:
        #     self.devices[device].write(field, value)
        # except _InvalidValue:
        #     print("[{:s}] - {:32s} = {} - INVALID VALUE".format(
        #         'W', reason, value))
        #     self.driver.setParamStatus(
        #         reason, _Alarm.TIMEOUT_ALARM, _Severity.INVALID_ALARM)
        # except _SerialError:
        #     print("[{:s}] - {:32s} = {} - SERIAL ERROR".format(
        #         'W', reason, value))
        #     self.driver.setParamStatus(
        #         reason, _Alarm.TIMEOUT_ALARM, _Severity.TIMEOUT_ALARM)
        # else:
        #     print("[{:s}] - {:32s} = {}".format('W', reason, value))
        #     self.driver.setParamStatus(
        #         reason, _Alarm.NO_ALARM, _Severity.NO_ALARM)
        #     self.driver.setParam(reason, value)
        self.driver.updatePVs()
        return

    def update_db(self, device_name):
        """Read variables and update DB."""
        dev = self.devices[device_name]
        vars = dev.read_all_variables()
        conn = dev.connected
        if not conn:
            for field in dev.device.database:
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

    def process(self, interval):
        """Process method."""
        if self._op_deque:
            op = self._op_deque.popleft()
            if op.kwargs:
                op.function(**op.kwargs)
            else:
                op.function()
        _time.sleep(0.01)

    def enqueue_scan(self):
        """Enqueue read methods run as a thread."""
        while self.scan:
            for psname, device in self.devices.items():
                op = App.Operation(
                    psname, self.update_db, {'device_name': psname})
                self._op_deque.append(op)
            _time.sleep(0.25)


# class App:
#     """App class."""
#
#     ps_devices = None
#     pvs_database = None
#
#     def __init__(self, driver):
#         """Init."""
#         _siriuspy.util.print_ioc_banner(
#             ioc_name='BeagleBone',
#             db=App.pvs_database[_pvs._PREFIX],
#             description='BeagleBone Power Supply IOC',
#             version=__version__,
#             prefix=_pvs._PREFIX)
#         _siriuspy.util.save_ioc_pv_list('as-ps',
#                                         ('',
#                                          _pvs._PREFIX),
#                                         App.pvs_database[_pvs._PREFIX])
#         self._driver = driver
#         # stores PS database
#         psname = tuple(_pvs.ps_devices.keys())[0]
#         self._ps_db = _pvs.ps_devices[psname].get_database()
#         # add callbacks
#         for psname in _pvs.ps_devices:
#             _pvs.ps_devices[psname].add_callback(self._mycallback)
#
#     @staticmethod
#     def init_class(bbblist, simulate=True):
#         """Init class."""
#         App.ps_devices = _pvs.get_ps_devices(bbblist, simulate=simulate)
#         App.pvs_database = _pvs.get_pvs_database(bbblist, simulate=simulate)
#
#     @staticmethod
#     def get_pvs_database():
#         """Get pvs database."""
#         if App.pvs_database is None:
#             App.pvs_database = _pvs.get_pvs_database()
#         return App.pvs_database
#
#     @staticmethod
#     def get_ps_devices():
#         """Get ps devices."""
#         if App.ps_devices is None:
#             App.ps_devices = _pvs.get_ps_devices()
#         return App.ps_devices
#
#     @property
#     def driver(self):
#         """Driver method."""
#         return self._driver
#
#     def process(self, interval):
#         """Process method."""
#         _time.sleep(interval)
#
#     def read(self, reason):
#         """Read pv method."""
#         return None
#
#     def write(self, reason, value):
#         """Write pv method."""
#         if isinstance(value, (int, float)):
#             print('write', reason, value)
#         else:
#             print('write', reason)
#         parts = reason.split(':')
#         propty = parts[-1]
#         psname = ':'.join(parts[:2])
#         ps = _pvs.ps_devices[psname]
#         status = ps.write(field=propty, value=value)
#         if status is not None:
#             self._driver.setParam(reason, value)
#             self._driver.updatePVs()
#
#         return True
#
#     def _mycallback(self, pvname, value, **kwargs):
#         """Mycallback method."""
#         # print('{0:<15s}: '.format('ioc callback'), pvname, value)
#         reason = pvname
#
#         # if ControllerIOC is disconnected to ControllerPS
#         if _PowerSupply.CONNECTED in reason:
#             self._set_connected_pvs(reason, value)
#             self._driver.updatePVs()
#             return
#
#         prev_value = self._driver.getParam(reason)
#         if isinstance(value, _np.ndarray):
#             if _np.any(value != prev_value):
#                 self._driver.setParam(reason, value)
#                 self._driver.updatePVs()
#         else:
#             if value != prev_value:
#                 self._driver.setParam(reason, value)
#                 self._driver.updatePVs()
#
#     def _set_connected_pvs(self, reason, value):
#         psname = reason.replace(':'+_PowerSupply.CONNECTED,'')
#         if value is True:
#             print('{} connected.'.format(psname))
#         else:
#             print('{} disconnected.'.format(psname))
#         if value is True:
#             alarm = _Alarm.NO_ALARM
#             severity = _Severity.NO_ALARM
#         else:
#             alarm = _Alarm.TIMEOUT_ALARM
#             severity = _Severity.INVALID_ALARM
#         for field in self._ps_db:
#             pvname = reason.replace(_PowerSupply.CONNECTED, field)
#             # print(pvname)
#             # value = self._driver.getParam(pvname)
#             # self._driver.setParam(pvname, value)
#             self._driver.setParamStatus(pvname, alarm, severity)
