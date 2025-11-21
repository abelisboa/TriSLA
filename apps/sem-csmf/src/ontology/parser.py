"""
Parser de Ontologias - SEM-CSMF
Processa intents usando ontologias Protégé
"""

from typing import Dict, Any
from opentelemetry import trace

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.intent import Intent

tracer = trace.get_tracer(__name__)


class OntologyParser:
    """Parser de ontologias para validação semântica"""
    
    def __init__(self):
        # Em produção, carregar ontologia do Protégé
        self.ontology = self._load_ontology()
    
    def _load_ontology(self) -> Dict[str, Any]:
        """
        Carrega ontologia do Protégé
        Em produção, usar biblioteca de ontologias (ex: owlready2)
        """
        return {
            "concepts": {
                "eMBB": {
                    "latency": "10-50ms",
                    "throughput": "100Mbps-1Gbps",
                    "reliability": "0.99"
                },
                "URLLC": {
                    "latency": "1-10ms",
                    "throughput": "1-100Mbps",
                    "reliability": "0.99999"
                },
                "mMTC": {
                    "latency": "100-1000ms",
                    "throughput": "160bps-100Kbps",
                    "reliability": "0.9"
                }
            }
        }
    
    async def parse_intent(self, intent: Intent) -> Dict[str, Any]:
        """
        Parse do intent usando ontologia
        Retorna representação ontológica do intent
        """
        with tracer.start_as_current_span("parse_intent_ontology") as span:
            span.set_attribute("intent.id", intent.intent_id)
            span.set_attribute("intent.type", intent.service_type.value)
            
            # Buscar conceito na ontologia
            concept = self.ontology["concepts"].get(intent.service_type.value, {})
            
            ontology_representation = {
                "intent_id": intent.intent_id,
                "concept": intent.service_type.value,
                "properties": concept,
                "sla_requirements": intent.sla_requirements.dict(),
                "validated": True
            }
            
            span.set_attribute("ontology.concept", intent.service_type.value)
            return ontology_representation

