# installation and setup of wlctl

## Installation
1 - Clone the wazo-load-stack repository
```
git clone git@github.com:wazo-platform/wazo-load-stack.git
```

2 - Move to wazo_load_cli directory
```
cd wazo_load_cli
```
3 - create and activate a virtualenv
```
python3.10 -m venv ~/.wlctl
source /tmp/wlctl/bin/activate
```
4 - install wlctl
```
pip install -r requirements.txt
pip install .
```

5 - test
```
$ wlctl --help
Usage: wlctl [OPTIONS] COMMAND [ARGS]...

  wlctl is the Wazo Load cli, that alows to perform convenient operations in
  order to generate load and manage the load stack.

Options:
  -c, --config TEXT  Path to the configuration file
  --help             Show this message and exit.

Commands:
  load  Subcommand that handles loads.
```

## configuration
1 - create the directory and file:
```
mkdir ~/.wlctl/
touch ~/.wlctl/config
```
2 - edit the config file with pilot  instance url
```
[DEFAULT]
pilot = https://10.0.0.1:9990
```
