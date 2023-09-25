# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import random
import configparser
from abc import ABC, abstractmethod
from typing import TextIO


class Timer(ABC):
    """Timer is an abstract class which is used mainly to be able to mock
    the timer. A timer is injected into the LoadGenerator class."""

    @abstractmethod
    def get_timer(self, delay):
        pass


class RandomizedTimer(Timer):
    """Concrete class for the timer, which randomizes the delay."""

    def get_timer(self, delay: int = 60) -> int:
        return random.randint(1, delay)


class LoadGenerator:
    """LoadGenerator class aimed to provide load creation file facilities."""

    def __init__(self, load_config: str, load_file: str, timer: Timer) -> None:
        self.timer = timer
        self.config = configparser.ConfigParser()
        self.config.read(load_config)

        # Extract DEFAULT section
        self.debug = int(self.config.get("DEFAULT", "DEBUG", fallback=1))
        self.docker = int(self.config.get("DEFAULT", "DOCKER", fallback=1))
        self.delay_cnx_rand = int(self.config.get("DEFAULT", "DELAY_CNX_RAND"))
        self.ttl = int(self.config.get("DEFAULT", "TTL", fallback=30))
        self.server = self.config.get(
            "DEFAULT", "SERVER", fallback="wazo-5000-1.load.wazo.io"
        )
        self.port = int(self.config.get("DEFAULT", "PORT", fallback=9900))
        self.load_sections = int(
            self.config.get("DEFAULT", "LOAD_SECTIONS", fallback=10)
        )
        self.clients = int(self.config.get("DEFAULT", "CLIENTS", fallback=10))
        self.containers = int(self.config.get("DEFAULT", "CONTAINERS", fallback=100))
        self.request_timeout = int(
            self.config.get("DEFAULT", "REQUEST_TIMEOUT", fallback=300)
        )
        self.disable_header_check = int(
            self.config.get("DEFAULT", "DISABLE_HEADER_CHECK", fallback=1)
        )
        self.trafgen_number = int(
            self.config.get("DEFAULT", "TRAFGEN_NUMBER", fallback=10)
        )
        self.load_files_number = int(
            self.config.get("DEFAULT", "LOAD_FILES_NUMBER", fallback=1)
        )
        self.ext = self.config.get("DEFAULT", "EXT", fallback="@wazo.io")
        self.load_yaml = load_file
        self.cmd = self.config.get(
            "DEFAULT", "CMD", fallback="node /usr/src/app/index.js"
        )
        self.password = self.config.get("DEFAULT", "PASSWORD", fallback="your_password")
        self.tag = self.config.get("DEFAULT", "TAG", fallback="wda-load")
        self.compose = self.config.get(
            "DEFAULT", "COMPOSE", fallback="/etc/trafgen/docker-compose.yml"
        )

        # Extract WDA section
        self.disable_chatd = int(self.config.get("WDA", "DISABLE_CHATD", fallback=1))
        self.duration = int(self.config.get("WDA", "DURATION", fallback=300))
        self.token_expiration = int(
            self.config.get("WDA", "TOKEN_EXPIRATION", fallback=600)
        )

        self.start_user = 1000
        self.track_file = 10000

    def generate_load_files(self) -> None:
        with open(self.load_yaml, "w") as f:
            f.write("loads:\n")
            for _ in range(self.load_sections):
                f.write("  - load:\n")
                self.generate_load_section(f)

    def generate_load_section(self, file: TextIO) -> None:
        for _ in range(self.trafgen_number):
            for _ in range(self.clients):
                self.start_user += 1
                self.track_file += 2
                file.write("    - node:\n")
                file.write(f'      cmd: "{self.cmd}"\n')
                file.write("      env:\n")
                file.write(f"        LOGIN: {self.start_user}{self.ext}\n")
                file.write(f"        PASSWORD: {self.password}\n")
                file.write(f"        SERVER: {self.server}\n")
                file.write(f"        SESSION_DURATION: {self.duration}\n")
                file.write(f"        DEBUG: {self.debug}\n")
                file.write(f"        TOKEN_EXPIRATION: {self.token_expiration}\n")
                file.write(f"        DISABLE_CHATD: {self.disable_chatd}\n")
                file.write(
                    f"        DISABLE_HEADER_CHECK: {self.disable_header_check}\n"
                )
                file.write(f"        REQUEST_TIMEOUT: {self.request_timeout}\n")
                file.write(f"        DOCKER: {self.docker}\n")
        file.write(f"    ttl: {self.ttl}\n")
        file.write(f"    tag: {self.tag}\n")
        file.write(f"    compose: {self.compose}\n")
        file.write("    forever: True\n")
