from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi import HTTPException, Depends, APIRouter

from schemas.schemas import ActivityResponse, AccountResponse
from database.session import get_db

from services.account_service import AccountService
from repositories.account_respository import AccountRepository
from sqlalchemy.orm import Session

router = APIRouter()
account_service = AccountService(None, AccountRepository())


def get_account_service(db=Depends(get_db)) -> AccountService:
    return AccountService(db)


@router.get("/dividends/total", response_model=float)
async def get_account_dividends_total(
    service: AccountService = Depends(get_account_service),
):
    try:
        return await service.get_total_dividends()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/commissions", response_model=list[ActivityResponse])
async def get_account_commissions(
    service: AccountService = Depends(get_account_service),
):
    try:
        return await service.get_commissions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{account_id}/trades_count", response_model=int)
async def get_account_trades_count(
    service: AccountService = Depends(get_account_service),
):
    try:
        return await service.get_trades_count()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_all", response_model=List[AccountResponse])
async def get_accounts(db: Session = Depends(get_db)):
    return await account_service.get_all_accounts(db)


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account_by_id(account_id: str, db: Session = Depends(get_db)):
    return await account_service.get_account_by_id(db, account_id)
