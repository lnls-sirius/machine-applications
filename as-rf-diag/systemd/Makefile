
install:
	@printf "Installing sirius-ioc-as-rf-diag service...\n"
	cp -rf sirius-ioc-as-rf-diag.service /etc/systemd/system/
	mkdir -p /home/sirius/iocs-log
	systemctl daemon-reload

stop:
	@printf "Stopping  sirius-ioc-as-rf-diag...\n"
	systemctl stop sirius-ioc-as-rf-diag.service

start:
	@printf "Starting  sirius-ioc-as-rf-diag...\n"
	systemctl start sirius-ioc-as-rf-diag.service

uninstall: stop
	@printf "Uninstalling  sirius-ioc-as-rf-diag...\n"
	systemctl disable sirius-ioc-as-rf-diag.service
	rm -rf /etc/systemd/system/sirius-ioc-as-rf-diag.service
	systemctl daemon-reload
	systemctl reset-failed


install-services: install

uninstall-services: uninstall
