#!/usr/bin/env bash


# sirius-ioc-as-ti-trig.service
/usr/local/bin/sirius-ioc-as-ti-control.py -s as >& /iocs-log/sirius-ioc-as-ti-trig &

# sirius-ioc-li-ti-trig.service
/usr/local/bin/sirius-ioc-as-ti-control.py -s li >& /iocs-log/sirius-ioc-li-ti-trig &

# sirius-ioc-tb-ti-trig.service
/usr/local/bin/sirius-ioc-as-ti-control.py -s tb >& /iocs-log/sirius-ioc-tb-ti-trig &

# sirius-ioc-bo-ti-trig.service
/usr/local/bin/sirius-ioc-as-ti-control.py -s bo >& /iocs-log/sirius-ioc-bo-ti-trig &

# sirius-ioc-ts-ti-trig.service
/usr/local/bin/sirius-ioc-as-ti-control.py -s ts >& /iocs-log/sirius-ioc-ts-ti-trig &

# sirius-ioc-si-ti-trig.service
/usr/local/bin/sirius-ioc-as-ti-control.py -s si >& /iocs-log/sirius-ioc-si-ti-trig &

# sirius-ioc-bo-ti-trig-bpms.service
/usr/local/bin/sirius-ioc-as-ti-control.py -s bo-bpms >& /iocs-log/sirius-ioc-bo-ti-trig-bpms &

# sirius-ioc-bo-ti-trig-corrs.service
/usr/local/bin/sirius-ioc-as-ti-control.py -s bo-corrs >& /iocs-log/sirius-ioc-bo-ti-trig-corrs &

# sirius-ioc-si-ti-trig-bpms.service
/usr/local/bin/sirius-ioc-as-ti-control.py -s si-bpms >& /iocs-log/sirius-ioc-si-ti-trig-bpms &

# sirius-ioc-si-ti-trig-corrs.service
/usr/local/bin/sirius-ioc-as-ti-control.py -s si-corrs >& /iocs-log/sirius-ioc-si-ti-trig-corrs &

# sirius-ioc-si-ti-trig-qtrims.service
/usr/local/bin/sirius-ioc-as-ti-control.py -s si-qtrims >& /iocs-log/sirius-ioc-si-ti-trig-qtrims &

# sirius-ioc-si-ti-trig-skews.service
/usr/local/bin/sirius-ioc-as-ti-control.py -s si-skews >& /iocs-log/sirius-ioc-si-ti-trig-skews &


# keep entry point running
sleep infinity
