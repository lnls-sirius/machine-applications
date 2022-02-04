#!/usr/bin/env python-sirius
"""BeagleBone Black IOCs Launcher."""
import sys
import os
from as_ps import as_ps as ioc_module


# NOTE: maximum epics array size
os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '100000'


def print_help():
    """Print help."""
    name = os.path.basename(sys.argv[0])
    print('NAME')
    print('       {} - start IOC for a given beaglebone '
          'power supplies.'.format(name))
    print()
    print('SYNOPSIS')
    print('       {} BBBNAME'.format(name))
    print()
    print('DESCRIPTION')
    print('       Start execution of beaglebone IOC.')
    print()
    print('       --help')
    print('               print this help.')
    print()


def main():
    """Launch PS IOC."""
    if len(sys.argv) == 1:
        print_help()
        return

    # run sets of beaglebone
    args = [arg for arg in sys.argv[1:]]
    if '--help' in args:
        args.remove('--help')
        print_help()
    if args:
        ioc_module.run(args)


if __name__ == "__main__":
    main()
