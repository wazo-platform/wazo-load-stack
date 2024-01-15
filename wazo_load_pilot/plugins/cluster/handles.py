# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import docker
from docker.models.containers import Container


class DockerHandles:
    def __init__(self):
        self.client = docker.from_env()

    def run_container_echo(self, image: str, tag: str) -> Container:
        """
        Run a temporary container with the specified image and tag, echoing "Image with labels".

        Args:
        - image (str): The image name.
        - tag (str): The image tag.

        Returns:
        - Container: The created container object.
        """
        container = self.client.containers.run(
            f"{image}:{tag}",
            detach=True,
            name="temp_container",
            command="echo 'Image with labels'",
        )
        return container

    def commit_container_with_labels(
        self, container: Container, image: str, tag: str, labels: dict
    ) -> None:
        """
        Commit a container with the given labels.

        Args:
        - container (Container): The container to commit.
        - image (str): The image name.
        - tag (str): The image tag.
        - labels (dict): Dictionary containing the labels to set.
        """
        # Commit the container with the provided labels
        result = ' '.join([f"{key}={value}" for key, value in labels.items()])
        container.commit(repository=f"{image}:{tag}", changes=f"LABEL {result}")

    def inspect_image_labels(self, image: str, tag: str) -> dict:
        """
        Inspect an image and retrieve its labels.

        Args:
        - image (str): The image name.
        - tag (str): The image tag.

        Returns:
        - dict: Dictionary containing the labels of the image.
        """
        image_obj = self.client.images.get(f"{image}:{tag}")
        inspect_data = image_obj.attrs['Config']['Labels']
        return inspect_data
