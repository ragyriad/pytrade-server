from database.models import User
from database.connection import async_session


class UserRepository:
    @staticmethod
    async def get_by_email(email: str):
        async with async_session() as session:
            return await session.query(User).filter(User.email == email).first()

    @staticmethod
    async def create(user_data):
        async with async_session() as session:
            user = User(**user_data.dict())
            session.add(user)
            await session.commit()
            return user
