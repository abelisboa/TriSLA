from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from src.schemas.slas import (
    SLACreatePLN,
    SLACreateTemplate,
    SLATemplate,
    BatchJob,
)
from src.services.slas import SLAService

router = APIRouter()
sla_service = SLAService()


@router.post("/create/pln")
async def create_sla_pln(sla: SLACreatePLN):
    """Cria SLA via Processamento de Linguagem Natural"""
    try:
        result = await sla_service.create_pln(sla.intent_text, sla.tenant_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate")
async def validate_sla(sla: SLACreatePLN):
    """Valida intent PLN"""
    try:
        result = await sla_service.validate_pln(sla.intent_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates", response_model=List[SLATemplate])
async def get_templates():
    """Lista templates NEST disponíveis"""
    try:
        templates = await sla_service.get_templates()
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/{template_id}", response_model=SLATemplate)
async def get_template(template_id: str):
    """Retorna detalhes de um template"""
    try:
        template = await sla_service.get_template(template_id)
        return template
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/create/template")
async def create_sla_template(sla: SLACreateTemplate):
    """Cria SLA via template NEST"""
    try:
        result = await sla_service.create_template(
            sla.template_id, sla.form_values, sla.tenant_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create/batch", response_model=BatchJob)
async def create_sla_batch(
    file: UploadFile = File(...),
    tenant_id: str = None,
):
    """Cria SLAs em lote via arquivo CSV/JSON"""
    try:
        batch_job = await sla_service.create_batch(file, tenant_id)
        return batch_job
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/batch/{batch_id}", response_model=BatchJob)
async def get_batch_status(batch_id: str):
    """Retorna status de um batch job"""
    try:
        batch_job = await sla_service.get_batch_status(batch_id)
        return batch_job
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/batch/{batch_id}/results")
async def get_batch_results(batch_id: str):
    """Retorna resultados de um batch job"""
    try:
        results = await sla_service.get_batch_results(batch_id)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))







