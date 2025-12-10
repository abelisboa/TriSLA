from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from src.services.intents import IntentService

router = APIRouter()
intent_service = IntentService()


@router.get("/")
async def list_intents(
    status: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    tenant: Optional[str] = Query(None),
):
    """Lista intents"""
    try:
        intents = await intent_service.list_intents(status, type, tenant)
        return intents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{intent_id}")
async def get_intent(intent_id: str):
    """Retorna detalhes de um intent"""
    try:
        intent = await intent_service.get_intent(intent_id)
        return intent
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{intent_id}/trace")
async def get_intent_trace(intent_id: str):
    """Retorna trace de um intent"""
    try:
        trace = await intent_service.get_intent_trace(intent_id)
        return trace
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






