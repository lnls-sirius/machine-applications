

preparation:
	@printf "Creating ioc-logs directory...\n"
	mkdir -p /home/sirius/iocs-log

install-service-bbb:
	@printf "Installing sirius-bbb-ioc-ps service...\n"
	cp -rf sirius-bbb-ioc-ps.service /etc/systemd/system/
	systemctl daemon-reload

install-services-ioc-ps: preparation
	@printf "Installing sirius-ioc-ps services...\n"
	cp -rf sirius-ioc-tb-ps-dipoles.service /etc/systemd/system/
	cp -rf sirius-ioc-tb-ps-quadrupoles.service /etc/systemd/system/
	cp -rf sirius-ioc-tb-ps-correctors.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-dipole-1.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-dipole-2.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-quadrupole-qf.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-quadrupole-qd.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-sextupole-sf.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-sextupole-sd.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-ia01.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-ia02.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-ia04.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-ia05.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-ia07.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-ia08.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-ia10.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-ia11.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-ia13.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-ia14.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-ia16.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-ia17.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-ia20.service /etc/systemd/system/
	cp -rf sirius-ioc-ts-ps-dipoles.service /etc/systemd/system/
	cp -rf sirius-ioc-ts-ps-quadrupoles-12.service /etc/systemd/system/
	cp -rf sirius-ioc-ts-ps-quadrupoles-34.service /etc/systemd/system/
	cp -rf sirius-ioc-ts-ps-correctors.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-tbts.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia01.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia02.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia04.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia05.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia07.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia08.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia10.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia11.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia13.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia14.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia16.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia17.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia20.service /etc/systemd/system/
	systemctl daemon-reload

install-services: install-service-bbb install-services-ioc-ps
stop:
	@printf "Stopping sirius-ioc-ps services...\n"
	systemctl stop sirius-bbb-ioc-ps.service
	systemctl stop sirius-ioc-tb-ps-dipoles.service
	systemctl stop sirius-ioc-tb-ps-quadrupoles.service
	systemctl stop sirius-ioc-tb-ps-correctors.service
	systemctl stop sirius-ioc-bo-ps-dipole-1.service
	systemctl stop sirius-ioc-bo-ps-dipole-2.service
	systemctl stop sirius-ioc-bo-ps-quadrupole-qf.service
	systemctl stop sirius-ioc-bo-ps-quadrupole-qd.service
	systemctl stop sirius-ioc-bo-ps-sextupole-sf.service
	systemctl stop sirius-ioc-bo-ps-sextupole-sd.service
	systemctl stop sirius-ioc-bo-ps-correctors-ia01.service
	systemctl stop sirius-ioc-bo-ps-correctors-ia02.service
	systemctl stop sirius-ioc-bo-ps-correctors-ia04.service
	systemctl stop sirius-ioc-bo-ps-correctors-ia05.service
	systemctl stop sirius-ioc-bo-ps-correctors-ia07.service
	systemctl stop sirius-ioc-bo-ps-correctors-ia08.service
	systemctl stop sirius-ioc-bo-ps-correctors-ia10.service
	systemctl stop sirius-ioc-bo-ps-correctors-ia11.service
	systemctl stop sirius-ioc-bo-ps-correctors-ia13.service
	systemctl stop sirius-ioc-bo-ps-correctors-ia14.service
	systemctl stop sirius-ioc-bo-ps-correctors-ia16.service
	systemctl stop sirius-ioc-bo-ps-correctors-ia17.service
	systemctl stop sirius-ioc-bo-ps-correctors-ia20.service
	systemctl stop sirius-ioc-ts-ps-dipoles.service
	systemctl stop sirius-ioc-ts-ps-quadrupoles-12.service
	systemctl stop sirius-ioc-ts-ps-quadrupoles-34.service
	systemctl stop sirius-ioc-ts-ps-correctors.service
	systemctl stop sirius-ioc-as-ps-dclink-tbts.service
	systemctl stop sirius-ioc-as-ps-dclink-ia01.service
	systemctl stop sirius-ioc-as-ps-dclink-ia02.service
	systemctl stop sirius-ioc-as-ps-dclink-ia04.service
	systemctl stop sirius-ioc-as-ps-dclink-ia05.service
	systemctl stop sirius-ioc-as-ps-dclink-ia07.service
	systemctl stop sirius-ioc-as-ps-dclink-ia08.service
	systemctl stop sirius-ioc-as-ps-dclink-ia10.service
	systemctl stop sirius-ioc-as-ps-dclink-ia11.service
	systemctl stop sirius-ioc-as-ps-dclink-ia13.service
	systemctl stop sirius-ioc-as-ps-dclink-ia14.service
	systemctl stop sirius-ioc-as-ps-dclink-ia16.service
	systemctl stop sirius-ioc-as-ps-dclink-ia17.service
	systemctl stop sirius-ioc-as-ps-dclink-ia20.service

