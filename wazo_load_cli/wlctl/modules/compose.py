import configparser


class ConfigParserIni:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

    def get_config_as_dict(self) -> dict[str, str]:
        if 'COMPOSE' in self.config:
            return dict(self.config['COMPOSE'])
        else:
            raise ValueError("COMPOSE section not found in the configuration file.")


class DockerComposeGenerator:
    def __init__(
        self,
        compose_file: str = "docker-compose.yml",
        image: str = "wazoplatform/wlapi",
        tag: str = "1.1.2",
        start_exposed: int = 9900,
        sip_port: int = 5060,
        media_port: int = 10000,
    ):
        self.compose_file = compose_file
        self.image = image
        self.tag = tag
        self.start_exposed = start_exposed
        self.sip_port = sip_port
        self.media_port = media_port
        self.services: dict = {"services": {}}

    def _generate_service_config(self, x):
        exposed = self.start_exposed + x
        sip_start = self.sip_port
        sip_end = sip_start + 10
        media_start = self.media_port
        media_end = media_start + 40
        image = f"{self.image}:{self.tag}"
        image = ''.join(c for c in image if c not in '"')

        return {
            f"wlapi{x}": {
                "image": image,
                "ulimits": {
                    "core": -1,
                },
                "environment": {
                    "API_PORT": exposed,
                    "SIP_PORTS": f"{sip_start}-{sip_end}",
                    "MEDIA_PORTS": f"{media_start}-{media_end}",
                },
                "container_name": f"wlapi{x}",
                "network_mode": "host",
                "tty": True,
                "volumes": [
                    {
                        "type": "bind",
                        "source": "/etc/resolv.conf",
                        "target": "/etc/resolv.conf",
                    },
                    {
                        "type": "bind",
                        "source": "/opt/voipctl/debug",
                        "target": "/opt/voipctl/debug",
                    },
                    {
                        "type": "bind",
                        "source": f"/opt/wda/logs/{x}.log",
                        "target": "/debug.log",
                    },
                ],
            }
        }

    def _update_services(self, num_services):
        for x in range(num_services):
            self.services["services"].update(self._generate_service_config(x))

    def generate_compose_file(self, num_services=100):
        self._update_services(num_services)

        with open(self.compose_file, 'w') as f:
            f.write("services:\n")
            for service, config in self.services["services"].items():
                f.write(f"  {service}:\n")
                for key, value in config.items():
                    if key == "environment":
                        f.write("    environment:\n")
                        for env_key, env_value in value.items():
                            f.write(f"      - {env_key}={env_value}\n")
                    elif key == "ulimits":
                        f.write("    ulimits:\n")
                        for ulimits_key, ulimits_value in value.items():
                            f.write(f"      {ulimits_key}: {ulimits_value}\n")
                    elif key == "volumes":
                        f.write("    volumes:\n")
                        for volume in value:
                            f.write(f"      - type: {volume['type']}\n")
                            f.write(f"        source: {volume['source']}\n")
                            f.write(f"        target: {volume['target']}\n")
                    else:
                        f.write(f"    {key}: {value}\n")
