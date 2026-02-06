from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
import io
from typing import Optional
from ..models.goal import Goal
from ..models.account import Account
from ..models.goal_daily_plan import GoalDailyPlan
from ..models.withdrawal import Withdrawal

# Nota: Las librerías de reportlab y openpyxl se instalarán después
# Por ahora, definimos las funciones que las usarán

def generate_pdf_report(
    db: Session,
    user_id: int,
    goal_id: int,
    lang: str = "en"
) -> bytes:
    """
    Generar reporte PDF del objetivo
    TODO: Implementar con reportlab después de instalar las dependencias
    """
    # Verificar que el objetivo existe y pertenece al usuario
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.account_id == account.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Obtener datos del objetivo
    daily_plans = db.query(GoalDailyPlan).filter(
        GoalDailyPlan.goal_id == goal_id
    ).order_by(GoalDailyPlan.date).all()
    
    withdrawals = db.query(Withdrawal).filter(
        Withdrawal.goal_id == goal_id
    ).order_by(Withdrawal.withdrawn_at).all()
    
    # TODO: Implementar generación de PDF con reportlab
    # Por ahora, retornamos un placeholder
    raise HTTPException(
        status_code=501,
        detail="PDF generation not implemented yet. Install 'reportlab' first."
    )

def generate_excel_report(
    db: Session,
    user_id: int,
    goal_id: int,
    lang: str = "en"
) -> bytes:
    """
    Generar reporte Excel del objetivo
    TODO: Implementar con openpyxl después de instalar las dependencias
    """
    # Verificar que el objetivo existe y pertenece al usuario
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.account_id == account.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Obtener datos del objetivo
    daily_plans = db.query(GoalDailyPlan).filter(
        GoalDailyPlan.goal_id == goal_id
    ).order_by(GoalDailyPlan.date).all()
    
    withdrawals = db.query(Withdrawal).filter(
        Withdrawal.goal_id == goal_id
    ).order_by(Withdrawal.withdrawn_at).all()
    
    # TODO: Implementar generación de Excel con openpyxl
    # Por ahora, retornamos un placeholder
    raise HTTPException(
        status_code=501,
        detail="Excel generation not implemented yet. Install 'openpyxl' first."
    )

def generate_csv_report(
    db: Session,
    user_id: int,
    goal_id: int,
    lang: str = "en"
) -> str:
    """
    Generar reporte CSV del objetivo (sin dependencias externas)
    """
    import csv
    from io import StringIO
    
    # Verificar que el objetivo existe y pertenece al usuario
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.account_id == account.id
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Obtener planes diarios
    daily_plans = db.query(GoalDailyPlan).filter(
        GoalDailyPlan.goal_id == goal_id
    ).order_by(GoalDailyPlan.date).all()
    
    # Crear CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "Date", "Capital Start", "Planned Sessions", "Planned Ops",
        "Actual Sessions", "Actual Ops", "Wins", "Losses", "Draws",
        "Realized PnL", "Status", "Notes"
    ])
    
    # Rows
    for plan in daily_plans:
        writer.writerow([
            plan.date.isoformat(),
            plan.capital_start_of_day,
            plan.planned_sessions,
            plan.planned_ops_total,
            plan.actual_sessions,
            plan.actual_ops,
            plan.wins,
            plan.losses,
            plan.draws,
            plan.realized_pnl,
            plan.status.value,
            plan.notes or ""
        ])
    
    return output.getvalue()