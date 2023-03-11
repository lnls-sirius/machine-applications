import numpy as _np

from siriuspy.devices import DVF as _DVF
from mathphys import imgproc as _imgproc


class Measurement():
    """."""

    def __init__(self,
            devname, fwhmx_factor, fwhmy_factor, roi_with_fwhm, callback=None):
        """."""
        self._devname = devname
        self._callback = callback
        self._update_success = True
        self._dvf = None
        self._imgproc = None
        self._sizex = None
        self._sizey = None
        self._fwhmx_factor = fwhmx_factor
        self._fwhmy_factor = fwhmy_factor
        self._roi_with_fwhm = roi_with_fwhm
        self._create_dvf()

    @property
    def imgproc(self):
        """."""
        return self._imgproc

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
    def callback(self):
        """."""
        return self._callback

    @callback.setter
    def callback(self, value):
        """."""
        self._callback = value

    @property
    def fitx_is_nan(self):
        return _np.isnan(self._imgproc.fitx.roi_fit_error)

    @property
    def fity_is_nan(self):
        return _np.isnan(self._imgproc.fity.roi_fit_error)

    def set_roix(self, value):
        """."""
        _, roiy = self._imgproc.roi
        try:
            self._imgproc.roi = [value, roiy]
            self._update_success = True
        except:
            self._update_success = False

    def set_roiy(self, value):
        """."""
        roix, _ = self._imgproc.roi
        try:
            self._imgproc.roi = [roix, value]
            self._update_success = True
        except:
            self._update_success = False

    def pvname2attrname(self, pvname):
        return pvname[:-3].lower()

    def process_image(self, **kwargs):
        """."""
        try:
            if not self._imgproc:
                roix, roiy = (None, None)
            elif self._roi_with_fwhm:
                roix = self._imgproc.fitx.calc_roi_with_fwhm(self.fwhmx_factor)
                roiy = self._imgproc.fity.calc_roi_with_fwhm(self.fwhmy_factor)
            else:
                roix = self._imgproc.fitx.roi
                roiy = self._imgproc.fity.roi
            data = self._dvf.image
            self._imgproc = _imgproc.Image2D_Fit(
                data=data, roix=roix, roiy=roiy)
            self._update_success = True
        except:
            self._update_success = False
        if self._callback:
            self._callback()

    def _create_dvf(self):
        self._dvf = _DVF(self._devname)
        self._sizey = self._dvf.parameters.IMAGE_SIZE_Y
        self._sizex = self._dvf.parameters.IMAGE_SIZE_X
        self._dvf.wait_for_connection(timeout=5)
        imgpv = self._dvf.pv_object('image1:ArrayData')
        imgpv.add_callback(self.process_image)


