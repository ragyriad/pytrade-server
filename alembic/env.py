from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context
from database.connection import Base
from config import settings

sync_engine = create_engine(
    settings.DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
)


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=settings.DATABASE_URL, target_metadata=Base.metadata, literal_binds=True
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    with sync_engine.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)
        with context.begin_transaction():
            context.run_migrations()
