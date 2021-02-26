#!/usr/bin/env bash


# li-ap-energy
/usr/local/bin/sirius-ioc-li-ap-energy.py &> /iocs-log/sirius-ioc-li-ap-energy &

# as-ap-currinfo
/usr/local/bin/sirius-ioc-li-ap-currinfo.py &> /iocs-log/sirius-ioc-li-ap-currinfo &
# /usr/local/bin/sirius-ioc-tb-ap-currinfo.py &> /iocs-log/sirius-ioc-tb-ap-currinfo &
/usr/local/bin/sirius-ioc-bo-ap-currinfo.py &> /iocs-log/sirius-ioc-bo-ap-currinfo &
/usr/local/bin/sirius-ioc-ts-ap-currinfo.py &> /iocs-log/sirius-ioc-ts-ap-currinfo &
/usr/local/bin/sirius-ioc-si-ap-currinfo.py &> /iocs-log/sirius-ioc-si-ap-currinfo &
/usr/local/bin/sirius-ioc-si-ap-currinfo-lifetime.py &> /iocs-log/sirius-ioc-si-ap-currinfo-lifetime &


# keep entry point running
sleep infinity
