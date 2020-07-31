"""Main application."""

import time as _time
import logging as _log
import re as _re
import numpy as _np
from pcaspy import Alarm as _Alarm
from pcaspy import Severity as _Severity

from siriuspy.util import print_ioc_banner as _print_ioc_banner
from siriuspy.util import get_last_commit_hash as _get_last_commit_hash
from siriuspy.thread import DequeThread as _DequeThread
from siriuspy.namesys import SiriusPVName as _SiriusPVName
from siriuspy.pwrsupply.csdev import PSSOFB_MAX_NR_UDC as _PSSOFB_MAX_NR_UDC
from siriuspy.pwrsupply.csdev import UDC_MAX_NR_DEV as _UDC_MAX_NR_DEV


__version__ = _get_last_commit_hash()


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
    """Power Supply IOC Application."""

    _sleep_scan = 0.050  # [s]
    _regexp_setpoint = _re.compile('^.*-(SP|Sel)$')
    _sofb_value_length = _PSSOFB_MAX_NR_UDC * _UDC_MAX_NR_DEV

    def __init__(self, driver, bbblist, dbset, prefix):
        """Init application."""
        # --- init begin

        self._driver = driver

        # flag to indicate sofb processing is taking place
        self._sofb_processing = False

        # write operation queue
        self._dequethread = _DequeThread()

        # mapping device to bbb
        self._bbblist = bbblist
        # NOTE: change IOC to accept only one BBB
        self._sofbmode_sts_pvname = \
            self.bbblist[0].psnames[0] + ':SOFBMode-Sts'

        # build dictionaries
        self._dev2bbb, self._dev2conn, self._interval = \
            self._create_bbb_dev_dict()

        # initializes beaglebones
        for bbb in bbblist:
            bbb.init()

        # -- init end
        print('---\n')

        # print info about the IOC
        _print_ioc_banner(
            ioc_name='PS IOC',
            db=dbset[prefix],
            description='Power Supply IOC (FAC)',
            version=__version__,
            prefix=prefix)

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
        t0_ = _time.time()

        # first process write requests, if any in queue
        if self._dequethread:
            status = self._dequethread.process()
            if status:
                txt = ("[{:.2s}] - new thread started for write queue item. "
                       "items left: {}")
                logmsg = txt.format('Q ', len(self._dequethread))
                _log.info(logmsg)
            # TODO: this sleep seems unnecessary now.
            # test commenting it out!
            _time.sleep(self._sleep_scan)

        # then scan bbb state for updates.
        for bbb in self.bbblist:
            self.scan_bbb(bbb)

        # sleep, if necessary
        t1_ = _time.time()
        if t1_ - t0_ < self._interval:
            _time.sleep(self._interval - (t1_ - t0_))

        # NOTE: measure this interval for various BBBs...
        # _log.info("process.... {:.3f} ms".format(1000*(t1_-t0_)))

    def read(self, reason):
        """Read from database."""
        # _log.info("[{:.2s}] - {:.32s} = {:.50s}".format(
        #     'R ', reason, str(self.driver.getParam(reason))))

    def write(self, reason, value):
        """Enqueue write request."""
        # print('{:<30s} : {:>9.3f} ms'.format(
        #     'IOC.write (beg)', 1e3*(_time.time() % 1)))
        pvname = _SiriusPVName(reason)

        sofb_state = self.driver.getParam(self._sofbmode_sts_pvname)
        ignorestr, wstr = \
            (' (SOFBMode On)', 'W!') if sofb_state and 'SOFB' not in reason \
            else ('', 'W ')

        _log.info("[{:.2s}] - {:.32s} = {:.50s}{}".format(
            wstr, reason, str(value), ignorestr))

        # NOTE: This modified behaviour is to allow loading
        # global_config to complete without artificial warning
        # messages or unnecessary delays. Whether we should extend
        # it to all power supplies remains to be checked.
        if self._check_write_immediate(reason, value):
            self.driver.setParam(reason, value)
            self.driver.updatePV(reason)

        bbb = self._dev2bbb[pvname.device_name]
        operation = (self._write_operation, (bbb, pvname, value))
        self._dequethread.append(operation)

        self._dequethread.process()

    def scan_bbb(self, bbb):
        """Scan BBB devices and update ioc epics DB."""
        for devname in bbb.psnames:
            # forcing scan everytime!
            if not self._sofb_processing:
                self.scan_device(bbb, devname, force_update=True)

    def scan_device(self, bbb, devname, force_update=False):
        """Scan BBB device and update ioc epics DB."""
        dev_connected = \
            bbb.check_connected(devname) and \
            bbb.check_connected_strength(devname)
        self._update_ioc_database(bbb, devname, dev_connected,
                                  force_update)

    # --- private methods ---

    def _create_bbb_dev_dict(self):
        # build _bbb_devices dict
        dev2bbb = dict()
        dev2conn = dict()
        interval = float('Inf')
        for bbb in self.bbblist:
            # get minimum time interval for BBB
            interval = min(interval, bbb.update_interval())
            # create bbb_device dict
            for dev_name in bbb.psnames:
                dev2conn[dev_name] = None
                dev2bbb[dev_name] = bbb
        return dev2bbb, dev2conn, interval

    def _write_operation(self, bbb, pvname, value):
        # NOTE: check if using SiriusPVName subs alters efficiency
        if pvname.endswith('SOFBCurrent-SP'):
            #  signal SOFB processing
            status = self._check_write_sofb(pvname, value)
            if not status:
                _log.info("[{:.2s}] - {:.32s} = {:.50s}".format(
                    'W!', pvname, 'Invalid length!'))
                return
            self._sofb_processing = True

        # process priority changed PVs
        priority_pvs = bbb.write(pvname.device_name, pvname.propty, value)
        for reason, val in priority_pvs.items():
            if val is not None:
                self.driver.setParam(reason, val)
            else:
                self.driver.setParamStatus(
                    reason, _Alarm.TIMEOUT_ALARM, _Severity.INVALID_ALARM)
            self.driver.updatePV(reason)

        # signal end of eventual SOFB processing
        self._sofb_processing = False

        # print('{:<30s} : {:>9.3f} ms'.format(
        #     'IOC.write (end)', 1e3*(_time.time() % 1)))

    def _check_write_immediate(self, reason, value):
        """Check if reason is immediatly writeable."""
        # Accept *-SP and *-Sel right away (not *-Cmd !)
        if not App._regexp_setpoint.match(reason):
            return False
        return self._check_write_sofb(reason, value)

    def _check_write_sofb(self, reason, value):
        # NOTE: check if using SiriusPVName subs alters efficiency
        if not reason.endswith('SOFBCurrent-SP'):
            return True
        value_len = 1 if not \
            isinstance(value, (tuple, list, _np.ndarray)) else len(value)
        return value_len == App._sofb_value_length

    def _update_ioc_database(self, bbb, devname,
                             dev_connected=True,
                             force_update=False):

        # connection state changed?
        if dev_connected == self._dev2conn[devname]:
            conn_changed = False
        else:
            conn_changed = True

        # Return dict indexed with reason
        data, updated = bbb.read(devname, force_update=force_update)

        # return if nothing changed at all
        if not updated and not conn_changed:
            return

        # get name of strength
        strength_name = bbb.strength_name(devname)

        for reason, new_value in data.items():

            # if sofb processing abort update
            if self._sofb_processing:
                return

            # set strength limits
            if strength_name is not None and strength_name in reason:
                lims = bbb.strength_limits(devname)
                if None not in lims:
                    kwargs = self.driver.getParamInfo(reason)
                    kwargs.update({
                        'hihi': lims[1], 'high': lims[1], 'hilim': lims[1],
                        'lolim': lims[0], 'low': lims[0], 'lolo': lims[0]})
                    self.driver.setParamInfo(reason, kwargs)
                    self.driver.updatePV(reason)

            if self._dequethread and App._regexp_setpoint.match(reason):
                # While there are pending write operations in the queue we
                # cannot update setpoint variables or we will spoil the
                # accepted value in the write method.
                continue

            # check if specific reason value did change
            if updated:
                value_changed = self._check_value_changed(reason, new_value)
            else:
                value_changed = False

            # if it changed and is not None, set new value in PV database entry
            if value_changed and new_value is not None:
                self.driver.setParam(reason, new_value)

            # update alarm state
            if conn_changed:
                if dev_connected:
                    self.driver.setParamStatus(
                        reason, _Alarm.NO_ALARM, _Severity.NO_ALARM)
                else:
                    self.driver.setParamStatus(
                        reason, _Alarm.TIMEOUT_ALARM, _Severity.INVALID_ALARM)

            # if reason state was set, update its PV db entry
            if value_changed or conn_changed:
                self.driver.updatePV(reason)

        # update device connection state
        self._dev2conn[devname] = dev_connected

    def _check_value_changed(self, reason, new_value):
        if new_value is None:
            return False
        old_value = self.driver.getParam(reason)
        try:
            if isinstance(old_value, (tuple, list, _np.ndarray)) or \
                    isinstance(new_value, (tuple, list, _np.ndarray)):
                # transform to numpy arrays
                if not isinstance(old_value, _np.ndarray):
                    old_value = _np.array(old_value)
                if not isinstance(new_value, _np.ndarray):
                    new_value = _np.array(new_value)
                # compare
                if len(old_value) != len(new_value) or \
                        not _np.all(old_value == new_value):
                    # NOTE: for a 4000-element numpy array comparison in
                    # a standard intel CPU takes:
                    # 1) np.all(a == b) -> ~4 us
                    # 2) np.allclose(a, b) -> 30 us
                    # 3) np.array_equal(a, b) -> ~4 us
                    # NOTE: it is not clear if numpy comparisons to avoid
                    # updating this PV do improve performance.
                    # how long does it take for pcaspy to update the numpy PV?
                    return True
                else:
                    return False
            else:
                # simple type comparison
                return new_value != old_value
        except Exception as exception:
            print()
            print('--- debug ---')
            print('exception : {}'.format(type(exception)))
            print('reason    : {}'.format(reason))
            print('old_value : {}'.format(str(old_value)[:1000]))
            print('new_value : {}'.format(str(new_value)[:1000]))
            print(' !!!')
            return True
