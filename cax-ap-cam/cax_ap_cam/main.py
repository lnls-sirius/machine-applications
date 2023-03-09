"""Module with main IOC Class."""

import time as _time
import logging as _log
from .image_proc import MeasProc


class App:
    """Main Class of the IOC Logic."""

    def __init__(self, driver=None, const=None):
        """Initialize the instance
        """
        self.driver = driver
        if const:
            self._database = const.get_database()
        else:
            self._database = {}
        self.meas = MeasProc(callback=self._update_driver)
        self._map2writepvs = self.get_funct_dict()

    def process(self, interval):
        """Run continuously in the main thread."""
        _time.sleep(interval)

    def write(self, reason, value):
        """Write value in objects and database."""
        fun_ = self._map2writepvs.get(reason)
        if fun_ is None:
            _log.warning('Not OK: PV %s is not settable.', reason)
            return False
        return fun_(reason, value)

    def get_avg_intensity(self, image_processed):
        inten_sum_val = getattr(image_processed,'intensity_sum')
        size_val = getattr(image_processed, 'size')
        return inten_sum_val/size_val

    def get_attribute_value(self, pvname, image_processed):
        attr_name = self.meas.pvname2attrname(pvname)
        return getattr(image_processed, attr_name)

    def update_with_roi_change(self, image_processed):
        for pvname in self._database.keys():
            changes_wroi = pvname not in [
                'Version-Cte', 'ROIY-SP', 'ROIX-SP',
                'SizeX-RB', 'SizeY-RB']
            if changes_wroi:
                value = 0
                if pvname == 'Intensity_Avg-RB':
                    value = self.get_avg_intensity(
                        image_processed)
                else:
                    value = self.get_attribute_value(
                        pvname, image_processed)
                if 'Error' in pvname:
                    value *= 100
                self.driver.setParam(pvname, value)

    def callback_caput(self, reason, value):
        self.meas.update_roi(
            reason, value,
            self.update_with_roi_change)
        return value

    def get_funct_dict(self):
        map2functpvs = dict()
        for axis in ['X', 'Y']:
            map2functpvs.update({
                'ROI' + axis + '-SP': self.callback_caput
            })
        return {k: v for k, v in map2functpvs.items() if k in self._database}

    def _update_driver(
            self, pvname, value, **kwargs):
        if pvname not in self._database or self.driver is None:
            return
        if value is not None:
            self.driver.setParam(pvname, value)
            _log.debug('{0:40s}: updated'.format(pvname))

        self.driver.updatePV(pvname)
