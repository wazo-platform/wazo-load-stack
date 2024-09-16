# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os

import requests

from .helpers import base

TRAFGEN_COUNT = 2


@base.use_asset('vms')
class TestFleetStart(base.VmsIntegrationTest):
    def setUp(self):
        for log_filename in self.list_docker_mock_log_filenames():
            try:
                os.remove(log_filename)
            except FileNotFoundError:
                continue
        super().setUp()

    def test_start_fleet(self):
        port = self.asset_cls.service_port(9990)
        url = f'https://127.0.0.1:{port}/fleet/start'

        response = requests.get(url, verify=False)

        assert response.status_code == 200

        for log_filename in self.list_docker_mock_log_filenames():
            with open(log_filename) as f:
                content = f.read().strip()
                assert (
                    content
                    == '/usr/bin/docker compose -f /etc/trafgen/docker-compose.yml up -d'
                )

    def test_stop_fleet(self):
        port = self.asset_cls.service_port(9990)
        url = f'https://127.0.0.1:{port}/fleet/stop'

        response = requests.get(url, verify=False)

        assert response.status_code == 200

        for log_filename in self.list_docker_mock_log_filenames():
            with open(log_filename) as f:
                content = f.read().strip()
                assert (
                    content
                    == '/usr/bin/docker compose -f /etc/trafgen/docker-compose.yml down'
                )

    def list_docker_mock_log_filenames(self):
        trafgen_log_dir = os.path.join(self.asset_cls.assets_root, 'vms', 'logs')
        for n in range(1, TRAFGEN_COUNT + 1):
            yield os.path.join(trafgen_log_dir, str(n), 'docker-mock.log')
