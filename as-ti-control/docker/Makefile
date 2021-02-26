
preparation:
	@printf "Creating ioc-logs and iocs-service directory...\n"
	mkdir -p /iocs-log
	mkdir -p /iocs-service

install-services: preparation
	@printf "Installing docker service entry-points...\n"
	cp -rf as-ti.bash /iocs-service/
