"""PVs definition for the IOC."""

from siriuspy import csdev as _csdev


class Const(_csdev.Const):
    """Const class."""
    _register = _csdev.Const.register

    DisconnConn = _register("DisconnConn", _csdev.ETypes.DISCONN_CONN)


pvs_database = {

    'Version-Cte': {'type': 'str', 'value': 'UNDEF'},
    'TimestampBoot-Cte': {
        'type': 'float', 'value': 0,
        'prec': 7, 'unit': 'timestamp'},
    'TimestampUpdate-Mon': {
        'type': 'float', 'value': 0,
        'prec': 7, 'unit': 'timestamp'},
    'Log-Mon': {'type': 'str', 'value': 'Starting...'},
    'ConnStatus-Mon': {
        'type': 'enum', 'value': Const.DisconnConn.Disconnected,
        'enums': _csdev.ETypes.DISCONN_CONN,
        'unit': 'DisconnConn',
    },

}
