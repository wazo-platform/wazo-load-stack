# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from abc import ABC, abstractmethod

import httpx


class Command(ABC):
    """Abstract class for command factory"""

    @abstractmethod
    def send(self):
        pass


class SendCmd(Command):
    """Command used to send a command to a load API instance."""

    def __init__(self, urls, command, environment=None):
        self.urls = urls
        self.command = command
        self.environment = environment

    async def send(self):
        responses = []
        payload = {'cmd': self.command, 'env': self.environment}
        print(f"PAYLOAD TO BE SENT ========= {payload}")
        async with httpx.AsyncClient(timeout=60, verify=False) as client:
            for url in self.urls:
                print(f"PAYLOAD TO BE SENT TO THIS URL ==========  {url}")
                response = await client.post(url, json=payload)
                responses.append({"response": response, "url": url})

        return responses


class MockCmd(Command):
    """Command used as a mock command that prints infos."""

    def __init__(self, host, container, cmd, env=None):
        self.container = container

        if env:
            pairs = []
            for key, value in env.items():
                pairs.append(f"-e {key.upper()}={value}")
            self.env = ' '.join(pairs)

        self.command = (
            f'echo docker exec {self.env} -d {self.container} '
            f'bash -c \'{cmd}\' > /dev/null 2>&1 &'
        )
        self.host = host

    def send(self):
        print(f"HOST:      {self.host}")
        print(f"CONTAINER: {self.container}")
        print(f"CMD:       {self.command}")
        print(f"ENV:       {self.env}")


class CommandBuilderFactory(ABC):
    """Abstract class for command factory"""

    @abstractmethod
    def new(self):
        pass


class DockerComposeCmdFactory(CommandBuilderFactory):
    """Factory used to create a DockerComposeStart command."""

    def __init__(self, **kwargs):
        self.compose = kwargs["compose"]
        self.container = kwargs["container"]
        self.servers = kwargs["servers"]
        self.cmd_tag = kwargs["cmd_tag"]
        self.commands = {
            "start-fleet": f"docker-compose -f {self.compose} up -d",
            "stop-fleet": f"docker-compose -f {self.compose} down",
            "restart-fleet": f"docker-compose -f {self.compose} restart",
            "start-container": f"docker-compose -f {self.compose} up -d {self.container}",
            "stop-container": f"docker-compose -f {self.compose} stop {self.container}",
            "restart-container": f"docker-compose -f {self.compose} restart {self.container}",
        }

    def new(self):
        urls = []
        if self.servers:
            for server in self.servers:
                url = f"https://{server}/compose"
                urls.append(url)

        command = {"cmd": self.commands[self.cmd_tag]}
        return SendCmd(urls=urls, command=command)


class DockerCmdFactory(CommandBuilderFactory):
    """Factory used to create a DockerStart command."""

    def __init__(self, **kwargs):
        self.container = kwargs.get("container")
        self.cmd = kwargs.get("cmd")
        self.env = kwargs.get("env")
        self.server = kwargs.get("server")

    def new(self):
        if self.env:
            pairs = []
            for key, value in self.env.items():
                pairs.append(f"-e {key.upper()}={value}")
            env = ' '.join(pairs)

        url = f"https://{self.server}"

        command = {
            "cmd": f'docker exec {env} -d {self.container} bash -c \'{self.cmd}\''
        }
        return SendCmd(urls=[url], command=command)


class ShellCmdFactory(CommandBuilderFactory):
    """Factory used to create a Shell command."""

    def __init__(self, **kwargs):
        try:
            self.cmd = kwargs["cmd"]
        except KeyError:
            self.cmd = None
        try:
            self.env = kwargs["env"]
        except KeyError:
            self.env = None
        try:
            self.cluster = kwargs["cluster"]
        except KeyError:
            self.cluster = None
        try:
            self.protocol = kwargs["protocol"]
        except KeyError:
            self.protocol = 'http'

    def new(self):
        urls = []
        url = f"{self.protocol}://{self.cluster['host']}:{self.cluster['port']}/run"
        print(f"URL IS ============== {url} FROM ShellCmdFactory")
        urls.append(url)

        self.command = f'bash -c \'{self.cmd}\''
        return SendCmd(urls=urls, command=self.command, environment=self.env)
