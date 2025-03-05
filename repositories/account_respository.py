from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models import Account


class AccountRepository:
    @staticmethod
    async def get_all_accounts(db: AsyncSession) -> List[Account]:
        result = await db.execute(select(Account))
        return result.scalars().all()

    @staticmethod
    async def get_account_by_id(db: AsyncSession, account_id: int) -> Optional[Account]:
        result = await db.execute(select(Account).filter(Account.id == account_id))
        return result.scalars().first()
