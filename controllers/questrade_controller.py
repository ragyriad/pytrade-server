from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from services.questrade_service import QuestradeService
from dependencies import get_questrade_service
from database.session import get_db

router = APIRouter()


@router.get("/sync-accounts")
async def sync_accounts(
    db: AsyncSession = Depends(get_db),
    service: QuestradeService = Depends(get_questrade_service),
):
    try:
        return await service.sync_accounts(db)
    except Exception as e:
        import traceback

        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-activities")
async def sync_activities(
    db: AsyncSession = Depends(get_db),
    service: QuestradeService = Depends(get_questrade_service),
):
    return await service.sync_activities(db)


@router.post("/sync-all")
async def sync_all(
    db: AsyncSession = Depends(get_db),
    service: QuestradeService = Depends(get_questrade_service),
):
    return await service.sync_with_questrade(db)
