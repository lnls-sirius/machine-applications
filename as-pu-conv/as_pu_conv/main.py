"""Main application."""

import time as _time
import logging as _log
import re as _re

from pcaspy import Alarm as _Alarm
from pcaspy import Severity as _Severity

import siriuspy as _siriuspy
import siriuspy.util as _util

from siriuspy.thread import DequeThread as _DequeThread
from siriuspy.namesys import SiriusPVName as _SiriusPVName

from siriuspy.pwrsupply.maepics import PUEpicsConn as _PUEpicsConn
from siriuspy.pwrsupply.maepics import SConvEpics as _SConvEpics


__version__ = _util.get_last_commit_hash()


# Select whether to queue write requests or process them right away.
_USE_WRITE_QUEUE = True

# update frequency of strength PVs
UPDATE_FREQUECY = 10.0  # [Hz]


class App:
    """Responsible for updating the IOC database.

    Update values and parameters such as alarms.
    """

    _setpoint_regexp = _re.compile('^.*-(SP)$')

    def __init__(self, driver, psnames, dbset, prefix):
        """Create Power Supply controllers."""
        self._driver = driver

        # write operation queue
        self._dequethread = _DequeThread() if _USE_WRITE_QUEUE else None

        # mapping device to bbb
        self._psnames = psnames

        # define update interval
        self._interval = 1 / UPDATE_FREQUECY

        # print info about the IOC
        _siriuspy.util.print_ioc_banner(
            ioc_name='AS_PU_Conv',
            db=dbset,
            description='AS PU Conversion IOC',
            version=__version__,
            prefix=prefix)

        # build connectors and streconv dicts
        self._connectors, self._streconvs = \
            self._create_connectors_and_streconv()

    # --- public interface ---

    @property
    def driver(self):
        """Pcaspy driver."""
        return self._driver

    @property
    def psnames(self):
        """Return list of psnames."""
        return self._psnames

    def check_connected(self, psname):
        """Return connection status."""
        streconv = self._streconvs[psname]
        conns = self._connectors[psname]
        if not streconv.connected:
            return False
        for conn in conns.values():
            if not conn.connected:
                return False
        return True

    def process(self):
        """Process all write requests in queue and does a BBB scan."""
        time0 = _time.time()
        if self._dequethread:  # Not None and not empty
            status = self._dequethread.process()
            if status:
                txt = ("[{:.2s}] - new thread started for write queue item. "
                       "items left: {}")
                logmsg = txt.format('Q ', len(self._dequethread))
                _log.info(logmsg)
            for psname in self.psnames:
                self.scan_device(psname)
            _time.sleep(0.050)
        else:
            for psname in self.psnames:
                self.scan_device(psname)
            time1 = _time.time()
            _time.sleep(abs(self._interval-(time1-time0)))

    def read(self, reason):
        """Read from database."""
        return None

    def write(self, reason, value):
        """Enqueue write request."""
        _log.info("[{:.2s}] - {:.32s} = {:.50s}".format(
            'W ', reason, str(value)))
        pvname = _SiriusPVName(reason)
        if _USE_WRITE_QUEUE:
            # NOTE: This modified behaviour is to allow loading
            # global_config to complete without artificial warning
            # messages or unnecessary delays. Whether we should extend
            # it to all power supplies remains to be checked.
            if App._setpoint_regexp.match(reason):
                self.driver.setParam(reason, value)
                self.driver.updatePV(reason)
                operation = (self._write_operation, (pvname, value))
                self._dequethread.append(operation)
                self._dequethread.process()
        else:
            self.driver.setParam(reason, value)
            self.driver.updatePV(reason)
            time0 = _time.time()
            self._write_operation(pvname, value)
            time1 = _time.time()
            _log.info("[{:.2s}] - {:.32s} : {:.50s}".format(
                'T ', reason, '{:.3f} ms'.format((time1-time0)*1000)))

    def scan_device(self, psname):
        """Scan BBB device and update ioc epics DB."""
        # not connected
        if not self.check_connected(psname):
            conns = self._connectors[psname]
            for proptype in conns.keys():
                reason = psname + ':Kick' + proptype
                self.driver.setParamStatus(
                    reason, _Alarm.NO_ALARM, _Severity.NO_ALARM)
            return

        # all connected, calculate strengths
        streconv = self._streconvs[psname]
        conns = self._connectors[psname]
        values = (conns['-SP'].value, conns['-RB'].value, conns['-Mon'].value)
        strength = streconv.conv_current_2_strength(values)

        # update epics database
        for i, proptype in enumerate(conns.keys()):
            reason = psname + ':Kick' + proptype
            self.driver.setParam(reason, strength[i])
            self.driver.updatePV(reason)

    # --- private methods ---

    def _create_connectors_and_streconv(self):
        connectors = dict()
        streconv = dict()
        for psname in self.psnames:
            connectors[psname] = dict()
            connectors[psname]['-SP'] = _PUEpicsConn(psname, '-SP')
            connectors[psname]['-RB'] = _PUEpicsConn(psname, '-RB')
            connectors[psname]['-Mon'] = _PUEpicsConn(psname, '-Mon')
            streconv[psname] = _SConvEpics(psname=psname, proptype='Ref-Mon')
        return connectors, streconv

    def _write_operation(self, pvname, value):
        time0 = _time.time()
        psname = pvname.device_name
        streconv = self._streconvs[psname]
        voltage = streconv.conv_strength_2_current(value)
        conn = self._connectors[psname]['-SP']
        if conn.connected:
            self._connectors[psname]['-SP'].value = voltage
        time1 = _time.time()
        _log.info("[{:.2s}] - {:.32s} : {:.50s}".format(
            'T ', pvname,
            'write operation took {:.3f} ms'.format((time1-time0)*1000)))