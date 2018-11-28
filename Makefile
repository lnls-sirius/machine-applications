develop:
	cd as-ap-currinfo; sudo ./setup.py develop; cd systemd; sudo make install-services
	cd as-ap-posang; sudo ./setup.py develop; cd systemd; sudo make install-services
	cd as-ap-opticscorr; sudo ./setup.py develop; cd systemd; sudo make install-services
	cd as-ma; sudo ./setup.py develop; cd systemd; sudo make install-services
	cd as-ps; sudo ./setup.py develop; cd systemd; sudo make install-services
	cd as-ti-control; sudo ./setup.py develop; cd systemd; sudo make install-services
	cd as-ap-sofb; sudo ./setup.py develop; cd systemd; sudo make install-services
	sudo systemctl daemon-reload

develop-scripts:
	cd as-ap-currinfo; sudo ./setup.py develop
	cd as-ap-posang; sudo ./setup.py develop
	cd as-ap-opticscorr; sudo ./setup.py develop
	cd as-ma; sudo ./setup.py develop
	cd as-ps; sudo ./setup.py develop
	cd as-ti-control; sudo ./setup.py develop
	cd as-ap-sofb; sudo ./setup.py develop

develop-services:
	cd as-ap-currinfo; cd systemd; sudo make install-services
	cd as-ap-posang; cd systemd; sudo make install-services
	cd as-ap-opticscorr; cd systemd; sudo make install-services
	cd as-ma; cd systemd; sudo make install-services
	cd as-ps; cd systemd; sudo make install-services
	cd as-ti-control; cd systemd; sudo make install-services
	cd as-ap-sofb; cd systemd; sudo make install-services
	sudo systemctl daemon-reload

install:
	cd as-ap-currinfo; sudo ./setup.py install; cd systemd; sudo make install-services
	cd as-ap-posang; sudo ./setup.py install; cd systemd; sudo make install-services
	cd as-ap-opticscorr; sudo ./setup.py install; cd systemd; sudo make install-services
	cd as-ma; sudo ./setup.py install; cd systemd; sudo make install-services
	cd as-ps; sudo ./setup.py install; cd systemd; sudo make install-services
	cd as-ti-control; sudo ./setup.py install; cd systemd; sudo make install-services
	cd as-ap-sofb; sudo ./setup.py install; cd systemd; sudo make install-services
	sudo systemctl daemon-reload

install-scripts:
	cd as-ap-sofb; sudo ./setup.py install
	cd as-ti-control; sudo ./setup.py install
	cd as-ps; sudo ./setup.py install
	cd as-ma; sudo ./setup.py install
	cd as-ap-opticscorr; sudo ./setup.py install
	cd as-ap-posang; sudo ./setup.py install
	cd as-ap-currinfo; sudo ./setup.py install

install-services:
	cd as-ap-currinfo; cd systemd; sudo make install-services
	cd as-ap-posang; cd systemd; sudo make install-services
	cd as-ap-opticscorr; cd systemd; sudo make install-services
	cd as-ma; cd systemd; sudo make install-services
	cd as-ps; cd systemd; sudo make install-services
	cd as-ti-control; cd systemd; sudo make install-services
	cd as-ap-sofb; cd systemd; sudo make install-services
	sudo systemctl daemon-reload

