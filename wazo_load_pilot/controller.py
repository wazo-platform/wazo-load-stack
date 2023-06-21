# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import logging

from xivo import plugin_helpers

from http_server import api, SysconfdApplication

logger = logging.getLogger(__name__)


class Controller:
    def __init__(self, config: dict):
        self.config = config
        self.http_server = SysconfdApplication('%(prog)s', config=config)
        plugin_manager = plugin_helpers.load(
            namespace='plugins',
            names=config['enabled_plugins'],
            dependencies={
                'api': api,
                'config': config,
            },
        )
        logger.debug('Loaded plugins:\n%s', plugin_manager.names())
        logger.debug('Loaded routes:\n%s', self.list_routes())

    def list_routes(self) -> list:
        url_list = [{'path': route.path, 'name': route.name} for route in api.routes]
        return url_list

    def run(self):
        logger.info('wazo-load-pilot starting...')
        self.http_server.run()
