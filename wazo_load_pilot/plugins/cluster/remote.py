# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import docker


class RemoteDockerClient:
    def __init__(self, base_url: str):
        """
        Initialize the Docker client with a remote URL.

        Args:
        - base_url (str): The base URL of the remote Docker instance ('tcp://<IP_ADDRESS>:<PORT>').
        """
        self.base_url = base_url
        self.client: docker.DockerClient = docker.DockerClient(base_url=self.base_url)

    def list_containers(self) -> list[docker.models.containers.Container]:
        """List all containers on the remote Docker instance."""
        return self.client.containers.list()
