from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.models import Broker


class BrokerRepository:
    def __init__(self, logger=None):
        self.logger = logger

    @staticmethod
    async def get_all_brokers(db: AsyncSession) -> List[Broker]:
        result = await db.execute(select(Broker))
        return result.scalars().all()

    @staticmethod
    async def get_broker_by_id(db: AsyncSession, broker_id: str) -> Optional[Broker]:
        result = await db.execute(select(Broker).where(Broker.id == broker_id))
        return result.scalars().first()

    @staticmethod
    async def get_broker_by_name(
        db: AsyncSession, broker_name: str
    ) -> Optional[Broker]:
        result = await db.execute(select(Broker).where(Broker.name == broker_name))
        return result.scalars().first()

    @staticmethod
    async def create_broker(db: AsyncSession, name: str) -> Broker:
        broker = Broker(name=name)
        db.add(broker)
        await db.commit()
        await db.refresh(broker)
        return broker


def get_broker_repository(logger=None) -> BrokerRepository:
    return BrokerRepository(logger=logger)
