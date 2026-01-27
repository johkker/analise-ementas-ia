from abc import ABC, abstractmethod
import httpx

class BaseExtractor(ABC):
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def fetch_raw_data(self, endpoint: str, params: dict = None):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()

    @abstractmethod
    def parse_schema(self, data: dict):
        pass
