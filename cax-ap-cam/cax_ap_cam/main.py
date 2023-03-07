"""Module with main IOC Class."""

import time as _time
import logging as _log


class App:
    """Main Class of the IOC Logic."""

    def __init__(self, driver=None, const=None):
        """Initialize the instance.

        driver : is the driver associated with this app;
        triggers_list: is the list of the high level triggers to be managed;
        """
        self.driver = driver
        if const:
            self._database = const.get_database()
        else:
            self._database = {}
        self._map2writepvs = self.get_map2writepvs()
        self._map2readpvs = self.get_map2readpvs()

    def process(self, interval):
        """Run continuously in the main thread."""
        _time.sleep(interval)

    def write(self, reason, value):
        """Write value in objects and database."""
        fun_ = self._map2writepvs.get(reason)
        if fun_ is None:
            _log.warning('Not OK: PV %s is not settable.', reason)
            return False
        return fun_(value)

    def read(self, reason, from_db=False):
        """Read PV value from objects or database."""
        if from_db and self.driver is not None:
            value = self.driver.getParam(reason)
        else:
            fun_ = self._map2readpvs.get(reason)
            value = fun_()
        return value

    def callbackR(self):
        print("callback to be used to read a pv - CAGET")

    def callbackW(self, value):
        print("callback to be used to update a pv - CAPUT" + str(value))

    def get_map2writepvs(self):
        """Get dictionary to write pvs to objects."""
        map2writepvs = dict()
        map2writepvs.update({
            'Dispersion-SP': self.callbackW
        })
        return {k: v for k, v in map2writepvs.items() if k in self._database}

    def get_map2readpvs(self):
        """Get dictionary to read pvs from objects."""
        map2readpvs = dict()
        map2readpvs.update({
            'Dispersion-SP': self.callbackR
        })
        return {k: v for k, v in map2readpvs.items() if k in self._database}

    def _update_driver(
            self, pvname, value, **kwargs):
        if pvname not in self._database or self.driver is None:
            return
        if value is not None:
            self.driver.setParam(pvname, value)
            _log.debug('{0:40s}: updated'.format(pvname))

        self.driver.updatePV(pvname)
