from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import update, delete
from sqlalchemy.orm import selectinload

from app.database.models import Account, Broker
from app.repositories.broker_repository import BrokerRepository


class AccountRepository:
    def __init__(self, logger=None):
        self.logger = logger

    @staticmethod
    async def get_all_accounts(db: AsyncSession) -> List[Account]:
        result = await db.execute(select(Account))
        return result.scalars().all()

    @staticmethod
    async def get_account_by_id(db: AsyncSession, account_id: str) -> Optional[Account]:
        result = await db.execute(
            select(Account).filter(Account.account_number == account_id)
        )
        return result.scalars().first()

    @staticmethod
    async def get_accounts_by_broker_name(
        db: AsyncSession, broker_name: str
    ) -> List[Account]:
        stmt = (
            select(Account)
            .join(Account.account_broker)
            .filter(Broker.name == broker_name)
            .options(selectinload(Account.account_broker))
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def save_accounts(
        self, db: AsyncSession, accounts_data: List[dict], broker: str = None
    ) -> List["Account"]:
        if not accounts_data:
            if self.logger:
                self.logger.warning("Empty accounts_data provided to save_accounts")
            return []

        fetched_account_broker_id = None
        if broker:
            broker_obj = await BrokerRepository.get_broker_by_name(db, broker)
            if not broker_obj:
                raise ValueError(f"Broker with name '{broker}' not found")
            if self.logger:
                self.logger.info(f"Broker found: {broker_obj.name}")
            fetched_account_broker_id = broker_obj.id

        account_objs = []
        for acc in accounts_data:
            if not acc.get("number"):
                raise ValueError("Account number is required")

            account = Account(
                type=acc.get("type"),
                account_number=acc.get("number"),
                status=acc.get("status"),
                is_primary=acc.get("isPrimary", False),
                last_synced=datetime.now(tz=timezone.utc),
                currency=acc.get("currency"),
                account_broker_id=fetched_account_broker_id,
            )
            account_objs.append(account)

        try:
            db.add_all(account_objs)
            await db.commit()
        except SQLAlchemyError as e:
            await db.rollback()
            if self.logger:
                self.logger.error(f"Error saving accounts: {e}")
            raise

        for account in account_objs:
            await db.refresh(account)

        if self.logger:
            self.logger.info(f"Saved {len(account_objs)} accounts")

        return account_objs

    async def update_account(
        self, db: AsyncSession, account_id: str, update_data: dict
    ) -> Optional[Account]:
        """Update account fields"""
        if not update_data:
            return None

        await db.execute(
            update(Account)
            .where(Account.account_number == account_id)
            .values(**update_data)
        )
        await db.commit()

        return await self.get_account_by_id(db, account_id)

    async def delete_account(self, db: AsyncSession, account_id: str) -> bool:
        """Delete an account by account_number"""
        result = await db.execute(
            delete(Account).where(Account.account_number == account_id)
        )
        await db.commit()
        return result.rowcount > 0
