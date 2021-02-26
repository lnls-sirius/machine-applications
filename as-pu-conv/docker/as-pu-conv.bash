#!/usr/bin/env bash

# sirius-ioc-as-pu-conv.service
/usr/local/bin/sirius-ioc-as-pu-conv.py \
TB-04:PU-InjSept \
BO-01D:PU-InjKckr \
BO-48D:PU-EjeKckr \
TS-01:PU-EjeSeptF \
TS-01:PU-EjeSeptG \
TS-04:PU-InjSeptG-1 \
TS-04:PU-InjSeptG-2 \
TS-04:PU-InjSeptF \
SI-01SA:PU-InjDpKckr \
SI-01SA:PU-InjNLKckr \
SI-01SA:PU-PingH \
SI-19C4:PU-PingV &> /iocs-log/sirius-ioc-as-pu-conv &

# sirius-ioc-si-id-conv.service
/usr/local/bin/sirius-ioc-si-id-conv.py \
SI-06SB:ID-APU22 \
SI-07SP:ID-APU22 \
SI-08SB:ID-APU22 \
SI-09SA:ID-APU22 \
SI-11SP:ID-APU58 &> /iocs-log/sirius-ioc-si-id-conv &


# keep entry point running
sleep infinity
