#!/usr/bin/env bash

/usr/local/bin/sirius-ioc-tb-ap-sofb.py &> /iocs-log/sirius-ioc-tb-ap-sofb &
/usr/local/bin/sirius-ioc-bo-ap-sofb.py &> /iocs-log/sirius-ioc-bo-ap-sofb &
/usr/local/bin/sirius-ioc-ts-ap-sofb.py &> /iocs-log/sirius-ioc-ts-ap-sofb &

# keep entry point running
sleep infinity
