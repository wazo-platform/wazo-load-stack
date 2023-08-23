API_TAG = 0.0.1
API_DOCKERFILE = docker/Dockerfile
API_CONTAINER = wlapi
API_IMAGE = $(API_CONTAINER)
build-api: $(API_DOCKERFILE)
	sudo docker build -t $(API_IMAGE):$(API_TAG) -f $(API_DOCKERFILE) .

API_PORT = 9900
run-api: 
	sudo docker run -p $(API_PORT):$(API_PORT) --rm --name $(API_CONTAINER) -d $(API_IMAGE):$(API_TAG)
stop-api:
	-sudo docker stop $(API_CONTAINER)
	-sudo docker rm $(API_CONTAINER)

shell-api:
	sudo docker exec -ti $(API_CONTAINER) bash

api: build-api stop-api run-api

REQS = requirements.txt
install: $(REQS)
	pip install -r $(REQS)
	pip install --editable .

clean:
	-rm -rf __pycache__/
	-rm -rf build/
	-rm -rf .pytest_cache/
	-rm -rf dist/
	-rm -rf modules/__pycache__/
	-rm -rf wlapi.egg-info/
	-rm wda*.yml

KEY = etc/wazo-load-api/private.key
CERT = etc/wazo-load-api/certificate.pem
CSR = etc/wazo-load-api/certificate.csr
CN = example.com
certs:
	openssl genrsa -out $(KEY) 2048
	openssl req -new -key $(KEY) -out $(CSR) -subj "/CN=$(CN)"
	openssl x509 -req -in $(CSR) -signkey $(KEY) -out $(CERT) -days 3650