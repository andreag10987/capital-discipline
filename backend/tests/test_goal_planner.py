def create_user_with_account(client):
    """Helper: crear usuario y cuenta"""
    register_response = client.post("/auth/register", json={
        "email": "goaltest@example.com",
        "password": "Test1234"
    })
    token = register_response.json()["access_token"]
    
    client.post("/account", json={
        "capital": 1000.0,
        "payout": 0.85
    }, headers={"Authorization": f"Bearer {token}"})
    
    return token

def test_create_goal_success(client):
    """Test: Crear objetivo exitosamente"""
    token = create_user_with_account(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/goal-planner/goal", json={
        "target_capital": 5000.0
    }, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["target_capital"] == 5000.0
    assert data["current_capital"] == 1000.0
    assert data["progress_percent"] == 20.0

def test_goal_must_be_greater_than_current(client):
    """Test: Objetivo debe ser mayor al capital actual"""
    token = create_user_with_account(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/goal-planner/goal", json={
        "target_capital": 500.0
    }, headers=headers)
    
    assert response.status_code == 400

def test_calculate_plan_success(client):
    """Test: Calcular plan exitosamente"""
    token = create_user_with_account(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    client.post("/goal-planner/goal", json={
        "target_capital": 2000.0
    }, headers=headers)
    
    response = client.post("/goal-planner/calculate", json={
        "sessions_per_day": 2,
        "ops_per_session": 5,
        "risk_percent": 2,
        "winrate": 0.60
    }, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["stake_per_operation"] == 20.0
    assert data["win_profit"] == 17.0
    assert data["loss_amount"] == 20.0
    assert data["ops_per_day"] == 10
    assert "days_to_goal" in data

def test_payout_warning(client):
    """Test: Warning cuando payout < 0.80"""
    token = create_user_with_account(client)
    headers = {"Authorization": f"Bearer {token}"}
    
    client.put("/account", json={
        "payout": 0.75
    }, headers=headers)
    
    response = client.post("/goal-planner/calculate", json={
        "sessions_per_day": 2,
        "ops_per_session": 5,
        "risk_percent": 2,
        "winrate": 0.60
    }, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["blocked_recommended"] == True
    assert len(data["warnings"]) > 0