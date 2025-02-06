from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db


def get_db_session(db: AsyncSession = Depends(get_db)):
    return db
