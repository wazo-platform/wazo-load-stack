# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import docker
import requests
from .services import docker_registry, docker_registry_port

class DockerRegistry:
    """This is a stateless class, allowing to get it instanciated once at start up."""
    def __init__(self, private_docker_registry=f"{docker_registry}:{docker_registry_port}"):
        self.private_docker_registry = private_docker_registry
        self.client = docker.from_env()

    def list_image_tags(self, image):
        if not image:
            raise ValueError("Error: missing the repository to list")
        response = requests.get(
            f"http://{self.private_docker_registry}/v2/{image}/tags/list",
            headers={"Accept": "application/vnd.docker.distribution.manifest.v2+json"}
        )
        return response.json()

    def get_manifest_id(self, image, tag):
        if not image or not tag:
            raise ValueError("Error while invoking registry-get-manifest-id")
        response = requests.head(
            f"http://{self.private_docker_registry}/v2/{image}/manifests/{tag}",
            headers={"Accept": "application/vnd.docker.distribution.manifest.v2+json"}
        )
        digest_header = response.headers.get('Docker-Content-Digest')
        return digest_header

    def get_manifest(self, image, tag):
        if not image or not tag:
            raise ValueError("Error while invoking registry-get-manifest")
        response = requests.get(
            f"http://{self.private_docker_registry}/v2/{image}/manifests/{tag}",
            headers={"Accept": "application/vnd.docker.distribution.manifest.v2+json"}
        )
        return response.json()

    def get_image_labels(self, image, tag, force=False):
        if self.is_image_present(f"{image}:{tag}"):
            blob = self.client.images.get(image)
            labels = blob.attrs['Config']['Labels']
            return labels
        elif force:
            blob = self.client.images.pull(f"{self.private_docker_registry}/{image}:{tag}")
            labels = blob.attrs['Config']['Labels']
            return labels
        else:
            # by default if the image is not present on the system we don't download it.
            return None

    def registry_push_image(self, image):
        """
        Push an image to a private Docker registry.

        Args:
        - image (str): The image name and tag (e.g., "wlpd:1.0.3").
        """
        if not image:
            raise ValueError("Error: Missing image argument.")
        
        # Tag the image for the private registry
        tagged_image = f"{self.private_docker_registry}/{image}"
        image_obj = self.client.images.get(image)
        image_obj.tag(tagged_image)

        # Push the tagged image to the private registry
        for line in self.client.images.push(repository=tagged_image, stream=True, decode=True):
            print(line.get('status', ''), end='\r')

        print(f"Successfully pushed {tagged_image} to the private Docker registry.")

    def registry_pull_image(self, image):
        """
        Pull an image from a private Docker registry.

        Args:
        - image (str): The image name and tag (e.g., "wlpd:1.0.3").
        """
        if not image:
            raise ValueError("Error: Missing image argument.")
        
        # Pull the image from the private registry
        pulled_image = f"{self.private_docker_registry}/{image}"
        self.client.images.pull(pulled_image)
        
        # Tag the pulled image to remove the private registry part
        image_obj = self.client.images.get(pulled_image)
        image_obj.tag(image)

        print(f"Successfully pulled {pulled_image} and tagged as {image}.")

    def is_image_present(self,image_name):
        local_images = self.client.images.list()

        for img in local_images:
            for tag in img.tags:
                if tag == image_name:
                    return True
        return False

if __name__ == "__main__":
    PRIVATE_DOCKER_REGISTRY = "registry.load.wazo.io:5000"
    registry = DockerRegistry(PRIVATE_DOCKER_REGISTRY)
	#registry = DockerRegistry(private_docker_registry="your_private_docker_registry")
    print(registry.list_image_tags("wlpd"))
    print(registry.get_manifest_id("wlpd", "1.0.3"))
    print(registry.get_manifest("wlpd", "1.0.3"))
    print(registry.get_image_label("wlpd", "1.0.3"))

    #registry.registry_pull_image("wlpd:1.0.3")
	#if __name__ == "__main__":
    #PRIVATE_DOCKER_REGISTRY = "registry.load.wazo.io:5000"
    #registry = DockerRegistry(PRIVATE_DOCKER_REGISTRY)
    #registry.registry_push_image("wlpd:1.0.3")

