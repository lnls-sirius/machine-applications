#!/usr/local/bin/python-sirius -u
"""BeagleBone Black IOCs Launcher."""
import sys
import os
import socket
from as_ps import as_ps as ioc_module
from siriuspy.search import PSSearch


def print_help():
    """Print help."""
    name = os.path.basename(sys.argv[0])
    print('NAME')
    print('       {} - start beaglebone black IOC.'.format(name))
    print()
    print('SYNOPSIS')
    print('       {} [BBBNAME] []...'.format(name))
    print()
    print('DESCRIPTION')
    print('       Start execution of BeagleBone Black IOC.')
    print()
    print('       <no arguments>')
    print('               list all beaglebone black names and power supplies.')
    print()
    print('       --help')
    print('               print this help.')
    print()
    print('       --simul')
    print('               create simulated PRU and SerialComm objects, not '
          'real ones.')
    print('       --hostname')
    print('               take beaglebone name from hostname')
    print()


def main():
    """Launch BBB IOC."""
    bbb_dict = PSSearch.get_bbbname_dict()
    bbbnames = sorted(bbb_dict.keys())
    if len(sys.argv) == 1:
        print_help()
        print('List of beaglebone black names:')
        print()
        for i in range(len(bbbnames)):
            bbbname = bbbnames[i]
            print('{:<20s} '.format(bbbname), end='')
            bsmps = bbb_dict[bbbname]
            psnames = [bsmp[0] for bsmp in bsmps]
            for psname in psnames:
                print('{:<16s} '.format(psname), end='')
            print()
    else:
        args = [arg for arg in sys.argv[1:]]
        simulate = False
        if '--simul' in args:
            simulate = True
            args.remove('--simul')
        if '--help' in args:
            args.remove('--help')
            print_help()
        if '--hostname' in args:
            hostname = socket.gethostname()
            bbbname = hostname.replace('--', ':')
            args = [hostname, ]
        if args:
            ioc_module.run(args, simulate=simulate)


if __name__ == "__main__":
    main()
