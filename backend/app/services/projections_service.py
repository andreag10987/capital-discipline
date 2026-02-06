from sqlalchemy.orm import Session
from ..models.account import Account
from ..schemas.reports import ProjectionResponse

def get_projections(db: Session, user_id: int, days: int) -> ProjectionResponse:
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        return ProjectionResponse(
            days=days,
            estimated_capital=0.0,
            estimated_profit=0.0,
            scenario="conservative"
        )
    
    winrate = 0.60
    risk_percent = 2.0
    operations_per_day = 5
    
    current_capital = account.capital
    estimated_capital = current_capital
    
    for _ in range(days):
        for _ in range(operations_per_day):
            amount = estimated_capital * (risk_percent / 100.0)
            profit = amount * account.payout * winrate
            loss = amount * (1 - winrate)
            estimated_capital += profit - loss
    
    estimated_profit = estimated_capital - current_capital
    
    return ProjectionResponse(
        days=days,
        estimated_capital=round(estimated_capital, 2),
        estimated_profit=round(estimated_profit, 2),
        scenario="conservative"
    )