# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

config = None


def set_dependencies(dependencies: dict) -> None:
    global config
    config = dependencies['config']
