from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_champs_vide():
    data={
  "name": "",
  "email": "",
  "password": "",
  "profile": "",
  "update_rate": ""
}
    response = client.post(
        "/register",
        json=data
    )

    assert response.status_code == 422

def test_name_vide():
    data={
  "name": "",
  "email": "test.test@ulb.be",
  "password": "password123",
  "profile": "profile",
  "update_rate": "weekly"
}
    response = client.post(
        "/register",
        json=data
    )

    assert response.status_code == 422

def test_email_vide():
    data={
  "name": "name",
  "email": "",
  "password": "password123",
  "profile": "profile",
  "update_rate": "weekly"
}
    response = client.post(
        "/register",
        json=data
    )

    assert response.status_code == 422

def test_password_vide():
    data={
  "name": "name",
  "email": "test.test@ulb.be",
  "password": "",
  "profile": "profile",
  "update_rate": "weekly"
}
    response = client.post(
        "/register",
        json=data
    )

    assert response.status_code == 422

def test_profile_vide():
    data={
  "name": "name",
  "email": "test.test@ulb.be",
  "password": "password123",
  "profile": "",
  "update_rate": "weekly"
}
    response = client.post(
        "/register",
        json=data
    )

    assert response.status_code == 422

def test_update_rate_vide():
    data={
  "name": "name",
  "email": "test.test@ulb.be",
  "password": "password123",
  "profile": "profile",
  "update_rate": ""
}
    response = client.post(
        "/register",
        json=data
    )

    assert response.status_code == 422

def test_name_manquant():
    data={
  "email": "test.test@ulb.be",
  "password": "password123",
  "profile": "profile",
  "update_rate": "weekly"
}
    response = client.post(
        "/register",
        json=data
    )

    assert response.status_code == 422

def test_email_manquant():
    data={
  "name": "name",
  "password": "password123",
  "profile": "profile",
  "update_rate": "weekly"
}
    response = client.post(
        "/register",
        json=data
    )

    assert response.status_code == 422

def test_password_manquant():
    data={
  "name": "name",
  "email": "test.test@ulb.be",
  "profile": "profile",
  "update_rate": "weekly"
}
    response = client.post(
        "/register",
        json=data
    )

    assert response.status_code == 422

def test_profile_manquant():
    data={
  "name": "name",
  "email": "test.test@ulb.be",
  "password": "password123",
  "update_rate": "weekly"
}
    response = client.post(
        "/register",
        json=data
    )

    assert response.status_code == 422

def test_update_rate_manquant():
    data={
  "name": "name",
  "email": "test.test@ulb.be",
  "password": "password123",
  "profile": "profile"
}
    response = client.post(
        "/register",
        json=data
    )

    assert response.status_code == 422

def test_password():
    data={
  "name": "name",
  "email": "test.test@ulb.be",
  "password": "123",
  "profile": "profile",
  "update_rate": "weekly"
}
    response = client.post(
        "/register",
        json=data
    )

    assert response.status_code == 422

def test_token_creation():
    data={
  "name": "name",
  "email": "data.data@ulb.be",
  "password": "password123",
  "profile": "profile",
  "update_rate": "weekly"
    }
    response = client.post(
        "/register",
        json = data
    )
    assert response.status_code == 200
    


