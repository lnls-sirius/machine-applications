from siriuspy.envars import VACA_PREFIX as _vaca_prefix
from siriuspy import util as _util


class Constants:

    def __init__(self, devname=''):
        self.ioc_prefix = _vaca_prefix + ('-' if _vaca_prefix else '')
        self.ioc_prefix += devname + ':'

        self.set_database()

    def _get_intensity_saturated_db(self):
        sufix = '-RB'
        return {
            'Intensity_Min' + sufix: {
                'type': 'int'
            },
            'Intensity_Max' + sufix: {
                'type': 'int'
            },
            'Intensity_Avg' + sufix: {
                'type': 'float'
            },
            'Intensity_Sum' + sufix: {
                'type': 'int'
            },
            'Is_Saturated' + sufix: {
                'type': 'int'
            }
        }

    def _get_ROI_db(self):
        db = {}
        sufix = '-RB'
        sufixW = '-SP'
        for axis in ['X', 'Y']:
            db.update({
                'Size' + axis + sufix: {
                    'type': 'int'
                },
                'ROI' + axis + sufixW: {
                    'type': 'int', 'count': 2
                },
                'ROI' + axis + '_Center' + sufix: {
                    'type': 'int'
                },
                'ROI' + axis + '_FWHM' + sufix: {
                    'type': 'int'
                },
                'ROI' + axis + '_Sigma' + sufix: {
                    'type': 'float'
                },
                'ROI' + axis + '_Mean' + sufix: {
                    'type': 'float'
                },
                'ROI' + axis + '_Amplitude' + sufix: {
                    'type': 'float'
                },
                'ROI' + axis + '_Fit_Error' + sufix: {
                    'type': 'float', 'unit': '%'
                }
            })

        return db

    def set_database(self):
        self.database = dict()
        self.database.update(
            self._get_intensity_saturated_db())
        self.database.update(
            self._get_ROI_db())
        self.database['Version-Cte'] = {
            'type': 'string',
            'value': _util.get_last_commit_hash()
        }

    def get_database(self):
        return self.database

    def get_prefix(self):
        return self.ioc_prefix
