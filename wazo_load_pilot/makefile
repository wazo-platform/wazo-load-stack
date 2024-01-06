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


.PHONY: build-pilot run-pilot shell-pilot curl-pilot

VERSION_FILE=version
VERSION ?= $(shell cat $(VERSION_FILE))
# SEMVER cat take the following values: patch|minor|major|version
SEMVER ?= patch
IMAGES_BUILD_DIR = .images_built
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

build: bump-version build-pilot mark-image

PILOT_TAG ?= $(shell cat $(VERSION_FILE))
PILOT_DOCKERFILE ?= docker/pilot.Dockerfile
PILOT_CONTAINER ?= wlpd
PILOT_IMAGE ?= $(PILOT_CONTAINER)
# IMAGE STATUS could be: dev|prod|test|donotuse|deprecated
IMAGE_STATUS ?= dev
build-pilot: $(PILOT_DOCKERFILE)
	docker build -t $(PILOT_IMAGE):$(PILOT_TAG)	\
		--label maintainer="dev@wazo.io" \
		--label image_status=$(IMAGE_STATUS) \
		-f $(PILOT_DOCKERFILE) .

DOCKER_FUNCTIONS ?= ./docker-funcs
update-image-status-dev:
	@. $(DOCKER_FUNCTIONS)
	registry-update-image-labels $(PILOT_IMAGE) $(PILOT_TAG) "image_status=dev"
update-image-status-prod:
	@. $(DOCKER_FUNCTIONS)
	registry-update-image-labels $(PILOT_IMAGE) $(PILOT_TAG) "image_status=prod"
update-image-status-donotuse:
	@. $(DOCKER_FUNCTIONS)
	registry-update-image-labels $(PILOT_IMAGE) $(PILOT_TAG) "image_status=donotuse"
update-image-status-deprecated:
	@. $(DOCKER_FUNCTIONS)
	registry-update-image-labels $(PILOT_IMAGE) $(PILOT_TAG) "image_status=deprecated"

LAST_BUILD_FILE = .last_image_built
mark-image:
	echo $(PILOT_TAG) >> $(IMAGES_BUILD_DIR)/$(PILOT_IMAGE)
	echo $(PILOT_IMAGE):$(PILOT_TAG) > $(LAST_BUILD_FILE)


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

commit: $(LAST_BUILD_FILE) $(VERSION_FILE)
	if [ ! -s $(LAST_BUILD_FILE) ] || [ ! -s $(VERSION_FILE) ]; then
		echo "Error: empty file detected"; \
	else \
		BRANCH="wlpd-$(LAST_BUILD)""; \
		git checkout -b $$BRANCH; \
		git add $(LAST_BUILD_FILE) $(VERSION_FILE); \
		git commit -m "wazo load pilot wlpd docker image update"; \
		git push --set-upstream origin $$BRANCH; \
	fi

