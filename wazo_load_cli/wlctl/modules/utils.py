# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import configparser
import os
from typing import Any

import requests
import yaml


def load_config(config_file: str) -> Any:
    """load_config is a function used to easily load a file
    whatever the path is absolute or relative.
    It returns a ConfigParser class instance."""

    config_file_path = os.path.expanduser(config_file)
    config = configparser.ConfigParser()
    config.read(config_file_path)
    return config


def load_yaml_file(file_path: str) -> Any:
    """load_yaml_file loads a valid yaml and returns a dict."""
    config_file_path = os.path.expanduser(file_path)
    with open(config_file_path) as file:
        data = yaml.safe_load(file)
    return data


def send_json(data: dict, url: str) -> None:
    """send_json takes a dictionary and send it to the url as json data."""

    response = requests.post(url, json=data, verify=False)

    if response.status_code == 200:
        print(f"Data succesfully sent to {url}")
    else:
        print("An error occured while sending data.")
        print(f"Status code: {response.status_code}")
        print(f"Message: {response.text}")


def send_query(url: str) -> requests.Response:
    """send a query to the url."""

    response = requests.get(url, verify=False)
    return response


def send_delete(url: str) -> requests.Response:
    """send a delete query to the url."""

    response = requests.delete(url, verify=False)
    return response
