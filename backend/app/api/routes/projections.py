from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ...database import get_db
from ...api.deps import get_current_user
from ...models.user import User
from ...schemas.reports import ProjectionResponse
from ...services.projections_service import get_projections

router = APIRouter(prefix="/projections", tags=["projections"])

@router.get("", response_model=ProjectionResponse)
def get_capital_projections(
    days: int = Query(15, ge=1, le=60),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_projections(db, current_user.id, days)