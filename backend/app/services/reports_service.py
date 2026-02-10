from sqlalchemy import case, func
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
    
    aggregated_days = (
        db.query(
            TradingDay.date.label("date"),
            TradingDay.drawdown.label("drawdown"),
            func.coalesce(
                func.sum(
                    case((Operation.result == OperationResult.WIN, Operation.profit), else_=0.0)
                ),
                0.0,
            ).label("day_profit"),
            func.coalesce(
                func.sum(
                    case((Operation.result == OperationResult.LOSS, -Operation.profit), else_=0.0)
                ),
                0.0,
            ).label("day_loss"),
            func.coalesce(func.count(Operation.id), 0).label("day_operations"),
            func.coalesce(
                func.sum(case((Operation.result == OperationResult.WIN, 1), else_=0)),
                0,
            ).label("day_wins"),
            func.coalesce(
                func.sum(case((Operation.result == OperationResult.LOSS, 1), else_=0)),
                0,
            ).label("day_losses"),
            func.coalesce(
                func.sum(case((Operation.result == OperationResult.DRAW, 1), else_=0)),
                0,
            ).label("day_draws"),
        )
        .outerjoin(TradingSession, TradingSession.trading_day_id == TradingDay.id)
        .outerjoin(Operation, Operation.session_id == TradingSession.id)
        .filter(
            TradingDay.account_id == account.id,
            TradingDay.date >= start_date,
            TradingDay.date <= end_date,
        )
        .group_by(TradingDay.id, TradingDay.date, TradingDay.drawdown)
        .order_by(TradingDay.date.asc())
        .all()
    )

    metrics = []
    total_operations = 0
    total_profit = 0.0
    total_loss = 0.0
    total_wins = 0
    total_drawdown = 0.0

    for row in aggregated_days:
        day_profit = float(row.day_profit or 0.0)
        day_loss = float(row.day_loss or 0.0)
        day_operations = int(row.day_operations or 0)
        day_wins = int(row.day_wins or 0)
        day_losses = int(row.day_losses or 0)
        day_draws = int(row.day_draws or 0)

        metrics.append(
            DailyMetric(
                date=row.date,
                capital=float(account.capital),
                profit=day_profit,
                loss=day_loss,
                operations=day_operations,
                wins=day_wins,
                losses=day_losses,
                draws=day_draws,
            )
        )

        total_operations += day_operations
        total_profit += day_profit
        total_loss += day_loss
        total_wins += day_wins
        total_drawdown += float(row.drawdown or 0.0)

    winrate = (total_wins / total_operations * 100) if total_operations > 0 else 0.0
    avg_drawdown = (total_drawdown / len(aggregated_days)) if aggregated_days else 0.0
    
    return ReportResponse(
        metrics=metrics,
        total_operations=total_operations,
        total_profit=total_profit,
        total_loss=total_loss,
        winrate=winrate,
        avg_drawdown=avg_drawdown
    )
