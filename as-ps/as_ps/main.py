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
    """Responsible for updating the IOC database."""

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
        self._psname_2_bbbdev = dict()
        for bbb in self.bbblist:
            for psname in bbb.psnames:
                self._psname_2_bbbdev[psname] = bbb

        # read Constants once and for all
        # self._constants_update = False

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
        """Process IOC updates."""
        for bbb in self.bbblist:
            bbbstate = bbb.read_state()
            for reason, db in bbbstate.items():
                value = db['value']
                if value is not None:
                    self.driver.setParam(reason, value)
                else:
                    # set alarm state
                    pass
        self.driver.updatePVs()
        _time.sleep(1.0/FREQUENCY_SCAN/10.0)  # sleep a little.

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
        self._write_to_device(psname=device, field=field, value=value)
        return None

    # def _read_constants(self):
    #     for psname, bbb in self._psname_2_bbbdev.items():
    #         version = bbb[psname].read('Version-Cte')
    #         reason = psname + ':Version-Cte'
    #         self.driver.setParam(reason, version)
    #     self.driver.updatePVs()
    #     self._constants_update = True

    def _write_to_device(self, psname, field, value):
        """Write value to device field."""
        # TODO: use logging
        bbb = self._psname_2_bbbdev[psname]
        reason = psname + ':' + field
        if bbb.write(psname, field, value):
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

    @staticmethod
    def _print_scan(t, op):
        # TEMPORARY UTILITY
        return
        # dt = _time.time() - t
        strop = str(op)
        _, *strop = strop.split('.')
        strop, *_ = strop[0].split(' ')
        # _log.info(
        #     'operation "{}" processed in {:.4f} ms'.format(strop, 1000*dt))
