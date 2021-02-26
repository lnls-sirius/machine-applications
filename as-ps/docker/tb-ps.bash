#!/usr/bin/env bash

# Dipole
/usr/local/bin/sirius-ioc-as-ps.py LA-RaPS02:CO-PSCtrl-TB &> /iocs-log/sirius-ioc-tb-ps-dipoles &
sleep 2 # before starting other IOCs

# Quadrupoles
/usr/local/bin/sirius-ioc-as-ps.py LA-RaCtrl:CO-PSCtrl-TB1 &> /iocs-log/sirius-ioc-tb-ps-quadrupoles &

# Correctors
/usr/local/bin/sirius-ioc-as-ps.py LA-RaCtrl:CO-PSCtrl-TB2 &> /iocs-log/sirius-ioc-tb-ps-correctors &

# Diagnostics
/usr/local/bin/sirius-ioc-as-ps-diag.py TB ".*" ".*" &> /iocs-log/sirius-ioc-tb-ps-diag &


# keep entry point running
sleep infinity
