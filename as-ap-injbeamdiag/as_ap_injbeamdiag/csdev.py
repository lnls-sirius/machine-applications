"""PVs definition for the IOC."""

from siriuspy import csdev as _csdev


class Const(_csdev.Const):
    """Const class."""

    _register = _csdev.Const.register

    NRPTS_TB_TRAJ_DEF = 20
    NRPTS_TB_TRAJ_MAX = 100
    DisconnConn = _register('DisconnConn', _csdev.ETypes.DISCONN_CONN)


pvs_database = {
    'Version-Cte': {'type': 'str', 'value': 'UNDEF'},
    'TimestampBoot-Cte': {
        'type': 'float',
        'value': 0,
        'prec': 7,
        'unit': 'timestamp',
    },
    'TimestampUpdate-Mon': {
        'type': 'float',
        'value': 0,
        'prec': 7,
        'unit': 'timestamp',
    },
    'Log-Mon': {'type': 'str', 'value': 'Starting...'},
    'DevsConnStatus-Mon': {
        'type': 'enum',
        'value': Const.DisconnConn.Disconnected,
        'enums': _csdev.ETypes.DISCONN_CONN,
        'unit': 'DisconnConn',
    },
    'TBTrajNrPts-SP': {
        'type': int,
        'value': Const.NRPTS_TB_TRAJ_DEF,
        'lolim': 1,
        'hilim': Const.NRPTS_TB_TRAJ_MAX,
        'unit': '#',
    },
}
