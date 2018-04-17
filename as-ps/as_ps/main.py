"""Main application."""

import time as _time
import numpy as _np
import logging as _log
from collections import deque as _deque
from collections import namedtuple as _namedtuple
from threading import Thread as _Thread
from threading import Lock as _Lock

from pcaspy import Alarm as _Alarm
from pcaspy import Severity as _Severity

# import as_ps.pvs as _pvs
import siriuspy as _siriuspy
import siriuspy.util as _util

__version__ = _util.get_last_commit_hash()

FREQUENCY_SCAN = 10.0  # [Hz]
FREQUENCY_RAMP = 2.0  # [Hz]


class App:
    """Responsible for updating the IOC database.

    Update values and parameters such as alarms.

    Issues 2 threads:
        - thread to queue all request to devices underneath it.
        - thread to enqueue a read request for each device (10 Hz per dev)
    """

    # Queue size over this value is interpreted as communication overflow
    QUEUE_SIZE_OVERFLOW = 500

    Operation = _namedtuple('Operation', 'function, kwargs')

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
        self._op_deque = _deque()  # TODO: is dequeu thread-safe ?!
        self._lock = _Lock()

        # scan
        # TODO: there should be one _scan_interval for each BBB !!!
        # rethink IOC duties.
        self._scan_interval = 1.0/FREQUENCY_SCAN
        self.scan = True

        # read Constants once and for all
        self._constants_update = False

        # symbol to threads that execute BSMP blocking operations
        self._op_thread = None

    # --- public interface ---

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
        n = self.queue_length()
        if n > 0:
            # check if instance of exec_operation
            if self._op_thread is None or \
               not self._op_thread.is_alive():
                # get operation
                op = self.queue_pop()
                self._op_thread = _Thread(
                    target=self._exec_operation,
                    args=(op, ), daemon=True)
                self._op_thread.start()
        _time.sleep(1.0/FREQUENCY_SCAN/10.0)  # sleep a little.

    def _exec_operation(self, op):
        time_init = _time.time()
        if op.kwargs:
            op.function(**op.kwargs)
        else:
            op.function()
        App._print_scan(time_init, op)

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
        if 'OpMode-Sel' in reason:
            # TODO: workaround to be cleaned.
            self._write_to_device(device_name=device, field=field, value=value)
        else:
            op = App.Operation(
                self._write_to_device,
                {'device_name': device, 'field': field, 'value': value})
            self.queue_append(op)
        return

    def scan_bbb(self, bbb):
        """Scan PRU and power supply devices."""
        # self._scan_pru(bbb.controller.pru)
        for psname, ps in bbb.power_supplies.items():
            self._set_device_setpoints(psname, ps)
            self._set_device_variables(psname, ps)
        self.driver.updatePVs()
        return

    def enqueue_scan(self):
        """Enqueue read methods run as a thread."""
        while self.scan:
            t = _time.time()

            # scan PRU
            for bbb in self.bbblist:
                self._scan_pru(bbb.controller.pru)

            # enqueue read_constants, if necessary
            if not self._constants_update:
                op = App.Operation(self._read_constants, {})
                self.queue_append(op)

            # enqueue a scan for each bbb
            for bbb in self.bbblist:
                op = App.Operation(self.scan_bbb, {'bbb': bbb})
                self.queue_append(op)

            # wait until proper scan interval is reached
            dt = _time.time() - t
            _time.sleep(abs(self._scan_interval - dt))

    # --- private methods ---

    def queue_pop(self):
        """Queue pop operation."""
        self._lock.acquire(blocking=True)
        op = self._op_deque.popleft() if self._op_deque else None
        self._lock.release()
        return op

    def queue_append(self, op):
        """Right-append operation to queue."""
        self._lock.acquire(blocking=True)
        is_ok = len(self._op_deque) < App.QUEUE_SIZE_OVERFLOW
        if is_ok:
            self._op_deque.append(op)
        self._lock.release()
        # TODO:  do something in IOC database to indicate boundless growth of
        # deque. Maybe a new bit-PV 'CommOverflow-Mon' or use one bit of the
        # power supplies interlock.
        # print('queue len: {}'.format(len(self._op_deque)))
        pass

    def queue_length(self):
        """Return length of queue."""
        self._lock.acquire(blocking=True)
        n = len(self._op_deque)
        self._lock.release()
        return n

    # def queue_appendleft(self, op):
    #     """Left-append operation to queue."""
    #     if self._is_queue_ok():
    #         self._op_deque.appendleft(op)

    # def _is_queue_ok(self):
    #     # TODO:  do something in IOC database to indicate boundless growth of
    #     # deque. Maybe a new bit-PV 'CommOverflow-Mon' or use one bit of the
    #     # power supplies interlock.
    #     # print('queue len: {}'.format(len(self._op_deque)))
    #     return len(self._op_deque) < App.QUEUE_SIZE_OVERFLOW

    def _read_constants(self):
        for psname, bbb in self._bbb_devices.items():
            version = bbb[psname].read('Version-Cte')
            reason = psname + ':Version-Cte'
            self.driver.setParam(reason, version)
        self.driver.updatePVs()
        self._constants_update = True

    def _write_to_device(self, device_name, field, value):
        """Write value to device field."""
        # TODO: use logging
        bbb = self._bbb_devices[device_name]
        reason = device_name + ':' + field
        if bbb.write(device_name, field, value):
            if isinstance(value, _np.ndarray):
                _log.info("[{:.2s}] - {:.32s}".format('W ', reason))
            else:
                _log.info("[{:.2s}] - {:.32s} = {:.50s}".format(
                    'W ', reason, str(value)))
            self.driver.setParamStatus(
                reason, _Alarm.NO_ALARM, _Severity.NO_ALARM)
        else:
            _log.warning("[!!] - {:.32s} = {:.50s} - SERIAL ERROR".format(
                reason, str(value)))
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
        if not device.connected or variables is None:
            self._set_fields_invalid(device_name, device.database.keys())
        elif device.connected and variables is not None:
            self._set_fields(device_name, variables)
        else:
            # Log
            pass

    def _scan_pru(self, pru):
        # Scan PRU
        if pru.sync_status == pru._SYNC_ON:
            self._scan_interval = 1.0/FREQUENCY_RAMP  # Ramp interval
        else:
            self._scan_interval = 1.0/FREQUENCY_SCAN  # Scan interval

    @staticmethod
    def _print_scan(t, op):
        # TEMPORARY UTILITY
        return
        dt = _time.time() - t
        strop = str(op)
        _, *strop = strop.split('.')
        strop, *_ = strop[0].split(' ')
        _log.info(
            'operation "{}" processed in {:.4f} ms'.format(strop, 1000*dt))
