# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import requests
from wazo_test_helpers import until

from .helpers import base


@base.use_asset('base')
class TestStatusAllOK(base.BaseIntegrationTest):
    def test_head_status_ok(self):
        port = self.asset_cls.service_port(9990)

        def status_ok():
            url = f'https://127.0.0.1:{port}/status'

            response = requests.get(url, verify=False)

            assert response.status_code == 200

        until.assert_(status_ok, timeout=5)
