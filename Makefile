develop:
	cd as-ap-currinfo; sudo ./setup.py develop; cd systemd; sudo make install-services
	cd as-ap-posang; sudo ./setup.py develop; cd systemd; sudo make install-services
	cd as-ap-opticscorr; sudo ./setup.py develop; cd systemd; sudo make install-services
	cd as-ma; sudo ./setup.py develop; cd systemd; sudo make install-services
	cd as-ps; sudo ./setup.py develop; cd systemd; sudo make install-services
	cd as-ti-control; sudo ./setup.py develop; cd systemd; sudo make install-services
	cd si-ap-sofb; sudo ./setup.py develop; cd systemd; sudo make install-services
	sudo systemctl daemon-reload


install:
	cd as-ap-currinfo; sudo ./setup.py install; cd systemd; sudo make install-services
	cd as-ap-posang; sudo ./setup.py install; cd systemd; sudo make install-services
	cd as-ap-opticscorr; sudo ./setup.py install; cd systemd; sudo make install-services
	cd as-ma; sudo ./setup.py install; cd systemd; sudo make install-services
	cd as-ps; sudo ./setup.py install; cd systemd; sudo make install-services
	cd as-ti-control; sudo ./setup.py install; cd systemd; sudo make install-services
	cd si-ap-sofb; sudo ./setup.py install; cd systemd; sudo make install-services
	sudo systemctl daemon-reload
