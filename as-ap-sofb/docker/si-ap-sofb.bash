#!/usr/bin/env bash

/usr/local/bin/sirius-ioc-si-ap-sofb.py &> /iocs-log/sirius-ioc-si-ap-sofb &

# keep entry point running
sleep infinity
