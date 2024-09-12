.PHONY: test-setup test-image egg-info

test-setup: test-image egg-info

egg-info:
	cd .. && python3 setup.py egg_info

test-image:
	cd .. && make --makefile=makefile build-dockerfile
	cd .. && PILOT_TAG=latest make --makefile=makefile build-pilot
