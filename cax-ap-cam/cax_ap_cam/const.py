from siriuspy.envars import VACA_PREFIX as _vaca_prefix

class Constants:

    def __init__(self, devname=''):
        self.ioc_prefix = _vaca_prefix + ('-' if _vaca_prefix else '')
        self.ioc_prefix += devname + ':'

        self.set_database()

    # Base_IOC_Change measurement object
    def set_database(self):
        self.database = {'Dispersion-SP': {
                'type': 'string', 'prec': 4, 'unit': 'mm',
                'value': '213'}}
        self.database['Version-Cte'] = {
            'type': 'string',
            'value': '1.0' #_util.get_last_commit_hash()
        }

    def get_database(self):
        return self.database

    def get_prefix(self):
        return self.ioc_prefix
