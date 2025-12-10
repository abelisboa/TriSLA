from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Any
from src.services.loki import LokiService

router = APIRouter()
loki_service = LokiService()


@router.get("/")
async def get_logs(
    module: Optional[str] = Query(None, description="Filter by module"),
    level: Optional[str] = Query(None, description="Filter by log level"),
    start: Optional[str] = Query(None, description="Start timestamp"),
    end: Optional[str] = Query(None, description="End timestamp"),
):
    """Retorna logs do Loki"""
    try:
        logs = await loki_service.get_logs(module, level, start, end)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/query")
async def query_logs(
    query: str = Query(..., description="Loki query"),
):
    """Executa query customizada no Loki"""
    try:
        logs = await loki_service.query(query)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


