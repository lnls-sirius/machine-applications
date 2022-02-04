#!/usr/bin/env python-sirius
"""Script for the AS PS Diagnostics IOC."""

import argparse
from as_ps_diag import as_ps_diag


parser = argparse.ArgumentParser()
parser.add_argument(
    'section',
    help='Regexp for the accelerator (LI, TB, BO, TS, SI).')
parser.add_argument(
    'sub_section',
    help='Regexp for the the sub_section (Fam, 01, 01U, ...).')
parser.add_argument(
    'device',
    help='Regexp for the device (CV, CH, QD1, SF, B1B1-1, ...).')


if __name__ == '__main__':
    args = parser.parse_args()
    as_ps_diag.run(args.section, args.sub_section, args.device, False)
