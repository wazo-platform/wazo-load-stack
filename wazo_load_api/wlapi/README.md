# Building and deploying wlapi

## Building a new wlapi image
The wlapi images can be built using the Dockerfile template
Move to the wlapi root directory that contains the makefile.
Bump the version of the image in the version directory commit and push.
```
cd wazo-load-stack/wazo_load_api
make build-dockerfile
make build-api
```

### Push the built image:
```
docker tag wazocommunicationinc/wlapi:<version> wazocommunicationinc/wlapi:<version>
docker push wazocommunicationinc/wlapi:<version>
```

## Deploying the image
[WIP: docker swarm]
So far it is addressed by a collection of scripts.
