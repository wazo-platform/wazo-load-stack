import pytest

from ..commands import DockerComposeCmdFactory, DockerCmdFactory, SendCmd, ShellCmdFactory
from wazo_load_pilot.plugins.pilot.commands import SendCmd


def test_cmd_send(requests_mock):
    url = "https://example.com/load"
    command = {"cmd": "start"}

    requests_mock.post(f"{url}", json={"response": "success"})
    send_cmd = SendCmd(urls=[url], command=command)

    responses = send_cmd.send()

    for response in responses:
        assert "response" in response
        assert "url" in response
        assert response["response"].status_code == 200

    
class TestDockerComposeCmdFactory:
    @pytest.fixture
    def factory(self):
        compose = "docker-compose.yml"
        container = "my_container"
        servers = ["example.com", "test.com"]
        cmd_tag = "start-fleet"
        return DockerComposeCmdFactory(compose=compose, container=container, servers=servers, cmd_tag=cmd_tag)

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
        expected_command = f'docker exec -e KEY1=value1 -e KEY2=value2 -d {factory.container} bash -c \'{factory.cmd}\''
        assert cmd.command["cmd"] == expected_command


def test_shell_cmd_factory():
        servers = ["example.com", "test.com"]
        cmd = "echo hello"
        factory = ShellCmdFactory(servers=servers, cmd=cmd)
        shell_cmd = factory.new()
        assert isinstance(shell_cmd, SendCmd)
        assert len(shell_cmd.urls) == len(factory.servers)
        assert shell_cmd.command["cmd"] == f"bash -c \'{cmd}\'"
