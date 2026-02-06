def create_user_and_account(client):
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

def test_session_blocks_after_2_losses(client):
    token = create_user_and_account(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    session_response = client.post("/sessions", json={"risk_percent": 2}, headers=headers)
    session_id = session_response.json()["id"]
    
    client.post("/operations", json={
        "session_id": session_id,
        "result": "LOSS",
        "risk_percent": 2,
        "comment": "Test loss 1"
    }, headers=headers)
    
    client.post("/operations", json={
        "session_id": session_id,
        "result": "LOSS",
        "risk_percent": 2,
        "comment": "Test loss 2"
    }, headers=headers)
    
    response = client.post("/operations", json={
        "session_id": session_id,
        "result": "WIN",
        "risk_percent": 2
    }, headers=headers)
    
    assert response.status_code == 403