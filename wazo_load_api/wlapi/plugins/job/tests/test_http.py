from fastapi.testclient import TestClient
import requests_mock

# import pytest
from ..http import router
from wazo_load_pilot.plugins.pilot.commands import SendCmd

client = TestClient(router)


def test_run_load_success():
    command = {"cmd": "start"}

    with requests_mock.Mocker() as m:
        url = "https://example.com/load"
        m.post(url, json={"status": "ok"})

        send_cmd = SendCmd(urls=[url], command=command)

        responses = send_cmd.send()

    for response in responses:
        assert "response" in response
        assert "url" in response
        assert response["response"].status_code == 200