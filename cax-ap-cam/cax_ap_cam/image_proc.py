import numpy as np
from mathphys import images

class MeasProc():
    def __init__(self, callback=None):
        data = images.Image2D.generate_gaussian_2d(
            amp=255, angle=0*np.pi/180, offset=0, rand_amp=0,
            saturation_intensity=None,
            sizex=1280, sigmax=50, meanx=500,
            sizey=1024, sigmay=20, meany=600,
        )
        self.imag_processor = images.Image2D_Fit(data=data)

    def pvname2attrname(self, pvname):
        return pvname[:-3].lower()

    def update_roi(self, reason, value, update_pvs):
        if 'X' in reason:
            self.imag_processor.roix = value
        else:
            self.imag_processor.roiy = value
        update_pvs(self.imag_processor)
