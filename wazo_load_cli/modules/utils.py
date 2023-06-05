import configparser
import json
import os
import requests
import yaml

from typing import Dict, Any


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
    with open(config_file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data


def send_json(data: Dict, url: str) -> None:
    """send_json takes a dictionary and send it to the url as json data."""
    data_json = json.dumps(data)

    response = requests.post(url, json=data_json)

    if response.status_code == 200:
        print(f"Data succesfully sent to {url}")
    else:
        print("An error occured while sending data.")
        print(f"Status code: {response.status_code}")
        print(f"Message: {response.text}")
