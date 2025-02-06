from database.connection import SessionLocal


async def get_db():
    async with SessionLocal() as session:
        yield session
