#!/usr/bin/env bash

/usr/local/bin/sirius-ioc-as-ps.py LA-RaCtrl:CO-DCLinkCtrl &> /iocs-log/sirius-ioc-as-ps-dclink-tbts &
/usr/local/bin/sirius-ioc-as-ps.py IA-01RaCtrl:CO-DCLinkCtrl &> /iocs-log/sirius-ioc-as-ps-dclink-ia01 &
/usr/local/bin/sirius-ioc-as-ps.py IA-02RaCtrl:CO-DCLinkCtrl &> /iocs-log/sirius-ioc-as-ps-dclink-ia02 &
/usr/local/bin/sirius-ioc-as-ps.py IA-03RaCtrl:CO-DCLinkCtrl &> /iocs-log/sirius-ioc-as-ps-dclink-ia03 &
/usr/local/bin/sirius-ioc-as-ps.py IA-04RaCtrl:CO-DCLinkCtrl &> /iocs-log/sirius-ioc-as-ps-dclink-ia04 &
/usr/local/bin/sirius-ioc-as-ps.py IA-05RaCtrl:CO-DCLinkCtrl &> /iocs-log/sirius-ioc-as-ps-dclink-ia05 &
/usr/local/bin/sirius-ioc-as-ps.py IA-06RaCtrl:CO-DCLinkCtrl &> /iocs-log/sirius-ioc-as-ps-dclink-ia06 &
/usr/local/bin/sirius-ioc-as-ps.py IA-07RaCtrl:CO-DCLinkCtrl &> /iocs-log/sirius-ioc-as-ps-dclink-ia07 &
/usr/local/bin/sirius-ioc-as-ps.py IA-08RaCtrl:CO-DCLinkCtrl &> /iocs-log/sirius-ioc-as-ps-dclink-ia08 &
/usr/local/bin/sirius-ioc-as-ps.py IA-09RaCtrl:CO-DCLinkCtrl &> /iocs-log/sirius-ioc-as-ps-dclink-ia09 &
/usr/local/bin/sirius-ioc-as-ps.py IA-10RaCtrl:CO-DCLinkCtrl &> /iocs-log/sirius-ioc-as-ps-dclink-ia10 &
/usr/local/bin/sirius-ioc-as-ps.py IA-11RaCtrl:CO-DCLinkCtrl &> /iocs-log/sirius-ioc-as-ps-dclink-ia11 &
/usr/local/bin/sirius-ioc-as-ps.py IA-12RaCtrl:CO-DCLinkCtrl &> /iocs-log/sirius-ioc-as-ps-dclink-ia12 &
/usr/local/bin/sirius-ioc-as-ps.py IA-13RaCtrl:CO-DCLinkCtrl &> /iocs-log/sirius-ioc-as-ps-dclink-ia13 &
/usr/local/bin/sirius-ioc-as-ps.py IA-14RaCtrl:CO-DCLinkCtrl &> /iocs-log/sirius-ioc-as-ps-dclink-ia14 &
/usr/local/bin/sirius-ioc-as-ps.py IA-15RaCtrl:CO-DCLinkCtrl &> /iocs-log/sirius-ioc-as-ps-dclink-ia15 &
/usr/local/bin/sirius-ioc-as-ps.py IA-16RaCtrl:CO-DCLinkCtrl &> /iocs-log/sirius-ioc-as-ps-dclink-ia16 &
/usr/local/bin/sirius-ioc-as-ps.py IA-17RaCtrl:CO-DCLinkCtrl &> /iocs-log/sirius-ioc-as-ps-dclink-ia17 &
/usr/local/bin/sirius-ioc-as-ps.py IA-18RaCtrl:CO-DCLinkCtrl &> /iocs-log/sirius-ioc-as-ps-dclink-ia18 &
/usr/local/bin/sirius-ioc-as-ps.py IA-19RaCtrl:CO-DCLinkCtrl &> /iocs-log/sirius-ioc-as-ps-dclink-ia19 &
/usr/local/bin/sirius-ioc-as-ps.py IA-20RaCtrl:CO-DCLinkCtrl &> /iocs-log/sirius-ioc-as-ps-dclink-ia20 &


# keep entry point running
sleep infinity
