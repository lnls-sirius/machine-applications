#!/usr/bin/env bash


# BO opticscorr
/usr/local/bin/sirius-ioc-bo-ap-tunecorr.py &> /iocs-log/sirius-ioc-bo-ap-tunecorr &
/usr/local/bin/sirius-ioc-bo-ap-chromcorr.py &> /iocs-log/sirius-ioc-bo-ap-chromcorr &

# SI opticscorr
/usr/local/bin/sirius-ioc-si-ap-tunecorr.py &> /iocs-log/sirius-iocsio-ap-tunecorr &
/usr/local/bin/sirius-ioc-si-ap-chromcorr.py &> /iocs-log/sirius-ioc-si-ap-chromcorr &

# TB and TS posang
/usr/local/bin/sirius-ioc-tb-ap-posang.py &> /iocs-log/sirius-ioc-tb-ap-posang &
/usr/local/bin/sirius-ioc-ts-ap-posang.py &> /iocs-log/sirius-ioc-ts-ap-posang &

# AS machshift
/usr/local/bin/sirius-ioc-as-ap-machshift.py &> /iocs-log/sirius-ioc-as-ap-machshift &


# keep entry point running
sleep infinity
