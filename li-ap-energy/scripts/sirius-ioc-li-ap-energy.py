#!/usr/local/bin/python-sirius -u

import argparse as _argparse
from as_ti_control import run, TRIG_TYPES

parser = _argparse.ArgumentParser(description="Run Timing IOC.")
parser.add_argument(
    '-t', "--timing", type=str, default='trig-all',
    help="Which high level Timing properties to manage (trig-all)",
    choices=sorted(TRIG_TYPES)
    )
parser.add_argument(
    '-l', '--lock', action='store_true', default=False,
    help="Force default initial HL state on LL IOCs. (False)",
    )
parser.add_argument(
    '-w', '--wait', type=float, default=5,
    help='In case -l is not given, this is the time to wait in [s]' +
         'before start locking. (5s)'
    )
parser.add_argument(
    '-d', '--debug', action='store_true', default=False,
    help="Starts IOC in Debug Mode. (False)"
    )
parser.add_argument(
    '-i', '--interval', type=float, default=0.1,
    help="Set interval for server process in seconds. (0.1s)"
    )

args = parser.parse_args()
run(timing=args.timing, lock=args.lock, wait=args.wait,
    debug=args.debug, interval=args.interval)
