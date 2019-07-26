# Destination directory
SERVICES = $(shell ls *.service | grep -v Makefile)

# test:
# 	for ser in $(SERVICES) ; do \
# 	echo $$ser ; \
# 	done

install-services:
	@echo " --- install services ---"
	for ser in $(SERVICES) ; do \
	  cp -rf $$ser /etc/systemd/system/ ; \
	done
	systemctl daemon-reload
	mkdir -p /home/sirius/iocs-log/tb-ap-posang
	mkdir -p /home/sirius/iocs-log/ts-ap-posang
	chown -R sirius.sirius /home/sirius/iocs-log

stop-services:
	@echo " --- stop services ---"
	for ser in $(SERVICES) ; do \
	  systemctl stop $$ser ; \
	done

start-services: install-services
	@echo " --- start services ---"
	for ser in $(SERVICES) ; do \
	  #systemctl enable $$ser ; \
	  systemctl start $$ser  ; \
	done

uninstall-services: stop-services
	@echo " --- uninstall services ---"
	for ser in $(SERVICES) ; do \
	  systemctl disable $$ser ; \
		rm -rf /etc/systemd/system/$$ser ; \
	done
	systemctl daemon-reload
