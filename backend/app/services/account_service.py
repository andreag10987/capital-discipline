from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models.account import Account
from ..schemas.account import AccountCreate, AccountUpdate, AccountResponse
from ..utils.messages import get_message

def create_account(db: Session, user_id: int, account_data: AccountCreate, lang: str = "en") -> AccountResponse:
    if account_data.payout < 0.80:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_message("payout_too_low", lang)
        )
    
    existing = db.query(Account).filter(Account.user_id == user_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account already exists"
        )
    
    new_account = Account(
        user_id=user_id,
        capital=account_data.capital,
        payout=account_data.payout
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return AccountResponse.from_orm(new_account)

def get_account(db: Session, user_id: int, lang: str = "en") -> AccountResponse:
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_message("account_not_found", lang)
        )
    return AccountResponse.from_orm(account)

def update_account(db: Session, user_id: int, account_data: AccountUpdate, lang: str = "en") -> AccountResponse:
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=get_message("account_not_found", lang)
        )
    
    if account_data.payout and account_data.payout < 0.80:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=get_message("payout_too_low", lang)
        )
    
    if account_data.capital is not None:
        account.capital = account_data.capital
    if account_data.payout is not None:
        account.payout = account_data.payout
    
    db.commit()
    db.refresh(account)
    return AccountResponse.from_orm(account)