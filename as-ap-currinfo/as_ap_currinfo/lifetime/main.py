"""Main Module of the IOC Logic."""

import time as _time
import numpy as _np
import epics as _epics
from siriuspy.epics import SiriusPVTimeSerie as _SiriusPVTimeSerie
from siriuspy.csdevice.currinfo import Const as _Const
import as_ap_currinfo.lifetime.pvs as _pvs

# Coding guidelines:
# =================
# 01 - pay special attention to code readability
# 02 - simplify logic as much as possible
# 03 - unroll expressions in order to simplify code
# 04 - dont be afraid to generate simingly repeatitive flat code (they may be
#      easier to read!)
# 05 - 'copy and paste' is your friend and it allows you to code 'repeatitive'
#      (but clearer) sections fast.
# 06 - be consistent in coding style (variable naming, spacings, prefixes,
#      suffixes, etc)


class App:
    """Main Class of the IOC Logic."""

    pvs_database = None

    def __init__(self, driver):
        """Class constructor."""
        _pvs.print_banner()

        self._driver = driver
        self._PREFIX_VACA = _pvs.get_pvs_vaca_prefix()
        self._PREFIX = _pvs.get_pvs_prefix()

        self._mode = _Const.Fit.Exponential
        self._lifetime = 0
        self._lifetime_bpm = 0
        self._current_offset = 0.0
        self._rstbuff_cmd_count = 0
        self._buffautorst_mode = _Const.BuffAutoRst.Off
        self._buffautorst_dcurr = 0.1
        self._sampling_interval = 2000.0
        self._min_intvl_btw_spl = 0.0
        self._is_stored = 0

        self._current_pv = _epics.PV(self._PREFIX+'Current-Mon')
        self._bpmsum_pv = _epics.PV(self._PREFIX_VACA+'SI-01M1:DI-BPM:Sum-Mon')
        self._storedebeam_pv = _epics.PV(self._PREFIX+'StoredEBeam-Mon')

        self._current_buffer = _SiriusPVTimeSerie(
            pv=self._current_pv, time_window=self._sampling_interval, mode=0,
            time_min_interval=self._min_intvl_btw_spl)
        self._bpmsum_buffer = _SiriusPVTimeSerie(
            pv=self._bpmsum_pv, time_window=self._sampling_interval, mode=0,
            time_min_interval=self._min_intvl_btw_spl)

        self._current_pv.add_callback(self._callback_calclifetime)
        self._bpmsum_pv.add_callback(self._callback_calclifetime)
        self._storedebeam_pv.add_callback(self._callback_get_storedebeam)

    @staticmethod
    def init_class():
        """Init class."""
        App.pvs_database = _pvs.get_pvs_database()

    @property
    def driver(self):
        """Return driver."""
        return self._driver

    def process(self, interval):
        """Sleep."""
        _time.sleep(interval)

    def read(self, reason):
        """Read from IOC database."""
        value = None
        return value

    def write(self, reason, value):
        """Write value to reason and let callback update PV database."""
        status = False
        if reason == 'SplIntvl-SP':
            self._update_splintvl(value)
            self.driver.setParam('SplIntvl-RB', self._sampling_interval)
            self.driver.updatePV('SplIntvl-RB')
            status = True
        elif reason == 'MinIntvlBtwSpl-SP':
            self._update_min_intvl_btw_spl(value)
            self.driver.setParam('MinIntvlBtwSpl-RB', self._min_intvl_btw_spl)
            self.driver.updatePV('MinIntvlBtwSpl-RB')
            status = True
        elif reason == 'BuffRst-Cmd':
            self._clear_buffer()
            self.driver.setParam('BuffRst-Cmd', self._rstbuff_cmd_count)
            self.driver.updatePV('BuffRst-Cmd')
            status = True
        elif reason == 'BuffAutoRst-Sel':
            self._buffautorst_mode = value
            self.driver.setParam('BuffAutoRst-Sts', self._buffautorst_mode)
            self.driver.updatePV('BuffAutoRst-Sts')
            status = True
        elif reason == 'BuffAutoRstDCurr-SP':
            self._buffautorst_dcurr = value
            self.driver.setParam('BuffAutoRstDCurr-RB',
                                 self._buffautorst_dcurr)
            self.driver.updatePV('BuffAutoRstDCurr-RB')
            status = True
        elif reason == 'LtFitMode-Sel':
            self._mode = value
            self.driver.setParam('LtFitMode-Sts', value)
            self.driver.updatePV('LtFitMode-Sts')
            status = True
        elif reason == 'CurrOffset-SP':
            self._current_offset = value
            self.driver.setParam('CurrOffset-RB', value)
            self.driver.updatePV('CurrOffset-RB')
            status = True
        return status

    def _update_min_intvl_btw_spl(self, value):
        if value < 0:
            value = 0
        self._min_intvl_btw_spl = value
        self._current_buffer.time_min_interval = value
        self._bpmsum_buffer.time_min_interval = value

    def _update_splintvl(self, value):
        self._sampling_interval = value
        self._current_buffer.time_window = value
        self._bpmsum_buffer.time_window = value

    def _clear_buffer(self):
        self._rstbuff_cmd_count += 1
        self._reset_buff()

    def _callback_get_storedebeam(self, value, **kws):
        self._is_stored = value

    def _callback_calclifetime(self, pvname, timestamp, **kws):
        buffer = self._bpmsum_buffer if 'BPM' in pvname \
            else self._current_buffer
        attrname = '_lifetime'+('_bpm' if 'BPM' in pvname else '')

        # check DCCT StoredEBeam PV
        if not self._is_stored:
            return

        # try to add a new point to buffer
        acquireflag = buffer.acquire()
        if not acquireflag:
            return

        # check whether the buffer must be reset
        self._buffautorst_check()

        # check min number of points in buffer to calculate lifetime
        [timestamp_dq, value_dq] = buffer.serie
        timestamp_dq = _np.array(timestamp_dq)
        value_dq = _np.array(value_dq)
        if not len(timestamp_dq):
            setattr(self, attrname, 0)
            first_ts = 0
            last_ts = 0
        else:
            value_dq -= self._current_offset
            if len(value_dq) > 100:
                fit = 'exp' if self._mode == _Const.Fit.Exponential else 'lin'
                lt = self._least_squares_fit(timestamp_dq, value_dq, fit=fit)
                setattr(self, attrname, lt)
            first_ts = timestamp_dq[0]
            last_ts = timestamp_dq[-1]

        # update pvs
        if 'BPM' in pvname:
            self.driver.setParam('LifetimeBPM-Mon', self._lifetime_bpm)
            self.driver.updatePV('LifetimeBPM-Mon')
            self.driver.setParam('BuffSizeBPM-Mon', len(value_dq))
            self.driver.updatePV('BuffSizeBPM-Mon')
            self._update_buff_samples_timestamps(
                first_ts, last_ts, is_bpm=True)
        else:
            self.driver.setParam('Lifetime-Mon', self._lifetime)
            self.driver.updatePV('Lifetime-Mon')
            self.driver.setParam('BuffSize-Mon', len(value_dq))
            self.driver.updatePV('BuffSize-Mon')
            self._update_buff_samples_timestamps(first_ts, last_ts)

    def _buffautorst_check(self):
        """Check situations to clear internal buffer.
        If BuffAutoRst == DCurrCheck, check abrupt variation of current by
        a factor of 20 times the DCCT fluctuation/resolution.
        """
        if self._buffautorst_mode == _Const.BuffAutoRst.Off:
            return

        reset = False
        [_, value] = self._current_buffer.serie
        if len(value) >= 2:
            deltacurr = abs(value[-1] - value[-2])
        else:
            deltacurr = 0.0
        if deltacurr > self._buffautorst_dcurr:
            reset = True
        if reset:
            self._reset_buff()

    def _reset_buff(self):
        self._current_buffer.clearserie()
        self.driver.setParam('BuffSize-Mon', 0)
        self.driver.updatePV('BuffSize-Mon')
        self._lifetime = 0
        self.driver.setParam('Lifetime-Mon', self._lifetime)
        self.driver.updatePV('Lifetime-Mon')
        self._update_buff_samples_timestamps(0, 0)

        self._bpmsum_buffer.clearserie()
        self.driver.setParam('BuffSizeBPM-Mon', 0)
        self.driver.updatePV('BuffSizeBPM-Mon')
        self._lifetime_bpm = 0
        self.driver.setParam('LifetimeBPM-Mon', self._lifetime_bpm)
        self.driver.updatePV('LifetimeBPM-Mon')
        self._update_buff_samples_timestamps(0, 0, is_bpm=True)

    def _update_buff_samples_timestamps(self, first, last, is_bpm=False):
        typ = ('BPM' if is_bpm else '')
        self.driver.setParam('BuffFirstSplTimestamp'+typ+'-Mon', first)
        self.driver.updatePV('BuffFirstSplTimestamp'+typ+'-Mon')
        self.driver.setParam('BuffLastSplTimestamp'+typ+'-Mon', last)
        self.driver.updatePV('BuffLastSplTimestamp'+typ+'-Mon')

    @staticmethod
    def _least_squares_fit(timestamp, value, fit='exp'):
        if fit == 'exp':
            value = _np.log(value)
        n = len(timestamp)
        x = _np.sum(timestamp)
        y = _np.sum(value)
        x2 = _np.sum(_np.power(timestamp, 2))
        xy = _np.sum(timestamp*value)
        a = (x2*y - xy*x)/(n*x2 - x*x)
        b = (n*xy - x*y)/(n*x2 - x*x)

        if fit == 'exp':
            lt = - 1/b
        else:
            lt = - a/b
        return lt
