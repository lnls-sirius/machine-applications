"""Main Module of the IOC Logic."""

import time as _time
from threading import Event as _Event

import numpy as _np

import pvs as _pvs
from siriuspy.epics import PV as _PV, SiriusPVTimeSerie as _SiriusPVTimeSerie, CAThread as _Thread

__version__ = _pvs.__version__

_MIN_BUFFER_SIZE = 100
_MAX_BUFFER_SIZE = 36000


class App:
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

        self._thread_top = _Thread(
            target=self._calc_rate,
            args=('top', ),
            daemon=True
        )
        self._thread_bot = _Thread(
            target=self._calc_rate,
            args=('bot', ),
            daemon=True
        )
        self._thread_ves = _Thread(
            target=self._calc_rate,
            args=('ves', ),
            daemon=True
        )

    def _calc_rate(self, which):
        if which == 'top':
            evt = self._evt_top
            buf = self._buffer_top
        elif which == 'bot':
            evt = self._evt_bot
            buf = self._buffer_bot
        elif which == 'ves':
            evt = self._evt_ves
            buf = self._buffer_ves
        else:
            raise ValueError('Wrong value for input "which".')

        buffer_dt = self._bpmsum_buffer if is_bpm else self._current_buffer

        # calculate lifetime
        tim, vals = buffer_dt.get_serie(time_absolute=False)

        if tim.size < 3:
            return

        _np.po
        fit = 'lin' if self._mode == _Const.Fit.Linear else 'exp'
        value = self._least_squares_fit(ts_dq, val_dq, fit=fit)
        setattr(self, lt_name, value)
        lt_hour = 'Lifetime' + lt_type + 'Hour-Mon'
        self.run_callbacks(lt_hour, value / 3600)

        # update pvs
        self.run_callbacks('BufferValue'+lt_type+'-Mon', val_dq)
        self.run_callbacks('BufferTimestamp'+lt_type+'-Mon', ts_dq)
        self.run_callbacks('BuffSize'+lt_type+'-Mon', len(val_dq))
        self.run_callbacks('BuffSizeTot'+lt_type+'-Mon', len(val_dqorg))

    def _update_buffer(self, pvname, value, **kwargs):
        if pvname == self._pv_top.pvname:
            self._buffer_top.acquire()
            self._evt_top.set()
        elif pvname == self._pv_bot.pvname:
            self._buffer_bot.acquire()
            self._evt_bot.set()
        elif pvname == self._pv_ves.pvname:
            self._buffer_ves.acquire()
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
