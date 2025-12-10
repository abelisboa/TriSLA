from fastapi import APIRouter, HTTPException
from typing import Any
from src.services.modules import ModuleService

router = APIRouter()
module_service = ModuleService()


@router.get("/")
async def list_modules():
    """Lista todos os módulos"""
    try:
        modules = await module_service.list_modules()
        return modules
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{module}")
async def get_module(module: str):
    """Retorna detalhes de um módulo"""
    try:
        module_data = await module_service.get_module(module)
        return module_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{module}/metrics")
async def get_module_metrics(module: str):
    """Retorna métricas de um módulo"""
    try:
        metrics = await module_service.get_module_metrics(module)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{module}/status")
async def get_module_status(module: str):
    """Retorna status (pods, deployments) de um módulo"""
    try:
        status = await module_service.get_module_status(module)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


