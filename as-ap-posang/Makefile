# Destination directory
DEST_DIR = /usr/local/bin/sirius-iocs

IOC_DIR = as-ap-posang

CWD = $(shell pwd)


install: install-module-links install-service-links

install-module-links:
	@echo " --- install module links ---"
	sudo mkdir -p $(DEST_DIR)/$(IOC_DIR); sudo chmod g+w $(DEST_DIR)
	sudo ln -sf $(CWD)/as-ap-posang.py $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/as_ap_posang.py $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/main.py $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/pvs.py $(DEST_DIR)/$(IOC_DIR)/
	sudo chown -R fac.fac $(DEST_DIR)

install-service-links:
	@echo " --- install service links ---"
	sudo ln -sf $(CWD)/systemd/ioc-ts-ap-posang.service /etc/systemd/system/
	sudo ln -sf $(CWD)/systemd/ioc-ts-ap-posang.bash $(DEST_DIR)/$(IOC_DIR)/
	sudo ln -sf $(CWD)/systemd/ioc-tb-ap-posang.service /etc/systemd/system/
	sudo ln -sf $(CWD)/systemd/ioc-tb-ap-posang.bash $(DEST_DIR)/$(IOC_DIR)/
	sudo systemctl daemon-reload


start-ioc-tb-ap-posang:
	@echo " --- start ioc-tb-ap-posang ---"
	sudo systemctl start ioc-tb-ap-posang.service

stop-ioc-tb-ap-posang:
	@echo " --- stop ioc-tb-ap-posang ---"
	sudo systemctl stop ioc-tb-ap-posang.service

start-ioc-ts-ap-posang:
	@echo " --- start ioc-ts-ap-posang ---"
	sudo systemctl start ioc-ts-ap-posang.service

stop-ioc-ts-ap-posang:
	@echo " --- stoping ioc-ts-ap-posang  ---"
	sudo systemctl stop ioc-ts-ap-posang.service
