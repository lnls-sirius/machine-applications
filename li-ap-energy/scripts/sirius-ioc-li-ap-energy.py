#!/usr/local/bin/python-sirius -u

import argparse as _argparse
from li_ap_energy import run

parser = _argparse.ArgumentParser(description="Run LI Energy IOC.")
parser.add_argument(
    '-d', '--debug', action='store_true', default=False,
    help="Starts IOC in Debug Mode. (False)"
    )

args = parser.parse_args()
run(debug=args.debug)