start-bbb:
	@printf "Starting sirius-bbb-ioc-ps service...\n"
	systemctl start sirius-bbb-ioc-ps.service

start-ioc-ps: preparation
	@printf "Starting sirius-ioc-ps services...\n"
	systemctl start sirius-ioc-tb-ps-dipoles.service
	systemctl start sirius-ioc-tb-ps-quadrupoles.service
	systemctl start sirius-ioc-tb-ps-correctors.service
	systemctl start sirius-ioc-bo-ps-dipole-1.service
	systemctl start sirius-ioc-bo-ps-dipole-2.service
	systemctl start sirius-ioc-bo-ps-quadrupole-qf.service
	systemctl start sirius-ioc-bo-ps-quadrupole-qd.service
	systemctl start sirius-ioc-bo-ps-sextupole-sf.service
	systemctl start sirius-ioc-bo-ps-sextupole-sd.service
	systemctl start sirius-ioc-bo-ps-correctors-ia01.service
	systemctl start sirius-ioc-bo-ps-correctors-ia02.service
	systemctl start sirius-ioc-bo-ps-correctors-ia04.service
	systemctl start sirius-ioc-bo-ps-correctors-ia05.service
	systemctl start sirius-ioc-bo-ps-correctors-ia07.service
	systemctl start sirius-ioc-bo-ps-correctors-ia08.service
	systemctl start sirius-ioc-bo-ps-correctors-ia10.service
	systemctl start sirius-ioc-bo-ps-correctors-ia11.service
	systemctl start sirius-ioc-bo-ps-correctors-ia13.service
	systemctl start sirius-ioc-bo-ps-correctors-ia14.service
	systemctl start sirius-ioc-bo-ps-correctors-ia16.service
	systemctl start sirius-ioc-bo-ps-correctors-ia17.service
	systemctl start sirius-ioc-bo-ps-correctors-ia20.service
	systemctl start sirius-ioc-ts-ps-dipoles.service
	systemctl start sirius-ioc-ts-ps-quadrupoles-12.service
	systemctl start sirius-ioc-ts-ps-quadrupoles-34.service
	systemctl start sirius-ioc-ts-ps-correctors.service
	systemctl start sirius-ioc-as-ps-dclink-tbts.service
	systemctl start sirius-ioc-as-ps-dclink-ia01.service
	systemctl start sirius-ioc-as-ps-dclink-ia02.service
	systemctl start sirius-ioc-as-ps-dclink-ia04.service
	systemctl start sirius-ioc-as-ps-dclink-ia05.service
	systemctl start sirius-ioc-as-ps-dclink-ia07.service
	systemctl start sirius-ioc-as-ps-dclink-ia08.service
	systemctl start sirius-ioc-as-ps-dclink-ia10.service
	systemctl start sirius-ioc-as-ps-dclink-ia11.service
	systemctl start sirius-ioc-as-ps-dclink-ia13.service
	systemctl start sirius-ioc-as-ps-dclink-ia14.service
	systemctl start sirius-ioc-as-ps-dclink-ia16.service
	systemctl start sirius-ioc-as-ps-dclink-ia17.service
	systemctl start sirius-ioc-as-ps-dclink-ia20.service



