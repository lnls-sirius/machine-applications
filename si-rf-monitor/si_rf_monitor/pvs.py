"""PVs definition for the IOC."""

MAX_BUFFER_SIZE = 3600
MIN_INTERVAL = 0.1  # [s]
MAX_TEMP_DIFF = 50  # [K]
MAX_TEMP_RATE = 0.5  # [K/min]
DEF_TIME_WIN = 40  # [s]
MIN_TIME_WIN = 3  # [s]
MAX_TIME_WIN = 1800  # [s]

IOC_PREFIX = 'SI-03SP:RF-CryoMod-2:'

pvs_database = {
    'CavTempRateTimeInterval-SP': {
        'type': 'float', 'value': DEF_TIME_WIN, 'prec': 3, 'unit': 's',
        'hilim': MIN_TIME_WIN, 'high': MIN_TIME_WIN, 'hihi': MIN_TIME_WIN,
        'lolim': MAX_TIME_WIN, 'low': MAX_TIME_WIN, 'lolo': MAX_TIME_WIN,
    },
    'CavTempRateTimeInterval-RB': {
        'type': 'float', 'value': DEF_TIME_WIN, 'prec': 3, 'unit': 's',
        'hilim': MIN_TIME_WIN, 'high': MIN_TIME_WIN, 'hihi': MIN_TIME_WIN,
        'lolim': MAX_TIME_WIN, 'low': MAX_TIME_WIN, 'lolo': MAX_TIME_WIN,
    },

    'BT212_CavTopTempRate-Mon': {
        'type': 'float', 'value': 0, 'prec': 3, 'unit': 'K/min',
        'hilim': MAX_TEMP_RATE, 'high': MAX_TEMP_RATE, 'hihi': MAX_TEMP_RATE,
        'lolim': -MAX_TEMP_RATE, 'low': -MAX_TEMP_RATE, 'lolo': -MAX_TEMP_RATE,
    },
    'BT211_CavBotTempRate-Mon': {
        'type': 'float', 'value': 0, 'prec': 3, 'unit': 'K/min',
        'hilim': MAX_TEMP_RATE, 'high': MAX_TEMP_RATE, 'hihi': MAX_TEMP_RATE,
        'lolim': -MAX_TEMP_RATE, 'low': -MAX_TEMP_RATE, 'lolo': -MAX_TEMP_RATE,
    },
    'BT210_HeVesselHeaterTempRate-Mon': {
        'type': 'float', 'value': 0, 'prec': 3, 'unit': 'K/min',
        'hilim': MAX_TEMP_RATE, 'high': MAX_TEMP_RATE, 'hihi': MAX_TEMP_RATE,
        'lolim': -MAX_TEMP_RATE, 'low': -MAX_TEMP_RATE, 'lolo': -MAX_TEMP_RATE,
    },

    'BT212_CavTopTempMaxRate-Mon': {
        'type': 'float', 'value': MAX_TEMP_RATE, 'prec': 3, 'unit': 'K/min',
    },
    'BT211_CavBotTempMaxRate-Mon': {
        'type': 'float', 'value': MAX_TEMP_RATE, 'prec': 3, 'unit': 'K/min',
    },
    'BT210_HeVesselHeaterTempMaxRate-Mon': {
        'type': 'float', 'value': MAX_TEMP_RATE, 'prec': 3, 'unit': 'K/min',
    },
    'BT212_CavTopTempMinRate-Mon': {
        'type': 'float', 'value': -MAX_TEMP_RATE, 'prec': 3, 'unit': 'K/min',
    },
    'BT211_CavBotTempMinRate-Mon': {
        'type': 'float', 'value': -MAX_TEMP_RATE, 'prec': 3, 'unit': 'K/min',
    },
    'BT210_HeVesselHeaterTempMinRate-Mon': {
        'type': 'float', 'value': -MAX_TEMP_RATE, 'prec': 3, 'unit': 'K/min',
    },

    'CavTopBotTempDiff-Mon': {
        'type': 'float', 'value': 0, 'prec': 3, 'unit': 'K',
        'hilim': MAX_TEMP_DIFF, 'high': MAX_TEMP_DIFF, 'hihi': MAX_TEMP_DIFF,
        'lolim': -MAX_TEMP_DIFF, 'low': -MAX_TEMP_DIFF, 'lolo': -MAX_TEMP_DIFF,
    },
    'CavTopBotTempMaxDiff-Mon': {
        'type': 'float', 'value': MAX_TEMP_DIFF, 'prec': 3, 'unit': 'K',
    },
    'CavTopBotTempMinDiff-Mon': {
        'type': 'float', 'value': -MAX_TEMP_DIFF, 'prec': 3, 'unit': 'K',
    },
}
