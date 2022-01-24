develop:
	cd as-ap-currinfo; sudo make develop
	cd as-ap-opticscorr; sudo make develop
	cd as-ap-posang; sudo make develop
	cd as-ap-sofb; sudo make develop
	cd as-ps; sudo make develop
	cd as-ps-diag; sudo make develop
	cd as-ti-control; sudo make develop
	cd li-ap-energy; sudo make develop
	cd si-ap-manaca; sudo make develop
	cd as-pu-conv; sudo make develop
	cd as-pu-diag; sudo make develop
	cd li-ps-conv; sudo make develop
	cd li-ap-diag; sudo make develop
	cd si-id-conv; sudo make develop
	cd as-ap-machshift; sudo make develop
	cd as-rf-diag; sudo make develop

install:
	cd as-ap-currinfo; sudo make install
	cd as-ap-opticscorr; sudo make install
	cd as-ap-posang; sudo make install
	cd as-ap-sofb; sudo make install
	cd as-ps; sudo make install
	cd as-ps-diag; sudo make install
	cd as-ti-control; sudo make install
	cd li-ap-energy; sudo make install
	cd si-ap-manaca; sudo make install
	cd as-pu-conv; sudo make install
	cd as-pu-diag; sudo make install
	cd li-ps-conv; sudo make install
	cd li-ap-diag; sudo make install
	cd si-id-conv; sudo make install
	cd as-ap-machshift; sudo make install
	cd as-rf-diag; sudo make install

uninstall:
	cd as-ap-currinfo; sudo make uninstall
	cd as-ap-opticscorr; sudo make uninstall
	cd as-ap-posang; sudo make uninstall
	cd as-ap-sofb; sudo make uninstall
	cd as-ps; sudo make uninstall
	cd as-ps-diag; sudo make uninstall
	cd as-ti-control; sudo make uninstall
	cd li-ap-energy; sudo make uninstall
	cd si-ap-manaca; sudo make uninstall
	cd as-pu-conv; sudo make uninstall
	cd as-pu-diag; sudo make uninstall
	cd li-ps-conv; sudo make uninstall
	cd li-ap-diag; sudo make uninstall
	cd si-id-conv; sudo make uninstall
	cd as-ap-machshift; sudo make uninstall
	cd as-rf-diag; sudo make uninstall

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
