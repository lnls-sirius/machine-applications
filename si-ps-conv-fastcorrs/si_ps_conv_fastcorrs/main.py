"""Main application."""

import time as _time
import logging as _log

from pcaspy import Alarm as _Alarm
from pcaspy import Severity as _Severity

import siriuspy as _siriuspy
import siriuspy.util as _util

from siriuspy.thread import LoopQueueThread as _LoopQueueThread, \
    RepeaterThread as _RepeaterThread
from siriuspy.namesys import SiriusPVName as _SiriusPVName

from siriuspy.devices import PSProperty as _PSProperty
from siriuspy.devices import StrengthConv as _StrengthConv


__version__ = _util.get_last_commit_hash()


# update frequency of strength PVs
UPDATE_FREQ = 10.0  # [Hz]


class App:
    """Responsible for updating the IOC database.

    Update values and parameters such as alarms.
    """

    def __init__(self, driver, psnames, dbset, prefix):
        """Create Power Supply controllers."""
        self._driver = driver

        # write operation queue
        self._queue_write = _LoopQueueThread()
        self._queue_write.start()

        # mapping device to bbb
        self._psnames = psnames

        # strength string
        self._strenname = self._get_strennames(dbset)

        # print info about the IOC
        _siriuspy.util.print_ioc_banner(
            ioc_name='SI_PS_FCConv',
            db=dbset,
            description='SI PS Fast Corrector Conversion IOC',
            version=__version__,
            prefix=prefix)

        # build connectors and streconv dicts
        self._connectors, self._streconvs = \
            self._create_connectors_and_streconv()

        # scan thread
        self._interval = 1 / UPDATE_FREQ
        self._thread_scan = _RepeaterThread(
            self._interval, self.scan, niter=0)
        self._thread_scan.start()

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

        # log write queue size
        qsize = self._queue_write.qsize()
        if qsize > 2:
            logmsg = f'[Q] - write queue size is large: {qsize}'
            _log.warning(logmsg)

        dt_ = self._interval - (_time.time() - t0_)
        _time.sleep(max(dt_, 0))

    def read(self, reason):
        """Read from database."""
        _ = reason
        return None

    def write(self, reason, value):
        """Enqueue write request."""
        _log.info("[{:.2s}] - {:.32s} = {:.50s}".format(
            'W ', reason, str(value)))
        pvname = _SiriusPVName(reason)
        self.driver.setParam(reason, value)
        self.driver.updatePV(reason)
        self._queue_write.put(
            (self._write_operation, (pvname, value)), block=False)

    def scan(self):
        """Scan all devices"""
        for psname in self.psnames:
            self.scan_device(psname)

    def scan_device(self, psname):
        """Scan device and update ioc epics DB."""
        strenname = self._strenname[psname]

        # not connected
        if not self.check_connected(psname):
            conns = self._connectors[psname]
            for proptype in conns.keys():
                reason = psname + ':' + strenname + proptype
                self.driver.setParamStatus(
                    reason, _Alarm.NO_ALARM, _Severity.NO_ALARM)
            return

        # all connected, calculate strengths
        streconv = self._streconvs[psname]
        conn = self._connectors[psname]
        limits = conn['-SP'].limits
        curr0 = conn['-SP'].value
        curr1 = conn['-RB'].value
        curr2 = conn['Ref-Mon'].value
        curr3 = conn['Acc-Mon'].value
        curr4 = conn['-Mon'].value
        curr5 = limits[3]
        curr6 = limits[4]
        values = (curr0, curr1, curr2, curr3, curr4, curr5, curr6)
        try:
            strengths = streconv.conv_current_2_strength(values)
        except TypeError:
            # this exception occurs when low level IOC crashes
            strengths = None
        if strengths is None or None in strengths:
            slims = None
        else:
            slims = strengths[-2:]
            if slims[0] > slims[1]:
                slims = slims[1], slims[0]

        # update epics database
        for i, proptype in enumerate(conn.keys()):
            reason = psname + ':' + strenname + proptype
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
        conns = dict()
        streconv = dict()
        opts = {'auto_monitor_mon': True}
        for psn in self.psnames:
            conns[psn] = dict()
            conns[psn]['-SP'] = _PSProperty(psn, 'Current-SP', **opts)
            conns[psn]['-RB'] = _PSProperty(psn, 'Current-RB', **opts)
            conns[psn]['Ref-Mon'] = _PSProperty(psn, 'CurrentRef-Mon', **opts)
            conns[psn]['Acc-Mon'] = _PSProperty(psn, 'FOFBAcc-Mon', **opts)
            conns[psn]['-Mon'] = _PSProperty(psn, 'Current-Mon', **opts)
            streconv[psn] = _StrengthConv(psn, proptype='Ref-Mon', **opts)
        return conns, streconv

    def _write_operation(self, pvname, value):
        t0_ = _time.time()
        psname = pvname.device_name
        streconv = self._streconvs[psname]
        current = streconv.conv_strength_2_current(value)
        conn = self._connectors[psname]['-SP']
        if conn.connected:
            self._connectors[psname]['-SP'].value = current
        t1_ = _time.time()
        _log.info("[{:.2s}] - {:.32s} : {:.50s}".format(
            'T ', pvname,
            'write operation took {:.3f} ms'.format((t1_-t0_)*1000)))

    def _get_strennames(self, dbset):
        strennames = dict()
        for psname in self._psnames:
            for prop in dbset:
                if prop.startswith(psname):
                    *_, tmpstr = prop.split(':')
                    stren, *_ = tmpstr.split('-')
                    break
            strennames[psname] = stren
        return strennames
