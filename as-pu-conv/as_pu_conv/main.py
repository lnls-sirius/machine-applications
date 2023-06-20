"""Main application."""

import time as _time
import logging as _log
import re as _re

from pcaspy import Alarm as _Alarm
from pcaspy import Severity as _Severity

import siriuspy as _siriuspy
import siriuspy.util as _util

from siriuspy.thread import QueueThreads as _QueueThreads
from siriuspy.namesys import SiriusPVName as _SiriusPVName

from siriuspy.devices import PSProperty as _PSProperty
from siriuspy.devices import StrengthConv as _StrengthConv


__version__ = _util.get_last_commit_hash()


# Select whether to queue write requests or process them right away.
_USE_WRITE_QUEUE = True

# update frequency of strength PVs
UPDATE_FREQUECY = 10.0  # [Hz]


class App:
    """Responsible for updating the IOC database.

    Update values and parameters such as alarms.
    """

    _regexp_setpoint = _re.compile('^.*-(SP)$')

    def __init__(self, driver, psnames, dbset, prefix):
        """Create Power Supply controllers."""
        self._driver = driver

        # write operation queue
        self._queuethread = _QueueThreads() if _USE_WRITE_QUEUE else None

        # mapping device to bbb
        self._psnames = [_SiriusPVName(psn) for psn in psnames]

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
        t0_ = _time.time()
        if self._queuethread is not None and self._queuethread.qsize():
            status = self._queuethread.process(block=False)
            if status:
                txt = ("[{:.2s}] - new thread started for write queue item. "
                       "items left: {}")
                logmsg = txt.format('Q ', self._queuethread.qsize())
                _log.info(logmsg)
            for psname in self.psnames:
                self.scan_device(psname)
            _time.sleep(0.050)
        else:
            for psname in self.psnames:
                self.scan_device(psname)
            t1_ = _time.time()
            if t1_ - t0_ < self._interval:
                _time.sleep(self._interval - (t1_ - t0_))

    def read(self, reason):
        """Read from database."""
        _ = reason
        return None

    def write(self, reason, value):
        """Enqueue write request."""
        _log.info("[{:.2s}] - {:.36s} = {:.50s}".format(
            'W ', reason, str(value)))
        pvname = _SiriusPVName(reason)
        if _USE_WRITE_QUEUE:
            # NOTE: This modified behaviour is to allow loading
            # global_config to complete without artificial warning
            # messages or unnecessary delays. Whether we should extend
            # it to all power supplies remains to be checked.
            if App._regexp_setpoint.match(reason):
                self.driver.setParam(reason, value)
                self.driver.updatePV(reason)
                operation = (self._write_operation, (pvname, value))
                self._queuethread.put(operation, block=False)
                self._queuethread.process()
        else:
            self.driver.setParam(reason, value)
            self.driver.updatePV(reason)
            t0_ = _time.time()
            self._write_operation(pvname, value)
            t1_ = _time.time()
            _log.info("[{:.2s}] - {:.36s} : {:.50s}".format(
                'T ', reason, '{:.3f} ms'.format((t1_ - t0_)*1000)))

    def scan_device(self, psname):
        """Scan BBB device and update ioc epics DB."""
        # not connected
        if not self.check_connected(psname):
            conns = self._connectors[psname]
            for proptype in conns.keys():
                reason = psname.substitute(
                    propty_name=psname.propty_name+'Kick',
                    propty_suffix=proptype)
                self.driver.setParamStatus(
                    reason, _Alarm.NO_ALARM, _Severity.NO_ALARM)
            return

        # all connected, calculate strengths
        streconv = self._streconvs[psname]
        conn = self._connectors[psname]
        limits = conn['SP'].limits
        curr0 = conn['SP'].value
        curr1 = conn['RB'].value
        curr2 = conn['Mon'].value
        curr3 = limits[0]
        curr4 = limits[-1]

        # NOTE: temporary fix
        if curr3 != curr3:
            curr3 = 0
        if curr4 != curr4:
            curr4 = 10000

        values = (curr0, curr1, curr2, curr3, curr4)
        # NOTE: investigate!
        #
        # usr/local/lib/python3.6/site-packages/epics/ca.py:1507:
        # UserWarning: ca.get('SI-01SA:PU-InjNLKckr:Voltage-Mon') timed out
        # after 1.00 seconds.
        # sirius-ioc-as-pu-conv.py[11332]:   warnings.warn(msg %
        # (name(chid), timeout))
        # File "/usr/local/lib/python3.6/site-packages/siriuspy/magnet/excdata.py",
        # line 173, in _calc_interp
        # xvals, xtab, ytab, left=float('nan'), right=float('inf'))
        # File "<__array_function__ internals>", line 6, in interp
        # File "/usr/local/lib/python3.6/site-packages/numpy/lib/function_base.py",
        # line 1403, in interp
        # sirius-ioc-as-pu-conv.py[11332]: return interp_func(x, xp, fp, left, right)
        # TypeError: Cannot cast array data from dtype('O') to dtype('float64')
        # according to the rule 'safe'
        try:
            strengths = streconv.conv_current_2_strength(values)
        except TypeError:
            print('Could not convert voltage to strength!')
            strengths = None

        if strengths is None or None in strengths:
            slims = None
        else:
            slims = strengths[-2:]
            if slims[0] > slims[1]:
                slims = slims[1], slims[0]

        # update SP, RB and Mon epics database
        for i, proptype in enumerate(conn.keys()):
            reason = psname.substitute(
                propty_name=psname.propty_name+'Kick',
                propty_suffix=proptype)
            if slims is None:
                self.driver.setParamStatus(
                    reason, _Alarm.TIMEOUT_ALARM, _Severity.INVALID_ALARM)
            else:
                # update value
                self.driver.setParam(reason, strengths[i])
                # update limits
                kwargs = self.driver.getParamInfo(reason)
                kwargs.update({
                    'lolim': slims[0], 'low': slims[0], 'lolo': slims[0],
                    'hihi': slims[1], 'high': slims[1], 'hilim': slims[1]})
                self.driver.setParamInfo(reason, kwargs)
                # update alarm
                self.driver.setParamStatus(
                    reason, _Alarm.NO_ALARM, _Severity.NO_ALARM)
            # update PV info
            self.driver.updatePV(reason)

    # --- private methods ---

    def _create_connectors_and_streconv(self):
        connectors = dict()
        streconv = dict()
        for psname in self.psnames:
            connectors[psname] = dict()
            conn = connectors[psname]
            conn['SP'] = _PSProperty(psname, propty='Voltage-SP')
            conn['RB'] = _PSProperty(psname, propty='Voltage-RB')
            conn['Mon'] = _PSProperty(psname, propty='Voltage-Mon')
            streconv[psname] = _StrengthConv(psname, proptype='Ref-Mon')
        return connectors, streconv

    def _write_operation(self, pvname, value):
        t0_ = _time.time()
        psname = pvname.device_name
        if 'CCoil' in pvname:
            psname += ':' + pvname.propty_name.split('Kick')[0]
        streconv = self._streconvs[psname]
        voltage = streconv.conv_strength_2_current(value)
        conn = self._connectors[psname]['SP']
        if conn.connected:
            self._connectors[psname]['SP'].value = voltage
        t1_ = _time.time()
        _log.info("[{:.2s}] - {:.36s} : {:.50s}".format(
            'T ', pvname,
            'write operation took {:.3f} ms'.format((t1_-t0_)*1000)))
