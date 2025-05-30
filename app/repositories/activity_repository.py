from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import insert
import sqlalchemy as sa

from app.database.models import Activity
from app.schemas.activity import ActivityCreate, ActivityUpdate


class ActivityRepository:
    def __init__(self, logger=None):
        self.logger = logger

    async def get_all(self) -> List[Activity]:
        result = await self.session.execute(select(Activity))
        return result.scalars().all()

    async def get_by_id(self, activity_id: str) -> Optional[Activity]:
        result = await self.session.execute(
            select(Activity).where(Activity.id == activity_id)
        )
        return result.scalars().first()

    async def find_by_type(self, activity_type: str) -> List[Activity]:
        result = await self.session.execute(
            select(Activity).where(Activity.type == activity_type)
        )
        return result.scalars().all()

    async def find_negative_commissions(self) -> List[Activity]:
        result = await self.session.execute(
            select(Activity).where(Activity.commission < 0)
        )
        return result.scalars().all()

    async def save(self, activity: ActivityCreate) -> Activity:
        db_activity = Activity(**activity.dict())
        self.session.add(db_activity)
        await self.session.commit()
        await self.session.refresh(db_activity)
        return db_activity

    async def save_activities(
        self, db: AsyncSession, activities: list["Activity"]
    ) -> list["Activity"]:
        if not activities:
            return []

        now = datetime.now(tz=timezone.utc)
        activity_dicts = []
        activity_ids = []
        for activity in activities:
            if not hasattr(activity, "last_synced") or activity.last_synced is None:
                activity.last_synced = now
            data = activity.__dict__.copy()
            data.pop("_sa_instance_state", None)
            activity_dicts.append(data)
            activity_ids.append(activity.id)

        try:
            stmt = insert(Activity).values(activity_dicts)
            stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
            await db.execute(stmt)
            await db.commit()
        except SQLAlchemyError as e:
            await db.rollback()
            # Optionally log the error if you have a logger in scope
            if hasattr(self, "logger") and self.logger:
                self.logger.error(f"Error inserting activities: {e}")
            raise  # re-raise so caller knows insert failed

        try:
            result = await db.execute(
                sa.select(Activity).where(Activity.id.in_(activity_ids))
            )
            saved_activities = result.scalars().all()
        except SQLAlchemyError as e:
            if hasattr(self, "logger") and self.logger:
                self.logger.error(f"Error querying inserted activities: {e}")
            raise

        return saved_activities

    async def update(
        self, activity_id: str, activity: ActivityUpdate
    ) -> Optional[Activity]:
        await self.session.execute(
            update(Activity)
            .where(Activity.id == activity_id)
            .values(**activity.dict(exclude_unset=True))
        )
        await self.session.commit()
        return await self.get(activity_id)

    async def delete(self, activity_id: str) -> bool:
        await self.session.execute(delete(Activity).where(Activity.id == activity_id))
        await self.session.commit()
        return True
