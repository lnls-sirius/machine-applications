develop: develop-scripts

develop-scripts:
	cd as-ap-currinfo; sudo make develop
	cd as-ap-posang; sudo make develop
	cd as-ap-opticscorr; sudo make develop
	cd as-ps; sudo make develop
	cd as-ps-diag; sudo make develop
	cd as-ma; sudo make develop
	cd as-ti-control; sudo make develop
	cd as-ap-sofb; sudo make develop
	cd li-di-charge; sudo make develop

install: install-scripts install-services
	sudo systemctl daemon-reload

install-scripts:
	cd as-ap-sofb; sudo make install-scripts
	cd as-ti-control; sudo make install-scripts
	cd as-ps; sudo make install-scripts
	cd as-ps-diag; sudo make install-scripts
	cd as-ma; sudo make install-scripts
	cd as-ap-opticscorr; sudo make install-scripts
	cd as-ap-posang; sudo make install-scripts
	cd as-ap-currinfo; sudo make install-scripts
	cd li-di-charge; sudo make install-scripts

install-services:
	cd as-ap-currinfo; sudo make install-services
	cd as-ap-posang; sudo make install-services
	cd as-ap-opticscorr; sudo make install-services
	cd as-ps; sudo make install-services
	cd as-ps-diag; sudo make install-services
	cd as-ma; sudo make install-services
	cd as-ti-control; sudo make install-services
	cd as-ap-sofb; sudo make install-services
	cd li-di-charge; sudo make install-services
	sudo systemctl daemon-reload

uninstall-services:
	cd as-ap-currinfo; sudo make uninstall-services
	cd as-ap-posang; sudo make uninstall-services
	cd as-ap-opticscorr; sudo make uninstall-services
	cd as-ps; sudo make uninstall-services
	cd as-ps-diag; sudo make uninstall-services
	cd as-ma; sudo make uninstall-services
	cd as-ti-control; sudo make uninstall-services
	cd as-ap-sofb; sudo make uninstall-services
	cd li-di-charge; sudo make uninstall-services
	sudo systemctl daemon-reload

clean:
	cd as-ap-currinfo; sudo make clean
	cd as-ap-posang; sudo make clean
	cd as-ap-opticscorr; sudo make clean
	cd as-ps; sudo make clean
	cd as-ps-diag; sudo make clean
	cd as-ma; sudo make clean
	cd as-ti-control; sudo make clean
	cd as-ap-sofb; sudo make clean
	cd li-di-charge; sudo make clean
