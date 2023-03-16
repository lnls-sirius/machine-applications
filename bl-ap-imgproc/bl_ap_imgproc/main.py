"""Module with main IOC Class."""

import time as _time
import logging as _log

from pcaspy import Alarm as _Alarm
from pcaspy import Severity as _Severity

from siriuspy import util as _util

from .meas import Measurement


class App:
    """BL Image Processing IOC Application."""

    CHECK_IMG_ACQUIRE = True

    _MON_PVS_2_IMGFIT = {
            # These PVs are updated at evry image processing
            # --- image intensity ---
            'ImgIntensityMin-Mon': 'intensity_min',
            'ImgIntensityMax-Mon': 'intensity_max',
            'ImgIntensitySum-Mon': 'intensity_sum',
            'ImgIsSaturated-Mon': 'is_saturated',
            # --- roix ---
            'ImgROIX-RB': ('fitx', 'roi'),
            'ImgROIXCenter-Mon': ('fitx', 'roi_center'),
            'ImgROIXFWHM-Mon': ('fitx', 'roi_fwhm'),
            # --- roix_fit ---
            'ImgROIXFitAmplitude-Mon': ('fitx', 'roi_amplitude'),
            'ImgROIXFitMean-Mon': ('fitx', 'roi_mean'),
            'ImgROIXFitSigma-Mon': ('fitx', 'roi_sigma'),
            'ImgROIXFitError-Mon': ('fitx', 'roi_fit_error'),
            # --- roixy ---
            'ImgROIY-RB': ('fity', 'roi'),
            'ImgROIYCenter-Mon': ('fity', 'roi_center'),
            'ImgROIYFWHM-Mon': ('fity', 'roi_fwhm'),
            # --- roiy_fit ---
            'ImgROIYFitAmplitude-Mon': ('fity', 'roi_amplitude'),
            'ImgROIYFitMean-Mon': ('fity', 'roi_mean'),
            'ImgROIYFitSigma-Mon': ('fity', 'roi_sigma'),
            'ImgROIYFitError-Mon': ('fity', 'roi_fit_error'),
            # --- gauss2d fit ---
            'ImgFitAngle-Mon': 'angle',
        }

    _INIT_PVS_2_IMGFIT = {
            # These are either constant PVs or readback PVs whose
            # initializations need external input
            'ImgSizeX-Cte': ('fitx', 'size'),
            'ImgSizeY-Cte': ('fity', 'size'),
            'ImgROIX-RB': ('fitx', 'roi'),
            'ImgROIY-RB': ('fity', 'roi'),
            'ImgROIX-SP': ('fitx', 'roi'),  # NOTE: should we initialize this?
            'ImgROIY-SP': ('fity', 'roi'),  # NOTE: should we initialize this?
        }

    def __init__(self, driver=None, const=None):
        """Initialize the instance."""
        self._driver = driver
        self._const = const
        self._database = const.get_database()
        self._heartbeat = 0
        self._timestamp_last_update = _time.time()

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
            version=dbase['ImgVersion-Cte']['value'],
            prefix=const.devname)

        self._meas.callback = self.update_driver

    @property
    def const(self):
        """."""
        return self._const

    @property
    def driver(self):
        """."""
        return self._driver

    @driver.setter
    def driver(self, value):
        """."""
        self._driver = value

    @property
    def meas(self):
        """."""
        return self._meas

    @property
    def heartbeat(self):
        """."""
        return self._heartbeat

    def increment_heartbeat(self):
        """."""
        self._heartbeat += 1

    def process(self, interval):
        """Run continuously in the main thread."""
        # update heartbeat
        self.increment_heartbeat()
        self._write_pv('ImgTimestampUpdate-Mon', _time.time())

        # if enabled, check if image acquisition is not working and set it
        if App.CHECK_IMG_ACQUIRE:
            self._check_acquisition_timeout()

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

    def init_driver(self):
        """Initialize PVs at startup."""
        # NOTE: this method has the same struct as _update_driver.
        # maybe they should be unified.
        for pvname, attr in App._INIT_PVS_2_IMGFIT.items():
            if self.meas.update_success == self.meas.UPDATE_SUCCESS:
                # get image attribute value
                value = self._conv_imgattr2value(attr)
                # update epics db successfully
                if value is not None:
                    self._write_pv(pvname, value)
                else:
                    msg = f'PV {pvname} could not be initialized!'
                    _log.warning(msg)
            else:
                # update epics db failure
                self._write_pv(pvname, success=False)
                # update Log
                self._write_log(self.meas.update_success)

    def update_driver(self):
        """Update all parameters at every image PV callback."""
        self._timestamp_last_update = _time.time()
        for pvname, attr in App._MON_PVS_2_IMGFIT.items():

            # check if is roi_rb and if it needs updating
            if pvname in ('ImgROIX-RB', 'ImgROIY-RB'):
                if not self.meas.update_roi_with_fwhm:
                    continue

            # get image attribute value
            value = self._conv_imgattr2value(attr)
            if value is None:
                msg = f'PV {pvname} could not be updated!'
                _log.warning(msg)
                continue

            # check if fit is valid and update value
            if 'XFit' in pvname and self.meas.image2dfit.fitx.invalid_fit:
                valid = False
            elif 'YFit' in pvname and self.meas.image2dfit.fity.invalid_fit:
                valid = False
            elif 'FitAngle' in pvname:
                valid = \
                    not self.meas.image2dfit.fitx.invalid_fit and \
                    not self.meas.image2dfit.fity.invalid_fit
            else:
                valid = True

            new_value = value if valid else 0

            # update epics db
            if self.meas.update_success == self.meas.UPDATE_SUCCESS:
                self._write_pv(pvname, new_value)
            else:
                self._write_pv(pvname, success=False)

        if self.meas.update_success != self.meas.UPDATE_SUCCESS:
            # update Log
            self._write_log(self.meas.update_success)

    def _check_acquisition_timeout(self):
        """."""
        interval = _time.time() - self._timestamp_last_update
        if self.meas.acquisition_timeout(interval):
            # NOTE: this set_acquire is a long process. should we run it
            # in a unique thread?
            self._write_log('DVF Image update timeout!')
            self.meas.set_acquire()
            self._timestamp_last_update = _time.time()

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

    def _write_pv(self, pvname, value=None, success=True):
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

    def _write_log(self, message, success=True):
        """."""
        message += f' (heartbeat {self.heartbeat})'
        self._write_pv('ImgLog-Mon', message, success)

    def _write_pv_sp_rb(self, reason, value):
        # update SP
        self._write_pv(reason, value)

        reason = reason.replace('-SP', '-RB')
        reason = reason.replace('-Sel', '-Sts')

        # update RB
        self._write_pv(reason, value)

    def _write_roi(self, reason, value):
        if reason not in ('ImgROIX-SP', 'ImgROIY-SP'):
            return None
        if 'X' in reason:
            self.meas.set_roix(value)
        else:
            self._meas.set_roiy(value)

        if self.meas.update_success == self.meas.UPDATE_SUCCESS:
            self._write_pv_sp_rb(reason, value)
            self._write_pv('ImgLog-Mon', self.meas.update_success)
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
            self.meas.fwhmx_factor = value
        else:
            self.meas.fwhmy_factor = value
        self._write_pv_sp_rb(reason, value)

        return True

    def _write_update_roi_with_fwhm(self, reason, value):
        """."""
        if reason not in ('ImgROIUpdateWithFWHM-Sel'):
            return None
        self.meas.update_roi_with_fwhm = value
        self._write_pv_sp_rb(reason, value)

        return True

    def _conv_imgattr2value(self, attr):
        value = self.meas.image2dfit
        if value is None:
            # image2dfit object anomalously not created yet!
            return None
        if isinstance(attr, tuple):
            for obj in attr:
                value = getattr(value, obj)
        else:
            value = getattr(value, attr)
        return value
