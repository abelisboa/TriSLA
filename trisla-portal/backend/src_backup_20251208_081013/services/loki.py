import httpx
from typing import Any, Optional, List
from src.config import settings


class LokiService:
    def __init__(self):
        self.base_url = settings.loki_url

    async def get_logs(
        self,
        module: Optional[str] = None,
        level: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> List[Any]:
        """Retorna logs do Loki"""
        # Build query
        query_parts = []
        if module:
            query_parts.append(f'{{job="{module}"}}')
        else:
            query_parts.append('{job=~".+"}')

        query = "".join(query_parts)

        url = f"{self.base_url}/loki/api/v1/query_range"
        params = {"query": query}
        if start:
            params["start"] = start
        if end:
            params["end"] = end

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("result", [])

    async def query(self, query: str) -> List[Any]:
        """Executa query customizada no Loki"""
        url = f"{self.base_url}/loki/api/v1/query_range"
        params = {"query": query}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("result", [])


