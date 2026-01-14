"""Main Module of the IOC Logic."""

import logging as _log
import time as _time

from siriuspy import epics as _epics
from siriuspy.callbacks import Callback as _Callback
from siriuspy.devices import DeviceSet as _DeviceSet

from . import csdev as _csdev


class App(_DeviceSet, _Callback):
    """Main Class of the IOC Logic."""

    SCAN_FREQUENCY = 1  # [Hz]

    def __init__(self, driver=None):
        """Initialize the instance."""
        _Callback.__init__(self)

        self.driver = driver
        devs = tuple()
        _DeviceSet.__init__(self, devices=devs)

        self._pvs_database = _csdev.pvs_database
        # use pyepics recommendations for threading
        _epics.ca.use_initial_context()

        # status scanning
        self.quit = False
        self.scanning = False
        self.thread_check_conns = _epics.ca.CAThread(
            target=self._run_updates, daemon=True)
        self.thread_check_conns.start()

    def init_database(self):
        """Set initial PV values."""
        pvn2vals = {
            'TimestampUpdate-Mon': _time.time(),
            'Log-Mon': 'Started.',
        }
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

            # update sections status
            self.run_callbacks('TimestampUpdate-Mon', _time.time())
            self.run_callbacks('ConnStatus-Mon', self.connected)

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
