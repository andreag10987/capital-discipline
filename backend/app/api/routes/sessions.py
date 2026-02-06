from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from ...database import get_db
from ...api.deps import get_current_user
from ...models.user import User
from ...models.account import Account
from ...models.trading_day import TradingDay
from ...models.trading_session import TradingSession
from ...schemas.session import SessionCreate, SessionResponse
from ...services.session_service import create_session, get_sessions_today
from ...middleware.plan_permissions import get_session_limit

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse)
def create_trading_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    accept_language: str = Header(default="en"),
    plan_and_limit: tuple = Depends(get_session_limit),  # ← Plan limit
):
    """
    Crea una nueva sesión de trading.
    Protegido por límite de plan: max_daily_sessions.
    """
    plan, max_sessions = plan_and_limit
    lang = "es" if "es" in accept_language.lower() else "en"
    
    # Verificar límite del plan
    account = db.query(Account).filter(Account.user_id == current_user.id).first()
    if account:
        today = date.today()
        trading_day = db.query(TradingDay).filter(
            TradingDay.account_id == account.id,
            TradingDay.date == today
        ).first()
        
        if trading_day:
            session_count = db.query(TradingSession).filter(
                TradingSession.trading_day_id == trading_day.id
            ).count()
            
            if session_count >= max_sessions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "plan_limit_reached",
                        "message": f"Maximum daily sessions ({max_sessions}) reached. Upgrade your plan for more sessions.",
                        "current_plan": plan.name,
                        "limit": max_sessions
                    }
                )
    
    return create_session(db, current_user.id, session_data, lang)


@router.get("", response_model=List[SessionResponse])
def get_today_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene las sesiones de hoy del usuario."""
    return get_sessions_today(db, current_user.id)