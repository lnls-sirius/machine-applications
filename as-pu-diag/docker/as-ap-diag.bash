#!/usr/bin/env bash

# sirius-ioc-as-pu-diag.service
/usr/local/bin/sirius-ioc-as-pu-diag.py &> /iocs-log/sirius-ioc-as-pu-diag &

# sirius-ioc-as-rf-diag.service
/usr/local/bin/sirius-ioc-as-rf-diag.py &> /iocs-log/sirius-ioc-as-rf-diag &

# sirius-ioc-li-ap-diag.service
/usr/local/bin/sirius-ioc-li-ap-diag.py &> /iocs-log/sirius-ioc-li-ap-diag &


# keep entry point running
sleep infinity
