# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import configparser
from ..modules.load_generator import LoadGenerator, Timer


class MockTimer(Timer):
    def get_timer(self, delay: int = 60) -> int:
        return 28


def test_generate_load_files(tmpdir, capfd):
    out, err = capfd.readouterr()

    config = configparser.ConfigParser()
    config["DEFAULT"] = {
        "DEBUG": "1",
        "DISABLE_CHATD": "0",
        "DURATION": "300",
        "TOKEN_EXPIRATION": "600",
        "DELAY_CNX_RAND": "60",
        "TTL": "30",
        "SERVER": "router-1.load.wazo.io",
        "LOAD_SECTIONS": "1",
        "CLIENTS": "1",
        "CONTAINERS": "100",
        "REQUEST_TIMEOUT": "300000",
        "DISABLE_HEADER_CHECK": "1",
        "TRAFGEN_NUMBER": "1",
        "LOAD_FILES_NUMBER": "1",
        "EXT": "@wazo.io",
        "CMD": "node /usr/src/app/index.js",
    }

    config_file = tmpdir.join("genwda-load.conf")
    with open(config_file, "w") as f:
        config.write(f)

    os.chdir(tmpdir)

    mock_timer = MockTimer()
    load = LoadGenerator(config_file, "/opt/wda", mock_timer)
    load.generate_load_files()
    load_file = "/opt/wda1"

    expected_content = """loads:
  - load:
    - node:
      host: trafgen1.load.wazo.io
      container: wda-load-test1
      cmd: "sleep 28 && node /usr/src/app/index.js"
      env:
        LOGIN: 1001@wazo.io
        PASSWORD: superpass
        SERVER: router-1.load.wazo.io
        SESSION_DURATION: 300
        DEBUG: 1
        TOKEN_EXPIRATION: 600
        DISABLE_CHATD: 0
        DISABLE_HEADER_CHECK: 1
        REQUEST_TIMEOUT: 300000
        DOCKER: 1
    ttl: 30
    tag: wda-load
    compose: /etc/trafgen/Docker-compose.yml
    forever: True
"""
    with open(load_file) as f:
        content = f.read()
        print(content)
        print(out)
        print(err)
        expected_file = tmpdir.join("expected_content.txt")
        with open(expected_file, "w") as f:
            f.write(expected_content)

        actual_file = tmpdir.join("actual_content.txt")
        with open(actual_file, "w") as f:
            f.write(content)
        # assert content == expected_content
        assert expected_content == content
