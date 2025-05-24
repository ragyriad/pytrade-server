from services.wealthsimple_service import WealthsimpleService
from services.questrade_service import QuestradeService


class BrokerAuthService:
    async def authenticate(self, broker: str):
        if broker == "wealthsimple":
            return await WealthsimpleService().authenticate()
        elif broker == "questrade":
            return await QuestradeService().authenticate()
        else:
            raise ValueError("Unsupported broker")

    async def sync_data(self, broker: str):
        if broker == "wealthsimple":
            return await WealthsimpleService().sync_data()
        elif broker == "questrade":
            return await QuestradeService().sync_data()
        else:
            raise ValueError("Unsupported broker")
