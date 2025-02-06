# app/services/account_service.py
from typing import List
from repositories.activity_repository import ActivityRepository
from database.schemas import ActivityResponse


class AccountService:
    def __init__(self, activity_repo: ActivityRepository):
        self.activity_repo = activity_repo

    async def get_total_dividends(self) -> float:
        activities = await self.activity_repo.find_by_type("Dividends")
        return sum(abs(activity.net_amount) for activity in activities)

    async def get_commissions(self) -> List[ActivityResponse]:
        activities = await self.activity_repo.find_negative_commissions()
        return [
            ActivityResponse(
                id=activity.id,
                type=activity.type,
                commission=abs(activity.commission),
                currency=activity.currency,
                created_at=activity.created_at,
            )
            for activity in activities
        ]

    async def get_trades_count(self) -> int:
        activities = await self.activity_repo.find_by_type("Trades")
        return len(activities)

    async def refresh_activities(self, source_id: str) -> List[ActivityResponse]:
        """Example of extended functionality"""
        new_activities = await self.activity_repo.regenerate_from_source(source_id)
        return [ActivityResponse.from_orm(a) for a in new_activities]
