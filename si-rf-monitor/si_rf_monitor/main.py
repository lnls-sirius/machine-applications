"""Main Module of the IOC Logic."""

import logging as _log
import time as _time
from copy import deepcopy as _dcopy
from threading import Event as _Event

import numpy as _np
from siriuspy.callbacks import Callback as _Callback
from siriuspy.epics import PV as _PV, SiriusPVTimeSerie as _SiriusPVTimeSerie
from siriuspy.thread import RepeaterThread as _Repeat

from . import pvs as _pvs


class App(_Callback):
    """Main Class of the IOC Logic."""

    pvs_database = _pvs.pvs_database

    def __init__(self, driver=None):
        """Initialize the instance."""
        self._driver = driver
        self._time_window = _pvs.DEF_TIME_WIN  # [s]
        # Temperatura no topo da cavidade
        self._pv_top = _PV(
            'SI-03SP:RF-CryoMod-2:BT212_CavTopTemp-Mon',
            connection_timeout=0.05
        )
        # Temperatura na parte de baixo da cavidade
        self._pv_bot = _PV(
            'SI-03SP:RF-CryoMod-2:BT211_CavBotTemp-Mon',
            connection_timeout=0.05
            )
        # Temperatura na parte mais baixa do tanque de hélio
        self._pv_ves = _PV(
            'SI-03SP:RF-CryoMod-2:BT210_HeVesselHeaterTemp-Mon',
            connection_timeout=0.05
        )

        self._buffer_top = _SiriusPVTimeSerie(
            pv=self._pv_top,
            mode=0,
            nr_max_points=_pvs.MAX_BUFFER_SIZE,
            use_pv_timestamp=False
        )
        self._buffer_bot = _SiriusPVTimeSerie(
            pv=self._pv_bot,
            mode=0,
            nr_max_points=_pvs.MAX_BUFFER_SIZE,
            use_pv_timestamp=False
        )
        self._buffer_ves = _SiriusPVTimeSerie(
            pv=self._pv_ves,
            mode=0,
            nr_max_points=_pvs.MAX_BUFFER_SIZE,
            use_pv_timestamp=False
        )

        self._evt_top = _Event()
        self._evt_bot = _Event()
        self._evt_ves = _Event()
        self._evt_dif = _Event()
        self._pv_top.add_callback(self._update_buffer)
        self._pv_bot.add_callback(self._update_buffer)
        self._pv_ves.add_callback(self._update_buffer)

        self._thread_top = _Repeat(
            _pvs.MIN_INTERVAL,
            self._calc_rate,
            args=('top', ),
            is_cathread=True
        )
        self._thread_bot = _Repeat(
            _pvs.MIN_INTERVAL,
            self._calc_rate,
            args=('bot', ),
            is_cathread=True
        )
        self._thread_ves = _Repeat(
            _pvs.MIN_INTERVAL,
            self._calc_rate,
            args=('ves', ),
            is_cathread=True
        )
        self._thread_dif = _Repeat(
            _pvs.MIN_INTERVAL,
            self._calc_diff,
            args=('ves', ),
            is_cathread=True
        )
        self._thread_top.start()
        self._thread_bot.start()
        self._thread_ves.start()
        self._thread_dif.start()

    def get_database(self):
        """Get the database."""
        return _dcopy(self.pvs_database)

    @property
    def driver(self):
        """Set the driver of the App."""
        return self._driver

    @driver.setter
    def driver(self, driver):
        self._driver = driver

    def process(self, interval):
        """Trigger connection to external PVs in other classes."""
        _time.sleep(interval)

    def read(self, reason):
        """Read PV from database."""
        _ = reason
        # The default behavior is to return None and let the driver read
        # from the database.
        return None

    def write(self, reason, value):
        """Write PV in the model."""
        if not reason.endswith('CavTempRateTimeInterval-SP'):
            return False

        val = max(min(float(value), _pvs.MAX_TIME_WIN), _pvs.MIN_TIME_WIN)
        self._time_window = val
        self.run_callbacks('CavTempRateTimeInterval-RB', val)
        return True

    def _calc_diff(self):
        while not self._evt_dif.wait(1):
            pass
        self._evt_dif.clear()

        vtop = self._pv_top.value
        vbot = self._pv_bot.value
        if vtop is None or vbot is None:
            return

        dtemp = vtop - vbot
        self.run_callbacks('CavTopBotTempDiff-Mon', dtemp)
        self.run_callbacks('CavTopBotTempMaxDiff-Mon', _pvs.MAX_TEMP_DIFF)
        self.run_callbacks('CavTopBotTempMinDiff-Mon', -_pvs.MAX_TEMP_DIFF)

    def _calc_rate(self, which):
        if which == 'top':
            evt = self._evt_top
            buf = self._buffer_top
            pref = 'BT212_CavTopTemp'
        elif which == 'bot':
            evt = self._evt_bot
            buf = self._buffer_bot
            pref = 'BT211_CavBotTemp'
        elif which == 'ves':
            evt = self._evt_ves
            buf = self._buffer_ves
            pref = 'BT210_HeVesselHeaterTemp'
        else:
            raise ValueError('Wrong value for input "which".')

        while not evt.wait(1):
            pass
        evt.clear()

        # calculate lifetime
        tim, vals = buf.get_serie(time_absolute=True)

        idcs = tim > _time.time() - self._time_window
        idcs &= _np.logical_not(_np.isnan(vals))

        if idcs.sum() < 3:
            _log.error('Did Not Fit. Size of buffer is too small.')
            return

        tim = tim[idcs]
        vals = vals[idcs]

        coefs = _np.polynomial.polynomial.polyfit(tim, vals, deg=1)

        slope = coefs[1] * 60  # [K/min]
        self.run_callbacks(pref + 'Rate-Mon', slope)
        self.run_callbacks(pref + 'MaxRate-Mon', _pvs.MAX_TEMP_RATE)
        self.run_callbacks(pref + 'MinRate-Mon', -_pvs.MAX_TEMP_RATE)

    def _update_buffer(self, pvname, value, **kwargs):
        _ = value, kwargs
        if pvname == self._pv_top.pvname and self._buffer_top.acquire():
            self._evt_top.set()
            self._evt_dif.set()
        elif pvname == self._pv_bot.pvname and self._buffer_bot.acquire():
            self._evt_bot.set()
            self._evt_dif.set()
        elif pvname == self._pv_ves.pvname and self._buffer_ves.acquire():
            self._evt_ves.set()
