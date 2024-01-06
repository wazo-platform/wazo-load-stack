import docker

from .services import ca_cert, client_cert, client_key

class RemoteDockerClient:
    def __init__(self, base_url, tls_ca_cert=ca_cert, tls_cert=client_cert, tls_key=client_key):
        """
        Initialize the Docker client with a remote URL and TLS parameters.

        Args:
        - base_url (str): The base URL of the remote Docker instance (e.g., 'tcp://<IP_ADDRESS>:<PORT>').
        - tls_ca_cert (str): Path to the CA certificate file.
        - tls_cert (str): Path to the client certificate file.
        - tls_key (str): Path to the client key file.
        """
        tls_config = None
        if tls_ca_cert and tls_cert and tls_key:
            tls_config = docker.tls.TLSConfig(
                client_cert=(tls_cert, tls_key),
                ca_cert=tls_ca_cert,
                verify=True
            )

        self.client = docker.DockerClient(base_url=base_url, tls=tls_config)

    def list_containers(self):
        """List all containers on the remote Docker instance."""
        return self.client.containers.list()


if __name__ == "__main__":
    remote_client = RemoteDockerClient(base_url='tcp://127.0.0.1:2375')
    
    # Docker ps on a remote host.
    containers = remote_client.list_containers()
    for container in containers:
        print(container.id, container.name)