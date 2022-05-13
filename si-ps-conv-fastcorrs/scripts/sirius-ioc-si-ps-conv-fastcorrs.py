#!/usr/bin/env python-sirius
"""SI PS Fast Corrector Current-Strength Converter IOC Launcher."""
import sys
import os
from si_ps_conv_fastcorrs import si_ps_conv_fastcorrs as ioc_module


# NOTE: maximum epics array size
os.environ['EPICS_CA_MAX_ARRAY_BYTES'] = '100000'


def main():
    """Launch SI PS Fast Corrector Conv IOC."""
    args = [arg for arg in sys.argv[1:]]
    ioc_module.run(args)


if __name__ == "__main__":
    main()
