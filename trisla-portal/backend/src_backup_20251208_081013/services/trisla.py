import httpx
from typing import Any
from src.config import settings


class TriSLAService:
    """Service para comunicação com módulos TriSLA"""
    
    async def call_sem_csmf(self, endpoint: str, method: str = "GET", **kwargs) -> Any:
        """Chama endpoint do SEM-CSMF"""
        async with httpx.AsyncClient() as client:
            url = f"{settings.trisla_sem_csmf_url}{endpoint}"
            if method == "GET":
                response = await client.get(url, timeout=30.0, **kwargs)
            elif method == "POST":
                response = await client.post(url, timeout=30.0, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
            response.raise_for_status()
            return response.json()
    
    async def call_ml_nsmf(self, endpoint: str, method: str = "GET", **kwargs) -> Any:
        """Chama endpoint do ML-NSMF"""
        async with httpx.AsyncClient() as client:
            url = f"{settings.trisla_ml_nsmf_url}{endpoint}"
            if method == "GET":
                response = await client.get(url, timeout=30.0, **kwargs)
            elif method == "POST":
                response = await client.post(url, timeout=30.0, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
            response.raise_for_status()
            return response.json()
    
    async def call_decision_engine(self, endpoint: str, method: str = "GET", **kwargs) -> Any:
        """Chama endpoint do Decision Engine"""
        async with httpx.AsyncClient() as client:
            url = f"{settings.trisla_decision_engine_url}{endpoint}"
            if method == "GET":
                response = await client.get(url, timeout=30.0, **kwargs)
            elif method == "POST":
                response = await client.post(url, timeout=30.0, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")
            response.raise_for_status()
            return response.json()






