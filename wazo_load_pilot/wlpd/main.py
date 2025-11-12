# Copyright 2023-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import sys

from xivo.xivo_logging import get_log_level_by_name, setup_logging

from .config import load_config
from .controller import Controller


def main():
    config = load_config(sys.argv[1:])
    setup_logging(
        config['log_file'], log_level=get_log_level_by_name(config['log_level'])
    )
    controller = Controller(config)
    controller.run()
