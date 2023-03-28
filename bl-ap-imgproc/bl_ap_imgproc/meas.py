"""."""

from siriuspy.devices import DVF as _DVF
from mathphys import imgproc as _imgproc


class Measurement():
    """."""

    STATUS_SUCCESS = ''
    DVF_IMAGE_PROPTY = 'image1:ArrayData'
    MIN_ROI_SIZE = 5  # [pixels]
    TIMEOUT_CONN = 5  # [s]

    def __init__(
            self, devname, fwhmx_factor, fwhmy_factor,
            roi_with_fwhm, callback=None):
        """."""
        self._devname = devname
        self._callback = callback
        self._status = Measurement.STATUS_SUCCESS
        self._dvf = None
        self._fitgauss = _imgproc.FitGaussianScipy()
        self._image2dfit = None
        self._sizex = None
        self._sizey = None
        self._fwhmx_factor = fwhmx_factor
        self._fwhmy_factor = fwhmy_factor
        self._roi_with_fwhm = roi_with_fwhm

        # create DVF device
        self._create_dvf()

        # init image2dfit object
        self.process_image()

        # add callback
        self._imgpv = self._dvf.pv_object(Measurement.DVF_IMAGE_PROPTY)
        self._imgpv.add_callback(self.process_image)

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

    @fwhmx_factor.setter
    def fwhmx_factor(self, value):
        """."""
        self._fwhmx_factor = value

    @property
    def fwhmy_factor(self):
        """."""
        return self._fwhmy_factor

    @fwhmy_factor.setter
    def fwhmy_factor(self, value):
        """."""
        self._fwhmy_factor = value

    @property
    def status(self):
        """."""
        return self._status

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

    def acquisition_timeout(self, interval):
        """Check if given interval defines an image update timeout."""
        if self.dvf.acquisition_time:
            return interval > 10 * self.dvf.acquisition_time
        return False

    def set_acquire(self):
        """."""
        self.dvf.cmd_acquire_off()
        self.dvf.cmd_acquire_on()

    def set_roix(self, value):
        """."""
        _, roiy = self._image2dfit.roi
        try:
            self._image2dfit.roi = [value, roiy]
            self._status = Measurement.STATUS_SUCCESS
        except Exception:
            self._status = 'Unable to set ROIX'

    def set_roiy(self, value):
        """."""
        roix, _ = self._image2dfit.roi
        try:
            self._image2dfit.roi = [roix, value]
            self._status = Measurement.STATUS_SUCCESS
        except Exception:
            self._status = 'Unable to set ROIY'

    def reset_dvf(self):
        self._dvf.cmd_reset()
        return True

    def process_image(self, **kwargs):
        """Process image."""
        # check if DVF is connected
        if not self._dvf.connected:
            self._status = 'DVF not connecetd'
            return

        # symbol to image2d fit object
        img2dfit = self._image2dfit

        # define roi based on previus image or fwhm factors
        if not self._image2dfit:
            # no image2dfit yet
            roix, roiy = (None, None)
        elif self.update_roi_with_fwhm:
            # recalc roi using fwhm factors
            roix = img2dfit.fitx.calc_roi_with_fwhm(
                image=img2dfit.fitx, fwhm_factor=self.fwhmx_factor)
            roiy = img2dfit.fity.calc_roi_with_fwhm(
                image=img2dfit.fity, fwhm_factor=self.fwhmy_factor)
            if roix[1] - roix[0] < Measurement.MIN_ROI_SIZE:
                roix = None
            if roiy[1] - roiy[0] < Measurement.MIN_ROI_SIZE:
                roiy = None
        else:
            # reuse current roi for new image
            roix = self._image2dfit.fitx.roi
            roiy = self._image2dfit.fity.roi

        # get image data and process fitting
        try:
            data = self._dvf.image
            self._image2dfit = _imgproc.Image2D_Fit(
                data=data, fitgauss=self._fitgauss,
                roix=roix, roiy=roiy)
            self._status = Measurement.STATUS_SUCCESS
        except Exception:
            self._status = \
                f'Unable to process image shape'

        # run registered driver callback
        if self._callback:
            self._callback()

    def _create_dvf(self):
        """Create DVF object and add process_image callback."""
        self._dvf = _DVF(self._devname)
        self._sizey = self._dvf.parameters.IMAGE_SIZE_Y
        self._sizex = self._dvf.parameters.IMAGE_SIZE_X
        self._dvf.wait_for_connection(timeout=Measurement.TIMEOUT_CONN)