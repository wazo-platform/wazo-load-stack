import configparser
import os

from typing import Any


def load_config(config_file: str) -> Any:
    config_file_path = os.path.expanduser(config_file)
    config = configparser.ConfigParser()
    config.read(config_file_path)
    return config
