#!/usr/bin/env python-sirius -u

import os
import argparse as _argparse
# NOTE: Avoid creation of a large number of threads by numpy.
# This was making numpy operations very slow in our servers.
os.environ['OMP_NUM_THREADS'] = '2'

from as_ap_sofb import run


if __name__ == '__main__':
    parser = _argparse.ArgumentParser(description="Run BO SOFB IOC.")
    parser.add_argument(
        '-d', '--debug', action='store_true', default=False,
        help="Starts IOC in Debug Mode.")
    args = parser.parse_args()
    run(acc='BO', debug=args.debug)
