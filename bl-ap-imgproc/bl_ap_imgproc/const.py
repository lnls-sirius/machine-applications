from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy import util as _util


class Constants:

    def __init__(self, devname=''):
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

    def _get_image_db(self):
        sufix = '-Mon'
        dbase = {
            'ImgSizeX-Cte': {
                'type': 'int', 'unit': 'px'
            },
            'ImgSizeY-Cte': {
                'type': 'int', 'unit': 'pixel'
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
                'type': 'int',
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
                    'type': 'int', 'count': 2, 'unit': 'px'
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
            })
        return db

    def _get_fit_db(self):
        db = {}
        mon_ = '-Mon'
        for axis in ['X', 'Y']:
            db.update({
                'ImgFit' + axis + 'Sigma' + mon_: {
                    'type': 'float', 'unit': 'px'
                },
                'ImgFit' + axis + 'Mean' + mon_: {
                    'type': 'float', 'unit': 'px'
                },
                'ImgFit' + axis + 'Amplitude' + mon_: {
                    'type': 'float', 'unit': 'intensity',
                },
                'ImgFit' + axis + 'Error' + mon_: {
                    'type': 'float', 'unit': '%'
                }
            })
        db.update({
            'ImgFitAngle' + mon_: {
                'type': 'float', 'unit': 'rad'
            },
            'ImgLog' + mon_: {
                'type': 'string', 'value': 'Starting...',
            },
            })
        return db

    def get_database(self):
        return self._database

    def get_prefix(self):
        return self.ioc_prefix

    def _create_database(self):
        database = dict()
        database.update(
            self._get_image_db())
        database.update(
            self._get_roi_db())
        database.update(
            self._get_fit_db())
        database['Version-Cte'] = {
            'type': 'string',
            'value': _util.get_last_commit_hash()
        }
        return database
