#!/usr/local/bin/python-sirius -u

import argparse as _argparse
from as_ap_sofb import as_ap_orbit

parser = _argparse.ArgumentParser(description="Run TB Orbit IOC.")
parser.add_argument('-d', '--debug', action='store_true', default=False,
                    help="Starts IOC in Debug Mode.")
args = parser.parse_args()
as_ap_orbit.run(acc='TB', debug=args.debug)
