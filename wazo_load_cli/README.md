# wlctl usage
To install wlctl refer to INSTALL.md

## Create a laod
you need to create a load ini file. For that you have examples here load-voip.ini and load-wda.ini

Once you've created your load file
```
wlctl load create -i my-load-voip.ini -o my-load-voip.yml
```

And the yaml load file could look like that:
```
$ cat my-voip-load.yml
loads:
- load:
  - cmd: /usr/local/bin/baresip-wrapper
    env:
      LOGIN: 1000@127.0.0.1
      PASSWORD: my_password
      STACK: 127.0.0.1
  - cmd: /usr/local/bin/baresip-wrapper
    env:
      LOGIN: 1001@127.0.0.1
      PASSWORD: my_password
      STACK: 127.0.0.1
  ttl: 5
- load:
  - cmd: /usr/local/bin/baresip-wrapper
    env:
      LOGIN: 1000@127.0.0.1
      PASSWORD: my_password
      STACK: 127.0.0.1
  - cmd: /usr/local/bin/baresip-wrapper
    env:
      LOGIN: 1001@127.0.0.1
      PASSWORD: my_password
      STACK: 127.0.0.1
  ttl: 5
```
## push the load
Once you've created your load file, you just need to push it
```
wltcl load push -f my-load-voip.yml
```
