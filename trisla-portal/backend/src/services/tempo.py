import httpx
from typing import Any, Optional, List
from src.config import settings


class TempoService:
    def __init__(self):
        self.base_url = settings.tempo_url

    async def get_traces(
        self,
        service: Optional[str] = None,
        operation: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Any]:
        """Retorna lista de traces"""
        url = f"{self.base_url}/api/search"
        params = {}
        if service:
            params["service.name"] = service
        if operation:
            params["name"] = operation
        if status:
            params["status"] = status

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            return data.get("traces", [])

    async def get_trace(self, trace_id: str) -> Any:
        """Retorna detalhes de um trace"""
        url = f"{self.base_url}/api/traces/{trace_id}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            return response.json()


