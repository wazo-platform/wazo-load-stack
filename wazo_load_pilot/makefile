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
