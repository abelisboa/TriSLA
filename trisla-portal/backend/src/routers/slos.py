from fastapi import APIRouter, HTTPException
from typing import List, Optional
from src.services.slos import SLOService

router = APIRouter()
slo_service = SLOService()


@router.get("/")
async def list_slos():
    """Lista todos os SLOs"""
    try:
        slos = await slo_service.list_slos()
        return slos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_slo_summary():
    """Retorna resumo de SLOs"""
    try:
        summary = await slo_service.get_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{module}")
async def get_module_slos(module: str):
    """Retorna SLOs de um módulo"""
    try:
        slos = await slo_service.get_module_slos(module)
        return slos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{module}/violations")
async def get_module_slo_violations(module: str):
    """Retorna violações de SLO de um módulo"""
    try:
        violations = await slo_service.get_module_violations(module)
        return violations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))







