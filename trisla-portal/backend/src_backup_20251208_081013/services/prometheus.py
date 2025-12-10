import httpx
from typing import Any, Optional
from src.config import settings


class PrometheusService:
    def __init__(self):
        self.base_url = settings.prometheus_url

    async def query(self, query: str, time: Optional[str] = None) -> Any:
        """Executa query Prometheus"""
        url = f"{self.base_url}/api/v1/query"
        params = {"query": query}
        if time:
            params["time"] = time

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()

    async def query_range(
        self, query: str, start: str, end: str, step: str
    ) -> Any:
        """Executa query range Prometheus"""
        url = f"{self.base_url}/api/v1/query_range"
        params = {
            "query": query,
            "start": start,
            "end": end,
            "step": step,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()

    async def get_targets(self) -> Any:
        """Retorna targets do Prometheus"""
        url = f"{self.base_url}/api/v1/targets"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            return response.json()


