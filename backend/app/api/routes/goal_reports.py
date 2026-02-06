from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
import io
from ...database import get_db
from ...api.deps import get_current_user
from ...models.user import User
from ...services import report_generator_service

router = APIRouter(prefix="/reports/goals", tags=["Goal Reports"])

@router.get("/{goal_id}/pdf")
def download_pdf_report(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    accept_language: str = Query("en", alias="Accept-Language")
):
    """
    Descargar reporte en PDF del objetivo
    
    Incluye:
    - Resumen del objetivo y progreso
    - Tabla de planes diarios
    - Historial de retiros
    - Gráficos de evolución
    
    **Nota:** Requiere instalar 'reportlab'
    """
    pdf_bytes = report_generator_service.generate_pdf_report(
        db, current_user.id, goal_id, accept_language
    )
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=goal_{goal_id}_report.pdf"
        }
    )

@router.get("/{goal_id}/excel")
def download_excel_report(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    accept_language: str = Query("en", alias="Accept-Language")
):
    """
    Descargar reporte en Excel del objetivo
    
    Incluye múltiples hojas:
    - Resumen del objetivo
    - Planes diarios
    - Retiros
    - Métricas calculadas
    
    **Nota:** Requiere instalar 'openpyxl'
    """
    excel_bytes = report_generator_service.generate_excel_report(
        db, current_user.id, goal_id, accept_language
    )
    
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=goal_{goal_id}_report.xlsx"
        }
    )

@router.get("/{goal_id}/csv")
def download_csv_report(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    accept_language: str = Query("en", alias="Accept-Language")
):
    """
    Descargar reporte en CSV del objetivo
    
    Formato simple de planes diarios para análisis en Excel/Google Sheets
    """
    csv_content = report_generator_service.generate_csv_report(
        db, current_user.id, goal_id, accept_language
    )
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=goal_{goal_id}_report.csv"
        }
    )