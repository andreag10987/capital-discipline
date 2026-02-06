from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import date, timedelta
from io import BytesIO

from ...database import get_db
from ...api.deps import get_current_user
from ...models.user import User
from ...schemas.reports import ReportResponse
from ...services.reports_service import get_reports
from ...middleware.plan_permissions import (
    require_pdf_export,
    require_excel_export,
    get_history_limit
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=ReportResponse)
def get_trading_reports(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    plan_and_limit: tuple = Depends(get_history_limit),  # ← Plan limit
):
    """
    Obtiene reportes de trading.
    Protegido por límite de plan: history_days.
    """
    plan, max_history_days = plan_and_limit
    
    # Limitar días según el plan
    if days > max_history_days:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "plan_limit_reached",
                "message": f"Your plan allows only {max_history_days} days of history. Upgrade to access more.",
                "current_plan": plan.name,
                "limit": max_history_days,
                "requested": days
            }
        )
    
    return get_reports(db, current_user.id, days)


@router.get("/export/pdf")
def export_report_pdf(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _plan = Depends(require_pdf_export),  # ← Requiere plan con PDF export
):
    """
    Exporta reporte en PDF.
    SOLO disponible para plan PRO.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "error": "not_implemented",
            "message": "PDF export will be implemented in next phase. Currently verifying plan permissions only."
        }
    )


@router.get("/export/excel")
def export_report_excel(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _plan = Depends(require_excel_export),  # ← Requiere plan con Excel export
):
    """
    Exporta reporte en Excel.
    SOLO disponible para plan PRO.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "error": "not_implemented",
            "message": "Excel export will be implemented in next phase. Currently verifying plan permissions only."
        }
    )