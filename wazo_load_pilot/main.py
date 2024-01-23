#!/usr/bin/env python3
import sys

from config import load_config
from controller import Controller
from xivo.xivo_logging import get_log_level_by_name, setup_logging


def main():
    config = load_config(sys.argv[1:])
    setup_logging(
        config['log_file'], log_level=get_log_level_by_name(config['log_level'])
    )
    controller = Controller(config)
    controller.run()
