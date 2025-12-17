from fastapi import APIRouter, Depends, HTTPException
import logging
from ws_api import OTPRequiredException, LoginFailedException

from app.services.wealthsimple_service import WealthsimpleService
from app.services.questrade_service import QuestradeService
from app.dependencies import get_questrade_service, get_wealthsimple_service
from app.schemas.auth import BrokerLoginRequest, BrokerLoginResponse

router = APIRouter()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@router.post("/wealthsimple/login", response_model=BrokerLoginResponse)
async def login_wealthsimple(credentials: BrokerLoginRequest):
    service = WealthsimpleService()
    try:
        tokens = await service.login(
            email=credentials.email,
            password=credentials.password,
            otp=credentials.otp,
        )
        return BrokerLoginResponse(message="Login successful", session_tokens=tokens)
    except OTPRequiredException:
        raise HTTPException(status_code=401, detail="MFA code required")
    except LoginFailedException:
        raise HTTPException(
            status_code=403, detail="Login failed. Invalid credentials."
        )


@router.post("/wealthsimple/refresh-token")
async def refresh_wealthsimple_token(
    service: WealthsimpleService = Depends(get_wealthsimple_service),
):
    try:
        await service.refresh_tokens()
        return {"message": "Wealthsimple token refreshed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/questrade/login")
async def login_questrade(service: QuestradeService = Depends(get_questrade_service)):
    try:
        await service.authenticate()
        return {"message": "Logged in to Questrade"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/questrade/refresh-token")
async def refresh_questrade_token(
    service: QuestradeService = Depends(get_questrade_service),
):
    try:
        await service.refresh_tokens()
        return {"message": "Questrade token refreshed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
