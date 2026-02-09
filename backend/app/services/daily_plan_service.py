from datetime import date, timedelta
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models.account import Account
from ..models.goal import Goal, GoalStatus
from ..models.goal_daily_plan import GoalDailyPlan, DailyPlanStatus
from ..models.operation import Operation, OperationResult
from ..models.trading_day import TradingDay
from ..models.trading_session import TradingSession
from ..schemas.daily_plan import DailyPlanResponse, DailyPlanUpdate, DailyPlanCloseRequest, CalendarRangeRequest, CalendarResponse

MAX_GENERATED_DAYS = 730


def create_or_get_daily_plan(
    db: Session,
    goal_id: int,
    plan_date: date,
    capital_start_of_day: float,
) -> GoalDailyPlan:
    """Create or fetch a daily plan for a goal/date."""
    existing = db.query(GoalDailyPlan).filter(
        GoalDailyPlan.goal_id == goal_id,
        GoalDailyPlan.date == plan_date,
    ).first()

    if existing:
        return existing

    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    stake = capital_start_of_day * (goal.risk_percent / 100.0)
    ops_total = goal.sessions_per_day * goal.ops_per_session

    new_plan = GoalDailyPlan(
        goal_id=goal_id,
        date=plan_date,
        capital_start_of_day=capital_start_of_day,
        planned_sessions=goal.sessions_per_day,
        planned_ops_total=ops_total,
        planned_stake=stake,
        expected_win_profit=stake * goal.payout_snapshot,
        expected_loss=stake,
        status=DailyPlanStatus.PLANNED,
    )

    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)

    return new_plan


