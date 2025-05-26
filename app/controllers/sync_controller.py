from fastapi import HTTPException, APIRouter

from app.services.questrade_service import QuestradeService
from app.services.wealthsimple_service import WealthsimpleService


router = APIRouter()


@router.get("/{broker}")
async def sync_broker_data(broker: str, db):

    if broker.lower() == "wealthsimple":
        return await WealthsimpleService.sync_wealthsimple_data(db)
    elif broker.lower() == "questrade":
        return await QuestradeService.sync_questrade_data(db)
    else:
        raise HTTPException(status_code=400, detail="Unsupported broker")
