import numpy as _np

from siriuspy.devices import DVF as _DVF
from mathphys import imgproc as _imgproc


class Measurement():
    """."""

    DVF_IMAGE_PROPTY = 'image1:ArrayData'

    def __init__(self,
            devname, fwhmx_factor, fwhmy_factor, roi_with_fwhm, callback=None):
        """."""
        self._devname = devname
        self._callback = callback
        self._update_success = True
        self._dvf = None
        self._image2dfit = None
        self._sizex = None
        self._sizey = None
        self._fwhmx_factor = fwhmx_factor
        self._fwhmy_factor = fwhmy_factor
        self._roi_with_fwhm = roi_with_fwhm
        self._create_dvf()

    @property
    def devname(self):
        """."""
        return self._devname

    @property
    def dvf(self):
        """."""
        return self._dvf

    @property
    def image2dfit(self):
        """."""
        return self._image2dfit

    @property
    def sizex(self):
        """."""
        return self._sizex

    @property
    def sizey(self):
        """."""
        return self._sizey

    @property
    def fwhmx_factor(self):
        """."""
        return self._fwhmx_factor

    @property
    def fwhmy_factor(self):
        """."""
        return self._fwhmy_factor

    @property
    def update_success(self):
        """."""
        return self._update_success

    @property
    def update_roi_with_fwhm(self):
        """."""
        return self._roi_with_fwhm

    @update_roi_with_fwhm.setter
    def update_roi_with_fwhm(self, value):
        """."""
        self._roi_with_fwhm = value

    @property
    def callback(self):
        """."""
        return self._callback

    @callback.setter
    def callback(self, value):
        """."""
        self._callback = value

    @property
    def fitx_is_nan(self):
        return _np.isnan(self._image2dfit.fitx.roi_fit_error)

    @property
    def fity_is_nan(self):
        return _np.isnan(self._image2dfit.fity.roi_fit_error)

    def set_roix(self, value):
        """."""
        _, roiy = self._image2dfit.roi
        try:
            self._image2dfit.roi = [value, roiy]
            self._update_success = True
        except:
            self._update_success = False

    def set_roiy(self, value):
        """."""
        roix, _ = self._image2dfit.roi
        try:
            self._image2dfit.roi = [roix, value]
            self._update_success = True
        except:
            self._update_success = False

    def process_image(self, **kwargs):
        """Process image."""
        # NOTE: should we check whether IOC is providing image
        # (DVF.acquisition_status) and run DVF.cmd_acquire_on if not?
        try:
            if not self._image2dfit:
                # no image2dfit yet
                roix, roiy = (None, None)
            elif self.update_roi_with_fwhm:
                # recalc roi using fwhm factors
                roix = self._image2dfit.fitx.calc_roi_with_fwhm(self.fwhmx_factor)
                roiy = self._image2dfit.fity.calc_roi_with_fwhm(self.fwhmy_factor)
            else:
                # reuse current roi for new image
                roix = self._image2dfit.fitx.roi
                roiy = self._image2dfit.fity.roi
            self._
            data = self._dvf.image
            self._image2dfit = _imgproc.Image2D_Fit(
                data=data, roix=roix, roiy=roiy)
            self._update_success = True
        except:
            self._update_success = False

        # run registered driver callback
        if self._callback:
            self._callback()

    def _create_dvf(self):
        """Create DVO object and add process_image callback."""
        self._dvf = _DVF(self._devname)
        self._sizey = self._dvf.parameters.IMAGE_SIZE_Y
        self._sizex = self._dvf.parameters.IMAGE_SIZE_X
        self._dvf.wait_for_connection(timeout=5)
        imgpv = self._dvf.pv_object(Measurement.DVF_IMAGE_PROPTY)
        imgpv.add_callback(self.process_image)


