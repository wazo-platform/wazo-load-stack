from fastapi.testclient import TestClient
import requests_mock
#import pytest
from ..http import router  # Remplacez "your_module" par le nom de votre module contenant la classe et le router

from wazo_load_pilot.plugins.pilot.commands import SendCmd

# Créer un client de test pour le routeur
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

# def test_run_load_internal_error(requests_mock):
#    url = "https://example.com/load"
#    command = {"invalid_key": "start"}  # Provoquer une KeyError

#    # Configurer requests_mock pour simuler la réponse
#    requests_mock.post(url, json={"response": "success"})

#    # Envoyer la requête au endpoint "run"
#    response = client.post("/run", json=command)

#    # Assurer que la réponse a un statut HTTP 200 et que le contenu est conforme à une erreur interne
#    assert response.status_code == 200
#    assert response.json() == {"status": "internal_error", "error": "'cmd'"}

#    # Assurer que la clé d'erreur "cmd" est présente dans la réponse JSON

#def test_run_load_exception(requests_mock):
#    url = "https://example.com/load"
#    command = {"cmd": "start"}

#    # Configurer requests_mock pour simuler une exception lors de l'appel
#    requests_mock.post(url, exc=Exception("Simulated exception"))

#    # Envoyer la requête au endpoint "run"
#    response = client.post("/run", json=command)

#    # Assurer que la réponse a un statut HTTP 200 et que le contenu est conforme à une erreur interne
#    assert response.status_code == 200
#    assert response.json() == {"status": "internal_error", "error": "Simulated exception"}
