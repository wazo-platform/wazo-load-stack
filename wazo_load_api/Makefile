.PHONY: build-api run-api stop-api clean api install 

API_TAG = 1.0.4
API_DOCKERFILE = wlapi/docker/Dockerfile
API_IMAGE = wlapi
API_CONTAINER = $(API_IMAGE)-2
build-api: $(API_DOCKERFILE)
	sudo docker build -t $(API_IMAGE):$(API_TAG) -f $(API_DOCKERFILE) .

API_PORT = 9900
run-api: stop-api 
	sudo docker run -ti --rm --name $(API_CONTAINER) \
	-p $(API_PORT):$(API_PORT) \
	--env PULSE_SERVER=unix:/tmp/pulseaudio.socket \
	--env PULSE_COOKIE=/tmp/pulseaudio.cookie \
	--volume /tmp/pulseaudio.socket:/tmp/pulseaudio.socket \
    --volume /tmp/pulseaudio.client.conf:/etc/pulse/client.conf \
	--device=/dev/snd:/dev/snd \
	$(API_IMAGE):$(API_TAG) bash

stop-api:
	-sudo docker stop $(API_CONTAINER)
	-sudo docker rm $(API_CONTAINER)

shell-api:
	sudo docker exec -ti $(API_CONTAINER) bash

api: build-api run-api

REQS = requirements.txt
install: $(REQS)
	pip install -r $(REQS)
	pip install .

clean:
	-rm -rf __pycache__/
	-rm -rf build/
	-rm -rf .pytest_cache/
	-rm -rf dist/
	-rm -rf modules/__pycache__/
	-rm -rf wlapi.egg-info/
	-rm wda*.yml

KEY = wlapi/etc/wazo-load-api/private.key
CERT = wlapi/etc/wazo-load-api/certificate.pem
CSR = wlapi/etc/wazo-load-api/certificate.csr
CN = example.com
certs:
	openssl genrsa -out $(KEY) 2048
	openssl req -new -key $(KEY) -out $(CSR) -subj "/CN=$(CN)"
	openssl x509 -req -in $(CSR) -signkey $(KEY) -out $(CERT) -days 3650
