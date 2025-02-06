from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from services.account_service import AccountService
from database.schemas import ActivityResponse
from repositories import get_account_service

router = APIRouter()


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


@router.get("/trades/count", response_model=int)
async def get_account_trades_count(
    service: AccountService = Depends(get_account_service),
):
    try:
        return await service.get_trades_count()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
