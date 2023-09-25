.PHONY: install

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

IMAGE = wlctl
TAG = 0.0.1
DOCKERFILE = docker/Dockerfile
build-cli: $(DOCKERFILE)
	sudo docker build -t $(IMAGE):$(TAG) -f $(DOCKERFILE) .
