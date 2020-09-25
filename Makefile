develop: develop-scripts install-services

develop-scripts:
	cd as-ap-currinfo; sudo make develop-scripts
	cd as-ap-opticscorr; sudo make develop-scripts
	cd as-ap-posang; sudo make develop-scripts
	cd as-ap-sofb; sudo make develop-scripts
	cd as-ps; sudo make develop-scripts
	cd as-ps-diag; sudo make develop-scripts
	cd as-ti-control; sudo make develop-scripts
	cd li-ap-energy; sudo make develop-scripts
	cd si-ap-manaca; sudo make develop-scripts
	cd as-pu-conv; sudo make develop-scripts
	cd as-pu-diag; sudo make develop-scripts
	cd li-ps-conv; sudo make develop-scripts
	cd li-ap-diag; sudo make develop-scripts
	cd si-id-conv; sudo make develop-scripts
	cd as-ap-machshift; sudo make develop-scripts
	cd as-rf-diag; sudo make develop-scripts

install: install-scripts install-services

uninstall: uninstall-scripts uninstall-services

install-scripts:
	cd as-ap-currinfo; sudo make install-scripts
	cd as-ap-opticscorr; sudo make install-scripts
	cd as-ap-posang; sudo make install-scripts
	cd as-ap-sofb; sudo make install-scripts
	cd as-ps; sudo make install-scripts
	cd as-ps-diag; sudo make install-scripts
	cd as-ti-control; sudo make install-scripts
	cd li-ap-energy; sudo make install-scripts
	cd si-ap-manaca; sudo make install-scripts
	cd as-pu-conv; sudo make install-scripts
	cd as-pu-diag; sudo make install-scripts
	cd li-ps-conv; sudo make install-scripts
	cd li-ap-diag; sudo make install-scripts
	cd si-id-conv; sudo make install-scripts
	cd as-ap-machshift; sudo make install-scripts
	cd as-rf-diag; sudo make install-scripts

uninstall-scripts:
	cd as-ap-currinfo; sudo make uninstall-scripts
	cd as-ap-opticscorr; sudo make uninstall-scripts
	cd as-ap-posang; sudo make uninstall-scripts
	cd as-ap-sofb; sudo make uninstall-scripts
	cd as-ps; sudo make uninstall-scripts
	cd as-ps-diag; sudo make uninstall-scripts
	cd as-ti-control; sudo make uninstall-scripts
	cd li-ap-energy; sudo make uninstall-scripts
	cd si-ap-manaca; sudo make uninstall-scripts
	cd as-pu-conv; sudo make uninstall-scripts
	cd as-pu-diag; sudo make uninstall-scripts
	cd li-ps-conv; sudo make uninstall-scripts
	cd li-ap-diag; sudo make uninstall-scripts
	cd si-id-conv; sudo make uninstall-scripts
	cd as-ap-machshift; sudo make uninstall-scripts
	cd as-rf-diag; sudo make uninstall-scripts

install-services:
	cd as-ap-currinfo; sudo make install-services
	cd as-ap-opticscorr; sudo make install-services
	cd as-ap-posang; sudo make install-services
	cd as-ap-sofb; sudo make install-services
	cd as-ps; sudo make install-services
	cd as-ps-diag; sudo make install-services
	cd as-ti-control; sudo make install-services
	cd li-ap-energy; sudo make install-services
	cd si-ap-manaca; sudo make install-services
	cd as-pu-conv; sudo make install-services
	cd as-pu-diag; sudo make install-services
	cd li-ps-conv; sudo make install-services
	cd li-ap-diag; sudo make install-services
	cd si-id-conv; sudo make install-services
	cd as-ap-machshift; sudo make install-services
	cd as-rf-diag; sudo make install-services
	sudo systemctl daemon-reload

uninstall-services:
	cd as-ap-currinfo; sudo make uninstall-services
	cd as-ap-opticscorr; sudo make uninstall-services
	cd as-ap-posang; sudo make uninstall-services
	cd as-ap-sofb; sudo make uninstall-services
	cd as-ps; sudo make uninstall-services
	cd as-ps-diag; sudo make uninstall-services
	cd as-ti-control; sudo make uninstall-services
	cd li-ap-energy; sudo make uninstall-services
	cd si-ap-manaca; sudo make uninstall-services
	cd as-pu-conv; sudo make uninstall-services
	cd as-pu-diag; sudo make uninstall-services
	cd li-ps-conv; sudo make uninstall-services
	cd li-ap-diag; sudo make uninstall-services
	cd si-id-conv; sudo make uninstall-services
	cd as-ap-machshift; sudo make uninstall-services
	cd as-rf-diag; sudo make uninstall-services
	sudo systemctl daemon-reload

clean:
	cd as-ap-currinfo; sudo make clean
	cd as-ap-opticscorr; sudo make clean
	cd as-ap-posang; sudo make clean
	cd as-ap-sofb; sudo make clean
	cd as-ps; sudo make clean
	cd as-ps-diag; sudo make clean
	cd as-ti-control; sudo make clean
	cd li-ap-energy; sudo make clean
	cd si-ap-manaca; sudo make clean
	cd as-pu-conv; sudo make clean
	cd as-pu-diag; sudo make clean
	cd li-ps-conv; sudo make clean
	cd li-ap-diag; sudo make clean
	cd si-id-conv; sudo make clean
	cd as-ap-machshift; sudo make clean
	cd as-rf-diag; sudo make clean
