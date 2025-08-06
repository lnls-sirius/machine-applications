"""Main Module of the IOC Logic."""

import time as _time
from threading import Event as _Event

import numpy as _np

import pvs as _pvs
from siriuspy.epics import PV as _PV, SiriusPVTimeSerie as _SiriusPVTimeSerie
from siriuspy.thread import RepeaterThread as _Repeat
from siriuspy.callbacks import Callback as _Callback

__version__ = _pvs.__version__

_MAX_BUFFER_SIZE = 1800
_MIN_INTERVAL = 0.1  # [s]
_MAX_TEMP_DIFF = 50  # [K]
_MAX_TEMP_RATE = 0.5  # [K/min]


class App(_Callback):
    """Main Class of the IOC Logic."""

    pvs_database = _pvs.pvs_database

    def get_database(self):
        """Get the database."""
        db = dict()
        for pre, pvs in self.pvs_database.items():
            for pvname, info in pvs.items():
                db[pre + pvname] = info
        return db

    def __init__(self, driver=None):
        """Initialize the instance."""
        self._driver = driver
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
            nr_max_points=_MAX_BUFFER_SIZE,
            use_pv_timestamp=False
        )
        self._buffer_bot = _SiriusPVTimeSerie(
            pv=self._pv_bot,
            mode=0,
            nr_max_points=_MAX_BUFFER_SIZE,
            use_pv_timestamp=False
        )
        self._buffer_ves = _SiriusPVTimeSerie(
            pv=self._pv_ves,
            mode=0,
            nr_max_points=_MAX_BUFFER_SIZE,
            use_pv_timestamp=False
        )

        self._evt_top = _Event()
        self._evt_bot = _Event()
        self._evt_ves = _Event()
        self._pv_top.add_callback(self._update_buffer)
        self._pv_bot.add_callback(self._update_buffer)
        self._pv_ves.add_callback(self._update_buffer)

        self._thread_top = _Repeat(
            _MIN_INTERVAL,
            self._calc_rate,
            args=('top', ),
            is_cathread=True
        )
        self._thread_bot = _Repeat(
            _MIN_INTERVAL,
            self._calc_rate,
            args=('bot', ),
            is_cathread=True
        )
        self._thread_ves = _Repeat(
            _MIN_INTERVAL,
            self._calc_rate,
            args=('ves', ),
            is_cathread=True
        )

        self._thread_dif = _Repeat(
            _MIN_INTERVAL,
            self._calc_diff,
            args=('ves', ),
            is_cathread=True
        )
        self._thread_top.start()
        self._thread_bot.start()
        self._thread_ves.start()
        self._thread_dif.start()

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

        idcs = tim > _time.time() - self._interval
        idcs &= _np.logical_not(_np.isnan(vals))

        if idcs.sum() < 3:
            return

        tim = tim[idcs]
        vals = vals[idcs]

        coefs = _np.polynomial.polynomial.polyfit(tim, vals, deg=1)

        slope = coefs[1] * 60  # [K/min]
        self.run_callbacks(pref + 'Rate-Mon', slope)
        self.run_callbacks(pref + 'MaxRate-Mon', self._max_rate)

    def _update_buffer(self, pvname, value, **kwargs):
        if pvname == self._pv_top.pvname and self._buffer_top.acquire():
            self._evt_top.set()
        elif pvname == self._pv_bot.pvname and self._buffer_bot.acquire():
            self._evt_bot.set()
        elif pvname == self._pv_ves.pvname and self._buffer_ves.acquire():
            self._evt_ves.set()

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
        # implementation here
        # The default behavior is to return None and let the driver read
        # from the database.
        return None

    def write(self, reason, value):
        """Write PV in the model."""
        # implementation here
        # this should be used in case PV state change.
        return True  # return True for successful write and False otherwise.
