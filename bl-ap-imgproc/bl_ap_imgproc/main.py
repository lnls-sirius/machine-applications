"""Module with main IOC Class."""

import time as _time
import logging as _log

from pcaspy import Alarm as _Alarm
from pcaspy import Severity as _Severity

from .imgproc import Measurement


class App:
    """Main Class of the IOC Logic."""

    def __init__(self, driver=None, const=None):
        """Initialize the instance."""
        self.driver = driver
        if const:
            self._database = const.get_database()
        else:
            self._database = {}
        self._meas = Measurement(const.devname)
        self._meas.callback = self._update_driver
        self._map2writepvs = self.get_funct_dict()

    def process(self, interval):
        """Run continuously in the main thread."""
        _time.sleep(interval)

    def write(self, reason, value):
        """Write value in objects and database."""
        if not reason.endswith('-SP'):
            _log.warning('PV %s is not settable!', reason)
            return False
        if reason in ('ImgROIX-SP', 'ImgROIY-SP'):
            if 'X' in reason:
                self._meas.set_roix(value)
            else:
                self._meas.set_roiy(value)
            if self._meas.update_success:
                # update SP
                self.driver.setParam(reason, value)
                _log.debug('{0:40s}: updated'.format(reason))
                self.driver.updatePV(reason)
                self.driver.setParamStatus(
                    reason, _Alarm.NO_ALARM, _Severity.NO_ALARM)
                # update RB
                reason = reason.replace('-SP', '-RB')
                self.driver.setParam(reason, value)
                _log.debug('{0:40s}: updated'.format(reason))
                self.driver.updatePV(reason)
                self.driver.setParamStatus(
                    reason, _Alarm.NO_ALARM, _Severity.NO_ALARM)
                return True
            else:
                self.driver.setParamStatus(
                    reason, _Alarm.TIMEOUT_ALARM, _Severity.INVALID_ALARM)
                return False
        return True

    def get_attribute_value(self, pvname, image_processed):
        attr_name = self._meas.pvname2attrname(pvname)
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
        self._meas.update_roi(
            reason, value,
            self.update_with_roi_change)
        return value

    def get_funct_dict(self):
        map2functpvs = dict()
        map2functpvs.update({'ImgROIX-SP': self.callback_caput})
        map2functpvs.update({'ImgROIY-SP': self.callback_caput})
        return {k: v for k, v in map2functpvs.items() if k in self._database}

    def init_driver(self):
        pv2attr = {
            'ImgSizeX-Cte': 'sizex',
            'ImgSizeY-Cte': 'sizey',
            }
        for pvname, attr in pv2attr.items():
            if self._meas.update_success:
                imgproc = self._meas
                # get image attribute value
                if not isinstance(attr, str):
                    field, attr = attr
                    obj = getattr(imgproc, field)
                else:
                    obj = imgproc
                value = getattr(obj, attr)
                # update epics db
                self.driver.setParam(pvname, value)
                _log.debug('{0:40s}: updated'.format(pvname))
                self.driver.updatePV(pvname)
                self.driver.setParamStatus(
                    pvname, _Alarm.NO_ALARM, _Severity.NO_ALARM)
            else:
                self.driver.setParamStatus(
                    pvname, _Alarm.TIMEOUT_ALARM, _Severity.INVALID_ALARM)
            
    def _update_driver(self):
        pv2attr = {
            'ImgIntensityMin-Mon': 'intensity_min',
            'ImgIntensityMax-Mon': 'intensity_max',
            'ImgIntensitySum-Mon': 'intensity_sum',
            'ImgIsSaturated-Mon': 'is_saturated',
            'ImgFitXAmplitude-Mon': ('fitx', 'roi_amplitude'),
            'ImgFitXMean-Mon': ('fitx', 'roi_mean'),
            'ImgFitXSigma-Mon': ('fitx', 'roi_sigma'),
            'ImgFitXError-Mon': ('fitx', 'roi_fit_error'),
            'ImgFitYAmplitude-Mon': ('fity', 'roi_amplitude'),
            'ImgFitYMean-Mon': ('fity', 'roi_mean'),
            'ImgFitYSigma-Mon': ('fity', 'roi_sigma'),
            'ImgFitYError-Mon': ('fity', 'roi_fit_error'),
            'ImgFitAngle-Mon': 'angle',
        }
        for pvname, attr in pv2attr.items():
            if self._meas.update_success:
                imgproc = self._meas.imgproc
                # get image attribute value
                if not isinstance(attr, str):
                    field, attr = attr
                    obj = getattr(imgproc, field)
                else:
                    obj = imgproc
                value = getattr(obj, attr)
                # update epics db
                self.driver.setParam(pvname, value)
                _log.debug('{0:40s}: updated'.format(pvname))
                self.driver.updatePV(pvname)
                self.driver.setParamStatus(
                    pvname, _Alarm.NO_ALARM, _Severity.NO_ALARM)
            else:
                self.driver.setParamStatus(
                    pvname, _Alarm.TIMEOUT_ALARM, _Severity.INVALID_ALARM)
            
