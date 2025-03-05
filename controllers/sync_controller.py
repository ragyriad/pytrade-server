from services.questrade_service import sync_with_questrade
from services.wealthsimple_service import sync_wealthsimple_data
from fastapi import HTTPException, APIRouter

router = APIRouter()


@router.get("/{broker}")
async def sync_broker_data(broker: str, db):

    if broker.lower() == "wealthsimple":
        return await sync_wealthsimple_data(db)
    elif broker.lower() == "questrade":
        return await sync_with_questrade(db)
    else:
        raise HTTPException(status_code=400, detail="Unsupported broker")
