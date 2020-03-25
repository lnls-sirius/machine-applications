#!/usr/local/bin/python-sirius -u

import argparse as _argparse
from as_ap_sofb import run

parser = _argparse.ArgumentParser(description="Run SI SOFB IOC.")
parser.add_argument('-d', '--debug', action='store_true', default=False,
                    help="Starts IOC in Debug Mode.")
args = parser.parse_args()
run(acc='SI', debug=args.debug)
