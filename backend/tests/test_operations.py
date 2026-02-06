def create_authenticated_user(client):
    register_response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "Test1234"
    })
    token = register_response.json()["access_token"]
    
    client.post("/account", json={
        "capital": 1000.0,
        "payout": 0.85
    }, headers={"Authorization": f"Bearer {token}"})
    
    return token

def test_create_operation_win(client):
    token = create_authenticated_user(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    session_response = client.post("/sessions", json={"risk_percent": 2}, headers=headers)
    session_id = session_response.json()["id"]
    
    response = client.post("/operations", json={
        "session_id": session_id,
        "result": "WIN",
        "risk_percent": 2
    }, headers=headers)
    
    assert response.status_code == 200
    assert response.json()["result"] == "WIN"
    assert response.json()["profit"] > 0