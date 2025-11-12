# Copyright 2023-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
from unittest.mock import patch

import httpx
import pytest

from ..commands import (
    DockerCmdFactory,
    DockerComposeCmdFactory,
    SendCmd,
    ShellCmdFactory,
)


@patch(
    'wlpd.plugins.pilot.commands.httpx.AsyncClient.post',
    return_value=httpx.Response(200, json={"response": "success"}),
)
def test_cmd_send(async_post_mock):
    loop = asyncio.get_event_loop()
    url = "https://example.com/load"
    command = {"cmd": "start"}
    environ = {"env": "'LOGIN': '1004@example.com'"}

    send_cmd = SendCmd(urls=[url], command=command, environment=environ)

    responses = loop.run_until_complete(send_cmd.send())

    loop.close()

    assert len(responses) == 1
    response = responses[0]
    assert response['response'].status_code == 200
    assert response['url'] == url
    assert response['response'].json() == {'response': 'success'}

    async_post_mock.assert_called_once_with(url, json={'cmd': command, 'env': environ})


class TestDockerComposeCmdFactory:
    @pytest.fixture
    def factory(self):
        compose = "docker-compose.yml"
        container = "my_container"
        servers = ["example.com", "test.com"]
        cmd_tag = "start-fleet"
        return DockerComposeCmdFactory(
            compose=compose, container=container, servers=servers, cmd_tag=cmd_tag
        )

    def test_new(self, factory):
        cmd = factory.new()
        assert isinstance(cmd, SendCmd)
        assert len(cmd.urls) == len(factory.servers)
        assert cmd.command["cmd"] == factory.commands[factory.cmd_tag]


class TestDockerCmdFactory:
    @pytest.fixture
    def factory(self):
        container = "my_container"
        cmd = "start"
        env = {"key1": "value1", "key2": "value2"}
        server = "example.com"
        return DockerCmdFactory(container=container, cmd=cmd, env=env, server=server)

    def test_new(self, factory):
        cmd = factory.new()
        assert isinstance(cmd, SendCmd)
        expected_command = (
            f'docker exec -e KEY1=value1 -e KEY2=value2 -d {factory.container} '
            f'bash -c \'{factory.cmd}\''
        )
        assert cmd.command["cmd"] == expected_command


def test_shell_cmd_factory():
    servers = ["example.com", "test.com"]
    cmd = "echo hello"
    environ = {"env": "'LOGIN': '1004@example.com'"}
    cluster = {'protocol': 'http', 'host': 'load.example.com', 'port': '443'}

    factory = ShellCmdFactory(
        servers=servers, cmd=cmd, environment=environ, cluster=cluster
    )
    shell_cmd = factory.new()
    assert isinstance(shell_cmd, SendCmd)
    assert shell_cmd.command == f'bash -c \'{cmd}\''
