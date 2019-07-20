
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
	cp -rf sirius-ioc-bo-ps-correctors-01.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-02.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-03.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-04.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-05.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-06.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-07.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-08.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-09.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-10.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-11.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-12.service /etc/systemd/system/
	cp -rf sirius-ioc-bo-ps-correctors-13.service /etc/systemd/system/
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
	systemctl stop sirius-ioc-bo-ps-correctors-01.service
	systemctl stop sirius-ioc-bo-ps-correctors-02.service
	systemctl stop sirius-ioc-bo-ps-correctors-03.service
	systemctl stop sirius-ioc-bo-ps-correctors-04.service
	systemctl stop sirius-ioc-bo-ps-correctors-05.service
	systemctl stop sirius-ioc-bo-ps-correctors-06.service
	systemctl stop sirius-ioc-bo-ps-correctors-07.service
	systemctl stop sirius-ioc-bo-ps-correctors-08.service
	systemctl stop sirius-ioc-bo-ps-correctors-09.service
	systemctl stop sirius-ioc-bo-ps-correctors-10.service
	systemctl stop sirius-ioc-bo-ps-correctors-11.service
	systemctl stop sirius-ioc-bo-ps-correctors-12.service
	systemctl stop sirius-ioc-bo-ps-correctors-13.service

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
	systemctl start sirius-ioc-bo-ps-correctors-01.service
	systemctl start sirius-ioc-bo-ps-correctors-02.service
	systemctl start sirius-ioc-bo-ps-correctors-03.service
	systemctl start sirius-ioc-bo-ps-correctors-04.service
	systemctl start sirius-ioc-bo-ps-correctors-05.service
	systemctl start sirius-ioc-bo-ps-correctors-06.service
	systemctl start sirius-ioc-bo-ps-correctors-07.service
	systemctl start sirius-ioc-bo-ps-correctors-08.service
	systemctl start sirius-ioc-bo-ps-correctors-09.service
	systemctl start sirius-ioc-bo-ps-correctors-10.service
	systemctl start sirius-ioc-bo-ps-correctors-11.service
	systemctl start sirius-ioc-bo-ps-correctors-12.service
	systemctl start sirius-ioc-bo-ps-correctors-13.service

uninstall: stop
	@printf "Uninstalling sirius-bbb-ioc-ps...\n"
	systemctl disable sirius-bbb-ioc-ps.service
	rm -rf /etc/systemd/system/sirius-bbb-ioc-ps.service
	rm -rf /etc/system/system/sirius-ioc-tb-ps-dipoles.service
	rm -rf /etc/system/system/sirius-ioc-tb-ps-quadrupoles.service
	rm -rf /etc/system/system/sirius-ioc-tb-ps-correctors.service
	rm -rf /etc/system/system/sirius-ioc-bo-ps-dipole-1.service
	rm -rf /etc/system/system/sirius-ioc-bo-ps-dipole-2.service
	rm -rf /etc/system/system/sirius-ioc-bo-ps-quadrupole-qf.service
	rm -rf /etc/system/system/sirius-ioc-bo-ps-quadrupole-qd.service
	rm -rf /etc/system/system/sirius-ioc-bo-ps-sextupole-sf.service
	rm -rf /etc/system/system/sirius-ioc-bo-ps-sextupole-sd.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-01.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-02.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-03.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-04.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-05.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-06.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-07.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-08.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-09.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-10.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-11.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-12.service
	rm -rf /etc/systemd/system/sirius-ioc-bo-ps-correctors-13.service
	systemctl daemon-reload
	systemctl reset-failed
