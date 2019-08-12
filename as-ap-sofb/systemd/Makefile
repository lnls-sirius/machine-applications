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
	mkdir -p /home/sirius/iocs-log/si-ap-sofb/data
	mkdir -p /home/sirius/iocs-log/bo-ap-sofb/data
	mkdir -p /home/sirius/iocs-log/ts-ap-sofb/data
	mkdir -p /home/sirius/iocs-log/tb-ap-sofb/data
	chown -R sirius.sirius /home/sirius/iocs-log

stop-services:
	@echo " --- stoping services ---"
	for ser in $(SERVICES) ; do \
	  systemctl stop $$ser ; \
	done

start-services: install-services
	@echo " --- start-services ---"
	for ser in $(SERVICES) ; do \
	  systemctl enable $$ser ; \
	  systemctl start $$ser  ; \
	done

uninstall-services: stop-services
	@echo " --- uninstall services ---"
	for ser in $(SERVICES) ; do \
	  systemctl disable $$ser ; \
		rm -rf /etc/systemd/system/$$ser ; \
	done
	systemctl daemon-reload
