#!/usr/bin/env python-sirius

import argparse as _argparse

from as_ti_control import run, TRIG_TYPES

parser = _argparse.ArgumentParser(description="Run Timing IOC.")
parser.add_argument(
    '-s', "--section", type=str, default='as',
    help="Which section high level Timing properties to manage (as)",
    choices=sorted(TRIG_TYPES)
    )
parser.add_argument(
    '-d', '--debug', action='store_true', default=False,
    help="Starts IOC in Debug Mode. (False)"
    )

args = parser.parse_args()
run(section=args.section, debug=args.debug)
