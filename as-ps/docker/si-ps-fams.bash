#!/usr/bin/env bash

# sirius-ioc-si-ps-dipoles.service
/usr/local/bin/sirius-ioc-as-ps.py PA-RaPSD04:CO-PSCtrl-SI &> /iocs-log/sirius-ioc-si-ps-dipoles &

# sirius-ioc-si-ps-quadrupoles-qd1.service
/usr/local/bin/sirius-ioc-as-ps.py PA-RaPSA02:CO-PSCtrl-SI2 &> /iocs-log/sirius-ioc-si-ps-quadrupoles-qd1 &

# sirius-ioc-si-ps-quadrupoles-qd2.service
/usr/local/bin/sirius-ioc-as-ps.py PA-RaPSA05:CO-PSCtrl-SI1 &> /iocs-log/sirius-ioc-si-ps-quadrupoles-qd2 &

# sirius-ioc-si-ps-quadrupoles-qf.service
/usr/local/bin/sirius-ioc-as-ps.py PA-RaPSA02:CO-PSCtrl-SI1 &> /iocs-log/sirius-ioc-si-ps-quadrupoles-qf &

# sirius-ioc-si-ps-quadrupoles-q.service
/usr/local/bin/sirius-ioc-as-ps.py PA-RaPSA05:CO-PSCtrl-SI2 &> /iocs-log/sirius-ioc-si-ps-quadrupoles-q &

# sirius-ioc-si-ps-sextupoles-sda12b2.service
/usr/local/bin/sirius-ioc-as-ps.py PA-RaPSB06:CO-PSCtrl-SI1 &> /iocs-log/sirius-ioc-si-ps-sda12b2  &

# sirius-ioc-si-ps-sextupoles-sfa0p0-sda0p0.service
/usr/local/bin/sirius-ioc-as-ps.py PA-RaPSB02:CO-PSCtrl-SI2 &> /iocs-log/sirius-ioc-si-ps-sfa0p0-sda0p0  &

# sirius-ioc-si-ps-sextupoles-sfa12-sda3p1.service
/usr/local/bin/sirius-ioc-as-ps.py PA-RaPSB06:CO-PSCtrl-SI2 &> /iocs-log/sirius-ioc-si-ps-sfa12-sda3p1  &

# sirius-ioc-si-ps-sextupoles-sfb0-sdb01.service
/usr/local/bin/sirius-ioc-as-ps.py PA-RaPSB02:CO-PSCtrl-SI1 &> /iocs-log/sirius-ioc-si-ps-sfb0-sdb01  &

# sirius-ioc-si-ps-sextupoles-sfb12-sdb3.service
/usr/local/bin/sirius-ioc-as-ps.py PA-RaPSB09:CO-PSCtrl-SI1 &> /iocs-log/sirius-ioc-si-ps-sfb12-sdb3  &

# sirius-ioc-si-ps-sextupoles-sfp12-sdp23.service
/usr/local/bin/sirius-ioc-as-ps.py PA-RaPSB09:CO-PSCtrl-SI2 &> /iocs-log/sirius-ioc-si-ps-sfp12-sdp23  &

# Diag
/usr/local/bin/sirius-ioc-as-ps-diag.py SI Fam ".*" &> /iocs-log/sirius-ioc-si-ps-diag-fam  &


# keep entry point running
sleep infinity
