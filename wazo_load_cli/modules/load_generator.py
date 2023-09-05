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

        self.debug = int(self.config.get("DEFAULT", "DEBUG", fallback=1))
        self.docker = int(self.config.get("DEFAULT", "DOCKER", fallback=1))
        self.disable_chatd = int(
            self.config.get("DEFAULT", "DISABLE_CHATD", fallback=1)
        )
        self.duration = int(self.config.get("DEFAULT", "DURATION", fallback=300))
        self.token_expiration = int(
            self.config.get("DEFAULT", "TOKEN_EXPIRATION", fallback=600)
        )
        self.delay_cnx_rand = int(self.config.get("DEFAULT", "DELAY_CNX_RAND"))
        self.ttl = int(self.config.get("DEFAULT", "TTL", fallback=30))
        self.server = self.config.get(
            "DEFAULT", "SERVER", fallback="wazo-5000-1.load.wazo.io"
        )
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

        max_clients_per_node = self.load_sections * self.clients
        if max_clients_per_node > self.containers:
            print("Cannot run such amount of clients on", self.containers, "containers")
            exit(1)

        self.start_user = 1000
        self.container_track = 0

    def generate_load_files(self) -> None:
        for load_file_num in range(1, self.load_files_number + 1):
            load_file = f"{self.load_yaml}{load_file_num}"
            with open(load_file, "w") as f:
                f.write("loads:\n")
                for _ in range(self.load_sections):
                    f.write("  - load:\n")
                    self.generate_load_section(f)

    def generate_load_section(self, file: TextIO) -> None:
        host_num = 0
        for _ in range(self.trafgen_number):
            host_num += 1
            host = f"trafgen{host_num}.load.wazo.io"
            container_num = self.container_track
            for _ in range(self.clients):
                container_num += 1
                self.start_user += 1
                file.write("    - node:\n")
                file.write(f"      host: {host}\n")
                file.write(f"      container: wda-load-test{container_num}\n")
                if self.delay_cnx_rand:
                    timer = self.timer.get_timer(self.delay_cnx_rand)
                    file.write(f'      cmd: "sleep {timer} && {self.cmd}"\n')
                else:
                    file.write(f'      cmd: "{self.cmd}"\n')
                file.write("      env:\n")
                file.write(f"        LOGIN: {self.start_user}{self.ext}\n")
                file.write("        PASSWORD: superpass\n")
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
        file.write("    tag: wda-load\n")
        file.write("    compose: /etc/trafgen/Docker-compose.yml\n")
        file.write("    forever: True\n")
        self.container_track = self.container_track + self.clients
