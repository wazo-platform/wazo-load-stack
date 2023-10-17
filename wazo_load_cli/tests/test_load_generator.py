# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import configparser
import os
from ..modules.load_generator import Configuration, LoadGenerator, Timer


class MockTimer(Timer):
    def get_timer(self, delay: int = 28) -> int:
        return delay


def test_generate_load_files(tmpdir, capfd):
    print("Test is running")
    config = configparser.ConfigParser()
    config["WDA"] = {
        "LOAD_SECTIONS": "1",
        "LOAD_JOBS": "1",
        "DISABLE_CHATD": "0",
        "DURATION": "300",
        "TOKEN_EXPIRATION": "600",
        "DEBUG": "1",
        "DELAY_CNX_RAND": "28",
        "STACK": "router-1.load.wazo.io",
        "REQUEST_TIMEOUT": "300000",
        "DISABLE_HEADER_CHECK": "1",
        "EXT": "wazo.io",
        "CMD": "node /usr/src/app/index.js",
        "PASSWORD": "my_password",
        "USER_START": "1000",
        "USER_END": "6000",
        "TTL": "5",
    }
    config_file = tmpdir.join("genwda-load.conf")
    with open(config_file, "w") as f:
        config.write(f)

    os.chdir(tmpdir)

    timer = MockTimer()
    configuration = Configuration(config_file, timer)
    load = LoadGenerator("wda", configuration)
    load.generate_load_files()

    expected_content = """loads:
- load:
  - cmd: sleep 28 && node /usr/src/app/index.js
    env:
      DEBUG: 1
      DISABLE_CHATD: 0
      DISABLE_HEADER_CHECK: 1
      DOCKER: 1
      LOGIN: 1000@wazo.io
      PASSWORD: my_password
      REQUEST_TIMEOUT: 300000
      SERVER: router-1.load.wazo.io
      SESSION_DURATION: 300
      TOKEN_EXPIRATION: 600
  ttl: 5
"""

    load_file = "wda"
    with open(load_file) as f:
        content = f.read()
        print(content)
        expected_file = tmpdir.join("expected_content.txt")
    with open(expected_file, "w") as f:
        f.write(expected_content)

    actual_file = tmpdir.join("actual_content.txt")
    with open(actual_file, "w") as f:
        f.write(content)
    assert expected_content == content
