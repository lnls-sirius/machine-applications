#!/usr/bin/env python-sirius
"""AS PU Current-Strength Converter IOC Launcher."""

import os
import sys

from as_pu_conv import as_pu_conv as ioc_module

# NOTE: maximum epics array size
os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '100000'


def main():
    """Launch PU Conv IOC."""
    args = [arg for arg in sys.argv[1:]]
    ioc_module.run(args)


if __name__ == "__main__":
    main()
