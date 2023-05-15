#!/usr/bin/env python-sirius

import os
import argparse as _argparse
from bl_ap_imgproc import run

os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '21000000'

BL_NAME = 'CAX'
BL_SECTOR = 'B'
BASLER_NAME = 'BASLER01'
DEVNAME = ':'.join(
    [BL_NAME, BL_SECTOR, BASLER_NAME])

parser = _argparse.ArgumentParser(
    description="Run Carcará X BASLER01 Image Processing IOC.")
parser.add_argument(
    '-d', '--debug', action='store_true', default=False,
    help="Starts IOC in Debug Mode. (False)")
parser.add_argument(
    '-n', '--devname', action='store_true', default=DEVNAME,
    help=f"Device name. ({DEVNAME})")

args = parser.parse_args()
run(devname=args.devname, debug=args.debug)
