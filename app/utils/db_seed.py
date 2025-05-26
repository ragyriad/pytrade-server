from sqlalchemy import select
from app.database.models import Broker


async def seed_brokers(session):
    broker_names = ["Questrade", "Wealthsimple", "Interactive Brokers"]
    for name in broker_names:
        result = await session.execute(select(Broker).where(Broker.name == name))
        if not result.scalar_one_or_none():
            session.add(Broker(name=name))
    await session.commit()
