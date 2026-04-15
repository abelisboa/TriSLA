import httpx
from typing import List, Optional
from src.config import settings
from src.schemas.xai import XAIExplanation
import uuid

class XAIService:
    async def get_explanations(self) -> List[XAIExplanation]:
        """Lista explicações XAI disponíveis"""
        # Em produção, buscar do banco de dados ou cache
        return []

    async def get_explanation(self, explanation_id: str) -> XAIExplanation:
        """Retorna detalhes de uma explicação"""
        # Em produção, buscar do banco de dados
        raise ValueError(f"Explanation {explanation_id} not found")

    async def explain(
        self, prediction_id: Optional[str] = None, decision_id: Optional[str] = None
    ) -> XAIExplanation:
        """Gera explicação XAI"""
        if prediction_id:
            # Buscar predição do ML-NSMF
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.trisla_ml_nsmf_url}/api/v1/predictions/{prediction_id}",
                    timeout=30.0,
                )
                response.raise_for_status()
                prediction = response.json()
                
                # Extrair explicação XAI
                explanation = prediction.get("explanation", {})
                return XAIExplanation(
                    explanation_id=str(uuid.uuid4()),
                    type="ml_prediction",
                    prediction_id=prediction_id,
                    method=explanation.get("method", "SHAP"),
                    viability_score=prediction.get("viability_score"),
                    recommendation=prediction.get("recommendation"),
                    features_importance=explanation.get("features_importance", {}),
                    shap_values=explanation.get("shap_values"),
                    reasoning=explanation.get("reasoning", ""),
                )
        elif decision_id:
            # Buscar decisão do Decision Engine
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.trisla_decision_engine_url}/api/v1/decisions/{decision_id}",
                    timeout=30.0,
                )
                response.raise_for_status()
                decision = response.json()
                
                return XAIExplanation(
                    explanation_id=str(uuid.uuid4()),
                    type="decision",
                    decision_id=decision_id,
                    method="rules",
                    reasoning=decision.get("reasoning", ""),
                    features_importance={},
                )
        else:
            raise ValueError("Either prediction_id or decision_id must be provided")






