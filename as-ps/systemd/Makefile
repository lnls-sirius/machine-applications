
install-services:
	@printf "Installing sirius-bbb-ioc-ps service...\n"
	cp -rf sirius-bbb-ioc-ps.service /etc/systemd/system/
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

stop:
	@printf "Stopping sirius-bbb-ioc-ps...\n"
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

start:
	@printf "Starting sirius-bbb-ioc-ps...\n"
	systemctl start sirius-bbb-ioc-ps.service
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

uninstall: stop
	@printf "Uninstalling sirius-bbb-ioc-ps...\n"
	systemctl disable sirius-bbb-ioc-ps.service
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