def update_daily_plan(
    db: Session,
    plan_id: int,
    update_data: DailyPlanUpdate,
) -> GoalDailyPlan:
    """Update actual metrics/state for a daily plan."""
    plan = db.query(GoalDailyPlan).filter(GoalDailyPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Daily plan not found")

    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(plan, field, value)

    db.commit()
    db.refresh(plan)

    return plan


def _build_operation_stats_by_date(db: Session, account_id: int, goal_start: date) -> dict:
    """Group real operation results by date."""
    operations = db.query(Operation, TradingDay.date).join(
        TradingSession, Operation.session_id == TradingSession.id
    ).join(
        TradingDay, TradingSession.trading_day_id == TradingDay.id
    ).filter(
        TradingDay.account_id == account_id,
        TradingDay.date >= goal_start,
    ).all()

    stats = {}
    for op, op_date in operations:
        if op_date not in stats:
            stats[op_date] = {
                "actual_ops": 0,
                "wins": 0,
                "losses": 0,
                "draws": 0,
                "realized_pnl": 0.0,
            }

        day = stats[op_date]
        day["actual_ops"] += 1
        day["realized_pnl"] += float(op.profit or 0.0)

        if op.result == OperationResult.WIN:
            day["wins"] += 1
        elif op.result == OperationResult.LOSS:
            day["losses"] += 1
        else:
            day["draws"] += 1

    return stats


def _build_sessions_count_by_date(db: Session, account_id: int, goal_start: date) -> dict:
    """Count sessions with at least one operation by date."""
    rows = db.query(TradingSession.id, TradingDay.date).join(
        TradingDay, TradingSession.trading_day_id == TradingDay.id
    ).join(
        Operation, Operation.session_id == TradingSession.id
    ).filter(
        TradingDay.account_id == account_id,
        TradingDay.date >= goal_start,
    ).all()

    sessions_by_date = {}
    for session_id, session_date in rows:
        sessions_by_date.setdefault(session_date, set()).add(session_id)

    return {k: len(v) for k, v in sessions_by_date.items()}


def regenerate_goal_calendar(db: Session, goal_id: int) -> None:
    """
    Rebuild goal calendar using:
    - real results for past/current days with operations
    - expected projection for future days
    """
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        return

    account = db.query(Account).filter(Account.id == goal.account_id).first()
    if not account:
        return

    if goal.status not in (GoalStatus.ACTIVE, GoalStatus.PAUSED):
        return

    start_date = goal.start_date or date.today()
    today = date.today()

    op_stats_by_date = _build_operation_stats_by_date(db, account.id, start_date)
    sessions_by_date = _build_sessions_count_by_date(db, account.id, start_date)

    existing_plans = db.query(GoalDailyPlan).filter(
        GoalDailyPlan.goal_id == goal.id,
        GoalDailyPlan.date >= start_date,
    ).all()
    plans_by_date = {p.date: p for p in existing_plans}

    current_date = start_date
    projected_capital = float(goal.start_capital_snapshot or account.capital or 0.0)
    generated_dates = []

    payout = float(goal.payout_snapshot or account.payout or 0.0)
    risk_fraction = float(goal.risk_percent or 0) / 100.0
    ops_total = int((goal.sessions_per_day or 0) * (goal.ops_per_session or 0))
    expected_return_per_op = float(goal.winrate_estimate or 0.0) * payout - (1 - float(goal.winrate_estimate or 0.0))

    for _ in range(MAX_GENERATED_DAYS):
        plan = plans_by_date.get(current_date)
        if not plan:
            plan = GoalDailyPlan(goal_id=goal.id, date=current_date)
            db.add(plan)
            plans_by_date[current_date] = plan

        capital_start = round(projected_capital, 2)
        planned_stake = round(max(capital_start, 0.0) * risk_fraction, 2)
        expected_win_profit = round(planned_stake * payout, 2)
        expected_loss = round(planned_stake, 2)
        expected_daily_pnl = round(planned_stake * ops_total * expected_return_per_op, 2)

        plan.capital_start_of_day = capital_start
        plan.planned_sessions = int(goal.sessions_per_day or 0)
        plan.planned_ops_total = ops_total
        plan.planned_stake = planned_stake
        plan.expected_win_profit = expected_win_profit
        plan.expected_loss = expected_loss

        day_stats = op_stats_by_date.get(current_date)
        if day_stats:
            plan.actual_sessions = sessions_by_date.get(current_date, 0)
            plan.actual_ops = day_stats["actual_ops"]
            plan.wins = day_stats["wins"]
            plan.losses = day_stats["losses"]
            plan.draws = day_stats["draws"]
            plan.realized_pnl = round(day_stats["realized_pnl"], 2)
            plan.status = (
                DailyPlanStatus.COMPLETED
                if plan.actual_ops >= ops_total and ops_total > 0
                else DailyPlanStatus.IN_PROGRESS
            )
            pnl_for_projection = plan.realized_pnl
        else:
            keep_manual_close = current_date <= today and plan.status in (
                DailyPlanStatus.COMPLETED,
                DailyPlanStatus.BLOCKED,
            )

            if keep_manual_close:
                plan.actual_sessions = plan.actual_sessions or 0
                plan.actual_ops = plan.actual_ops or 0
                plan.wins = plan.wins or 0
                plan.losses = plan.losses or 0
                plan.draws = plan.draws or 0
                plan.realized_pnl = round(float(plan.realized_pnl or 0.0), 2)
                pnl_for_projection = plan.realized_pnl
            else:
                plan.actual_sessions = 0
                plan.actual_ops = 0
                plan.wins = 0
                plan.losses = 0
                plan.draws = 0
                plan.realized_pnl = 0.0
                plan.status = DailyPlanStatus.PLANNED
                pnl_for_projection = 0.0 if current_date < today else expected_daily_pnl

        projected_capital = round(capital_start + pnl_for_projection, 2)
        generated_dates.append(current_date)

        if current_date >= today and projected_capital >= float(goal.target_capital):
            break

        if current_date >= today and projected_capital <= 0:
            break

        current_date += timedelta(days=1)

    if generated_dates:
        last_generated = generated_dates[-1]
        stale_plans = db.query(GoalDailyPlan).filter(
            GoalDailyPlan.goal_id == goal.id,
            GoalDailyPlan.date > last_generated,
            GoalDailyPlan.actual_ops == 0,
        ).all()
        for stale in stale_plans:
            db.delete(stale)

    db.commit()


def regenerate_active_goal_calendar_for_account(db: Session, account_id: int) -> None:
    """Recalculate calendar for active goal in account, if any."""
    goal = db.query(Goal).filter(
        Goal.account_id == account_id,
        Goal.status == GoalStatus.ACTIVE,
    ).first()

    if goal:
        regenerate_goal_calendar(db, goal.id)


def get_calendar(
    db: Session,
    user_id: int,
    goal_id: int,
    range_request: Optional[CalendarRangeRequest] = None,
    lang: str = "en",
) -> CalendarResponse:
    """Get goal calendar data."""
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.account_id == account.id,
    ).first()

    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    regenerate_goal_calendar(db, goal.id)

    if range_request and range_request.from_date and range_request.to_date:
        from_date = range_request.from_date
        to_date = range_request.to_date
    elif range_request and range_request.days:
        from_date = date.today()
        to_date = from_date + timedelta(days=range_request.days - 1)
    else:
        from_date = goal.start_date
        latest_plan = db.query(GoalDailyPlan).filter(
            GoalDailyPlan.goal_id == goal.id
        ).order_by(GoalDailyPlan.date.desc()).first()
        to_date = latest_plan.date if latest_plan else date.today()

    daily_plans = db.query(GoalDailyPlan).filter(
        GoalDailyPlan.goal_id == goal_id,
        GoalDailyPlan.date >= from_date,
        GoalDailyPlan.date <= to_date,
    ).order_by(GoalDailyPlan.date).all()

    total_days = len(daily_plans)
    completed_days = sum(1 for p in daily_plans if p.status == DailyPlanStatus.COMPLETED)
    blocked_days = sum(1 for p in daily_plans if p.status == DailyPlanStatus.BLOCKED)
    total_pnl = sum(p.realized_pnl for p in daily_plans)
    total_wins = sum(p.wins for p in daily_plans)
    total_losses = sum(p.losses for p in daily_plans)
    total_draws = sum(p.draws for p in daily_plans)

    total_ops = total_wins + total_losses + total_draws
    real_winrate = total_wins / total_ops if total_ops > 0 else None

    plan_responses = [DailyPlanResponse.from_orm(p) for p in daily_plans]

    return CalendarResponse(
        goal_id=goal_id,
        daily_plans=plan_responses,
        total_days=total_days,
        completed_days=completed_days,
        blocked_days=blocked_days,
        total_pnl=round(total_pnl, 2),
        total_wins=total_wins,
        total_losses=total_losses,
        total_draws=total_draws,
        real_winrate=round(real_winrate, 4) if real_winrate is not None else None,
    )

