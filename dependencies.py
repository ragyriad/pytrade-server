from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from repositories.account_respository import AccountRepository
from services.questrade_service import QuestradeService
import logging


def get_logger():
    return logging.getLogger("pytrade_api")


def get_account_repository(logger=Depends(get_logger)) -> AccountRepository:
    return AccountRepository(logger=logger)


def get_questrade_service(
    account_repo: AccountRepository = Depends(get_account_repository),
    logger=Depends(get_logger),
) -> QuestradeService:
    return QuestradeService(account_repo=account_repo, logger=logger)


def get_db_session(db: AsyncSession = Depends(get_db)):
    return db
