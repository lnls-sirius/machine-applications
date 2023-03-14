"""Module with main IOC Class."""

import time as _time
import logging as _log

from pcaspy import Alarm as _Alarm
from pcaspy import Severity as _Severity

from siriuspy import util as _util

from .meas import Measurement


class App:
    """BL Image Processing IOC Application."""

    _MON_PVS_2_IMGFIT = {
            'ImgROIX-RB': ('fitx', 'roi'),
            'ImgROIY-RB': ('fity', 'roi'),
            'ImgROIXCenter-Mon': ('fitx', 'roi_center'),
            'ImgROIYCenter-Mon': ('fity', 'roi_center'),
            'ImgROIXFWHM-Mon': ('fitx', 'roi_fwhm'),
            'ImgROIYFWHM-Mon': ('fity', 'roi_fwhm'),
            'ImgIntensityMin-Mon': 'intensity_min',
            'ImgIntensityMax-Mon': 'intensity_max',
            'ImgIntensitySum-Mon': 'intensity_sum',
            'ImgIsSaturated-Mon': 'is_saturated',
            'ImgROIXFitAmplitude-Mon': ('fitx', 'roi_amplitude'),
            'ImgROIXFitMean-Mon': ('fitx', 'roi_mean'),
            'ImgROIXFitSigma-Mon': ('fitx', 'roi_sigma'),
            'ImgROIXFitError-Mon': ('fitx', 'roi_fit_error'),
            'ImgROIYFitAmplitude-Mon': ('fity', 'roi_amplitude'),
            'ImgROIYFitMean-Mon': ('fity', 'roi_mean'),
            'ImgROIYFitSigma-Mon': ('fity', 'roi_sigma'),
            'ImgROIYFitError-Mon': ('fity', 'roi_fit_error'),
            'ImgFitAngle-Mon': 'angle',
        }

    _INIT_PVS_2_IMGFIT = {
            'ImgSizeX-Cte': ('fitx', 'size'),
            'ImgSizeY-Cte': ('fity', 'size'),
            'ImgROIX-RB': ('fitx', 'roi'),
            'ImgROIY-RB': ('fity', 'roi'),
        }

    def __init__(self, driver=None, const=None):
        """Initialize the instance."""
        self._driver = driver
        self._const = const
        self._database = const.get_database()

        # get measurement arguments
        fwhmx_factor = \
            self._database['ImgROIXUpdateWithFWHMFactor-RB']['value']
        fwhmy_factor = \
            self._database['ImgROIYUpdateWithFWHMFactor-RB']['value']
        roi_with_fwhm = \
            self._database['ImgROIUpdateWithFWHM-Sts']['value']

        # create measurement objects
        self._meas = Measurement(
            const.devname,
            fwhmx_factor=fwhmx_factor, fwhmy_factor=fwhmy_factor,
            roi_with_fwhm=roi_with_fwhm)

        # print info about the IOC
        dbase = self._database
        _util.print_ioc_banner(
            ioc_name='BL ImgProc IOC',
            db=dbase,
            description='Image Processing IOC (FAC)',
            version=dbase['Version-Cte']['value'],
            prefix=const.devname)

        self._meas.callback = self.update_driver

    @property
    def driver(self):
        """."""
        return self._driver

    @driver.setter
    def driver(self, value):
        """."""
        self._driver = value

    def process(self, interval):
        """Run continuously in the main thread."""
        self._update_pv('TimestampUpdate-Mon', _time.time())
        _time.sleep(interval)

    def write(self, reason, value):
        """Write value in objects and database."""
        if not reason.endswith('-SP') and not reason.endswith('-Sel'):
            _log.warning('PV %s is not writable!', reason)
            return False

        res = self._write_roi(reason, value)
        if res is not None:
            return res

        res = self._write_fwhm_factor(reason, value)
        if res is not None:
            return res

        res = self._write_update_roi_with_fwhm(reason, value)
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
        self._meas.callback = self.update_driver

    def _write_sp_rb(self, reason, value):
        # update SP
        self._update_pv(reason, value)

        reason = reason.replace('-SP', '-RB')
        reason = reason.replace('-Sel', '-Sts')

        # update RB
        self._update_pv(reason, value)

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
            self._driver.setParam('ImgLog-Mon', value)
            _log.debug(msg)
            self._driver.updatePV('ImgLog-Mon')
            self._driver.setParamStatus(
                reason, _Alarm.TIMEOUT_ALARM, _Severity.INVALID_ALARM)
            return False

    def _write_fwhm_factor(self, reason, value):
        if reason not in (
                'ImgROIXUpdateWithFWHMFactor-SP',
                'ImgROIYUpdateWithFWHMFactor-SP'
                ):
            return None
        if 'X' in reason:
            self._meas.fwhmx_factor = value
        else:
            self._meas.fwhmy_factor = value
        self._write_sp_rb(reason, value)

        return True

    def _write_update_roi_with_fwhm(self, reason, value):
        """."""
        if reason not in ('ImgROIUpdateWithFWHM-Sel'):
            return None
        self._meas.update_roi_with_fwhm = value
        self._write_sp_rb(reason, value)

        return True

    def _conv_imgattr2value(self, attr):
        value = self._meas.image2dfit
        if isinstance(attr, tuple):
            for obj in attr:
                value = getattr(value, obj)
        else:
            value = getattr(value, attr)
        return value

    def _update_pv(self, pvname, value=None, success=True):
        """."""
        if success:
            self._driver.setParam(pvname, value)
            _log.debug('{}: updated'.format(pvname))
            self._driver.updatePV(pvname)
            self._driver.setParamStatus(
            pvname, _Alarm.NO_ALARM, _Severity.NO_ALARM)
        else:
            self._driver.setParamStatus(
                    pvname, _Alarm.TIMEOUT_ALARM, _Severity.INVALID_ALARM)

    def _update_driver(self):
        """Update all parameters at every image PV callback."""
        # heartbeat update
        self._heart_beat_update()

        for pvname, attr in App._MON_PVS_2_IMGFIT.items():
            if pvname == 'TimestampUpdate-Mon':
                continue

            # check if is roi_rb and if it needs updating
            if pvname in ('ImgROIX-RB', 'ImgROIY-RB'):
                if not self._meas.update_roi_with_fwhm:
                    continue

            # get image attribute value
            value = self._conv_imgattr2value(attr)

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
            
            # update epics db
            if self._meas.update_success:
                self._update_pv(pvname, new_value)
            else:
                self._update_pv(pvname, success=False)
            