def close_goal_day(
    db: Session,
    user_id: int,
    goal_id: int,
    close_data: Optional[DailyPlanCloseRequest] = None,
) -> GoalDailyPlan:
    """
    Cierra manualmente un día del calendario del objetivo.
    - Si `blocked_reason` viene informado, el día se marca como BLOCKED.
    - En caso contrario, se marca como COMPLETED.
    """
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.account_id == account.id,
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    regenerate_goal_calendar(db, goal.id)

    target_date = close_data.date if close_data and close_data.date else date.today()
    plan = db.query(GoalDailyPlan).filter(
        GoalDailyPlan.goal_id == goal.id,
        GoalDailyPlan.date == target_date,
    ).first()

    if not plan:
        raise HTTPException(status_code=404, detail="Daily plan not found for selected date")

    if close_data and close_data.notes is not None:
        plan.notes = close_data.notes

    if close_data and close_data.realized_pnl is not None:
        plan.realized_pnl = round(float(close_data.realized_pnl), 2)

    if close_data and close_data.blocked_reason:
        plan.status = DailyPlanStatus.BLOCKED
        plan.blocked_reason = close_data.blocked_reason
    else:
        plan.status = DailyPlanStatus.COMPLETED
        plan.blocked_reason = None

    db.commit()
    regenerate_goal_calendar(db, goal.id)

    updated = db.query(GoalDailyPlan).filter(GoalDailyPlan.id == plan.id).first()
    return updated


def get_daily_plan_by_date(
    db: Session,
    goal_id: int,
    plan_date: date,
) -> Optional[GoalDailyPlan]:
    """Get a daily plan by goal and date."""
    return db.query(GoalDailyPlan).filter(
        GoalDailyPlan.goal_id == goal_id,
        GoalDailyPlan.date == plan_date,
    ).first()
