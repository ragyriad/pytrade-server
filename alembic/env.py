from sqlalchemy import create_engine
from alembic import context
from database.connection import Base
from config import settings


SYNC_DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql+asyncpg", "postgresql+psycopg2"
)
sync_engine = create_engine(SYNC_DATABASE_URL)


def run_migrations_offline():
    context.configure(
        url=SYNC_DATABASE_URL,
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    with sync_engine.begin() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
