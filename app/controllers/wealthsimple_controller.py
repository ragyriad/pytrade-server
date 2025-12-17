from fastapi import APIRouter, Depends, HTTPException
from starlette.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.services.wealthsimple_service import WealthsimpleService
from app.dependencies import get_wealthsimple_service
from app.database.connection import get_db

router = APIRouter()


@router.post("/login")
async def ws_login(
    username: str,
    password: str,
    otp: str = None,
    db: Session = Depends(get_db),
    service: WealthsimpleService = Depends(get_wealthsimple_service),
):
    try:
        session = await run_in_threadpool(service.login, db, username, password, otp)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/accounts")
async def sync_accounts(
    db: Session = Depends(get_db),
    service: WealthsimpleService = Depends(get_wealthsimple_service),
):
    try:
        return await run_in_threadpool(service.get_accounts, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/balances")
async def ws_account_balances(
    username: str,
    account_id: str,
    db: Session = Depends(get_db),
    service: WealthsimpleService = Depends(get_wealthsimple_service),
):
    try:
        return await run_in_threadpool(
            service.get_account_balances, db, username, account_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/activities")
async def ws_activities(
    username: str,
    account_id: str,
    how_many: int = 50,
    db: Session = Depends(get_db),
    service: WealthsimpleService = Depends(get_wealthsimple_service),
):
    try:
        return await run_in_threadpool(
            service.get_activities, db, username, account_id, how_many
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historical-financials")
async def ws_identity_historical_financials(
    username: str,
    account_ids: str = "",
    currency: str = "CAD",
    db: Session = Depends(get_db),
    service: WealthsimpleService = Depends(get_wealthsimple_service),
):
    try:
        ids = account_ids.split(",") if account_ids else []
        return await run_in_threadpool(
            service.get_identity_historical_financials, db, username, ids, currency
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search-security")
async def ws_search_security(
    username: str,
    query: str,
    db: Session = Depends(get_db),
    service: WealthsimpleService = Depends(get_wealthsimple_service),
):
    try:
        return await run_in_threadpool(service.search_security, db, username, query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/security-market-data")
async def ws_security_market_data(
    username: str,
    security_id: str,
    db: Session = Depends(get_db),
    service: WealthsimpleService = Depends(get_wealthsimple_service),
):
    try:
        return await run_in_threadpool(
            service.get_security_market_data, db, username, security_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/account-historical-financials")
async def ws_account_historical_financials(
    username: str,
    account_id: str,
    currency: str = "CAD",
    db: Session = Depends(get_db),
    service: WealthsimpleService = Depends(get_wealthsimple_service),
):
    try:
        return await run_in_threadpool(
            service.get_account_historical_financials,
            db,
            username,
            account_id,
            currency,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
