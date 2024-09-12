# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import requests

from .helpers import base


@base.use_asset('base')
class TestProcessLoad(base.BaseIntegrationTest):
    def test_post_invalid_load(self):
        payload = {'no': 'scheduler'}
        port = self.asset_cls.service_port(9990)
        url = f'https://127.0.0.1:{port}/process-load'

        response = requests.post(url, json=payload, verify=False)

        assert response.status_code == 200  # TODO(pc-m): should be a 400
