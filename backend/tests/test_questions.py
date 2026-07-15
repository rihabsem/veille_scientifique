from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_token():

    response = client.post(
        "/login",
        json={
            "email": "test.test@ulb.be",
            "password": "password123"
        }
    )
    return response.json()["access_token"]

def test_qst1_vide():
    token = get_token()
    response = client.post(
        "/set-results",
        headers={
            "Authorization":f"Bearer {token}"
        },
        json={
            "qst1":"",
            "qst2":"qst",
            "qst3":"qst"
        }
    )
    assert response.status_code == 422

def test_qst2_vide():
    token = get_token()
    response = client.post(
        "/set-results",
        headers={
            "Authorization":f"Bearer {token}"
        },
        json={
            "qst1":"qst",
            "qst2":"",
            "qst3":"qst"
        }
    )
    assert response.status_code == 422

def test_qst3_vide():
    token = get_token()
    response = client.post(
        "/set-results",
        headers={
            "Authorization":f"Bearer {token}"
        },
        json={
            "qst1":"qst",
            "qst2":"qst",
            "qst3":""
        }
    )
    assert response.status_code == 422

def test_qst1_manquant():
    token = get_token()
    response = client.post(
        "/set-results",
        headers={
            "Authorization":f"Bearer {token}"
        },
        json={
            "qst2":"qst",
            "qst3":"qst"
        }
    )
    assert response.status_code == 422

def test_qst2_manquant():
    token = get_token()
    response = client.post(
        "/set-results",
        headers={
            "Authorization":f"Bearer {token}"
        },
        json={
            "qst1":"qst",
            "qst3":"qst"
        }
    )
    assert response.status_code == 422

def test_qst3_manquant():
    token = get_token()
    response = client.post(
        "/set-results",
        headers={
            "Authorization":f"Bearer {token}"
        },
        json={
            "qst1":"qst",
            "qst2":"qst"
        }
    )
    assert response.status_code == 422
