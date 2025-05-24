from typing import List, Optional
from repositories.activity_repository import ActivityRepository
from repositories.base_repository import BaseRepository
from schemas.schemas import ActivityResponse, AccountBase, AccountResponse
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

    async def get_all_accounts(self, db) -> List[AccountResponse]:
        accounts = await self.account_repo.get_all_accounts(db)
        accounts_serialized = [
            AccountResponse.model_validate(account, from_attributes=True)
            for account in accounts
        ]
        return accounts_serialized

    async def get_account_by_id(self, db, account_id: str) -> Optional[AccountResponse]:
        account = await self.account_repo.get_account_by_id(db, account_id)
        account_serialized = (
            AccountResponse.model_validate(account, from_attributes=True)
            if account
            else None
        )
        return account_serialized

    async def create_account(self, account_data: AccountBase) -> AccountBase:
        new_account = await self.account_repo.create(account_data.dict())
        return AccountBase.model_validate(new_account)

    async def update_account(
        self, account_id: int, update_data: dict
    ) -> Optional[AccountResponse]:
        updated_account = await self.account_repo.update(account_id, update_data)
        return (
            AccountResponse.model_validate(updated_account) if updated_account else None
        )

    async def delete_account(self, account_id: int) -> bool:
        return await self.account_repo.delete(account_id)
