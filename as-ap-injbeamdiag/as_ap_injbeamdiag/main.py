"""Main Module of the IOC Logic."""

import logging as _log
import time as _time

import epics as _epics
import numpy as _np

from siriuspy.callbacks import Callback as _Callback
from siriuspy.devices import (
    DeviceSet as _DeviceSet,
    SOFB as _SOFB,
    DCCT as _DCCT,
)

from . import csdev as _csdev


class SOFTDevices(_DeviceSet):
    """."""

    def __init__(self):
        """Initialize the instance."""
        props = ('RawReadings-Mon',)
        self.dcct_bo = _DCCT(_DCCT.DEVICES.BO, props2init=props)
        props = ('SPassOrbX-Mon', 'SPassOrbY-Mon', 'SPassSum-Mon')
        # self.trajx_tb = _np.
        self.sofb_tb = _SOFB(_SOFB.DEVICES.TB, props2init=props)
        self.sofb_tb.pv_object('SPassSum-Mon').add_callback(
            self._update_tb_spass
        )
        props = ('MTurnOrbX-Mon', 'MTurnOrbY-Mon', 'MTurnSum-Mon')
        self.sofb_bo = _SOFB(_SOFB.DEVICES.BO, props2init=props)
        devs = (self.sofb_tb, self.sofb_bo)
        _DeviceSet.__init__(self, devices=devs)

    def _update_tb_spass(self):
        """."""


class App(_Callback):
    """Main Class of the IOC Logic."""

    SCAN_FREQUENCY = 1  # [Hz]

    def __init__(self, driver=None):
        """Initialize the instance."""
        _Callback.__init__(self)

        self.driver = driver
        self.devices = SOFTDevices()

        self._pvs_database = _csdev.pvs_database
        # use pyepics recommendations for threading
        _epics.ca.use_initial_context()

        # status scanning
        self.quit = False
        self.scanning = False
        self.thread_check_conns = _epics.ca.CAThread(
            target=self._run_updates, daemon=True
        )
        self.thread_check_conns.start()

    def init_database(self):
        """Set initial PV values."""
        pvn2vals = {'TimestampUpdate-Mon': _time.time(), 'Log-Mon': 'Started.'}
        for pvn, val in pvn2vals.items():
            self.run_callbacks(pvn, val)

    @property
    def pvs_database(self):
        """Return pvs_database."""
        return self._pvs_database

    def process(self, interval):
        """Sleep."""
        _time.sleep(interval)

    def read(self, reason):
        """Read PV from database."""
        # implementation here
        # The default behavior is to return None and let the driver read
        # from the database.
        value = None
        return value

    def write(self, reason, value):
        """Write PV in the model."""
        # implementation here
        # this should be used in case PV state change.
        return True  # return True for successful write and False otherwise.

    def _run_updates(self):
        # scan
        tplanned = 1.0 / App.SCAN_FREQUENCY
        while not self.quit:
            if not self.scanning:
                _time.sleep(tplanned)
                continue

            _t0 = _time.time()

            # update TimestampUpdate-Mon
            self.run_callbacks('TimestampUpdate-Mon', _time.time())

            # update DevsConnStatus-Mon
            if self.devices.connected:
                self.run_callbacks(
                    'DevsConnStatus-Mon', _csdev.Const.DisconnConn.Connected
                )
            else:
                self.run_callbacks(
                    'DevsConnStatus-Mon', _csdev.Const.DisconnConn.Disconnected
                )
                logmsg = 'ERR: Disconnected PVs: ' + ' '.join(
                    self.devices.disconnected_pvnames
                )
                self._update_log(logmsg)

            # time mgmnt
            ttook = _time.time() - _t0
            tsleep = tplanned - ttook
            if tsleep > 0:
                _time.sleep(tsleep)
            else:
                logstr = (
                    'Connections check took more than planned... '
                    '{0:.3f}/{1:.3f} s'.format(ttook, tplanned)
                )
                _log.warning(logstr)

    def _update_log(self, msg):
        if 'ERR' in msg:
            _log.error(msg[4:])
        elif 'FATAL' in msg:
            _log.error(msg[6:])
        elif 'WARN' in msg:
            _log.warning(msg[5:])
        else:
            _log.info(msg)
        self.run_callbacks('Log-Mon', msg)
