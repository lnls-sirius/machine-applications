#!/usr/bin/env python-sirius -u

import os
import argparse as _argparse
# NOTE: Avoid creation of a large number of threads by numpy.
# This was making numpy operations very slow in our servers.
os.environ['OMP_NUM_THREADS'] = '2'

from si_ap_manaca import run
from siriuspy.meas.manaca.csdev import Const

# image size is (1024 X 1280)
os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '6000000'
os.environ['EPICS_CA_ADDR_LIST'] += ' ' + Const.IP_IOC

parser = _argparse.ArgumentParser(description="Run SI AP Manaca IOC.")
parser.add_argument(
    '-d', '--debug', action='store_true', default=False,
    help="Starts IOC in Debug Mode. (False)"
    )

args = parser.parse_args()
run(debug=args.debug)
