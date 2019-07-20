
install-services:
	@printf "Installing sirius-bbb-ioc-ps service...\n"
	cp -rf sirius-bbb-ioc-ps.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-01.service /etc/systemd/system/
	systemctl daemon-reload


stop:
	@printf "Stopping sirius-bbb-ioc-ps...\n"
	systemctl stop sirius-bbb-ioc-ps.service
	systemctl stop sirius-ioc-bo-ps-correctors-01.service

start:
	@printf "Starting sirius-bbb-ioc-ps...\n"
	systemctl start sirius-bbb-ioc-ps.service
	systemctl start sirius-ioc-bo-ps-correctors-01.service

uninstall: stop
	@printf "Uninstalling sirius-bbb-ioc-ps...\n"
	systemctl disable sirius-bbb-ioc-ps.service
	rm -rf /etc/systemd/system/sirius-bbb-ioc-ps.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-01.service
	systemctl daemon-reload
	systemctl reset-failed
