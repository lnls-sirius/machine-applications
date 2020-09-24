
install:
	@printf "Installing sirius-ioc-li-ap-diag service...\n"
	cp -rf sirius-ioc-li-ap-diag.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs-log
	systemctl daemon-reload

stop:
	@printf "Stopping  sirius-ioc-li-ap-diag...\n"
	systemctl stop sirius-ioc-li-ap-diag.service

start:
	@printf "Starting  sirius-ioc-li-ap-diag...\n"
	systemctl start sirius-ioc-li-ap-diag.service

uninstall: stop
	@printf "Uninstalling  sirius-ioc-li-ap-diag...\n"
	systemctl disable sirius-ioc-li-ap-diag.service
	rm -rf /etc/systemd/system/sirius-ioc-li-ap-diag.service
	systemctl daemon-reload
	systemctl reset-failed


install-services: install

uninstall-services: uninstall
