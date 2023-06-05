# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import yaml
from ..modules.utils import send_json, load_yaml_file


def test_load_yaml_file(tmpdir):
    """test_load_yaml_file takes one argument: tmpdir.
    tmpdir is a fixture provided by pytest for temporary directory creation."""
    # Create a temporary yaml file for the tests
    data = {'key': 'value'}
    file_path = tmpdir.join("test.yaml")
    file_path.write(yaml.dump(data))

    # Function to test
    result = load_yaml_file(file_path)

    # Result validation
    assert result == data


def test_send_json(requests_mock):
    """test_send_json_file takes one parameter: requests_mock.
    requests_mock is a fixture provided by the requests-mock plugin."""
    data = {"key": "value"}
    url = "https://wazo.load.stack/api"
    
    # Setup the mock requests to intercept all POST at the url destination and return s a 200.
    requests_mock.post(url, status_code=200)
    
    send_json(data, url)
    
    assert requests_mock.called
    assert requests_mock.last_request.url == url
    
    assert isinstance(requests_mock.last_request.json(), str)
    assert requests_mock.last_request.json() == json.dumps(data)
    
