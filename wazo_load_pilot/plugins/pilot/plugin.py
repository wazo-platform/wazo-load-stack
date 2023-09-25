# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from .http import router
from .services import set_gateways, set_cluster


class Plugin:
    def load(self, dependencies: dict):
        api = dependencies['api']
        config = dependencies['config']
        set_gateways(config)
        set_cluster(config)
        api.include_router(router)
