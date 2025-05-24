from services.questrade_service import QuestradeService
from services.wealthsimple_service import WealthsimpleService
from fastapi import HTTPException, APIRouter

router = APIRouter()


@router.get("/{broker}")
async def sync_broker_data(broker: str, db):

    if broker.lower() == "wealthsimple":
        return await WealthsimpleService.sync_wealthsimple_data(db)
    elif broker.lower() == "questrade":
        return await QuestradeService.sync_questrade_data(db)
    else:
        raise HTTPException(status_code=400, detail="Unsupported broker")
