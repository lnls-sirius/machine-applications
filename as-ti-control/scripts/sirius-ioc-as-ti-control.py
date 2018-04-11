#!/usr/local/bin/python-sirius -u

import argparse as _argparse
from as_ti_control import as_ti_control

parser = _argparse.ArgumentParser(description="Run Timing IOC.")
parser.add_argument(
    '-e', '--evg', action='store_true', default=False,
    help="Manage high level interface for EVG Params: Clocks, Events, etc."
    )
parser.add_argument(
    '-t', "--triggers", type=str, default='none',
    help="Which high level Triggers to manage",
    choices=sorted(as_ti_control.TRIG_LISTS.keys())
    )
parser.add_argument(
    '-f', '--force', action='store_true', default=False,
    help="Force default initial HL state on LL IOCs.",
    )
parser.add_argument(
    '-w', '--wait', type=float, default=15,
    help='In case -f is not given, this is the time to wait in [s]' +
         'before start forcing.'
    )
parser.add_argument(
    '-d', '--debug', action='store_true', default=False,
    help="Starts IOC in Debug Mode."
    )

args = parser.parse_args()
as_ti_control.run(
    evg_params=args.evg, triggers=args.triggers,
    force=args.force, wait=args.wait, debug=args.debug,
    )
