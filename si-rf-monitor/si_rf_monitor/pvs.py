"""PVs definition for the IOC."""

MAX_BUFFER_SIZE = 3600
MIN_INTERVAL = 0.1  # [s]
MAX_TEMP_DIFF = 50  # [K]
MAX_TEMP_RATE = 0.5  # [K/min]
DEF_TIME_WIN = 300  # [s]
MIN_TIME_WIN = 20  # [s]
MAX_TIME_WIN = 1800  # [s]


PREFIX_TEMPLATE = 'SI-03SP:RF-CryoMod-{0:d}:'.format


def get_database(prefix='', system=1):
    """."""
    if system not in {1, 2}:
        raise ValueError('system must be an integer value of 1 or 2')

    prop_prefix = f'BT{system:d}'
    return {
        prefix + 'CavTempRateTimeInterval-SP': {
            'type': 'float',
            'value': DEF_TIME_WIN,
            'prec': 3,
            'unit': 's',
            'hilim': MIN_TIME_WIN,
            'high': MIN_TIME_WIN,
            'hihi': MIN_TIME_WIN,
            'lolim': MAX_TIME_WIN,
            'low': MAX_TIME_WIN,
            'lolo': MAX_TIME_WIN,
        },
        prefix + 'CavTempRateTimeInterval-RB': {
            'type': 'float',
            'value': DEF_TIME_WIN,
            'prec': 3,
            'unit': 's',
            'hilim': MIN_TIME_WIN,
            'high': MIN_TIME_WIN,
            'hihi': MIN_TIME_WIN,
            'lolim': MAX_TIME_WIN,
            'low': MAX_TIME_WIN,
            'lolo': MAX_TIME_WIN,
        },
        prefix + prop_prefix + '12_CavTopTempRate-Mon': {
            'type': 'float',
            'value': 0,
            'prec': 3,
            'unit': 'K/min',
            'hilim': MAX_TEMP_RATE,
            'high': MAX_TEMP_RATE,
            'hihi': MAX_TEMP_RATE,
            'lolim': -MAX_TEMP_RATE,
            'low': -MAX_TEMP_RATE,
            'lolo': -MAX_TEMP_RATE,
        },
        prefix + prop_prefix + '11_CavBotTempRate-Mon': {
            'type': 'float',
            'value': 0,
            'prec': 3,
            'unit': 'K/min',
            'hilim': MAX_TEMP_RATE,
            'high': MAX_TEMP_RATE,
            'hihi': MAX_TEMP_RATE,
            'lolim': -MAX_TEMP_RATE,
            'low': -MAX_TEMP_RATE,
            'lolo': -MAX_TEMP_RATE,
        },
        prefix + prop_prefix + '10_HeVesselHeaterTempRate-Mon': {
            'type': 'float',
            'value': 0,
            'prec': 3,
            'unit': 'K/min',
            'hilim': MAX_TEMP_RATE,
            'high': MAX_TEMP_RATE,
            'hihi': MAX_TEMP_RATE,
            'lolim': -MAX_TEMP_RATE,
            'low': -MAX_TEMP_RATE,
            'lolo': -MAX_TEMP_RATE,
        },
        prefix + prop_prefix + '12_CavTopTempMaxRate-Mon': {
            'type': 'float',
            'value': MAX_TEMP_RATE,
            'prec': 3,
            'unit': 'K/min',
        },
        prefix + prop_prefix + '11_CavBotTempMaxRate-Mon': {
            'type': 'float',
            'value': MAX_TEMP_RATE,
            'prec': 3,
            'unit': 'K/min',
        },
        prefix + prop_prefix + '10_HeVesselHeaterTempMaxRate-Mon': {
            'type': 'float',
            'value': MAX_TEMP_RATE,
            'prec': 3,
            'unit': 'K/min',
        },
        prefix + prop_prefix + '12_CavTopTempMinRate-Mon': {
            'type': 'float',
            'value': -MAX_TEMP_RATE,
            'prec': 3,
            'unit': 'K/min',
        },
        prefix + prop_prefix + '11_CavBotTempMinRate-Mon': {
            'type': 'float',
            'value': -MAX_TEMP_RATE,
            'prec': 3,
            'unit': 'K/min',
        },
        prefix + prop_prefix + '10_HeVesselHeaterTempMinRate-Mon': {
            'type': 'float',
            'value': -MAX_TEMP_RATE,
            'prec': 3,
            'unit': 'K/min',
        },
        prefix + 'CavTopBotTempDiff-Mon': {
            'type': 'float',
            'value': 0,
            'prec': 3,
            'unit': 'K',
            'hilim': MAX_TEMP_DIFF,
            'high': MAX_TEMP_DIFF,
            'hihi': MAX_TEMP_DIFF,
            'lolim': -MAX_TEMP_DIFF,
            'low': -MAX_TEMP_DIFF,
            'lolo': -MAX_TEMP_DIFF,
        },
        prefix + 'CavTopBotTempMaxDiff-Mon': {
            'type': 'float',
            'value': MAX_TEMP_DIFF,
            'prec': 3,
            'unit': 'K',
        },
        prefix + 'CavTopBotTempMinDiff-Mon': {
            'type': 'float',
            'value': -MAX_TEMP_DIFF,
            'prec': 3,
            'unit': 'K',
        },
    }
