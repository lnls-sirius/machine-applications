
install:
	@printf "Installing sirius-ioc-as-pu-diag service...\n"
	cp -rf sirius-ioc-as-pu-diag.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs-log
	systemctl daemon-reload

stop:
	@printf "Stopping  sirius-ioc-as-pu-diag...\n"
	systemctl stop sirius-ioc-as-pu-diag.service

start:
	@printf "Starting  sirius-ioc-as-pu-diag...\n"
	systemctl start sirius-ioc-as-pu-diag.service

uninstall: stop
	@printf "Uninstalling  sirius-ioc-as-pu-diag...\n"
	systemctl disable sirius-ioc-as-pu-diag.service
	rm -rf /etc/systemd/system/sirius-ioc-as-pu-diag.service
	systemctl daemon-reload
	systemctl reset-failed


install-services: install

uninstall-services: uninstall
