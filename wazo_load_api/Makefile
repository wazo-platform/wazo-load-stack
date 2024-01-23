.PHONY: build build-api run-api stop-api clean api install

VERSION_FILE ?= version
VERSION ?= $(shell cat $(VERSION_FILE))
# SEMVER cat take the following values: patch|minor|major|version
SEMVER ?= patch
IMAGES_BUILD_DIR ?= .images_built
MAKEFLAGS += --silent

pause:
	@bash -c 'read -n 1 -s -r -p "Hit any key to continue"'
	@echo

show-version: $(VERSION_FILE)
	@echo "Current version is: $(VERSION)"

show-version-and-pause: show-version pause

# ACTION can take the following values:
#      - inc: for incremeting the version
#      - dec: for decrementing the version
ACTION ?= inc
control-version: $(VERSION_FILE)
	mv $(VERSION_FILE) $(VERSION_FILE).prev
	-./semverctl $(ACTION)  $(SEMVER) $(VERSION) > $(VERSION_FILE)
	if [ ! -s version ]; then  mv $(VERSION_FILE).prev $(VERSION_FILE); fi

down-version:
	$(MAKE) control-version ACTION=dec

bump-version:
	$(MAKE) control-version ACTION=inc

NEW_VERSION ?= 0.0.0
set-version:
	$(MAKE) control-version ACTION=set SEMVER=version VERSION=$(NEW_VERSION)

down-version-validation:
	$(MAKE) show-version-and-pause
	$(MAKE) control-version ACTION=dec
	$(MAKE) show-version

bump-version-validation:
	$(MAKE) show-version-and-pause
	$(MAKE) control-version ACTION=inc
	$(MAKE) show-version


MAINTAINER ?= "dev@wazo.io"
STATUS ?= dev
API_DOCKERFILE_TEMPLATE ?= wlapi/docker/Dockerfile.tmpl
API_DOCKERFILE ?= wlapi/docker/Dockerfile

.PHONY: build-dockerfile
build-dockerfile: $(API_DOCKERFILE_TEMPLATE)
	sed 's/__MAINTAINER__/$(MAINTAINER)/g; s/__STATUS__/$(STATUS)/g' $(API_DOCKERFILE_TEMPLATE) > $(API_DOCKERFILE)

rebuild: down-version build
build: build-dockerfile bump-version build-api mark-image
IMAGE_STATUS ?= dev
API_TAG = $(VERSION)
API_IMAGE = wlapi
API_CONTAINER = $(API_IMAGE)-2
build-api: $(API_DOCKERFILE)
	docker build -t $(API_IMAGE):$(API_TAG) \
	-f $(API_DOCKERFILE) .

LAST_BUILD_FILE = .last_image_built
mark-image:
	echo $(API_TAG) > $(IMAGES_BUILD_DIR)/$(API_IMAGE)
	echo $(API_IMAGE):$(API_TAG) > $(LAST_BUILD_FILE)

REGISTRY ?= registry.load.wazo.io
PORT ?= 5000
LAST_BUILD = $(shell cat $(LAST_BUILD_FILE))
push: $(LAST_BUILD_FILE)
	if [ ! -s $(LAST_BUILD_FILE) ]; then \
		echo "Error: empty file"; \
	else \
		docker tag $(LAST_BUILD) $(REGISTRY):$(PORT)/$(LAST_BUILD); \
		docker push $(REGISTRY):$(PORT)/$(LAST_BUILD); \
	fi

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
