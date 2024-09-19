.PHONY: test-setup test-image egg-info fleet-vm test-ssh-keys

test-ssh-keys:
	rm -f assets/vms/mykey*
	ssh-keygen -N '' -f assets/vms/mykey -t ecdsa -b521

fleet-vm:
	mkdir -p assets/vms/logs/1 && mkdir -p assets/vms/logs/2
	docker build --no-cache -f assets/vms/Dockerfile -t wazoplatform/wazo-wlapi-vm-test:local assets/vms

test-setup: test-ssh-keys fleet-vm test-image egg-info

egg-info:
	cd .. && python3 setup.py egg_info

test-image:
	cd .. && make --makefile=makefile build-dockerfile
	cd .. && PILOT_TAG=latest make --makefile=makefile build-pilot
