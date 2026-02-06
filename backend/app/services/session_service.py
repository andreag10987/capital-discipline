from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, date
from ..models.account import Account
from ..models.trading_day import TradingDay
from ..models.trading_session import TradingSession
from ..schemas.session import SessionCreate, SessionResponse
from ..utils.messages import get_message
from ..config import settings
import pytz

def get_or_create_trading_day(db: Session, account_id: int, today: date, start_capital: float) -> TradingDay:
    trading_day = db.query(TradingDay).filter(
        TradingDay.account_id == account_id,
        TradingDay.date == today
    ).first()
    
    if not trading_day:
        trading_day = TradingDay(
            account_id=account_id,
            date=today,
            start_capital=start_capital,
            status="active"
        )
        db.add(trading_day)
        db.commit()
        db.refresh(trading_day)
    
    return trading_day

def check_day_unblocked(trading_day: TradingDay) -> bool:
    if trading_day.status == "blocked" and trading_day.blocked_until:
        tz = pytz.timezone(settings.TIMEZONE)
        now = datetime.now(tz)
        blocked_until_aware = trading_day.blocked_until.replace(tzinfo=pytz.UTC).astimezone(tz)
        if now < blocked_until_aware:
            return False
        trading_day.status = "active"
        trading_day.loss_count = 0
        trading_day.drawdown = 0.0
        return True
    return trading_day.status == "active"

def create_session(db: Session, user_id: int, session_data: SessionCreate, lang: str = "en") -> SessionResponse:
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_message("account_not_found", lang)
        )
    
    today = date.today()
    trading_day = get_or_create_trading_day(db, account.id, today, account.capital)
    
    if not check_day_unblocked(trading_day):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=get_message("day_blocked", lang)
        )
    
    session_count = db.query(TradingSession).filter(
        TradingSession.trading_day_id == trading_day.id
    ).count()
    
    if session_count >= 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_message("max_sessions_reached", lang)
        )
    
    new_session = TradingSession(
        trading_day_id=trading_day.id,
        session_number=session_count + 1,
        status="active"
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return SessionResponse.from_orm(new_session)

def get_sessions_today(db: Session, user_id: int) -> list[SessionResponse]:
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        return []
    
    today = date.today()
    trading_day = db.query(TradingDay).filter(
        TradingDay.account_id == account.id,
        TradingDay.date == today
    ).first()
    
    if not trading_day:
        return []
    
    sessions = db.query(TradingSession).filter(
        TradingSession.trading_day_id == trading_day.id
    ).all()
    
    return [SessionResponse.from_orm(s) for s in sessions]