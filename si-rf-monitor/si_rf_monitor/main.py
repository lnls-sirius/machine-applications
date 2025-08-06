"""Main Module of the IOC Logic."""

import time as _time

import pvs as _pvs
from siriuspy.epics import PV as _PV, SiriusPVTimeSerie as _SiriusPVTimeSerie

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
        self._cav_top_pv = _PV(
            'SI-03SP:RF-CryoMod-2:BT212_CavTopTemp-Mon',
            connection_timeout=0.05
        )
        # Temperatura na parte de baixo da cavidade
        self._cav_bot_pv = _PV(
            'SI-03SP:RF-CryoMod-2:BT211_CavBotTemp-Mon',
            connection_timeout=0.05
            )
        # Temperatura na parte mais baixa do tanque de hélio
        self._vessel_pv = _PV(
            'SI-03SP:RF-CryoMod-2:BT210_HeVesselHeaterTemp-Mon',
            connection_timeout=0.05
        )

        self._cav_top_buffer = _SiriusPVTimeSerie(
            pv=self._cav_top_pv,
            mode=0, nr_max_points=_MAX_BUFFER_SIZE,
            use_pv_timestamp=False
        )
        self._cav_bot_buffer = _SiriusPVTimeSerie(
            pv=self._cav_bot_pv,
            mode=0, nr_max_points=_MAX_BUFFER_SIZE,
            use_pv_timestamp=False
        )
        self._vessel_buffer = _SiriusPVTimeSerie(
            pv=self._vessel_pv,
            mode=0, nr_max_points=_MAX_BUFFER_SIZE,
            use_pv_timestamp=False
        )

        self._cav_top_pv.add_callback(self._callback_rate)
        self._cav_bot_pv.add_callback(self._callback_rate)
        self._vessel_pv.add_callback(self._callback_rate)

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
