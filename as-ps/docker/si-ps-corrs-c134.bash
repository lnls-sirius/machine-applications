#!/usr/bin/env bash

# NOTE: Temporary while IOCs still run in lnlsfac-srv1
#
# /usr/local/bin/sirius-ioc-as-ps.py IA-01RaCtrl:CO-PSCtrl-SI4 &> /iocs-log/sirius-ioc-si-ps-correctors-c134-ia01 &
# /usr/local/bin/sirius-ioc-as-ps.py IA-02RaCtrl:CO-PSCtrl-SI4 &> /iocs-log/sirius-ioc-si-ps-correctors-c134-ia02 &
# /usr/local/bin/sirius-ioc-as-ps.py IA-03RaCtrl:CO-PSCtrl-SI4 &> /iocs-log/sirius-ioc-si-ps-correctors-c134-ia03 &
# /usr/local/bin/sirius-ioc-as-ps.py IA-04RaCtrl:CO-PSCtrl-SI4 &> /iocs-log/sirius-ioc-si-ps-correctors-c134-ia04 &
# /usr/local/bin/sirius-ioc-as-ps.py IA-05RaCtrl:CO-PSCtrl-SI4 &> /iocs-log/sirius-ioc-si-ps-correctors-c134-ia05 &
# /usr/local/bin/sirius-ioc-as-ps.py IA-06RaCtrl:CO-PSCtrl-SI4 &> /iocs-log/sirius-ioc-si-ps-correctors-c134-ia06 &
# /usr/local/bin/sirius-ioc-as-ps.py IA-07RaCtrl:CO-PSCtrl-SI4 &> /iocs-log/sirius-ioc-si-ps-correctors-c134-ia07 &
# /usr/local/bin/sirius-ioc-as-ps.py IA-08RaCtrl:CO-PSCtrl-SI4 &> /iocs-log/sirius-ioc-si-ps-correctors-c134-ia08 &
# /usr/local/bin/sirius-ioc-as-ps.py IA-09RaCtrl:CO-PSCtrl-SI4 &> /iocs-log/sirius-ioc-si-ps-correctors-c134-ia09 &
# /usr/local/bin/sirius-ioc-as-ps.py IA-10RaCtrl:CO-PSCtrl-SI4 &> /iocs-log/sirius-ioc-si-ps-correctors-c134-ia10 &
# /usr/local/bin/sirius-ioc-as-ps.py IA-11RaCtrl:CO-PSCtrl-SI4 &> /iocs-log/sirius-ioc-si-ps-correctors-c134-ia11 &
# /usr/local/bin/sirius-ioc-as-ps.py IA-12RaCtrl:CO-PSCtrl-SI4 &> /iocs-log/sirius-ioc-si-ps-correctors-c134-ia12 &
# /usr/local/bin/sirius-ioc-as-ps.py IA-13RaCtrl:CO-PSCtrl-SI4 &> /iocs-log/sirius-ioc-si-ps-correctors-c134-ia13 &
# /usr/local/bin/sirius-ioc-as-ps.py IA-14RaCtrl:CO-PSCtrl-SI4 &> /iocs-log/sirius-ioc-si-ps-correctors-c134-ia14 &
# /usr/local/bin/sirius-ioc-as-ps.py IA-15RaCtrl:CO-PSCtrl-SI4 &> /iocs-log/sirius-ioc-si-ps-correctors-c134-ia15 &
# /usr/local/bin/sirius-ioc-as-ps.py IA-16RaCtrl:CO-PSCtrl-SI4 &> /iocs-log/sirius-ioc-si-ps-correctors-c134-ia16 &
# /usr/local/bin/sirius-ioc-as-ps.py IA-17RaCtrl:CO-PSCtrl-SI4 &> /iocs-log/sirius-ioc-si-ps-correctors-c134-ia17 &
# /usr/local/bin/sirius-ioc-as-ps.py IA-18RaCtrl:CO-PSCtrl-SI4 &> /iocs-log/sirius-ioc-si-ps-correctors-c134-ia18 &
# /usr/local/bin/sirius-ioc-as-ps.py IA-19RaCtrl:CO-PSCtrl-SI4 &> /iocs-log/sirius-ioc-si-ps-correctors-c134-ia19 &
# /usr/local/bin/sirius-ioc-as-ps.py IA-20RaCtrl:CO-PSCtrl-SI4 &> /iocs-log/sirius-ioc-si-ps-correctors-c134-ia20 &

# Diag
/usr/local/bin/sirius-ioc-as-ps-diag.py SI "[0-2][0-9]-C(1|3|4)" "C(H|V).*" &> /iocs-log/sirius-ioc-si-ps-diag-corrs-c134  &


# keep entry point running
sleep infinity
