#!/usr/local/bin/python-sirius -u
"""BeagleBone Black IOCs Launcher."""
import sys
import os
from li_ps_conv import li_ps_conv as ioc_module


# NOTE: maximum epics array size
os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '100000'


def main():
    """Launch LI PS Conv IOC."""
    args = [arg for arg in sys.argv[1:]]
    ioc_module.run(args)


if __name__ == "__main__":
    main()
