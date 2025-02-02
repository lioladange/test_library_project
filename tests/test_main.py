import pytest
def test_registration(client):
    data = {"name": "new_user", "email": "user@example.com", "password": "password123"}
    response = client.post("/registration", json=data)
    assert response.status_code == 200
    response_data = response.json()
    assert "id" in response_data
    assert response_data["name"] == "new_user"
    assert response_data["email"] == "user@example.com"
