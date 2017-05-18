import pvs as _pvs
import time as _time
import logging as _log
from siriuspy.timesys.time_data import Connections, Events
from siriuspy.namesys import SiriusPVName as _PVName
from data.triggers import get_triggers as _get_triggers
from hl_classes import get_hl_trigger_object, HL_Event

# Coding guidelines:
# =================
# 01 - pay special attention to code readability
# 02 - simplify logic as much as possible
# 03 - unroll expressions in order to simplify code
# 04 - dont be afraid to generate simingly repeatitive flat code (they may be easier to read!)
# 05 - 'copy and paste' is your friend and it allows you to code 'repeatitive' (but clearer) sections fast.
# 06 - be consistent in coding style (variable naming, spacings, prefixes, suffixes, etc)

__version__ = _pvs.__version__
_TIMEOUT = 0.05

def check_triggers_consistency():
    triggers = _get_triggers()
    Connections.add_bbb_info()
    Connections.add_crates_info()
    from_evg = Connections.get_connections_from_evg()
    twds_evg = Connections.get_connections_twds_evg()
    for trig, val in triggers.items():
        chans = {  _PVName(chan) for chan in val['channels']  }
        for chan in chans:
            tmp = twds_evg.get(chan)
            if tmp is None:
                _log.warning('Device '+chan+' defined in the high level trigger '+
                      trig+' not specified in timing connections data.')
                return False
            up_dev = tmp.pop()
            diff_devs = from_evg[up_dev] - chans
            if diff_devs and not chan.dev_type.endswith('BPM'):
                _log.warning('Devices: '+' '.join(diff_devs)+' are connected to the same output of '
                             +up_dev+' as '+chan+' but are not related to the sam trigger ('+trig+').')
                # return False
    return True


class App:

    def get_database(self):
        db = dict()
        for ev in self._events.values():
            db.update(ev.get_database())
        for trig in self._triggers.values():
            db.update(trig.get_database())
        return db

    def __init__(self,driver=None):
        _log.info('Starting App...')
        self._driver = driver
        if not check_triggers_consistency():
            raise Exception('Triggers not consistent.')
        # Build Event's Variables:
        _log.info('Creating High Level Events:')
        self._events = dict()
        for ev,code in Events.HL2LL_MAP.items():
            event = Events.HL_PREF + ev
            self._events[event] = HL_Event(event,code,self._update_driver)
        # Build triggers from data dictionary:
        _log.info('Creating High Level Triggers:')
        self._triggers = dict()
        triggers = _get_triggers()
        for trig_prefix, prop in triggers.items():
            trig = get_hl_trigger_object(trig_prefix, self._update_driver, **prop)
            self._triggers[trig_prefix] = trig

    def connect(self):
        _log.info('Connecting to Low Level Events:')
        # Build Event's Variables:
        for key,val in self._events.items():
            val.connect()
        _log.info('All Events connection opened.')
        # Build triggers from data dictionary:
        _log.info('Connecting to Low Level Triggers:')
        for key,val in self._triggers.items():
            val.connect()
        _log.info('All Triggers connection opened.')

    def _update_driver(self,pvname,value,**kwargs):
        _log.debug('PV {0:s} updated in driver database with value {1:s}'.format(pvname,str(value)))
        self._driver.setParam(pvname,value)
        self._driver.updatePVs()

    @property
    def driver(self):
        return self._driver

    @driver.setter
    def driver(self,driver):
        _log.debug("Setting App's driver.")
        self._driver = driver

    def process(self,interval):
        _time.sleep(interval)

    def read(self,reason):
        # _log.debug("PV {0:s} read from App.".format(reason))
        return None # Driver will read from database

    def write(self,reason,value):
        parts = _PVName(reason)
        _log.debug('App: Writing PV {0:s} with value {1:s}'.format(reason,str(value)))
        if parts.propty.endswith(('-Sts','-RB', '-Mon')):
            _log.debug('App: PV {0:s} is read only.'.format(reason))
            return False

        res_ = Events.HL_RGX.findall(parts.propty)
        if res_:
            ev, pv = res_
            _log.debug('App: Writing Event {0:s} property {1:s}'.format(ev,pv))
            ret_val = self._events[ev].set_propty(pv, value)
            if ret_val:
                _log.debug('App: Write complete.')
            else:
                _log.debug('App: Write unsuccessful.')
            return ret_val

        trig = [ val for key,val in self._triggers.items() if parts.startswith(key) ]
        if len(trig)>0:
            _log.debug('App: Writing Trigger property.')
            ret_val = trig[0].set_propty(reason,value)
            if ret_val:
                _log.debug('App: Write complete.')
            else:
                _log.debug('App: Write unsuccessful.')
            return ret_val

        _log.debug('App: Write unsuccessful. PV not recognized.')
        return False
