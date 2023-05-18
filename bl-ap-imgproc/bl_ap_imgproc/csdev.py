"""Const module."""

import time as _time

from mathphys.functions import get_namedtuple as _get_namedtuple

from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy import util as _util
from siriuspy import csdev as _csdev


# TODO: move this module to siriuspy

class ETypes(_csdev.ETypes):
    """Local enumerate types."""

    NO_YES = ('No', 'Yes')
    STS_LBLS_DVF = ('Connected', )


_et = ETypes  # syntactic sugar


class Constants(_csdev.Const):
    """."""

    NoYes = _get_namedtuple('NoYes', _et.NO_YES)
    StsLblsDVF = _get_namedtuple('StsLblsDVF', _et.STS_LBLS_DVF)

    def __init__(self, devname):
        """."""
        self._devname = devname
        self._ioc_prefix = _vaca_prefix + ('-' if _vaca_prefix else '')
        self._ioc_prefix += devname + ':'
        self._database = self._create_database()

    @property
    def devname(self):
        """."""
        return self._devname

    @property
    def ioc_prefix(self):
        """."""
        return self._ioc_prefix

    def get_database(self):
        """."""
        return self._database

    def get_prefix(self):
        """."""
        return self.ioc_prefix

    def _create_database(self):
        database = dict()
        database.update(self._get_image_db())
        database.update(self._get_roi_db())
        database.update(self._get_fit_db())
        database.update(self._get_others_db())
        database = _csdev.add_pvslist_cte(database)

        # rename Properties-Cte to ImgProperties-Cte
        database['ImgProperties-Cte'] = database['Properties-Cte']
        del database['Properties-Cte']

        # TODO: Version here will take value from siriuspy package, when
        # code is moved to this repo. Is this what we want? maybe we should
        # start composing the string from siriuspy + machine-applicaions?
        database['ImgVersion-Cte'] = {
            'type': 'string',
            'value': _util.get_last_commit_hash()
        }

        return database

    def _get_image_db(self):
        sufix = '-Mon'
        dbase = {
            'ImgDVFSizeX-Cte': {
                'type': 'int', 'unit': 'px'
            },
            'ImgDVFSizeY-Cte': {
                'type': 'int', 'unit': 'px'
            },
            'ImgSizeX' + sufix: {
                'type': 'int', 'unit': 'px'
            },
            'ImgSizeY' + sufix: {
                'type': 'int', 'unit': 'px'
            },
            'ImgIntensityMin' + sufix: {
                'type': 'int', 'unit': 'intensity'
            },
            'ImgIntensityMax' + sufix: {
                'type': 'int', 'unit': 'intensity'
            },
            'ImgIntensitySum' + sufix: {
                'type': 'int', 'unit': 'intensity'
            },
            'ImgIsSaturated' + sufix: {
                'type': 'enum', 'enums': _et.NO_YES,
                'value': self.NoYes.No,
            },
            'ImgIsWithBeam' + sufix: {
                'type': 'enum', 'enums': _et.NO_YES,
                'value': self.NoYes.No,
            },
            'ImgIsWithBeamThreshold-SP': {
                'type': 'int', 'unit': 'intensity', 'value': 10,
            },
            'ImgIsWithBeamThreshold-RB': {
                'type': 'int', 'unit': 'intensity', 'value': 10,
            },
            }
        return dbase

    def _get_roi_db(self):
        db = {}
        rb_ = '-RB'
        sp_ = '-SP'
        mon_ = '-Mon'
        for axis in ['X', 'Y']:
            db.update({
                'ImgROI' + axis + sp_: {
                    'type': 'int', 'count': 2, 'unit': 'px',
                },
                'ImgROI' + axis + rb_: {
                    'type': 'int', 'count': 2, 'unit': 'px'
                },
                'ImgROI' + axis + 'Center' + mon_: {
                    'type': 'int', 'unit': 'px'
                },
                'ImgROI' + axis + 'FWHM' + mon_: {
                    'type': 'int', 'unit': 'px'
                },
                'ImgROI' + axis + 'UpdateWithFWHMFactor-SP': {
                    'type': 'float', 'value': 2.0, 'unit': 'fwhm_factor',
                    'prec': 3, 'lolim': 0, 'hilim': 2000,
                },
                'ImgROI' + axis + 'UpdateWithFWHMFactor-RB': {
                    'type': 'float', 'value': 2.0, 'unit': 'fwhm_factor',
                    'prec': 3, 'lolim': 0, 'hilim': 2000,
                },
            })
        return db

    def _get_fit_db(self):
        db = {}
        mon_ = '-Mon'
        for axis in ['X', 'Y']:
            db.update({
                'ImgROI' + axis + 'FitSigma' + mon_: {
                    'type': 'float', 'unit': 'px', 'prec': 3,
                },
                'ImgROI' + axis + 'FitMean' + mon_: {
                    'type': 'float', 'unit': 'px', 'prec': 3,
                },
                'ImgROI' + axis + 'FitAmplitude' + mon_: {
                    'type': 'float', 'unit': 'intensity', 'prec': 3,
                },
                'ImgROI' + axis + 'FitError' + mon_: {
                    'type': 'float', 'unit': '%', 'prec': 3,
                },
            })
        db.update({
            'ImgROIUpdateWithFWHM-Sel': {
                'type': 'enum', 'enums': _et.DSBL_ENBL,
                'value': self.DsblEnbl.Dsbl,
            },
            'ImgROIUpdateWithFWHM-Sts': {
                'type': 'enum', 'enums': _et.DSBL_ENBL,
                'value': self.DsblEnbl.Dsbl,
            },
            'ImgFitAngle' + mon_: {
                'type': 'float', 'unit': 'deg', 'prec': 3,
            },
            'ImgFitSigma1' + mon_: {
                'type': 'float', 'unit': 'px', 'prec': 3,
            },
            'ImgFitSigma2' + mon_: {
                'type': 'float', 'unit': 'px', 'prec': 3,
            },
            'ImgFitProcTime' + mon_: {
                'type': 'float', 'unit': 'ms', 'prec': 3,
            },
            'ImgFitAngleUseCMomSVD-Sel': {
                'type': 'enum', 'enums': _et.NO_YES,
                'value': self.NoYes.No,
            },
            'ImgFitAngleUseCMomSVD-Sts': {
                'type': 'enum', 'enums': _et.NO_YES,
                'value': self.NoYes.No,
            },
            })
        return db

    def _get_others_db(self):
        db = {}
        mon_ = '-Mon'
        db.update({
            'ImgVersion-Cte': {
                'type': 'string',
                'value': _util.get_last_commit_hash()
            },
            'ImgLog' + mon_: {
                'type': 'string', 'value': 'Starting...',
            },
            'ImgTimestampBoot-Cte': {
                'type': 'float', 'value': _time.time(),
                'prec': 7, 'unit': 'timestamp',
            },
            'ImgTimestampUpdate-Mon': {
                'type': 'float',
                'prec': 7, 'unit': 'timestamp',
            },
            'ImgDVFStatus-Mon': {
                'type': 'int', 'value': 0b00000001,
            },
            'ImgDVFStatusLabels-Cte': {
                'type': 'string', 'count': len(self.StsLblsDVF._fields),
                'value': self.StsLblsDVF._fields,
            },
            })

        return db
