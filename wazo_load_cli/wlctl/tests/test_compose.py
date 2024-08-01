import os
import unittest

from wlctl.modules.compose import DockerComposeGenerator


class TestDockerComposeGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = DockerComposeGenerator(compose_file="test-docker-compose.yml")

    def tearDown(self):
        if os.path.exists("test-docker-compose.yml"):
            os.remove("test-docker-compose.yml")

    def test_generate_service_config(self):
        config = self.generator._generate_service_config(0)
        self.assertIn("wlapi0", config)

    def test_update_services(self):
        self.generator._update_services(2)
        self.assertEqual(len(self.generator.services["services"]), 2)
        self.assertIn("wlapi0", self.generator.services["services"])
        self.assertIn("wlapi1", self.generator.services["services"])

    def test_generate_compose_file(self):
        self.generator.generate_compose_file(2)
        self.assertTrue(os.path.exists("test-docker-compose.yml"))
        with open("test-docker-compose.yml") as f:
            content = f.read()
            self.assertIn("wlapi0:", content)
            self.assertIn("wlapi1:", content)
            self.assertIn("API_PORT", content)
            self.assertIn("SIP_PORTS", content)
            self.assertIn("MEDIA_PORTS", content)
            self.assertIn("/etc/resolv.conf", content)
            self.assertIn("/debug.log", content)
