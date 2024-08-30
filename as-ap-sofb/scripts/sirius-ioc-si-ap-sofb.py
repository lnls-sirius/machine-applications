#!/usr/bin/env python-sirius
"""SI SOFB IOC executable."""

import argparse as _argparse
import os

# NOTE: Avoid creation of a large number of threads by numpy.
# This was making numpy operations very slow in our servers.
os.environ['OMP_NUM_THREADS'] = '2'

from as_ap_sofb import run

if __name__ == '__main__':
    parser = _argparse.ArgumentParser(description="Run SI SOFB IOC.")
    parser.add_argument(
        '-d', '--debug', action='store_true', default=False,
        help="Starts IOC in Debug mode.")
    parser.add_argument(
        '-t', '--tests', action='store_true', default=False,
        help=(
            "Starts IOC in test mode. The automatic loop ignores the "
            "existence of stored beam, the current of the dipoles and the BPM "
            "readings, sending random kicks to the correctors."))
    args = parser.parse_args()
    run(acc='SI', debug=args.debug, tests=args.tests)
