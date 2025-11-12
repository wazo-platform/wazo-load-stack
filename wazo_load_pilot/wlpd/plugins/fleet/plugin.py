# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from .http import router
from .services import set_dependencies


class Plugin:
    def load(self, dependencies: dict):
        api = dependencies['api']

        set_dependencies(dependencies)

        api.include_router(router)
