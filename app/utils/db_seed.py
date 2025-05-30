from sqlalchemy import select
from app.database.models import Broker
from config.settings import settings


async def seed_brokers(session):
    broker_names = settings.DB_BROKERS_SEED
    for name in broker_names:
        result = await session.execute(select(Broker).where(Broker.name == name))
        if not result.scalar_one_or_none():
            session.add(Broker(name=name))
    await session.commit()
