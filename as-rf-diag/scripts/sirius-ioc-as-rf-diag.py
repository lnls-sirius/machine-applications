#!/usr/bin/env -S python-sirius -u
"""Script for the RF Diagnostics IOC."""

from as_rf_diag import as_rf_diag


if __name__ == '__main__':
    as_rf_diag.run(False)
