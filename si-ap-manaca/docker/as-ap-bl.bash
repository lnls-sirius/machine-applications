#!/usr/bin/env bash

# manaca
/usr/local/bin/sirius-ioc-si-ap-manaca.py &> /iocs-log/sirius-ioc-si-ap-manaca &

# keep entry point running
sleep infinity
