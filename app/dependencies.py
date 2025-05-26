from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.database.connection import get_db
from app.repositories.account_respository import AccountRepository
from app.repositories.broker_repository import BrokerRepository
from app.services.questrade_service import QuestradeService


def get_logger():
    return logging.getLogger("pytrade_api")


def get_account_repository(logger=Depends(get_logger)) -> AccountRepository:
    return AccountRepository(logger=logger)


def get_broker_repository(logger=Depends(get_logger)) -> BrokerRepository:
    return BrokerRepository(logger=logger)


def get_questrade_service(
    account_repo: AccountRepository = Depends(get_account_repository),
    logger=Depends(get_logger),
) -> QuestradeService:
    return QuestradeService(account_repo=account_repo, logger=logger)


def get_db_session(db: AsyncSession = Depends(get_db)):
    return db
