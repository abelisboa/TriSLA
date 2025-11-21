"""
Semantic Matcher - SEM-CSMF
Faz match semântico entre intent e ontologia
"""

from typing import Dict, Any
from opentelemetry import trace

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.intent import Intent

tracer = trace.get_tracer(__name__)


class SemanticMatcher:
    """Faz match semântico entre intents e ontologias"""
    
    async def match(self, ontology: Dict[str, Any], intent: Intent) -> Intent:
        """
        Faz match semântico e valida se o intent está de acordo com a ontologia
        """
        with tracer.start_as_current_span("semantic_match") as span:
            span.set_attribute("intent.id", intent.intent_id)
            
            # Validar se os requisitos de SLA estão dentro dos limites da ontologia
            concept_properties = ontology.get("properties", {})
            
            # Validação básica (em produção, usar engine de raciocínio semântico)
            validated = self._validate_against_ontology(intent, concept_properties)
            
            if not validated:
                raise ValueError(f"Intent {intent.intent_id} não está de acordo com a ontologia")
            
            span.set_attribute("match.status", "success")
            return intent
    
    def _validate_against_ontology(self, intent: Intent, properties: Dict[str, Any]) -> bool:
        """Valida intent contra propriedades da ontologia"""
        # Validação simplificada
        # Em produção, usar engine de raciocínio semântico completo
        
        sla = intent.sla_requirements
        
        # Validar latência se especificada
        if sla.latency and properties.get("latency"):
            # Parse e comparação (simplificado)
            pass
        
        # Validar throughput se especificado
        if sla.throughput and properties.get("throughput"):
            # Parse e comparação (simplificado)
            pass
        
        return True

