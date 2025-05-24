from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from database.models import Account


class AccountRepository:
    def __init__(self, logger=None):
        """
        Initialize with optional logger dependency.
        Can be extended with other dependencies like cache, metrics, etc.
        """
        self.logger = logger

    @staticmethod
    async def get_all_accounts(db: AsyncSession) -> List[Account]:
        """Get all accounts from the database"""
        result = await db.execute(select(Account))
        return result.scalars().all()

    @staticmethod
    async def get_account_by_id(db: AsyncSession, account_id: str) -> Optional[Account]:
        """Get single account by account_number"""
        result = await db.execute(
            select(Account).filter(Account.account_number == account_id)
        )
        return result.scalars().first()

    async def save_accounts(
        self, db: AsyncSession, accounts_data: List[dict]
    ) -> List[Account]:
        """Bulk insert accounts with validation"""
        if not accounts_data:
            if self.logger:
                self.logger.warning("Empty accounts_data provided to save_accounts")
            return []

        account_objs = []
        for acc in accounts_data:
            if not acc.get("number"):
                raise ValueError("Account number is required")

            account = Account(
                type=acc.get("type"),
                account_number=acc.get("number"),
                status=acc.get("status"),
                is_primary=acc.get("isPrimary", False),
                last_synced=datetime.utcnow(),
                currency=acc.get("currency"),
                account_broker_id=acc.get("account_broker_id", "Questrade"),
            )
            account_objs.append(account)

        db.add_all(account_objs)
        await db.commit()

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

    async def get_accounts_by_status(
        self, db: AsyncSession, status: str
    ) -> List[Account]:
        """Get accounts filtered by status"""
        result = await db.execute(select(Account).filter(Account.status == status))
        return result.scalars().all()

    async def get_primary_account(
        self, db: AsyncSession, user_id: str
    ) -> Optional[Account]:
        """Get a user's primary account"""
        result = await db.execute(
            select(Account).filter(
                Account.user_id == user_id, Account.is_primary == True
            )
        )
        return result.scalars().first()


def get_account_repository(logger=None) -> AccountRepository:
    """Dependency injection factory"""
    return AccountRepository(logger=logger)
