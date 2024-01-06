import docker
import json

class DockerHandles:

    def __init__(self):
        self.client = docker.from_env()

    def run_container_echo(self, image, tag):
        """
        Run a temporary container with the specified image and tag, echoing "Image with labels".

        Args:
        - image (str): The image name.
        - tag (str): The image tag.
        """
        container = self.client.containers.run(f"{image}:{tag}", detach=True, name="temp_container", command="echo 'Image with labels'")
        return container

    def commit_container_with_labels(self, container, image, tag, labels):
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

    def inspect_image_labels(self, image, tag):
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

if __name__ == "__main__":
    registry = DockerHandles()

	# Usage examples :
    
	# 1. Run a temporary container
    container = registry.run_container_echo("wlpd", "1.0.3")

    # 2. Commit the container with labels
    labels = {"maintainer": "amazing-coders@wazo.io"}
    registry.commit_container_with_labels(container, "wlpd", "1.0.3", labels)

    # 3. Remove the temporary container
    container.remove()

    # 4. Inspect the image and retrieve labels
    image_labels = registry.inspect_image_labels("wlpd", "1.0.3")
    print(json.dumps(image_labels, indent=4))
