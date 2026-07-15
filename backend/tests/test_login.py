from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_sucess():
    response = client.post(
        "/login",
        json={
            "email":"test.test@ulb.be",
            "password":"password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"

def test_email_vide():
    response = client.post(
        "/login",
        json={
            "email":"",
            "password":"password123"
        }
    )
    assert response.status_code == 422

def test_password_vide():
    response = client.post(
        "/login",
        json={
            "email":"test.test@ulb.be",
            "password":""
        }
    )
    assert response.status_code == 422

def test_email_manquant():
    response = client.post(
        "/login",
        json={
            "password":"password123"
        }
    )
    assert response.status_code == 422

def test_password_manquant():
    response = client.post(
        "/login",
        json={
            "email":"test.test@ulb.be"
        }
    )
    assert response.status_code == 422

def test_email_inconnu():
    response = client.post(
        "/login",
        json={
            "email":"someone.someone@ulb.be",
            "password":""
        }
    )
    assert response.status_code == 401

def test_email_inconnu():
    response = client.post(
        "/login",
        json={
            "email":"test.test@ulb.be",
            "password":"mauvais_mdp"
        }
    )
    assert response.status_code == 401

