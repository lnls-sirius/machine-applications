"""Module with main IOC Class."""

import time as _time
import logging as _log
from siriuspy.timesys.time_data import Events, Clocks, Triggers
from as_ti_control.hl_classes import HL_Event, HL_Clock, HL_Trigger, HL_EVG

_TIMEOUT = 0.05


class App:
    """Main Class of the IOC Logic."""

    def get_database(self):
        """Get the database."""
        db = dict()
        if self._evg is not None:
            db.update(self._evg.get_database())
        for cl in self._clocks.values():
            db.update(cl.get_database())
        for ev in self._events.values():
            db.update(ev.get_database())
        for trig in self._triggers.values():
            db.update(trig.get_database())
        return db

    def __init__(self, driver=None, triggers_list=[],
                 events=True, clocks_evg=True):
        """Initialize the instance.

        driver : is the driver associated with this app;
        triggers_list: is the list of the high level triggers to be managed;
        events : define if this app will manage events;
        clocks_evg : define if this app will manage clocks and evg.
        """
        _log.info('Starting App...')
        self.driver = driver
        self._evg = None
        self._clocks = dict()
        self._events = dict()
        self._triggers = dict()
        if clocks_evg:
            self._evg = HL_EVG(self._update_driver)
            _log.info('Creating High Level Interface for Clocks and EVG:')
            for cl_hl, cl_ll in Clocks.HL2LL_MAP.items():
                clock = Clocks.HL_PREF + cl_hl
                self._clocks[clock] = HL_Clock(clock, self._update_driver,
                                               cl_ll)
        if events:
            _log.info('Creating High Level Interface for Events:')
            for ev_hl, ev_ll in Events.HL2LL_MAP.items():
                event = Events.HL_PREF + ev_hl
                self._events[event] = HL_Event(event, self._update_driver,
                                               ev_ll)
        if triggers_list:
            _log.info('Creating High Level Triggers:')
            all_triggers = Triggers().hl_triggers
            for pref in triggers_list:
                prop = all_triggers[pref]
                self._triggers[pref] = HL_Trigger(pref,
                                                  self._update_driver,
                                                  **prop)
        self._database = self.get_database()

    def connect(self):
        """Trigger connection to external PVs in other classes."""
        if self._evg is not None:
            self._evg.connect()
        _log.info('Connecting to Low Level Interface for Clocks:')
        for key, val in self._clocks.items():
            val.connect()
        _log.info('All Clocks connection opened.')
        _log.info('Connecting to Low Level Interface for Events:')
        for key, val in self._events.items():
            val.connect()
        _log.info('All Events connection opened.')
        _log.info('Connecting to Low Level Triggers Controllers:')
        for key, val in self._triggers.items():
            val.connect()
        _log.info('All Triggers connection opened.')

    def process(self, interval):
        """Run continuously in the main thread."""
        t0 = _time.time()
        # _log.debug('App: Executing check.')
        tf = _time.time()
        dt = (tf-t0)
        if dt > 0.2:
            _log.debug('App: check took {0:f}ms.'.format(dt*1000))
        dt = interval - dt
        if dt > 0:
            _time.sleep(dt)

    def write(self, reason, value):
        """Write PV in the model."""
        _log.debug('Writing PV {0:s} with value {1:s}'
                   .format(reason, str(value)))
        if not self._isValid(reason, value):
            return False
        fun_ = self._database[reason].get('fun_set_pv')
        if fun_ is None:
            _log.warning('Write unsuccessful. PV ' +
                         '{0:s} does not have a set function.'.format(reason))
            return False
        ret_val = fun_(value)
        if ret_val:
            _log.debug('Write complete.')
        else:
            _log.warning('Unsuccessful write of PV {0:s}; value = {1:s}.'
                         .format(reason, str(value)))
        return ret_val

    def _update_driver(self, pvname, value, **kwargs):
        _log.debug('PV {0:s} updated in driver database with value {1:s}'
                   .format(pvname, str(value)))
        self.driver.setParam(pvname, value)
        self.driver.updatePVs()

    def _isValid(self, reason, value):
        if reason.endswith(('-Sts', '-RB', '-Mon')):
            _log.debug('PV {0:s} is read only.'.format(reason))
            return False
        enums = (self._database[reason].get('enums') or
                 self._database[reason].get('Enums'))
        if enums is not None:
            if isinstance(value, int):
                len_ = len(enums)
                if value >= len_:
                    _log.warning('value {0:d} too large '.format(value) +
                                 'for PV {0:s} of type enum'.format(reason))
                    return False
            elif isinstance(value, str):
                if value not in enums:
                    _log.warning('Value {0:s} not permited'.format(value))
                    return False
        return True
