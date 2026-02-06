import pytest
import bcrypt
from datetime import date
from app.models.user import User
from app.models.account import Account
from app.models.goal import Goal, GoalStatus
from app.models.goal_daily_plan import GoalDailyPlan, DailyPlanStatus


# ── Fixture compartida: usuario + cuenta + token ──────────────────────────
# Depende de test_db y client de conftest.py (se inyectan automáticamente).
# Crea el usuario directamente en la DB de prueba y hace login real
# para obtener un token JWT válido.
@pytest.fixture
def auth_data(test_db, client):
    # Crear usuario (el modelo solo tiene email, no username)
    hashed = bcrypt.hashpw("testpass123".encode(), bcrypt.gensalt()).decode()
    user = User(
        email="testgoals@example.com",
        hashed_password=hashed
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    # Crear cuenta (sin max_daily_loss_percent, no existe en el modelo)
    account = Account(
        user_id=user.id,
        capital=1000.0,
        payout=0.85
    )
    test_db.add(account)
    test_db.commit()
    test_db.refresh(account)

    # Login real → obtener token JWT
    # El schema UserLogin espera "email" y "password"
    response = client.post("/auth/login", json={
        "email": "testgoals@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200, f"Login fallido: {response.json()}"
    token = response.json()["access_token"]

    return {"user": user, "account": account, "token": token}


# ── Helper: headers de autenticación ───────────────────────────────────────
def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ════════════════════════════════════════════════════════════════════════════
# TESTS
# ════════════════════════════════════════════════════════════════════════════

# ── 1. Crear objetivo ──────────────────────────────────────────────────────
def test_create_goal(client, auth_data):
    response = client.post(
        "/goals/",
        headers=_headers(auth_data["token"]),
        json={
            "target_capital": 2000.0,
            "risk_percent": 2,
            "sessions_per_day": 2,
            "ops_per_session": 5,
            "winrate_estimate": 0.65
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["target_capital"] == 2000.0
    assert data["risk_percent"] == 2
    assert data["sessions_per_day"] == 2
    assert data["ops_per_session"] == 5
    assert data["status"] == "ACTIVE"
    assert data["start_capital_snapshot"] == 1000.0
    assert data["payout_snapshot"] == 0.85
    assert "id" in data


# ── 2. Obtener lista de objetivos ─────────────────────────────────────────
def test_get_goals(client, auth_data):
    # Crear objetivo primero
    client.post(
        "/goals/",
        headers=_headers(auth_data["token"]),
        json={
            "target_capital": 2000.0,
            "risk_percent": 2,
            "sessions_per_day": 2,
            "ops_per_session": 5,
            "winrate_estimate": 0.60
        }
    )

    # Obtener lista
    response = client.get("/goals/", headers=_headers(auth_data["token"]))

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["target_capital"] == 2000.0


# ── 3. Obtener progreso del objetivo ──────────────────────────────────────
def test_get_goal_progress(client, auth_data):
    # Crear objetivo
    create_resp = client.post(
        "/goals/",
        headers=_headers(auth_data["token"]),
        json={
            "target_capital": 2000.0,
            "risk_percent": 2,
            "sessions_per_day": 2,
            "ops_per_session": 5,
            "winrate_estimate": 0.60
        }
    )
    assert create_resp.status_code == 201
    goal_id = create_resp.json()["id"]

    # Obtener progreso (endpoint separado con schema GoalProgressResponse)
    response = client.get(
        f"/goals/{goal_id}/progress",
        headers=_headers(auth_data["token"])
    )

    assert response.status_code == 200
    data = response.json()
    # Campos que retorna GoalProgressResponse
    assert "goal" in data
    assert "current_capital" in data
    assert "progress_percent" in data
    assert "days_elapsed" in data
    assert "daily_growth_factor" in data
    # Validar valores iniciales
    assert data["current_capital"] == 1000.0
    assert data["progress_percent"] >= 0


# ── 4. Crear retiro ────────────────────────────────────────────────────────
def test_create_withdrawal(client, auth_data):
    response = client.post(
        "/withdrawals/",
        headers=_headers(auth_data["token"]),
        json={
            "amount": 100.0,
            "note": "Retiro de prueba"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 100.0
    assert data["note"] == "Retiro de prueba"
    assert data["capital_before"] == 1000.0
    assert data["capital_after"] == 900.0


# ── 5. Obtener lista de retiros ────────────────────────────────────────────
def test_get_withdrawals(client, auth_data):
    # Crear retiro primero
    client.post(
        "/withdrawals/",
        headers=_headers(auth_data["token"]),
        json={"amount": 50.0, "note": "Test withdrawal"}
    )

    # Obtener lista
    response = client.get("/withdrawals/", headers=_headers(auth_data["token"]))

    assert response.status_code == 200
    data = response.json()
    assert "withdrawals" in data
    assert "total_withdrawn" in data
    assert "count" in data
    assert data["count"] >= 1
    assert data["total_withdrawn"] >= 50.0


# ── 6. Calendario del objetivo (almanaque) ───────────────────────────────
# Este test crea el objetivo y el plan diario directamente en la DB
# porque necesita datos previos que no se generan por API.
def test_goal_calendar(client, test_db, auth_data):
    account = auth_data["account"]

    # Crear objetivo directamente en DB
    goal = Goal(
        account_id=account.id,
        target_capital=2000.0,
        start_capital_snapshot=1000.0,
        start_date=date.today(),
        payout_snapshot=0.85,
        risk_percent=2,
        sessions_per_day=2,
        ops_per_session=5,
        winrate_estimate=0.60,
        status=GoalStatus.ACTIVE
    )
    test_db.add(goal)
    test_db.commit()
    test_db.refresh(goal)

    # Crear plan diario de prueba
    daily_plan = GoalDailyPlan(
        goal_id=goal.id,
        date=date.today(),
        capital_start_of_day=1000.0,
        planned_sessions=2,
        planned_ops_total=10,
        planned_stake=20.0,
        expected_win_profit=17.0,
        expected_loss=20.0,
        actual_sessions=1,
        actual_ops=5,
        wins=3,
        losses=2,
        draws=0,
        realized_pnl=11.0,
        status=DailyPlanStatus.IN_PROGRESS
    )
    test_db.add(daily_plan)
    test_db.commit()

    # Obtener calendario via API
    response = client.post(
        f"/goals/{goal.id}/calendar",
        headers=_headers(auth_data["token"]),
        json={"days": 30}
    )

    assert response.status_code == 200
    data = response.json()
    assert "daily_plans" in data
    assert "total_days" in data
    assert "total_pnl" in data
    assert "real_winrate" in data
    # Verificar que el plan que creamos aparece
    assert len(data["daily_plans"]) >= 1


# ── 7. Retiro con capital insuficiente ────────────────────────────────────
def test_insufficient_capital_withdrawal(client, auth_data):
    response = client.post(
        "/withdrawals/",
        headers=_headers(auth_data["token"]),
        json={
            "amount": 2000.0,  # Capital es 1000, esto debe fallar
            "note": "Invalid withdrawal"
        }
    )

    assert response.status_code == 400


# ── 8. Generar reporte CSV ─────────────────────────────────────────────────
def test_csv_report_generation(client, test_db, auth_data):
    account = auth_data["account"]

    # Crear objetivo directamente en DB
    goal = Goal(
        account_id=account.id,
        target_capital=2000.0,
        start_capital_snapshot=1000.0,
        start_date=date.today(),
        payout_snapshot=0.85,
        risk_percent=2,
        sessions_per_day=2,
        ops_per_session=5,
        winrate_estimate=0.60,
        status=GoalStatus.ACTIVE
    )
    test_db.add(goal)
    test_db.commit()
    test_db.refresh(goal)

    # Descargar CSV
    response = client.get(
        f"/reports/goals/{goal.id}/csv",
        headers=_headers(auth_data["token"])
    )

    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "Date" in response.text


# ── 9. Actualizar objetivo (pause/resume) ─────────────────────────────────
def test_update_goal_status(client, auth_data):
    # Crear objetivo
    create_resp = client.post(
        "/goals/",
        headers=_headers(auth_data["token"]),
        json={
            "target_capital": 2000.0,
            "risk_percent": 2,
            "sessions_per_day": 2,
            "ops_per_session": 5,
            "winrate_estimate": 0.60
        }
    )
    goal_id = create_resp.json()["id"]

    # Pausar
    response = client.put(
        f"/goals/{goal_id}",
        headers=_headers(auth_data["token"]),
        json={"status": "PAUSED"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "PAUSED"

    # Retomar
    response = client.put(
        f"/goals/{goal_id}",
        headers=_headers(auth_data["token"]),
        json={"status": "ACTIVE"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ACTIVE"


# ── 10. Eliminar objetivo ──────────────────────────────────────────────────
def test_delete_goal(client, auth_data):
    # Crear objetivo
    create_resp = client.post(
        "/goals/",
        headers=_headers(auth_data["token"]),
        json={
            "target_capital": 2000.0,
            "risk_percent": 2,
            "sessions_per_day": 2,
            "ops_per_session": 5,
            "winrate_estimate": 0.60
        }
    )
    goal_id = create_resp.json()["id"]

    # Eliminar
    response = client.delete(
        f"/goals/{goal_id}",
        headers=_headers(auth_data["token"])
    )
    assert response.status_code == 204

    # Verificar que ya no existe
    response = client.get(
        f"/goals/{goal_id}",
        headers=_headers(auth_data["token"])
    )
    assert response.status_code == 404