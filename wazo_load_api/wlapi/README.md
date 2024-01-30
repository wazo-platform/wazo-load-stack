# Building and deploying wlapi

## Building a new wlapi image
Move to the wlapi root directory that conatins the makefile
```
cd wazo-load-stack/wazo_load_api
make build
```

By default this will build a new development version of wlapi. It manages
the semver patch by default, so if the previous version was for instance
1.1.3 the version that will be built will be 1.1.4.
If you made minor changes to the image you'll need to explicitly ink it:

```
make build SEMVER=minor
```

By default the built will mark the image with a developpment label:
```
$ registry-get-image-label wlapi 1.1.4
{
  "image_status": "dev",
  "maintainer": "dev@wazo.io"
}
```

You can build your image directly with the prod label:
```
make build IMAGE_STATUS=prod
```
If the pushed image was buggy, please mark it as do_not_use:
```
make build IMAGE_STATUS=do_not_use
```

### Push the built image:
```
make push
```

## Deploying the image
[WIP: docker swarm]
So far it is addressed by a collection of scripts.
