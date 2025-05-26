from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.database.models import Activity
from app.schemas.schemas import ActivityCreate, ActivityUpdate


class ActivityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

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

    async def bulk_save(self, activities: List[ActivityCreate]) -> List[Activity]:
        db_activities = [Activity(**activity.dict()) for activity in activities]
        self.session.add_all(db_activities)
        await self.session.commit()
        return db_activities

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

    async def regenerate_from_source(self, external_source_id: str) -> List[Activity]:
        """Regenerate activities from external source (e.g., Wealthsimple API)"""
        # 1. Fetch fresh data from external source
        # external_activities = await ExternalAPIService.get_activities(external_source_id)

        # 2. Clear existing data
        await self.session.execute(delete(Activity))

        # 3. Persist new data
        # activities = [Activity(**a.dict()) for a in external_activities]
        # self.session.add_all(activities)
        # await self.session.commit()
        # return activities

        # Placeholder until external service implementation
        return []
