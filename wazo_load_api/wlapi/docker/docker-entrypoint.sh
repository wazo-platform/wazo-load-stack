#!/bin/bash

dbus-uuidgen > /var/lib/dbus/machine-id
dbus-daemon --nofork --system --print-address &

/etc/init.d/pulse start

wlapi --config-file /etc/wazo-load-api/config.yml

sleep infinity
