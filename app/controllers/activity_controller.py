from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database.connection import get_db
from app.database.models import Activity
from app.schemas.schemas import ActivityResponse


router = APIRouter()


@router.get("/")
async def get_activities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Activity))
    activities = result.scalars().all()
    return {"activities": activities}


@router.post("/")
async def create_activity(
    activity: ActivityResponse, db: AsyncSession = Depends(get_db)
):
    db.add(activity)
    await db.commit()
    return {"message": "Activity created successfully"}
