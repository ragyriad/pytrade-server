from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.database.connection import get_db
from app.repositories.account_respository import AccountRepository
from app.repositories.activity_repository import ActivityRepository
from app.repositories.security_repository import SecurityRepository
from app.repositories.broker_repository import BrokerRepository
from app.services.questrade_service import QuestradeService
from app.services.wealthsimple_service import WealthsimpleService


def get_logger():
    return logging.getLogger("pytrade_api")


def get_account_repository(logger=Depends(get_logger)) -> AccountRepository:
    return AccountRepository(logger=logger)


def get_activity_repository(logger=Depends(get_logger)) -> ActivityRepository:
    return ActivityRepository(logger=logger)


def get_broker_repository(logger=Depends(get_logger)) -> BrokerRepository:
    return BrokerRepository(logger=logger)


def get_security_repository(logger=Depends(get_logger)) -> SecurityRepository:
    return SecurityRepository(logger=logger)


def get_questrade_service(
    account_repo: AccountRepository = Depends(get_account_repository),
    activity_repo: ActivityRepository = Depends(get_activity_repository),
    security_repo: SecurityRepository = Depends(get_security_repository),
    logger=Depends(get_logger),
) -> QuestradeService:
    return QuestradeService(
        account_repo=account_repo,
        activity_repo=activity_repo,
        security_repo=security_repo,
        logger=logger,
    )


def get_wealthsimple_service(
    account_repo: AccountRepository = Depends(get_account_repository),
    activity_repo: ActivityRepository = Depends(get_activity_repository),
    security_repo: SecurityRepository = Depends(get_security_repository),
    logger=Depends(get_logger),
) -> WealthsimpleService:
    return WealthsimpleService(
        account_repo=account_repo,
        activity_repo=activity_repo,
        security_repo=security_repo,
        logger=logger,
    )


def get_db_session(db: AsyncSession = Depends(get_db)):
    return db
