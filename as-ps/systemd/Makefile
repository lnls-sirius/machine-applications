
install:
	@printf "Intalling sirius-bbb-ioc-ps service...\n"
	cp -rf sirius-bbb-ioc-ps.service /etc/systemd/system/
	mkdir -p /root/sirius-iocs/pvs
	systemctl daemon-reload


stop:
	@printf "Stopping sirius-bbb-ioc-ps...\n"
	systemctl stop sirius-bbb-ioc-ps

start: 
	@printf "Starting sirius-bbb-ioc-ps---"
	systemctl start sirius-bbb-ioc-ps

uninstall: stop
	@printf "Uninstalling sirius-bbb-ioc-ps---"
	systemctl disable sirius-bbb-ioc-ps
	rm -rf /etc/systemd/system/sirius-bbb-ioc-ps.service
	systemctl daemon-reload
	systemctl reset-failed

