from fastapi import APIRouter, HTTPException
from typing import List
from src.schemas.xai import XAIExplanation, XAIExplainRequest
from src.services.xai import XAIService

router = APIRouter()
xai_service = XAIService()


@router.get("/explanations", response_model=List[XAIExplanation])
async def get_explanations():
    """Lista explicações XAI disponíveis"""
    try:
        explanations = await xai_service.get_explanations()
        return explanations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/explanations/{explanation_id}", response_model=XAIExplanation)
async def get_explanation(explanation_id: str):
    """Retorna detalhes de uma explicação"""
    try:
        explanation = await xai_service.get_explanation(explanation_id)
        return explanation
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/explain", response_model=XAIExplanation)
async def explain(request: XAIExplainRequest):
    """Gera explicação XAI para uma predição ou decisão"""
    try:
        explanation = await xai_service.explain(
            request.prediction_id, request.decision_id
        )
        return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))







