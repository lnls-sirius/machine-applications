#!/usr/bin/env -S python-sirius -u

import argparse as _argparse
from as_ap_sofb import run


if __name__ == '__main__':
    parser = _argparse.ArgumentParser(description="Run TB SOFB IOC.")
    parser.add_argument(
        '-d', '--debug', action='store_true', default=False,
        help="Starts IOC in Debug Mode.")
    args = parser.parse_args()
    run(acc='TB', debug=args.debug)
