

preparation:
	@printf "Creating ioc-logs directory...\n"
	mkdir -p /home/sirius/iocs-log

install-services-ioc-li-ps-conv: preparation
	@printf "Installing sirius-ioc-ps services...\n"
	cp -rf sirius-ioc-li-ps-conv.service /etc/systemd/system/
	systemctl daemon-reload

install-services: install-services-ioc-li-ps-conv

stop:
	@printf "Stopping sirius-ioc-li-ps-conv services...\n"
	systemctl stop sirius-ioc-li-ps-conv.service


start-ioc-li-ps-conv: preparation
	@printf "Starting sirius-ioc-li-ps-conv services...\n"
	systemctl start sirius-ioc-li-ps-conv.service

start: start-ioc-li-ps-conv

disable:
	@printf "Disabling sirius-ioc-li-ps-conv services...\n"
	systemctl disable sirius-ioc-li-ps-conv.service

uninstall: stop disable
	@printf "Uninstalling sirius-ioc-li-ps-conv services...\n"
	rm -rf /etc/systemd/system/sirius-ioc-li-ps-conv.service
	systemctl daemon-reload
	systemctl reset-failed

uninstall-services: uninstall
