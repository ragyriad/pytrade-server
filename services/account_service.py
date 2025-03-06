from typing import List, Optional
from repositories.activity_repository import ActivityRepository
from repositories.base_repository import BaseRepository
from database.schemas import ActivityResponse, AccountBase
from database.models import Account


class AccountService:
    def __init__(
        self, activity_repo: ActivityRepository, account_repo: BaseRepository[Account]
    ):
        self.activity_repo = activity_repo
        self.account_repo = account_repo

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
        new_activities = await self.activity_repo.regenerate_from_source(
            source_id
        ).__dict__
        return [ActivityResponse.model_validate(a) for a in new_activities]

    async def get_all_accounts(self, db) -> List[AccountBase]:
        accounts = await self.account_repo.get_all_accounts(db)
        print(accounts.__dict__)
        return [
            AccountBase.model_validate(account, from_attributes=True)
            for account in accounts
        ]

    async def get_account_by_id(self, account_id: int) -> Optional[AccountBase]:
        account = await self.account_repo.get_by_id(account_id)
        return (
            AccountBase.model_validate(account, from_attributes=True)
            if account
            else None
        )

    async def create_account(self, account_data: AccountBase) -> AccountBase:
        new_account = await self.account_repo.create(account_data.dict())
        return AccountBase.model_validate(new_account)

    async def update_account(
        self, account_id: int, update_data: dict
    ) -> Optional[AccountBase]:
        updated_account = await self.account_repo.update(account_id, update_data)
        return AccountBase.model_validate(updated_account) if updated_account else None

    async def delete_account(self, account_id: int) -> bool:
        return await self.account_repo.delete(account_id)
