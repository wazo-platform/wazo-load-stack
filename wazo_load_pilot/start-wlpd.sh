#/bin/bash

cp /etc/resolv.conf.override /etc/resolv.conf

/usr/local/bin/wlpd --config-file /etc/wazo-load-pilot/config.yml
