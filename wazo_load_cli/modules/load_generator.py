import random
import configparser
from abc import ABC, abstractmethod
from typing import TextIO
import yaml
import copy
import hcl
import sys


class Timer(ABC):
    @abstractmethod
    def get_timer(self, delay):
        pass

class RandomizedTimer(Timer):
    def get_timer(self, delay: int = 60) -> int:
        return random.randint(1, delay)

class LoadSection(ABC):
    @abstractmethod
    def generate_load_section(self) -> list:
        pass

class GlobalLoadSection(LoadSection):
    def __init__(self, config: configparser.ConfigParser):
        self.ttl = int(config.get("GLOBAL", "TTL", fallback=5))

    def generate_load_section(self) -> list:
        return {"ttl": self.ttl}


class WDALoadSection(LoadSection):
    def __init__(self, config: configparser.ConfigParser):
        try:
            self.ttl = int(config.get("WDA", "TTL", fallback=30))
            self.command = config.get("WDA", "CMD")
            self.user_start = int(config.get("WDA", "USER_START"))
            self.user_end = int(config.get("WDA", "USER_END"))
            self.extension = config.get("WDA", "EXT")
            self.password = config.get("WDA", "PASSWORD")
            self.stack = config.get("WDA", "STACK")
            self.disable_chatd = int(config.get("WDA", "DISABLE_CHATD", fallback=1))
            self.duration = int(config.get("WDA", "DURATION", fallback=300))
            self.token_expiration = int(config.get("WDA", "TOKEN_EXPIRATION", fallback=600))
            self.debug = int(config.get("WDA", "DEBUG", fallback=1))
            self.disable_header_check = int(config.get("WDA", "DISABLE_HEADER_CHECK", fallback=1))
            self.request_timeout = int(config.get("WDA", "REQUEST_TIMEOUT", fallback=3600))
            self.docker = int(config.get("WDA", "DOCKER", fallback=1))
            self.load_sections = int(config.get("WDA", "LOAD_SECTIONS", fallback=10))
            self.load_jobs = int(config.get("WDA", "LOAD_JOBS", fallback=10))
        except configparser.NoOptionError as e:
            print(f"error in your configuration file: {e}")
            sys.exit(1)
        self.__section_config_validator()


    def __section_config_validator(self):
        required_params = ["command", "password", "user_start", "user_end"]

        missing_params = [param for param in required_params if not getattr(self, param, None)]
        if missing_params:
            print(f"The following parameters are mandatory for WDA: {', '.join(missing_params)}")
            sys.exit(1)

    def generate_load_section(self) -> list:
        loads = []
        for _ in range(self.load_sections):
            jobs = []
            user_start = self.user_start
            for _ in range(self.load_jobs):
                if user_start < self.user_end:
                    user_start += 1
                else:
                    user_start = self.user_start

                load_job = {
                    "node": {
                        "cmd": self.command,
                        "env": {
                            "SESSION_DURATION": self.duration,
                            "TOKEN_EXPIRATION": self.token_expiration,
                            "DISABLE_CHATD": self.disable_chatd,
                            "LOGIN": f"{user_start}{self.extension}",
                            "PASSWORD": self.password,
                            "STACK": self.stack,
                            "DEBUG": self.debug,
                            "DISABLE_HEADER_CHECK": self.disable_header_check,
                            "REQUEST_TIMEOUT": self.request_timeout,
                            "DOCKER": self.docker,
                        }
                    },
                }
                jobs.append(copy.deepcopy(load_job))
            #loads.append(yaml.dump({"load":jobs,"ttl":self.ttl}, indent=2, width=1000))
            loads.append({"load":jobs,"ttl":self.ttl})

        return loads


class Configuration:
    def __init__(self, config_path: str):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        self.load_sections = []
         

        if "GLOBAL" in self.config:
            self.global_section = GlobalLoadSection(self.config)
        
        if "WDA" in self.config:
            self.load_sections.append(WDALoadSection(self.config))
        
        if "BARESIP" in self.config:
            self.load_sections.append(BareSIPLoadSection(self.config))

    def get_load_sections(self):
        return self.load_sections

    def get_global_load(self):
        return self.global_section

class LoadGenerator:
    def __init__(self, load_file: str, timer: Timer, configuration: Configuration):
        self.timer = timer
        self.load_file = load_file
        self.configuration = configuration

    def generate_load_files(self) -> None:
        load_sections = self.configuration.get_load_sections()

        if not load_sections:
            return

        with open(self.load_file, "w") as f:
            loads = []
            for load_section in load_sections:
                loads.append(load_section.generate_load_section())

            flat_loads = [load for sublist in loads for load in sublist]
            f.write(yaml.dump({"loads":flat_loads}, indent=2, width=1000))



