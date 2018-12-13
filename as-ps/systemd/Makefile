
install-services:
	@printf "Installing sirius-bbb-ioc-ps service...\n"
	cp -rf sirius-bbb-ioc-ps.service /etc/systemd/system/
	mkdir -p /root/sirius-iocs/pvs
	systemctl daemon-reload


stop:
	@printf "Stopping sirius-bbb-ioc-ps...\n"
	systemctl stop sirius-bbb-ioc-ps.service

start:
	@printf "Starting sirius-bbb-ioc-ps...\n"
	systemctl start sirius-bbb-ioc-ps.service

uninstall: stop
	@printf "Uninstalling sirius-bbb-ioc-ps...\n"
	systemctl disable sirius-bbb-ioc-ps.service
	rm -rf /etc/systemd/system/sirius-bbb-ioc-ps.service
	systemctl daemon-reload
	systemctl reset-failed
