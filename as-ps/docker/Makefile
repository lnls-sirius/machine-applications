
preparation:
	@printf "Creating ioc-logs and iocs-service directory...\n"
	mkdir -p /iocs-log
	mkdir -p /iocs-service

install-services: preparation
	@printf "Installing docker service entry-points...\n"
	cp -rf as-ps-dclinks.bash /iocs-service/
	cp -rf tb-ps.bash /iocs-service/
	cp -rf ts-ps.bash /iocs-service/
	cp -rf bo-ps-fams.bash /iocs-service/
	cp -rf bo-ps-corrs.bash /iocs-service/
	cp -rf si-ps-fams.bash /iocs-service/
	cp -rf si-ps-corrs-c2m12.bash /iocs-service/
	cp -rf si-ps-corrs-c134.bash /iocs-service/
	cp -rf si-ps-trims-m12.bash /iocs-service/
	cp -rf si-ps-trims-c134.bash /iocs-service/
