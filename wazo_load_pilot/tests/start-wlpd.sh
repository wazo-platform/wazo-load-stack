#/bin/bash

for x in $(seq 1 10); do
    echo "$TRAFGEN_HOSTS  trafgen$x.load.wazo.io" >> /etc/hosts
done

/usr/local/bin/wlpd --config-file /etc/wazo-load-pilot/config.yml 