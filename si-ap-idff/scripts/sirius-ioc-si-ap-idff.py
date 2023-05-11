#!/usr/bin/env python-sirius
"""ID feedforward IOC executable."""
import sys
from si_ap_idff import si_ap_idff as ioc_module


def main():
    """Launch IOC."""
    ioc_module.run(sys.argv[1])


if __name__ == "__main__":
    main()
