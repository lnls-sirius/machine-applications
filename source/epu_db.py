import globals

args = globals.pv_prefix

pv_prefix = args.pv_prefix
pvdb = {
    'DriveAPos-Mon' : {
        'type' : 'float',
        'prec' : globals.position_precision,
        'count' : 1,
        'unit' : globals.position_units,
        'mdel' : -1,
        'scan' : globals.scan_rate,
        'asyn' : True,
        'asg' : 'readonly',
    },
    'DriveBPos-Mon' : {
        'type' : 'float',
        'prec' : globals.position_precision,
        'count' : 1,
        'unit' : globals.position_units,
        'mdel' : -1,
        'scan' : globals.scan_rate,
        'asyn' : True,
        'asg' : 'readonly',
    },
    'DriveSPos-Mon' : {
        'type' : 'float',
        'prec' : globals.position_precision,
        'count' : 1,
        'unit' : globals.position_units,
        'mdel' : -1,
        'scan' : globals.scan_rate,
        'asyn' : True,
        'asg' : 'readonly',
    },
    'DriveIPos-Mon' : {
        'type' : 'float',
        'prec' : globals.position_precision,
        'count' : 1,
        'unit' : globals.position_units,
        'mdel' : -1,
        'scan' : globals.scan_rate,
        'asyn' : True,
        'asg' : 'readonly',
    },
}