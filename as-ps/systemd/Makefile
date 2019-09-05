

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
	cp -rf sirius-ioc-si-ps-dipoles.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-quadrupoles-qf.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-quadrupoles-qd1.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-quadrupoles-qd2.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-quadrupoles-q.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-sextupoles-sfb0-sdb01.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-sextupoles-sfa0p0-sda0p0.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-sextupoles-sda1b12.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-sextupoles-sfa12-sda3p1.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-sextupoles-sfb12-sdb3.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-sextupoles-sfp12-sdp23.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia01-c2.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia01-c134.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia01-m12.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia02-c2.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia02-c134.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia02-m12.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia03-c2.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia03-c134.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia03-m12.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia04-c2.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia04-c134.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia04-m12.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia05-c2.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia05-c134.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia05-m12.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia06-c2.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia06-c134.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia06-m12.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia07-c2.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia07-c134.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia07-m12.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia08-c2.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia08-c134.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia08-m12.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia09-c2.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia09-c134.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia09-m12.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia10-c2.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia10-c134.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia10-m12.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia11-c2.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia11-c134.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia11-m12.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia12-c2.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia12-c134.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia12-m12.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia13-c2.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia13-c134.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia13-m12.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia14-c2.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia14-c134.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia14-m12.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia15-c2.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia15-c134.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia15-m12.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia16-c2.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia16-c134.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia16-m12.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia17-c2.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia17-c134.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia17-m12.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia18-c2.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia18-c134.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia18-m12.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia19-c2.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia19-c134.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia19-m12.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia20-c2.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia20-c134.service /etc/systemd/system/
	cp -rf sirius-ioc-si-ps-correctors-ia20-m12.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-tbts.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia01.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia02.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia03.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia04.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia05.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia06.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia07.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia08.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia09.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia10.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia11.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia12.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia13.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia14.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia15.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia16.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia17.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia18.service /etc/systemd/system/
	cp -rf sirius-ioc-as-ps-dclink-ia19.service /etc/systemd/system/
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
	systemctl stop sirius-ioc-si-ps-dipoles.service
	systemctl stop sirius-ioc-si-ps-quadrupoles-qf.service
	systemctl stop sirius-ioc-si-ps-quadrupoles-qd1.service
	systemctl stop sirius-ioc-si-ps-quadrupoles-qd2.service
	systemctl stop sirius-ioc-si-ps-quadrupoles-q.service
	systemctl stop sirius-ioc-si-ps-sextupoles-sfb0-sdb01.service
	systemctl stop sirius-ioc-si-ps-sextupoles-sfa0p0-sda0p0.service
	systemctl stop sirius-ioc-si-ps-sextupoles-sda1b12.service
	systemctl stop sirius-ioc-si-ps-sextupoles-sfa12-sda3p1.service
	systemctl stop sirius-ioc-si-ps-sextupoles-sfb12-sdb3.service
	systemctl stop sirius-ioc-si-ps-sextupoles-sfp12-sdp23.service
	systemctl stop sirius-ioc-si-ps-correctors-ia01-c2.service
	systemctl stop sirius-ioc-si-ps-correctors-ia01-c134.service
	systemctl stop sirius-ioc-si-ps-correctors-ia01-m12.service
	systemctl stop sirius-ioc-si-ps-correctors-ia02-c2.service
	systemctl stop sirius-ioc-si-ps-correctors-ia02-c134.service
	systemctl stop sirius-ioc-si-ps-correctors-ia02-m12.service
	systemctl stop sirius-ioc-si-ps-correctors-ia03-c2.service
	systemctl stop sirius-ioc-si-ps-correctors-ia03-c134.service
	systemctl stop sirius-ioc-si-ps-correctors-ia03-m12.service
	systemctl stop sirius-ioc-si-ps-correctors-ia04-c2.service
	systemctl stop sirius-ioc-si-ps-correctors-ia04-c134.service
	systemctl stop sirius-ioc-si-ps-correctors-ia04-m12.service
	systemctl stop sirius-ioc-si-ps-correctors-ia05-c2.service
	systemctl stop sirius-ioc-si-ps-correctors-ia05-c134.service
	systemctl stop sirius-ioc-si-ps-correctors-ia05-m12.service
	systemctl stop sirius-ioc-si-ps-correctors-ia06-c2.service
	systemctl stop sirius-ioc-si-ps-correctors-ia06-c134.service
	systemctl stop sirius-ioc-si-ps-correctors-ia06-m12.service
	systemctl stop sirius-ioc-si-ps-correctors-ia07-c2.service
	systemctl stop sirius-ioc-si-ps-correctors-ia07-c134.service
	systemctl stop sirius-ioc-si-ps-correctors-ia07-m12.service
	systemctl stop sirius-ioc-si-ps-correctors-ia08-c2.service
	systemctl stop sirius-ioc-si-ps-correctors-ia08-c134.service
	systemctl stop sirius-ioc-si-ps-correctors-ia08-m12.service
	systemctl stop sirius-ioc-si-ps-correctors-ia09-c2.service
	systemctl stop sirius-ioc-si-ps-correctors-ia09-c134.service
	systemctl stop sirius-ioc-si-ps-correctors-ia09-m12.service
	systemctl stop sirius-ioc-si-ps-correctors-ia10-c2.service
	systemctl stop sirius-ioc-si-ps-correctors-ia10-c134.service
	systemctl stop sirius-ioc-si-ps-correctors-ia10-m12.service
	systemctl stop sirius-ioc-si-ps-correctors-ia11-c2.service
	systemctl stop sirius-ioc-si-ps-correctors-ia11-c134.service
	systemctl stop sirius-ioc-si-ps-correctors-ia11-m12.service
	systemctl stop sirius-ioc-si-ps-correctors-ia12-c2.service
	systemctl stop sirius-ioc-si-ps-correctors-ia12-c134.service
	systemctl stop sirius-ioc-si-ps-correctors-ia12-m12.service
	systemctl stop sirius-ioc-si-ps-correctors-ia13-c2.service
	systemctl stop sirius-ioc-si-ps-correctors-ia13-c134.service
	systemctl stop sirius-ioc-si-ps-correctors-ia13-m12.service
	systemctl stop sirius-ioc-si-ps-correctors-ia14-c2.service
	systemctl stop sirius-ioc-si-ps-correctors-ia14-c134.service
	systemctl stop sirius-ioc-si-ps-correctors-ia14-m12.service
	systemctl stop sirius-ioc-si-ps-correctors-ia15-c2.service
	systemctl stop sirius-ioc-si-ps-correctors-ia15-c134.service
	systemctl stop sirius-ioc-si-ps-correctors-ia15-m12.service
	systemctl stop sirius-ioc-si-ps-correctors-ia16-c2.service
	systemctl stop sirius-ioc-si-ps-correctors-ia16-c134.service
	systemctl stop sirius-ioc-si-ps-correctors-ia16-m12.service
	systemctl stop sirius-ioc-si-ps-correctors-ia17-c2.service
	systemctl stop sirius-ioc-si-ps-correctors-ia17-c134.service
	systemctl stop sirius-ioc-si-ps-correctors-ia17-m12.service
	systemctl stop sirius-ioc-si-ps-correctors-ia18-c2.service
	systemctl stop sirius-ioc-si-ps-correctors-ia18-c134.service
	systemctl stop sirius-ioc-si-ps-correctors-ia18-m12.service
	systemctl stop sirius-ioc-si-ps-correctors-ia19-c2.service
	systemctl stop sirius-ioc-si-ps-correctors-ia19-c134.service
	systemctl stop sirius-ioc-si-ps-correctors-ia19-m12.service
	systemctl stop sirius-ioc-si-ps-correctors-ia20-c2.service
	systemctl stop sirius-ioc-si-ps-correctors-ia20-c134.service
	systemctl stop sirius-ioc-si-ps-correctors-ia20-m12.service
	systemctl stop sirius-ioc-as-ps-dclink-tbts.service
	systemctl stop sirius-ioc-as-ps-dclink-ia01.service
	systemctl stop sirius-ioc-as-ps-dclink-ia02.service
	systemctl stop sirius-ioc-as-ps-dclink-ia03.service
	systemctl stop sirius-ioc-as-ps-dclink-ia04.service
	systemctl stop sirius-ioc-as-ps-dclink-ia05.service
	systemctl stop sirius-ioc-as-ps-dclink-ia06.service
	systemctl stop sirius-ioc-as-ps-dclink-ia07.service
	systemctl stop sirius-ioc-as-ps-dclink-ia08.service
	systemctl stop sirius-ioc-as-ps-dclink-ia09.service
	systemctl stop sirius-ioc-as-ps-dclink-ia10.service
	systemctl stop sirius-ioc-as-ps-dclink-ia11.service
	systemctl stop sirius-ioc-as-ps-dclink-ia12.service
	systemctl stop sirius-ioc-as-ps-dclink-ia13.service
	systemctl stop sirius-ioc-as-ps-dclink-ia14.service
	systemctl stop sirius-ioc-as-ps-dclink-ia15.service
	systemctl stop sirius-ioc-as-ps-dclink-ia16.service
	systemctl stop sirius-ioc-as-ps-dclink-ia17.service
	systemctl stop sirius-ioc-as-ps-dclink-ia18.service
	systemctl stop sirius-ioc-as-ps-dclink-ia19.service
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
	systemctl start sirius-ioc-si-ps-dipoles.service
	systemctl start sirius-ioc-si-ps-quadrupoles-qf.service
	systemctl start sirius-ioc-si-ps-quadrupoles-qd1.service
	systemctl start sirius-ioc-si-ps-quadrupoles-qd2.service
	systemctl start sirius-ioc-si-ps-quadrupoles-q.service
	systemctl start sirius-ioc-si-ps-sextupoles-sfb0-sdb01.service
	systemctl start sirius-ioc-si-ps-sextupoles-sfa0p0-sda0p0.service
	systemctl start sirius-ioc-si-ps-sextupoles-sda1b12.service
	systemctl start sirius-ioc-si-ps-sextupoles-sfa12-sda3p1.service
	systemctl start sirius-ioc-si-ps-sextupoles-sfb12-sdb3.service
	systemctl start sirius-ioc-si-ps-sextupoles-sfp12-sdp23.service
	systemctl start sirius-ioc-si-ps-correctors-ia01-c2.service
	systemctl start sirius-ioc-si-ps-correctors-ia01-c134.service
	systemctl start sirius-ioc-si-ps-correctors-ia01-m12.service
	systemctl start sirius-ioc-si-ps-correctors-ia02-c2.service
	systemctl start sirius-ioc-si-ps-correctors-ia02-c134.service
	systemctl start sirius-ioc-si-ps-correctors-ia02-m12.service
	systemctl start sirius-ioc-si-ps-correctors-ia03-c2.service
	systemctl start sirius-ioc-si-ps-correctors-ia03-c134.service
	systemctl start sirius-ioc-si-ps-correctors-ia03-m12.service
	systemctl start sirius-ioc-si-ps-correctors-ia04-c2.service
	systemctl start sirius-ioc-si-ps-correctors-ia04-c134.service
	systemctl start sirius-ioc-si-ps-correctors-ia04-m12.service
	systemctl start sirius-ioc-si-ps-correctors-ia05-c2.service
	systemctl start sirius-ioc-si-ps-correctors-ia05-c134.service
	systemctl start sirius-ioc-si-ps-correctors-ia05-m12.service
	systemctl start sirius-ioc-si-ps-correctors-ia06-c2.service
	systemctl start sirius-ioc-si-ps-correctors-ia06-c134.service
	systemctl start sirius-ioc-si-ps-correctors-ia06-m12.service
	systemctl start sirius-ioc-si-ps-correctors-ia07-c2.service
	systemctl start sirius-ioc-si-ps-correctors-ia07-c134.service
	systemctl start sirius-ioc-si-ps-correctors-ia07-m12.service
	systemctl start sirius-ioc-si-ps-correctors-ia08-c2.service
	systemctl start sirius-ioc-si-ps-correctors-ia08-c134.service
	systemctl start sirius-ioc-si-ps-correctors-ia08-m12.service
	systemctl start sirius-ioc-si-ps-correctors-ia09-c2.service
	systemctl start sirius-ioc-si-ps-correctors-ia09-c134.service
	systemctl start sirius-ioc-si-ps-correctors-ia09-m12.service
	systemctl start sirius-ioc-si-ps-correctors-ia10-c2.service
	systemctl start sirius-ioc-si-ps-correctors-ia10-c134.service
	systemctl start sirius-ioc-si-ps-correctors-ia10-m12.service
	systemctl start sirius-ioc-si-ps-correctors-ia11-c2.service
	systemctl start sirius-ioc-si-ps-correctors-ia11-c134.service
	systemctl start sirius-ioc-si-ps-correctors-ia11-m12.service
	systemctl start sirius-ioc-si-ps-correctors-ia12-c2.service
	systemctl start sirius-ioc-si-ps-correctors-ia12-c134.service
	systemctl start sirius-ioc-si-ps-correctors-ia12-m12.service
	systemctl start sirius-ioc-si-ps-correctors-ia13-c2.service
	systemctl start sirius-ioc-si-ps-correctors-ia13-c134.service
	systemctl start sirius-ioc-si-ps-correctors-ia13-m12.service
	systemctl start sirius-ioc-si-ps-correctors-ia14-c2.service
	systemctl start sirius-ioc-si-ps-correctors-ia14-c134.service
	systemctl start sirius-ioc-si-ps-correctors-ia14-m12.service
	systemctl start sirius-ioc-si-ps-correctors-ia15-c2.service
	systemctl start sirius-ioc-si-ps-correctors-ia15-c134.service
	systemctl start sirius-ioc-si-ps-correctors-ia15-m12.service
	systemctl start sirius-ioc-si-ps-correctors-ia16-c2.service
	systemctl start sirius-ioc-si-ps-correctors-ia16-c134.service
	systemctl start sirius-ioc-si-ps-correctors-ia16-m12.service
	systemctl start sirius-ioc-si-ps-correctors-ia17-c2.service
	systemctl start sirius-ioc-si-ps-correctors-ia17-c134.service
	systemctl start sirius-ioc-si-ps-correctors-ia17-m12.service
	systemctl start sirius-ioc-si-ps-correctors-ia18-c2.service
	systemctl start sirius-ioc-si-ps-correctors-ia18-c134.service
	systemctl start sirius-ioc-si-ps-correctors-ia18-m12.service
	systemctl start sirius-ioc-si-ps-correctors-ia19-c2.service
	systemctl start sirius-ioc-si-ps-correctors-ia19-c134.service
	systemctl start sirius-ioc-si-ps-correctors-ia19-m12.service
	systemctl start sirius-ioc-si-ps-correctors-ia20-c2.service
	systemctl start sirius-ioc-si-ps-correctors-ia20-c134.service
	systemctl start sirius-ioc-si-ps-correctors-ia20-m12.service
	systemctl start sirius-ioc-as-ps-dclink-tbts.service
	systemctl start sirius-ioc-as-ps-dclink-ia01.service
	systemctl start sirius-ioc-as-ps-dclink-ia02.service
	systemctl start sirius-ioc-as-ps-dclink-ia03.service
	systemctl start sirius-ioc-as-ps-dclink-ia04.service
	systemctl start sirius-ioc-as-ps-dclink-ia05.service
	systemctl start sirius-ioc-as-ps-dclink-ia06.service
	systemctl start sirius-ioc-as-ps-dclink-ia07.service
	systemctl start sirius-ioc-as-ps-dclink-ia08.service
	systemctl start sirius-ioc-as-ps-dclink-ia09.service
	systemctl start sirius-ioc-as-ps-dclink-ia10.service
	systemctl start sirius-ioc-as-ps-dclink-ia11.service
	systemctl start sirius-ioc-as-ps-dclink-ia12.service
	systemctl start sirius-ioc-as-ps-dclink-ia13.service
	systemctl start sirius-ioc-as-ps-dclink-ia14.service
	systemctl start sirius-ioc-as-ps-dclink-ia15.service
	systemctl start sirius-ioc-as-ps-dclink-ia16.service
	systemctl start sirius-ioc-as-ps-dclink-ia17.service
	systemctl start sirius-ioc-as-ps-dclink-ia18.service
	systemctl start sirius-ioc-as-ps-dclink-ia19.service
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
	systemctl disable sirius-ioc-si-ps-dipoles.service
	systemctl disable sirius-ioc-si-ps-quadrupoles-qf.service
	systemctl disable sirius-ioc-si-ps-quadrupoles-qd1.service
	systemctl disable sirius-ioc-si-ps-quadrupoles-qd2.service
	systemctl disable sirius-ioc-si-ps-quadrupoles-q.service
	systemctl disable sirius-ioc-si-ps-sextupoles-sfb0-sdb01.service
	systemctl disable sirius-ioc-si-ps-sextupoles-sfa0p0-sda0p0.service
	systemctl disable sirius-ioc-si-ps-sextupoles-sda1b12.service
	systemctl disable sirius-ioc-si-ps-sextupoles-sfa12-sda3p1.service
	systemctl disable sirius-ioc-si-ps-sextupoles-sfb12-sdb3.service
	systemctl disable sirius-ioc-si-ps-sextupoles-sfp12-sdp23.service
	systemctl disable sirius-ioc-si-ps-correctors-ia01-c2.service
	systemctl disable sirius-ioc-si-ps-correctors-ia01-c134.service
	systemctl disable sirius-ioc-si-ps-correctors-ia01-m12.service
	systemctl disable sirius-ioc-si-ps-correctors-ia02-c2.service
	systemctl disable sirius-ioc-si-ps-correctors-ia02-c134.service
	systemctl disable sirius-ioc-si-ps-correctors-ia02-m12.service
	systemctl disable sirius-ioc-si-ps-correctors-ia03-c2.service
	systemctl disable sirius-ioc-si-ps-correctors-ia03-c134.service
	systemctl disable sirius-ioc-si-ps-correctors-ia03-m12.service
	systemctl disable sirius-ioc-si-ps-correctors-ia04-c2.service
	systemctl disable sirius-ioc-si-ps-correctors-ia04-c134.service
	systemctl disable sirius-ioc-si-ps-correctors-ia04-m12.service
	systemctl disable sirius-ioc-si-ps-correctors-ia05-c2.service
	systemctl disable sirius-ioc-si-ps-correctors-ia05-c134.service
	systemctl disable sirius-ioc-si-ps-correctors-ia05-m12.service
	systemctl disable sirius-ioc-si-ps-correctors-ia06-c2.service
	systemctl disable sirius-ioc-si-ps-correctors-ia06-c134.service
	systemctl disable sirius-ioc-si-ps-correctors-ia06-m12.service
	systemctl disable sirius-ioc-si-ps-correctors-ia07-c2.service
	systemctl disable sirius-ioc-si-ps-correctors-ia07-c134.service
	systemctl disable sirius-ioc-si-ps-correctors-ia07-m12.service
	systemctl disable sirius-ioc-si-ps-correctors-ia08-c2.service
	systemctl disable sirius-ioc-si-ps-correctors-ia08-c134.service
	systemctl disable sirius-ioc-si-ps-correctors-ia08-m12.service
	systemctl disable sirius-ioc-si-ps-correctors-ia09-c2.service
	systemctl disable sirius-ioc-si-ps-correctors-ia09-c134.service
	systemctl disable sirius-ioc-si-ps-correctors-ia09-m12.service
	systemctl disable sirius-ioc-si-ps-correctors-ia10-c2.service
	systemctl disable sirius-ioc-si-ps-correctors-ia10-c134.service
	systemctl disable sirius-ioc-si-ps-correctors-ia10-m12.service
	systemctl disable sirius-ioc-si-ps-correctors-ia11-c2.service
	systemctl disable sirius-ioc-si-ps-correctors-ia11-c134.service
	systemctl disable sirius-ioc-si-ps-correctors-ia11-m12.service
	systemctl disable sirius-ioc-si-ps-correctors-ia12-c2.service
	systemctl disable sirius-ioc-si-ps-correctors-ia12-c134.service
	systemctl disable sirius-ioc-si-ps-correctors-ia12-m12.service
	systemctl disable sirius-ioc-si-ps-correctors-ia13-c2.service
	systemctl disable sirius-ioc-si-ps-correctors-ia13-c134.service
	systemctl disable sirius-ioc-si-ps-correctors-ia13-m12.service
	systemctl disable sirius-ioc-si-ps-correctors-ia14-c2.service
	systemctl disable sirius-ioc-si-ps-correctors-ia14-c134.service
	systemctl disable sirius-ioc-si-ps-correctors-ia14-m12.service
	systemctl disable sirius-ioc-si-ps-correctors-ia15-c2.service
	systemctl disable sirius-ioc-si-ps-correctors-ia15-c134.service
	systemctl disable sirius-ioc-si-ps-correctors-ia15-m12.service
	systemctl disable sirius-ioc-si-ps-correctors-ia16-c2.service
	systemctl disable sirius-ioc-si-ps-correctors-ia16-c134.service
	systemctl disable sirius-ioc-si-ps-correctors-ia16-m12.service
	systemctl disable sirius-ioc-si-ps-correctors-ia17-c2.service
	systemctl disable sirius-ioc-si-ps-correctors-ia17-c134.service
	systemctl disable sirius-ioc-si-ps-correctors-ia17-m12.service
	systemctl disable sirius-ioc-si-ps-correctors-ia18-c2.service
	systemctl disable sirius-ioc-si-ps-correctors-ia18-c134.service
	systemctl disable sirius-ioc-si-ps-correctors-ia18-m12.service
	systemctl disable sirius-ioc-si-ps-correctors-ia19-c2.service
	systemctl disable sirius-ioc-si-ps-correctors-ia19-c134.service
	systemctl disable sirius-ioc-si-ps-correctors-ia19-m12.service
	systemctl disable sirius-ioc-si-ps-correctors-ia20-c2.service
	systemctl disable sirius-ioc-si-ps-correctors-ia20-c134.service
	systemctl disable sirius-ioc-si-ps-correctors-ia20-m12.service
	systemctl disable sirius-ioc-as-ps-dclink-tbts.service
	systemctl disable sirius-ioc-as-ps-dclink-ia01.service
	systemctl disable sirius-ioc-as-ps-dclink-ia02.service
	systemctl disable sirius-ioc-as-ps-dclink-ia03.service
	systemctl disable sirius-ioc-as-ps-dclink-ia04.service
	systemctl disable sirius-ioc-as-ps-dclink-ia05.service
	systemctl disable sirius-ioc-as-ps-dclink-ia06.service
	systemctl disable sirius-ioc-as-ps-dclink-ia07.service
	systemctl disable sirius-ioc-as-ps-dclink-ia08.service
	systemctl disable sirius-ioc-as-ps-dclink-ia09.service
	systemctl disable sirius-ioc-as-ps-dclink-ia10.service
	systemctl disable sirius-ioc-as-ps-dclink-ia11.service
	systemctl disable sirius-ioc-as-ps-dclink-ia12.service
	systemctl disable sirius-ioc-as-ps-dclink-ia13.service
	systemctl disable sirius-ioc-as-ps-dclink-ia14.service
	systemctl disable sirius-ioc-as-ps-dclink-ia15.service
	systemctl disable sirius-ioc-as-ps-dclink-ia16.service
	systemctl disable sirius-ioc-as-ps-dclink-ia17.service
	systemctl disable sirius-ioc-as-ps-dclink-ia18.service
	systemctl disable sirius-ioc-as-ps-dclink-ia19.service
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
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-dipoles.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-quadrupoles-qf.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-quadrupoles-qd1.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-quadrupoles-qd2.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-quadrupoles-q.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-sextupoles-sfb0-sdb01.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-sextupoles-sfa0p0-sda0p0.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-sextupoles-sda1b12.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-sextupoles-sfa12-sda3p1.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-sextupoles-sfb12-sdb3.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-sextupoles-sfp12-sdp23.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia01-c2.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia01-c134.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia01-m12.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia02-c2.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia02-c134.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia02-m12.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia03-c2.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia03-c134.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia03-m12.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia04-c2.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia04-c134.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia04-m12.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia05-c2.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia05-c134.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia05-m12.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia06-c2.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia06-c134.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia06-m12.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia07-c2.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia07-c134.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia07-m12.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia08-c2.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia08-c134.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia08-m12.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia09-c2.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia09-c134.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia09-m12.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia10-c2.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia10-c134.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia10-m12.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia11-c2.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia11-c134.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia11-m12.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia12-c2.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia12-c134.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia12-m12.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia13-c2.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia13-c134.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia13-m12.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia14-c2.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia14-c134.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia14-m12.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia15-c2.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia15-c134.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia15-m12.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia16-c2.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia16-c134.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia16-m12.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia17-c2.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia17-c134.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia17-m12.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia18-c2.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia18-c134.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia18-m12.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia19-c2.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia19-c134.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia19-m12.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia20-c2.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia20-c134.service
	rm -rf /etc/systemd/system/sirius-ioc-si-ps-correctors-ia20-m12.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-tbts.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia01.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia02.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia03.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia04.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia05.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia06.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia07.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia08.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia09.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia10.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia11.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia12.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia13.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia14.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia15.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia16.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia17.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia18.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia19.service
	rm -rf /etc/systemd/system/sirius-ioc-as-ps-dclink-ia20.service
	systemctl daemon-reload
	systemctl reset-failed
