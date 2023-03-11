"""Module with main IOC Class."""

import time as _time
import logging as _log

from pcaspy import Alarm as _Alarm
from pcaspy import Severity as _Severity

from .meas import Measurement


class App:
    """Main Class of the IOC Logic."""

    def __init__(self, driver=None, const=None):
        """Initialize the instance."""
        self.driver = driver
        if const:
            self._database = const.get_database()
        else:
            self._database = {}
            self._const = const
        fwhmx_factor = \
            self._database['ImgFitXUpdateROIWithFWHMFactor-SP']['value']
        fwhmy_factor = \
            self._database['ImgFitYUpdateROIWithFWHMFactor-SP']['value']

        roi_with_fwhm = \
            self._database['ImgFitUpdateROIWithFWHM-Sts']['value']
        self._meas = Measurement(
            const.devname,
            fwhmx_factor=fwhmx_factor, fwhmy_factor=fwhmy_factor,
            roi_with_fwhm=roi_with_fwhm)
        self._meas.callback = self._update_driver

    def process(self, interval):
        """Run continuously in the main thread."""
        _time.sleep(interval)

    def init_driver(self):
        """Initialize PVs ate startup."""
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
    
    def write(self, reason, value):
        """Write value in objects and database."""
        if not reason.endswith('-SP'):
            _log.warning('PV %s is not settable!', reason)
            return False
        
        res = self._write_roi(reason, value)
        if res is not None:
            return res

        res = self._write_fwhm_factor(reason, value)
        if res is not None:
            return res
            
        return True

    def _create_meas(self):
        # build arguments
        fwhmx_factor = \
            self._database['ImgFitXUpdateROIWithFWHMFactor-SP']['value']
        fwhmy_factor = \
            self._database['ImgFitYUpdateROIWithFWHMFactor-SP']['value']
        roi_with_fwhm = \
            self._database['ImgFitUpdateROIWithFWHM-Sts']['value']
        
        # create object
        self._meas = Measurement(
            self._const.devname,
            fwhmx_factor=fwhmx_factor, fwhmy_factor=fwhmy_factor,
            roi_with_fwhm=roi_with_fwhm)

        # add callback
        self._meas.callback = self._update_driver

    def _write_sp_rb(self, reason, value):
        # update SP
        self.driver.setParam(reason, value)
        _log.debug('{}: updated'.format(reason))
        self.driver.updatePV(reason)
        self.driver.setParamStatus(
            reason, _Alarm.NO_ALARM, _Severity.NO_ALARM)

        # update RB
        reason = reason.replace('-SP', '-RB')
        self.driver.setParam(reason, value)
        _log.debug('{}: updated'.format(reason))
        self.driver.updatePV(reason)
        self.driver.setParamStatus(
            reason, _Alarm.NO_ALARM, _Severity.NO_ALARM)

    def _write_roi(self, reason, value):
        if reason not in ('ImgROIX-SP', 'ImgROIY-SP'):
            return None
        if 'X' in reason:
            self._meas.set_roix(value)
        else:
            self._meas.set_roiy(value)
        if self._meas.update_success:
            self._write_sp_rb(reason, value)
            return True
        else:
            msg = '{}: could not write value {}'.format(reason, value)
            self.driver.setParam('ImgLog-Mon', value)
            _log.debug(msg)
            self.driver.updatePV('ImgLog-Mon')
            self.driver.setParamStatus(
                reason, _Alarm.TIMEOUT_ALARM, _Severity.INVALID_ALARM)
            return False

    def _write_fwhm_factor(self, reason, value):
        if reason not in (
                'ImgFitXUpdateROIWithFWHMFactor-SP',
                'ImgFitYUpdateROIWithFWHMFactor-SP'
                ):
            return
        # TODO: check value
        if 'X' in reason:
            self._meas._fwhmx_factor = value
        else:
            self._meas._fwhmy_factor = value
        self._write_sp_rb(reason, value)

        return True
        
    def _update_driver(self):
        """Update all parameters at every image PV callback."""
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

                # check if fit is valid and update value
                if 'FitX' in pvname:
                    invalid = self._meas.fitx_is_nan
                elif 'FitY' in pvname:
                    invalid = self._meas.fity_is_nan
                elif 'FitAngle' in pvname:
                    invalid = self._meas.fitx_is_nan or self._meas.fity_is_nan
                else:
                    invalid = False

                new_value = 0 if invalid else value

                # if 'Fit' in pvname:
                #     print(pvname, value, invalid, new_value)

                # update epics db
                self.driver.setParam(pvname, value)
                _log.debug('{0:40s}: updated'.format(pvname))
                self.driver.updatePV(pvname)
                self.driver.setParamStatus(
                    pvname, _Alarm.NO_ALARM, _Severity.NO_ALARM)
            else:
                self.driver.setParamStatus(
                    pvname, _Alarm.TIMEOUT_ALARM, _Severity.INVALID_ALARM)
            
