#!/usr/bin/env bash

# Dipole
/usr/local/bin/sirius-ioc-as-ps.py LA-RaPS02:CO-PSCtrl-TS1 &> /iocs-log/sirius-ioc-ts-ps-dipoles &
sleep 2 # before starting other IOCs

# Quadrupoles
/usr/local/bin/sirius-ioc-as-ps.py LA-RaPS02:CO-PSCtrl-TS2 &> /iocs-log/sirius-ioc-ts-ps-quadrupoles-12 &
/usr/local/bin/sirius-ioc-as-ps.py LA-RaPS04:CO-PSCtrl-TS &> /iocs-log/sirius-ioc-ts-ps-quadrupoles-34 &

# Correctors
/usr/local/bin/sirius-ioc-as-ps.py LA-RaCtrl:CO-PSCtrl-TS &> /iocs-log/env-sirius-ioc-ts-ps-correctors &

# Diagnostics
/usr/local/bin/sirius-ioc-as-ps-diag.py TS ".*" ".*" &> /iocs-log/sirius-ioc-ts-ps-diag &


# keep entry point running
sleep infinity
