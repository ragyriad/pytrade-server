from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from database.models import Activity
from sqlalchemy.future import select

router = APIRouter()


@router.get("/")
async def get_activities(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Activity))
    activities = result.scalars().all()
    return {"activities": activities}


@router.post("/")
async def create_activity(activity: Activity, db: AsyncSession = Depends(get_db)):
    db.add(activity)
    await db.commit()
    return {"message": "Activity created successfully"}