start: start-ioc-ps
disable:
	@printf "Disabling sirius-ioc-ps services...\n"
	systemctl disable sirius-bbb-ioc-ps.service
	systemctl disable sirius-ioc-tb-ps-dipoles.service
	systemctl disable sirius-ioc-tb-ps-quadrupoles.service
	systemctl disable sirius-ioc-tb-ps-correctors.service
	systemctl disable sirius-ioc-bo-ps-dipole-1.service
	systemctl disable sirius-ioc-bo-ps-dipole-2.service
	systemctl disable sirius-ioc-bo-ps-quadrupole-qf.service
	systemctl disable sirius-ioc-bo-ps-quadrupole-qd.service
	systemctl disable sirius-ioc-bo-ps-sextupole-sf.service
	systemctl disable sirius-ioc-bo-ps-sextupole-sd.service
	systemctl disable sirius-ioc-bo-ps-correctors-ia01.service
	systemctl disable sirius-ioc-bo-ps-correctors-ia02.service
	systemctl disable sirius-ioc-bo-ps-correctors-ia04.service
	systemctl disable sirius-ioc-bo-ps-correctors-ia05.service
	systemctl disable sirius-ioc-bo-ps-correctors-ia07.service
	systemctl disable sirius-ioc-bo-ps-correctors-ia08.service
	systemctl disable sirius-ioc-bo-ps-correctors-ia10.service
	systemctl disable sirius-ioc-bo-ps-correctors-ia11.service
	systemctl disable sirius-ioc-bo-ps-correctors-ia13.service
	systemctl disable sirius-ioc-bo-ps-correctors-ia14.service
	systemctl disable sirius-ioc-bo-ps-correctors-ia16.service
	systemctl disable sirius-ioc-bo-ps-correctors-ia17.service
	systemctl disable sirius-ioc-bo-ps-correctors-ia20.service
	systemctl disable sirius-ioc-ts-ps-dipoles.service
	systemctl disable sirius-ioc-ts-ps-quadrupoles-12.service
	systemctl disable sirius-ioc-ts-ps-quadrupoles-34.service
	systemctl disable sirius-ioc-ts-ps-correctors.service
	systemctl disable sirius-ioc-as-ps-dclink-tbts.service
	systemctl disable sirius-ioc-as-ps-dclink-ia01.service
	systemctl disable sirius-ioc-as-ps-dclink-ia02.service
	systemctl disable sirius-ioc-as-ps-dclink-ia04.service
	systemctl disable sirius-ioc-as-ps-dclink-ia05.service
	systemctl disable sirius-ioc-as-ps-dclink-ia07.service
	systemctl disable sirius-ioc-as-ps-dclink-ia08.service
	systemctl disable sirius-ioc-as-ps-dclink-ia10.service
	systemctl disable sirius-ioc-as-ps-dclink-ia11.service
	systemctl disable sirius-ioc-as-ps-dclink-ia13.service
	systemctl disable sirius-ioc-as-ps-dclink-ia14.service
	systemctl disable sirius-ioc-as-ps-dclink-ia16.service
	systemctl disable sirius-ioc-as-ps-dclink-ia17.service
	systemctl disable sirius-ioc-as-ps-dclink-ia20.service

uninstall: stop disable
	@printf "Uninstalling sirius-ioc-ps services...\n"
	rm -rf /etc/systemd/system/sirius-bbb-ioc-ps.service
	rm -rf /etc/systemd/system/sirius-ioc-tb-ps-dipoles.service
	rm -rf /etc/systemd/system/sirius-ioc-tb-ps-quadrupoles.service
	rm -rf /etc/systemd/system/sirius-ioc-tb-ps-correctors.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-dipole-1.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-dipole-2.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-quadrupole-qf.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-quadrupole-qd.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-sextupole-sf.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-sextupole-sd.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-ia01.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-ia02.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-ia04.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-ia05.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-ia07.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-ia08.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-ia10.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-ia11.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-ia13.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-ia14.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-ia16.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-ia17.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-ia20.service
	rm -rf /etc/systemd/system/sirius-ioc-ts-ps-dipoles.service
	rm -rf /etc/systemd/system/sirius-ioc-ts-ps-quadrupoles-12.service
	rm -rf /etc/systemd/system/sirius-ioc-ts-ps-quadrupoles-34.service
	rm -rf /etc/systemd/system/sirius-ioc-ts-ps-correctors.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-tbts.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia01.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia02.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia04.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia05.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia07.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia08.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia10.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia11.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia13.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia14.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia16.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia17.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia20.service
	systemctl daemon-reload
	systemctl reset-failed
