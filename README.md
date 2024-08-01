# wazo-load-stack
Load platform to generate traffic over a Wazo stack.

This repository contains 3 different projects

- [wazo_load_api](wazo_load_api/wlapi/README.md)
- [wazo_load_cli](wazo_load_cli/README.md)
- [wazo_load_pilot](wazo_load_pilot/README.md)

# wazo_load_api

This is the REST API that runs on each load test worker. Those API are meant to be used by the pilot with the help of the load balancer that dispatches the jobs between all workers.

# wazo_load_cli

This is a command line interface (CLI) to facilitate the usage of the pilot API. It generates the job definition file and uses the pilot REST API to start a job set.

# wazo_load_pilot

The pilot is the orchestrator that manages the workers and that dispatches the work to all of them. It is the entry point to control the worker fleet.
