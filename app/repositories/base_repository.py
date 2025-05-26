from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import update as sa_update
import traceback
from typing import Type, TypeVar, Generic, List, Optional

from app.database.models import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    def get_all(self) -> List[T]:
        query = select(self.model)
        result = self.session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, entity_id: str) -> Optional[T]:
        return await self.session.get(self.model, entity_id)

    async def create(self, entity_data: dict) -> T:
        entity = self.model(**entity_data)
        async with self.session.begin():  # Ensures rollback on failure
            self.session.add(entity)
        await self.session.refresh(entity)
        return entity

    async def update(self, entity_id: int, update_data: dict) -> Optional[T]:
        async with self.session.begin():
            stmt = (
                sa_update(self.model)
                .where(self.model.id == entity_id)
                .values(**update_data)
                .returning(self.model)
            )
            result = await self.session.execute(stmt)
            updated_entity = result.scalar_one_or_none()
        return updated_entity

    async def delete(self, entity_id: int) -> bool:
        entity = await self.get_by_id(entity_id)
        if entity:
            async with self.session.begin():
                await self.session.delete(entity)
            return True
        return False

    async def safe_bulk_create(self, data: List[dict]) -> List[dict]:
        try:
            async with self.session.begin():
                stmt = insert(self.model).values(data).on_conflict_do_nothing()
                await self.session.execute(stmt)
        except IntegrityError:
            await self.session.rollback()
            print(traceback.format_exc())
            return []
        return data
