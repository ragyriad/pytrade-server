from contextlib import asynccontextmanager
from .connection import sessionLocal


@asynccontextmanager
async def get_db():
    async with sessionLocal() as session:
        yield session
