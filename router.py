from fastapi import APIRouter
from controllers import (
    auth_controller,
    account_controller,
    activity_controller,
    security_controller,
    sync_controller,
    position_controller,
    broker_controller,
    overview_controller,
)

router = APIRouter()

# Auth endpoints
router.include_router(auth_controller.router, prefix="/auth", tags=["Auth"])

# Sync endpoints
router.include_router(sync_controller.router, prefix="/sync", tags=["Sync"])

# Resource endpoints
router.include_router(account_controller.router, prefix="/account", tags=["Account"])
router.include_router(activity_controller.router, prefix="/activity", tags=["Activity"])
router.include_router(security_controller.router, prefix="/security", tags=["Security"])
router.include_router(position_controller.router, prefix="/position", tags=["Position"])
router.include_router(broker_controller.router, prefix="/broker", tags=["Broker"])

# Overview endpoints
router.include_router(overview_controller.router, prefix="/overview", tags=["Overview"])
