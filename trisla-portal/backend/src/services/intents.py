import httpx
from typing import List, Optional, Any
from src.config import settings


class IntentService:
    async def list_intents(
        self, status: Optional[str] = None, type: Optional[str] = None, tenant: Optional[str] = None
    ) -> List[Any]:
        """Lista intents"""
        # Em produção, buscar do banco de dados ou SEM-CSMF
        async with httpx.AsyncClient() as client:
            params = {}
            if status:
                params["status"] = status
            if type:
                params["type"] = type
            if tenant:
                params["tenant"] = tenant
            
            response = await client.get(
                f"{settings.trisla_sem_csmf_url}/api/v1/intents",
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def get_intent(self, intent_id: str) -> Any:
        """Retorna detalhes de um intent"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.trisla_sem_csmf_url}/api/v1/intents/{intent_id}",
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def get_intent_trace(self, intent_id: str) -> Any:
        """Retorna trace de um intent"""
        from src.services.tempo import TempoService
        tempo_service = TempoService()
        # Buscar traces relacionados ao intent
        traces = await tempo_service.get_traces()
        # Filtrar por intent_id
        for trace in traces:
            if intent_id in str(trace):
                return trace
        return None


