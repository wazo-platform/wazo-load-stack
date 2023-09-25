.PHONY: install clean 

REQS = requirements.txt
install: $(REQS)
	pip install -r $(REQS)
	pip install --editable .

clean:
	rm -rf __pycache__/
	rm -rf build/
	rm -rf .pytest_cache/
	rm -rf dist/
	rm -rf modules/__pycache__/
	rm -rf wlctl.egg-info/
	rm wda*.yml

KEY = etc/wazo-load-pilot/private.key
CERT = etc/wazo-load-pilot/certificate.pem
CSR = etc/wazo-load-pilot/certificate.csr
CN = example.com
certs:
	openssl genrsa -out $(KEY) 2048
	openssl req -new -key $(KEY) -out $(CSR) -subj "/CN=$(CN)"
	openssl x509 -req -in $(CSR) -signkey $(KEY) -out $(CERT) -days 3650

.PHONY: build-simple-server run-simple-server

SSERVER = tests/simple_serve.py
SSERVER_DOCKERFILE = docker/sserver.Dockerfile
SSERVER_TAG = 0.0.1
SSERVER_CONTAINER = sserver
SSERVER_IMAGE = $(SSERVER_CONTAINER)
build-simple-server: certs $(SSERVER_DOCKERFILE)
	sudo docker build -t $(SSERVER_CONTAINER):$(SSERVER_TAG) -f $(SSERVER_DOCKERFILE) .

SSERVER_PORT = 443
run-simple-server: stop-simple_server
	sudo docker run -p $(SSERVER_PORT):$(SSERVER_PORT) --rm --name $(SSERVER_CONTAINER) -d $(SSERVER_IMAGE):$(SSERVER_TAG)

stop-simple-server:
	sudo docker stop $(SSERVER_CONTAINER)
	sudo docker rm $(SSERVER_CONTAINER)


.PHONY: build-pilot run-pilot shell-pilot curl-pilot

PILOT_TAG = 1.0.0
PILOT_DOCKERFILE = docker/pilot.Dockerfile
PILOT_CONTAINER = wlpd
PILOT_IMAGE = $(PILOT_CONTAINER)
build-pilot: $(PILOT_DOCKERFILE)
	sudo docker build -t $(PILOT_IMAGE):$(PILOT_TAG) -f $(PILOT_DOCKERFILE) .

PILOT_PORT = 9990
SSERVER_IP_ADDRESS := $(shell sudo docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(SSERVER_CONTAINER))
run-pilot: 
	sudo docker run -p $(PILOT_PORT):$(PILOT_PORT) -e TRAFGEN_HOSTS=$(SSERVER_IP_ADDRESS) --rm --name $(PILOT_CONTAINER) -d $(PILOT_IMAGE):$(PILOT_TAG)
stop-pilot:
	-sudo docker stop $(PILOT_CONTAINER)
	-sudo docker rm $(PILOT_CONTAINER)

shell-pilot:
	sudo docker exec -ti $(PILOT_CONTAINER) bash

LOAD_FILE = tests/load1.json
HOST = 172.16.43.106
curl-pilot: $(LOAD_FILE)
	curl -k -X POST https://$(HOST):$(PILOT_PORT)/process-load -d '@$(LOAD_FILE)'


run-test-servers: run-simple_server run-pilot
