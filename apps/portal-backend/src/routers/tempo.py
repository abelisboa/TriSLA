from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Any
from src.services.tempo import TempoService

router = APIRouter()
tempo_service = TempoService()


@router.get("/")
async def get_traces(
    service: Optional[str] = Query(None, description="Filter by service"),
    operation: Optional[str] = Query(None, description="Filter by operation"),
    status: Optional[str] = Query(None, description="Filter by status"),
):
    """Retorna lista de traces"""
    try:
        traces = await tempo_service.get_traces(service, operation, status)
        return traces
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{trace_id}")
async def get_trace(trace_id: str):
    """Retorna detalhes de um trace"""
    try:
        trace = await tempo_service.get_trace(trace_id)
        return trace
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


