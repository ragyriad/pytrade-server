from typing import List, Optional
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import sqlalchemy as sa
from sqlalchemy import update, delete
from sqlalchemy.exc import SQLAlchemyError

from app.database.models import Security


class SecurityRepository:
    def __init__(self, logger=None):
        self.logger = logger

    @staticmethod
    async def get_all_securities(db: AsyncSession) -> List[Security]:
        result = await db.execute(select(Security))
        return result.scalars().all()

    @staticmethod
    async def get_security_by_id(
        db: AsyncSession, security_id: str
    ) -> Optional[Security]:
        result = await db.execute(select(Security).filter(Security.id == security_id))
        return result.scalars().first()

    @staticmethod
    async def get_security_by_symbol(
        db: AsyncSession, symbol: str
    ) -> Optional[Security]:
        result = await db.execute(select(Security).filter(Security.symbol == symbol))
        return result.scalars().first()

    async def save_securities(
        self, db: AsyncSession, securities: List["Security"]
    ) -> List["Security"]:
        if not securities:
            if self.logger:
                self.logger.warning("Empty securities list provided to save_securities")
            return []

        now = datetime.now(tz=timezone.utc)

        security_dicts = []
        security_ids = []
        for sec in securities:
            if not hasattr(sec, "last_synced") or sec.last_synced is None:
                sec.last_synced = now
            data = sec.__dict__.copy()
            data.pop("_sa_instance_state", None)
            security_dicts.append(data)
            security_ids.append(sec.id)

        try:
            stmt = insert(Security).values(security_dicts)
            stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
            await db.execute(stmt)
            await db.commit()
        except SQLAlchemyError as e:
            await db.rollback()
            if self.logger:
                self.logger.error(f"Error saving securities: {e}")
            raise

        try:
            result = await db.execute(
                sa.select(Security).where(Security.id.in_(security_ids))
            )
            saved_securities = result.scalars().all()
        except SQLAlchemyError as e:
            if self.logger:
                self.logger.error(f"Error querying saved securities: {e}")
            raise

        if self.logger:
            self.logger.info(f"Saved {len(saved_securities)} securities")

        return saved_securities

    async def update_security(
        self, db: AsyncSession, security_id: str, update_data: dict
    ) -> Optional[Security]:
        if not update_data:
            return None

        await db.execute(
            update(Security).where(Security.id == security_id).values(**update_data)
        )
        await db.commit()

        return await self.get_security_by_id(db, security_id)

    async def delete_security(self, db: AsyncSession, security_id: str) -> bool:
        result = await db.execute(delete(Security).where(Security.id == security_id))
        await db.commit()
        return result.rowcount > 0

    async def get_securities_by_status(
        self, db: AsyncSession, status: str
    ) -> List[Security]:
        result = await db.execute(select(Security).filter(Security.status == status))
        return result.scalars().all()

    async def get_securities_by_type(
        self, db: AsyncSession, security_type: str
    ) -> List[Security]:
        result = await db.execute(
            select(Security).filter(Security.type == security_type)
        )
        return result.scalars().all()
