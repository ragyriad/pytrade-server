from datetime import datetime, timezone
import traceback
import asyncio
from fastapi import APIRouter, HTTPException, Depends, status, Body
from pydantic import BaseModel
from typing import Optional, List, Dict

# Assuming SQLAlchemy setup
from sqlalchemy.orm import Session
from database.connection import get_db

# Import your models and schemas
from database.models import (
    Account,
    Activity,
    Security,
    Position,
    Deposit,
)
from database.schemas import (
    ActivityCreate,
    SecurityCreate,
    AccountCreate,
    DepositCreate,
    ActivityResponse,
    SecurityResponse,
    AccountResponse,
    DepositResponse,
)

# Other necessary imports
from .wealthsimple.wealthSimple import wealthSimple
from .wealthsimple.redis_cache import (
    get_instance_cache,
    set_instance_cache,
    del_instance_cache,
)
from errors import LoginError, WSOTPError, AppError
from helpers.helpers import safeBulkCreate, clean_fetch_activities_data

router = APIRouter()


# Pydantic models for requests/responses
class MFACode(BaseModel):
    code: str


class SyncResponse(BaseModel):
    count: int
    message: Optional[str] = None


# Exception handlers
async def http_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.detail})


async def generic_exception_handler(request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "detail": str(exc),
            "traceback": traceback.format_exc(),
        },
    )


# Dependency for WS connection
async def get_ws_connection(
    session_id: Optional[str] = None, mfa_code: Optional[str] = None
):
    instance = get_instance_cache(session_id)
    if not instance:
        wsimple_config = load_wsimple_config()  # Implement config loading
        new_instance = wealthSimple(
            email=wsimple_config["email"],
            password=wsimple_config["password"],
            mfa_code=mfa_code,
        )
        set_instance_cache(
            new_instance.box.access_token, new_instance, new_instance.box.access_expires
        )
        return new_instance
    return instance


@router.post("/login", response_model=Dict[str, str])
async def login(mfa_code: MFACode):
    try:
        ws_instance = await get_ws_connection(mfa_code=mfa_code.code)
        return {
            "access_token": ws_instance.box.access_token,
            "refresh_token": ws_instance.box.refresh_token,
            "expires_at": ws_instance.box.access_expires.isoformat(),
        }
    except (LoginError, WSOTPError) as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/sync/securities", response_model=SyncResponse)
async def sync_securities(db: Session = Depends(get_db)):
    try:
        ws_instance = await get_ws_connection()
        securities_data = ws_instance.get_securities()

        securities = [SecurityCreate(**security) for security in securities_data]
        count = safeBulkCreate(
            db, Security, securities, SECURITY_UNIQUE_FIELD, SECURITY_UPDATE_FIELDS
        )

        return {"count": count, "message": "Securities synchronized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sync/activities", response_model=SyncResponse)
async def sync_activities(db: Session = Depends(get_db)):
    try:
        ws_instance = await get_ws_connection()
        activities_data = await fetch_activities_async(ws_instance)

        activities, securities = clean_fetch_activities_data(activities_data)
        safeBulkCreate(
            db, Security, securities, SECURITY_UNIQUE_FIELD, SECURITY_UPDATE_FIELDS
        )
        count = safeBulkCreate(
            db, Activity, activities, ACTIVITY_UNIQUE_FIELD, ACTIVITY_UPDATE_FIELDS
        )

        return {"count": count, "message": "Activities synchronized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def fetch_activities_async(ws_instance):
    tasks = []
    for activity_type in WEALTHSIMPLE_ACTIVITIES_TYPES:
        if activity_type != "all":
            tasks.append(
                ws_instance.get_activities({"limit": 99, "type": activity_type})
            )
    return await asyncio.gather(*tasks)


# Add similar endpoints for positions, accounts, deposits, etc.


# Exception handling setup
def add_exception_handlers(app):
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
