# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from .registry import DockerRegistry

gateways = []
cluster = {}
docker_registry = ""
docker_registry_port = ""
registry_client = None
ca_cert = ""
client_cert = ""
client_key = ""



def set_gateways(config):
    global gateways
    gateways = config['gateways']


def set_cluster(config):
    global cluster
    cluster = config['load_cluster']

def set_docker_registry(config):
    global docker_registry
    docker_registry = config['docker']['registry']

def set_docker_registry_port(config):
    global docker_registry_port
    docker_registry_port = config['docker']['registry_port']

def set_registry():
    global registry_client
    registry_client = DockerRegistry(f"{docker_registry}:{docker_registry_port}")

def set_certs(config):
    global ca_cert
    ca_cert = config['docker']['ca_cert']
    global client_cert
    client_cert = config['docker']['client_cert']
    global client_key
    client_key = config['docker']['client_key']
