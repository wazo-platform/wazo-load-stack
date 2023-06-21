# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from abc import ABC, abstractmethod
import requests

class Command(ABC):
    """Abstract class for command factory"""
    @abstractmethod
    def send(self):
        pass

class SendCmd(Command):
    """Command used to send a command to a load API instance."""
    def __init__(self, urls, command):
        self.urls = urls
        self.command = command

    def send(self):
        responses = []
        for url in self.urls:
            response = requests.post(url, json=self.command, verify=False)
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
            self.env =  ' '.join(pairs)
        
        self.command =  f' echo docker exec {self.env} -d {self.container} bash -c \'{cmd}\' > /dev/null 2>&1 &'
        self.host =  host

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
        self.compose = kwargs.get("compose")
        self.container = kwargs.get("container")
        self.servers = kwargs.get("servers")
        self.cmd_tag = kwargs.get("cmd_tag")
        self.commands = {
            "start-fleet": f"docker-compose -f {self.compose} up -d",
            "stop-fleet": f"docker-compose -f {self.compose} down",
            "restart-fleet": f"docker-compose -f {self.compose} restart",
            "start-container": f"docker-compose -f {self.compose} up -d {self.container}",
            "stop-container": f"docker-compose -f {self.compose} stop {self.container}",
            "restart-container": f"docker-compose -f {self.compose} restart {self.container}"
        }


    def new(self):
        urls = []
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
            env =  ' '.join(pairs)

        url = f"https://{self.server}"
        
        command =  {"cmd": f'docker exec {env} -d {self.container} bash -c \'{self.cmd}\''}
        return SendCmd(urls=[url], command=command)

class ShellCmdFactory(CommandBuilderFactory):
    """Factory used to create a ShellStart command."""
    def __init__(self, **kwargs):
        self.cmd = kwargs.get("cmd")
        self.servers = kwargs.get("servers")

    def new(self):

        urls = []
        for server in self.servers:
            url = f"https://{server}/load"
            urls.append(url)
        
        command =  {"cmd": f'bash -c \'{self.cmd}\''}
        return SendCmd(urls=urls, command=command)
