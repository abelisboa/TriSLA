from fastapi import APIRouter, HTTPException, Query
from typing import Any, Optional
from src.services.prometheus import PrometheusService

router = APIRouter()
prometheus_service = PrometheusService()


@router.get("/query")
async def query_prometheus(
    query: str = Query(..., description="Prometheus query"),
    time: Optional[str] = Query(None, description="Timestamp for instant query"),
):
    """Executa query Prometheus"""
    try:
        result = await prometheus_service.query(query, time)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/query_range")
async def query_range_prometheus(
    query: str = Query(..., description="Prometheus query"),
    start: str = Query(..., description="Start timestamp"),
    end: str = Query(..., description="End timestamp"),
    step: str = Query(..., description="Step duration"),
):
    """Executa query range Prometheus"""
    try:
        result = await prometheus_service.query_range(query, start, end, step)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/targets")
async def get_targets():
    """Retorna lista de targets do Prometheus"""
    try:
        targets = await prometheus_service.get_targets()
        return targets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))







