import configparser
import copy
import csv
import os
import random
import sys
from abc import ABC, abstractmethod
from typing import Any

import yaml


def import_csv(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            if len(row) == 4:
                login, sip_password, line, wda_password = row
                yield (login, sip_password, line, wda_password)
            else:
                print(
                    f"line {reader.line_num} doesn't contain required fileds: login password line."
                )


class Timer(ABC):
    @abstractmethod
    def get_timer(self, delay):
        pass


class RandomizedTimer(Timer):
    def get_timer(self, delay: int = 60) -> int:
        return random.randint(1, delay)


class LoadSection(ABC):
    @abstractmethod
    def generate_load_section(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def generate_load_section_with_accounts(self) -> list[dict[str, Any]]:
        pass


class GlobalLoadSection:
    def __init__(self, config: configparser.ConfigParser):
        self.ttl = int(config.get("GLOBAL", "TTL", fallback=5))

    def generate_load_section(self) -> dict[str, Any]:
        return {"ttl": self.ttl}


class SchedulerLoadSection(LoadSection):
    def __init__(self, config: configparser.ConfigParser, timer: Timer):
        self.batch = int(config.get("SCHEDULER", "BATCH"))
        self.duration = int(config.get("SCHEDULER", "DURATION"))
        self.rate = float(config.get("SCHEDULER", "RATE"))
        self.label = config.get("SCHEDULER", "DESCRIPTION")

    def generate_load_section(self) -> list[dict[str, Any]]:
        return [
            {
                "batch": self.batch,
                "duration": self.duration,
                "rate": self.rate,
                "label": self.label,
            }
        ]

    def generate_load_section_with_accounts(self) -> list[dict[str, Any]]:
        return [
            {
                "batch": self.batch,
                "duration": self.duration,
                "rate": self.rate,
                "label": self.label,
            }
        ]


class BareSIPLoadSection(LoadSection):
    def __init__(self, config: configparser.ConfigParser, timer: Timer):
        self.command = config.get("BARESIP", "CMD")
        self.scenario = config.get("BARESIP", "SCENARIO", fallback="registration_only")
        self.start_line = int(config.get("BARESIP", "START_LINE"))
        self.end_line = int(config.get("BARESIP", "END_LINE"))
        self.password = config.get("BARESIP", "PASSWORD", fallback=None)
        self.domain = config.get("BARESIP", "DOMAIN", fallback="example.com")
        self.call_duration = int(config.get("BARESIP", "CALL_DURATION"))
        self.group_call = int(config.get("BARESIP", "GROUP_CALL", fallback=20000))
        self.ttl = int(config.get("BARESIP", "TTL", fallback=30))
        self.load_sections = int(config.get("BARESIP", "LOAD_SECTIONS", fallback=1))
        self.load_jobs = int(config.get("BARESIP", "LOAD_JOBS", fallback=1))
        self.stack = config.get("BARESIP", "STACK")
        self.accounts = config.get("BARESIP", "ACCOUNTS", fallback=None)
        self.debug = config.get("BARESIP", "DEBUG", fallback=False)

    def generate_load_section(self) -> list[dict[str, Any]]:
        loads = []
        line = self.start_line
        for _ in range(self.load_sections):
            jobs = []
            for _ in range(self.load_jobs):
                if not self.password:
                    self.password = str(line)

                load_job = {
                    "cmd": self.command,
                    "env": {
                        "LOGIN": f"{line}@{self.stack}",
                        "LINE": line,
                        "PASSWORD": self.password,
                        "STACK": self.stack,
                        "CALL_DURATION": self.call_duration,
                        "GROUP_CALL": self.group_call,
                        "SCENARIO": self.scenario,
                        "DEBUG": self.debug,
                    },
                }
                if line < self.end_line:
                    line += 1
                else:
                    line = self.start_line
                jobs.append(copy.deepcopy(load_job))
            loads.append({"load": jobs, "ttl": self.ttl})

        return loads

    def generate_load_section_with_accounts(self) -> list[dict[str, Any]]:
        loads = []
        end = False
        logins_passwords = import_csv(self.accounts)
        for _ in range(self.load_sections):
            jobs = []
            for _ in range(self.load_jobs):
                try:
                    login, password, line, _ = next(logins_passwords)
                except StopIteration:
                    end = True
                    break

                load_job = {
                    "cmd": self.command,
                    "env": {
                        "LOGIN": f"{login}@{self.stack}",
                        "LINE": line,
                        "PASSWORD": password,
                        "STACK": self.stack,
                        "CALL_DURATION": self.call_duration,
                        "GROUP_CALL": self.group_call,
                        "SCENARIO": self.scenario,
                        "DEBUG": self.debug,
                    },
                }
                jobs.append(copy.deepcopy(load_job))
            loads.append({"load": jobs, "ttl": self.ttl})
            if end:
                break

        return loads


class WDALoadSection(LoadSection):
    def __init__(self, config: configparser.ConfigParser, timer: Timer):
        try:
            self.timer = timer
            self.ttl = int(config.get("WDA", "TTL", fallback=0))
            self.command = config.get("WDA", "CMD")
            self.job_delay = int(config.get("WDA", "DELAY_CNX_RAND", fallback=60))
            self.user_start = int(config.get("WDA", "USER_START"))
            self.user_end = int(config.get("WDA", "USER_END"))
            self.extension = config.get("WDA", "EXT")
            self.password = config.get("WDA", "PASSWORD", fallback=None)
            self.stack = config.get("WDA", "STACK")
            self.disable_chatd = int(config.get("WDA", "DISABLE_CHATD", fallback=1))
            self.duration = int(config.get("WDA", "DURATION", fallback=300))
            self.token_expiration = int(
                config.get("WDA", "TOKEN_EXPIRATION", fallback=600)
            )
            self.debug = int(config.get("WDA", "DEBUG", fallback=1))
            self.disable_header_check = int(
                config.get("WDA", "DISABLE_HEADER_CHECK", fallback=1)
            )
            self.request_timeout = int(
                config.get("WDA", "REQUEST_TIMEOUT", fallback=3600)
            )
            self.docker = int(config.get("WDA", "DOCKER", fallback=1))
            self.load_sections = int(config.get("WDA", "LOAD_SECTIONS", fallback=1))
            self.load_jobs = int(config.get("WDA", "LOAD_JOBS", fallback=1))
            self.accounts = config.get("WDA", "ACCOUNTS", fallback=None)
        except configparser.NoOptionError as e:
            print(f"error in your configuration file: {e}")
            sys.exit(1)
        self.__section_config_validator()

    def __section_config_validator(self):
        required_params = ["command", "password", "user_start", "user_end"]

        missing_params = [
            param for param in required_params if not getattr(self, param, None)
        ]
        if missing_params:
            print(
                f"The following parameters are mandatory for WDA: {', '.join(missing_params)}"
            )
            sys.exit(1)

    def generate_load_section(self) -> list:
        loads = []
        for _ in range(self.load_sections):
            jobs = []
            user = self.user_start
            for _ in range(self.load_jobs):
                if self.job_delay > 0:
                    delay = self.timer.get_timer(self.job_delay)
                    command = f"sleep {delay} && {self.command}"
                else:
                    command = self.command
                if not self.password:
                    self.password = str(user)

                load_job = {
                    "cmd": command,
                    "env": {
                        "SESSION_DURATION": self.duration,
                        "TOKEN_EXPIRATION": self.token_expiration,
                        "DISABLE_CHATD": self.disable_chatd,
                        "LOGIN": f"{user}@{self.extension}",
                        "PASSWORD": self.password,
                        "SERVER": self.stack,
                        "DEBUG": self.debug,
                        "DISABLE_HEADER_CHECK": self.disable_header_check,
                        "REQUEST_TIMEOUT": self.request_timeout,
                        "DOCKER": self.docker,
                    },
                }
                if user < self.user_end:
                    user += 1
                else:
                    user = self.user_start
                jobs.append(copy.deepcopy(load_job))
            loads.append({"load": jobs, "ttl": self.ttl})

        return loads

    def generate_load_section_with_accounts(self) -> list:
        loads = []
        for _ in range(self.load_sections):
            jobs = []
            end = False
            logins_passwords = import_csv(self.accounts)
            for _ in range(self.load_jobs):
                try:
                    login, password, _, wda_password = next(logins_passwords)
                except StopIteration:
                    end = True
                    break

                if self.job_delay > 0:
                    delay = self.timer.get_timer(self.job_delay)
                    command = f"sleep {delay} && {self.command}"
                else:
                    command = self.command

                load_job = {
                    "cmd": command,
                    "env": {
                        "SESSION_DURATION": self.duration,
                        "TOKEN_EXPIRATION": self.token_expiration,
                        "DISABLE_CHATD": self.disable_chatd,
                        "LOGIN": f"{login}@{self.extension}",
                        "PASSWORD": wda_password,
                        "SERVER": self.stack,
                        "DEBUG": self.debug,
                        "DISABLE_HEADER_CHECK": self.disable_header_check,
                        "REQUEST_TIMEOUT": self.request_timeout,
                        "DOCKER": self.docker,
                    },
                }
                jobs.append(copy.deepcopy(load_job))
            loads.append({"load": jobs, "ttl": self.ttl})
            if end:
                break

        return loads


class Configuration:
    def __init__(self, config_path: str, timer: Timer):
        self.config_path = os.path.abspath(config_path)
        print(self.config_path)
        self.timer = timer
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)
        self.load_sections: list[Any] = []

        if "GLOBAL" in self.config:
            self.global_section = GlobalLoadSection(self.config)

        if "SCHEDULER" in self.config:
            self.scheduler_section = SchedulerLoadSection(self.config, self.timer)

        if "WDA" in self.config:
            self.load_sections.append(WDALoadSection(self.config, self.timer))

        if "BARESIP" in self.config:
            self.load_sections.append(BareSIPLoadSection(self.config, self.timer))
        else:
            print(self.config.sections())

    def get_load_sections(self):
        return self.load_sections

    def get_global_load(self):
        return self.global_section

    def get_scheduler_section(self):
        return self.scheduler_section.generate_load_section().pop()


class LoadGenerator:
    def __init__(self, load_file: str, configuration: Configuration):
        self.load_file = load_file
        self.configuration = configuration

    def generate_load_files(self) -> None:
        scheduler_section = self.configuration.get_scheduler_section()
        load_sections = self.configuration.get_load_sections()

        if not load_sections:
            return

        with open(self.load_file, "w") as f:
            f.write(yaml.dump({"scheduler": scheduler_section}, indent=2, width=1000))
            loads = []
            for load_section in load_sections:
                if load_section.accounts:
                    loads.append(load_section.generate_load_section_with_accounts())
                else:
                    loads.append(load_section.generate_load_section())

            flat_loads = [load for sublist in loads for load in sublist]
            f.write(yaml.dump({"loads": flat_loads}, indent=2, width=1000))
