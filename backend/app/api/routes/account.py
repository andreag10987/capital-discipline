from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from ...database import get_db
from ...api.deps import get_current_user
from ...models.user import User
from ...schemas.account import AccountCreate, AccountUpdate, AccountResponse
from ...services.account_service import create_account, get_account, update_account

router = APIRouter(prefix="/account", tags=["account"])

@router.post("", response_model=AccountResponse)
def create_user_account(
    account_data: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    accept_language: str = Header(default="en")
):
    lang = "es" if "es" in accept_language.lower() else "en"
    return create_account(db, current_user.id, account_data, lang)

@router.get("", response_model=AccountResponse)
def get_user_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    accept_language: str = Header(default="en")
):
    lang = "es" if "es" in accept_language.lower() else "en"
    return get_account(db, current_user.id, lang)

@router.put("", response_model=AccountResponse)
def update_user_account(
    account_data: AccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    accept_language: str = Header(default="en")
):
    lang = "es" if "es" in accept_language.lower() else "en"
    return update_account(db, current_user.id, account_data, lang)