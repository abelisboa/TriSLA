from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import List
from src.schemas.health import HealthResponse, ModuleStatus
from src.services.health import HealthService

router = APIRouter()
health_service = HealthService()


@router.get("/health/global", response_model=HealthResponse)
async def get_health_global():
    """Retorna a saúde global do TriSLA"""
    try:
        health = await health_service.get_global_health()
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/modules", response_model=List[ModuleStatus])
async def get_modules():
    """Retorna lista de módulos"""
    try:
        modules = await health_service.get_modules()
        return modules
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


