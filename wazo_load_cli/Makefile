.PHONY: install

REQS = requirements.txt
install: $(REQS)
	pip install -r $(REQS)
	#python3 setup.py install --prefix=/home/user/.local/bin/wlctl
	pip install --editable .
