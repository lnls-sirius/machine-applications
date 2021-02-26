#!/usr/bin/env bash

# Correctors
/usr/local/bin/sirius-ioc-as-ps.py IA-01RaCtrl:CO-PSCtrl-BO &> /iocs-log/sirius-ioc-bo-ps-correctors-ia01 &
/usr/local/bin/sirius-ioc-as-ps.py IA-02RaCtrl:CO-PSCtrl-BO &> /iocs-log/sirius-ioc-bo-ps-correctors-ia02 &
/usr/local/bin/sirius-ioc-as-ps.py IA-04RaCtrl:CO-PSCtrl-BO &> /iocs-log/sirius-ioc-bo-ps-correctors-ia04 &
/usr/local/bin/sirius-ioc-as-ps.py IA-05RaCtrl:CO-PSCtrl-BO &> /iocs-log/sirius-ioc-bo-ps-correctors-ia05 &
/usr/local/bin/sirius-ioc-as-ps.py IA-07RaCtrl:CO-PSCtrl-BO &> /iocs-log/sirius-ioc-bo-ps-correctors-ia07 &
/usr/local/bin/sirius-ioc-as-ps.py IA-08RaCtrl:CO-PSCtrl-BO &> /iocs-log/sirius-ioc-bo-ps-correctors-ia08 &
/usr/local/bin/sirius-ioc-as-ps.py IA-10RaCtrl:CO-PSCtrl-BO &> /iocs-log/sirius-ioc-bo-ps-correctors-ia10 &
/usr/local/bin/sirius-ioc-as-ps.py IA-11RaCtrl:CO-PSCtrl-BO &> /iocs-log/sirius-ioc-bo-ps-correctors-ia11 &
/usr/local/bin/sirius-ioc-as-ps.py IA-13RaCtrl:CO-PSCtrl-BO &> /iocs-log/sirius-ioc-bo-ps-correctors-ia13 &
/usr/local/bin/sirius-ioc-as-ps.py IA-14RaCtrl:CO-PSCtrl-BO &> /iocs-log/sirius-ioc-bo-ps-correctors-ia14 &
/usr/local/bin/sirius-ioc-as-ps.py IA-16RaCtrl:CO-PSCtrl-BO &> /iocs-log/sirius-ioc-bo-ps-correctors-ia16 &
/usr/local/bin/sirius-ioc-as-ps.py IA-17RaCtrl:CO-PSCtrl-BO &> /iocs-log/sirius-ioc-bo-ps-correctors-ia17 &
/usr/local/bin/sirius-ioc-as-ps.py IA-20RaCtrl:CO-PSCtrl-BO &> /iocs-log/sirius-ioc-bo-ps-correctors-ia20 &

# Diagnostics
/usr/local/bin/sirius-ioc-as-ps-diag.py BO ".*" "(CH|CV|QS)" &> /iocs-log/sirius-ioc-bo-ps-correctors-diag &


# keep entry point running
sleep infinity
