from sqlalchemy.orm import Session
from datetime import date, timedelta
from ..models.account import Account
from ..models.trading_day import TradingDay
from ..models.trading_session import TradingSession
from ..models.operation import Operation, OperationResult
from ..schemas.reports import ReportResponse, DailyMetric

def get_reports(db: Session, user_id: int, days: int) -> ReportResponse:
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        return ReportResponse(
            metrics=[],
            total_operations=0,
            total_profit=0.0,
            total_loss=0.0,
            winrate=0.0,
            avg_drawdown=0.0
        )
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)
    
    trading_days = db.query(TradingDay).filter(
        TradingDay.account_id == account.id,
        TradingDay.date >= start_date,
        TradingDay.date <= end_date
    ).all()
    
    metrics = []
    total_operations = 0
    total_profit = 0.0
    total_loss = 0.0
    total_wins = 0
    total_losses = 0
    total_draws = 0
    total_drawdown = 0.0
    
    for td in trading_days:
        sessions = db.query(TradingSession).filter(
            TradingSession.trading_day_id == td.id
        ).all()
        
        day_profit = 0.0
        day_loss = 0.0
        day_operations = 0
        day_wins = 0
        day_losses = 0
        day_draws = 0
        
        for session in sessions:
            operations = db.query(Operation).filter(
                Operation.session_id == session.id
            ).all()
            
            for op in operations:
                day_operations += 1
                if op.result == OperationResult.WIN:
                    day_wins += 1
                    day_profit += op.profit
                elif op.result == OperationResult.LOSS:
                    day_losses += 1
                    day_loss += abs(op.profit)
                else:
                    day_draws += 1
        
        metrics.append(DailyMetric(
            date=td.date,
            capital=account.capital,
            profit=day_profit,
            loss=day_loss,
            operations=day_operations,
            wins=day_wins,
            losses=day_losses,
            draws=day_draws
        ))
        
        total_operations += day_operations
        total_profit += day_profit
        total_loss += day_loss
        total_wins += day_wins
        total_losses += day_losses
        total_draws += day_draws
        total_drawdown += td.drawdown
    
    winrate = (total_wins / total_operations * 100) if total_operations > 0 else 0.0
    avg_drawdown = (total_drawdown / len(trading_days)) if trading_days else 0.0
    
    return ReportResponse(
        metrics=metrics,
        total_operations=total_operations,
        total_profit=total_profit,
        total_loss=total_loss,
        winrate=winrate,
        avg_drawdown=avg_drawdown
    )