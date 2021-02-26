#!/usr/bin/env bash

# Dipole DCLink
/usr/local/bin/sirius-ioc-as-ps.py PA-RaPSE05:CO-PSCtrl-BO2 &> /iocs-log/sirius-ioc-bo-ps-dipole-1-dclink &
/usr/local/bin/sirius-ioc-as-ps.py PA-RaPSF05:CO-PSCtrl-BO2 &> /iocs-log/sirius-ioc-bo-ps-dipole-2-dclink &

# Dipoles
/usr/local/bin/sirius-ioc-as-ps.py PA-RaPSE05:CO-PSCtrl-BO1 &> /iocs-log/sirius-ioc-bo-ps-dipole-1 &
/usr/local/bin/sirius-ioc-as-ps.py PA-RaPSF05:CO-PSCtrl-BO1 &> /iocs-log/sirius-ioc-bo-ps-dipole-2 &
sleep 2 # before starting other IOCs

# Quadrupoles
/usr/local/bin/sirius-ioc-as-ps.py PA-RaPSC03:CO-PSCtrl-BO1 &> /iocs-log/sirius-ioc-bo-ps-quadrupole-qf &
/usr/local/bin/sirius-ioc-as-ps.py PA-RaPSC03:CO-PSCtrl-BO4 &> /iocs-log/sirius-ioc-bo-ps-quadrupole-qd &

# Sextupoles
/usr/local/bin/sirius-ioc-as-ps.py PA-RaPSC03:CO-PSCtrl-BO2 &> /iocs-log/sirius-ioc-bo-ps-sextupole-sf &
/usr/local/bin/sirius-ioc-as-ps.py PA-RaPSC03:CO-PSCtrl-BO3 &> /iocs-log/sirius-ioc-bo-ps-sextupole-sd &

# Diagnostics
/usr/local/bin/sirius-ioc-as-ps-diag.py BO ".*" "B-(1|2)" &> /iocs-log/sirius-ioc-bo-ps-dipoles-diag &
/usr/local/bin/sirius-ioc-as-ps-diag.py BO ".*" "Q(F|D)" &> /iocs-log/sirius-ioc-bo-ps-quadrupoles-diag &
/usr/local/bin/sirius-ioc-as-ps-diag.py BO ".*" "S(F|D)" &> /iocs-log/sirius-ioc-bo-ps-sextupoles-diag &


# keep entry point running
sleep infinity
