#!/usr/bin/env python-sirius

import os
import argparse as _argparse
from cax_ap_cam import run


# Linac image is very large! (2448 X 2050)
os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '21000000'

parser = _argparse.ArgumentParser(description="Run Carcará X Image Processing IOC.")
parser.add_argument(
    '-d', '--debug', action='store_true', default=False,
    help="Starts IOC in Debug Mode. (False)")

args = parser.parse_args()
run(debug=args.debug)
