

preparation:
	@printf "Creating ioc-logs directory...\n"
	mkdir -p /home/sirius/iocs-log

install-services-ioc-pu: preparation
	@printf "Installing sirius-ioc-ps services...\n"
	cp -rf sirius-ioc-as-pu-conv.service /etc/systemd/system/
	systemctl daemon-reload

install-services: install-services-ioc-pu

stop:
	@printf "Stopping sirius-ioc-pu services...\n"
	systemctl stop sirius-ioc-as-pu-conv.service


start-ioc-pu: preparation
	@printf "Starting sirius-ioc-pu services...\n"
	systemctl start sirius-ioc-as-pu-conv.service

start: start-ioc-pu

disable:
	@printf "Disabling sirius-ioc-pu services...\n"
	systemctl disable sirius-ioc-as-pu-conv.service

uninstall: stop disable
	@printf "Uninstalling sirius-ioc-pu services...\n"
	rm -rf /etc/systemd/system/sirius-ioc-as-pu-conv.service
	systemctl daemon-reload
	systemctl reset-failed

uninstall-services: uninstall
