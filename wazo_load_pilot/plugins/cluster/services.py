# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any, Union

from .registry import DockerRegistry

gateways: list[str] = []
cluster: dict[str, Any] = {}
docker_registry: str = ""
docker_registry_port: str = ""
registry_client: Union[DockerRegistry, None] = None
ca_cert: str = ""
client_cert: str = ""
client_key: str = ""


def set_gateways(config: dict[str, Any]) -> None:
    global gateways
    gateways = config['gateways']


def set_cluster(config: dict[str, Any]) -> None:
    global cluster
    cluster = config['load_cluster']


def set_docker_registry(config: dict[str, Any]) -> None:
    global docker_registry
    docker_registry = config['docker']['registry']


def set_docker_registry_port(config: dict[str, Any]) -> None:
    global docker_registry_port
    docker_registry_port = config['docker']['registry_port']


def set_registry() -> None:
    global registry_client
    registry_client = DockerRegistry(f"{docker_registry}:{docker_registry_port}")


def set_certs(config: dict[str, Any]) -> None:
    global ca_cert
    ca_cert = config['docker']['ca_cert']
    global client_cert
    client_cert = config['docker']['client_cert']
    global client_key
    client_key = config['docker']['client_key']
