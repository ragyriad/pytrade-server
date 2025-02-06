from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import traceback
from sqlalchemy.future import select
from typing import Type, TypeVar, Generic
from database.models import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def get_all(self):
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, entity_id: int):
        return await self.session.get(self.model, entity_id)

    async def create(self, entity_data: dict):
        entity = self.model(**entity_data)
        self.session.add(entity)
        await self.session.commit()
        return entity

    async def delete(self, entity_id: int):
        entity = await self.get_by_id(entity_id)
        if entity:
            await self.session.delete(entity)
            await self.session.commit()
            return True
        return False

    def safe_bulk_create(
        db: Session, Model, data: list, unique_fields=None, update_fields=None
    ):
        created_records = []
        try:
            if unique_fields and update_fields:
                for obj in data:
                    db.merge(obj)  # Merge to handle duplicates
                db.commit()
            else:
                db.add_all(data)
                db.commit()
            created_records = data
        except IntegrityError:
            db.rollback()
            print(traceback.format_exc())
            for obj in data:
                try:
                    db.add(obj)
                    db.commit()
                    created_records.append(obj)
                except IntegrityError as integrity_err:
                    db.rollback()
                    print(integrity_err)
                    continue
        return created_records
