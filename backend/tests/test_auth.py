def test_register_success(client):
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "Test1234"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_register_duplicate_email(client):
    client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "Test1234"
    })
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "Test5678"
    })
    assert response.status_code == 409

def test_login_success(client):
    client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "Test1234"
    })
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "Test1234"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()