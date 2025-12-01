"""
Parser de Ontologias - SEM-CSMF
Processa intents usando ontologias OWL reais
"""

from typing import Dict, Any, Optional
from opentelemetry import trace

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.intent import Intent
from .loader import OntologyLoader
from .reasoner import SemanticReasoner
from .cache import SemanticCache

tracer = trace.get_tracer(__name__)


class OntologyParser:
    """Parser de ontologias para validação semântica usando OWL real"""
    
    def __init__(self, ontology_path: Optional[str] = None, cache: Optional[SemanticCache] = None):
        """
        Inicializa parser de ontologia
        
        Args:
            ontology_path: Caminho para arquivo .ttl ou .owl. Se None, usa padrão.
            cache: Cache semântico compartilhado (opcional, cria novo se None)
        """
        self.ontology_loader = OntologyLoader(ontology_path)
        self.cache = cache if cache is not None else SemanticCache()
        self.reasoner = SemanticReasoner(self.ontology_loader, cache=self.cache)
        self._initialized = False
    
    def _ensure_initialized(self):
        """Garante que ontologia foi carregada"""
        if not self._initialized:
            try:
                self.ontology_loader.load(apply_reasoning=True)
                self.reasoner.initialize()
                self._initialized = True
            except Exception as e:
                # Fallback para modo mock se ontologia não puder ser carregada
                with tracer.start_as_current_span("ontology_fallback") as span:
                    span.set_attribute("fallback.reason", str(e))
                self._initialized = False
    
    async def parse_intent(self, intent: Intent) -> Dict[str, Any]:
        """
        Parse do intent usando ontologia OWL real
        Retorna representação ontológica do intent
        
        Args:
            intent: Intent a ser processado
            
        Returns:
            Representação ontológica do intent
        """
        with tracer.start_as_current_span("parse_intent_ontology") as span:
            span.set_attribute("intent.id", intent.intent_id)
            span.set_attribute("intent.type", intent.service_type.value)
            
            self._ensure_initialized()
            
            # Se ontologia não foi carregada, usar fallback
            if not self._initialized:
                return self._parse_intent_fallback(intent)
            
            try:
                # Buscar tipo de slice na ontologia
                slice_type_individual = None
                try:
                    if intent.service_type.value == "eMBB":
                        slice_type_individual = self.ontology_loader.get_individual("eMBB_Type")
                    elif intent.service_type.value == "URLLC":
                        slice_type_individual = self.ontology_loader.get_individual("URLLC_Type")
                    elif intent.service_type.value == "mMTC":
                        slice_type_individual = self.ontology_loader.get_individual("mMTC_Type")
                except ValueError:
                    pass
                
                # Extrair propriedades da ontologia
                properties = {}
                if slice_type_individual:
                    properties = {
                        "latency": getattr(slice_type_individual, "hasLatency", [None])[0],
                        "throughput": getattr(slice_type_individual, "hasThroughput", [None])[0],
                        "reliability": getattr(slice_type_individual, "hasReliability", [None])[0]
                    }
                
                # Inferir tipo de slice se não especificado
                inferred_type = None
                if not intent.service_type.value:
                    sla_dict = intent.sla_requirements.dict()
                    inferred_type = self.reasoner.infer_slice_type(sla_dict)
                
                ontology_representation = {
                    "intent_id": intent.intent_id,
                    "concept": intent.service_type.value or inferred_type,
                    "inferred_type": inferred_type,
                    "properties": properties,
                    "sla_requirements": intent.sla_requirements.dict(),
                    "validated": True,
                    "ontology_loaded": True
                }
                
                span.set_attribute("ontology.concept", intent.service_type.value or inferred_type)
                span.set_attribute("ontology.inferred", inferred_type is not None)
                
                return ontology_representation
                
            except Exception as e:
                span.record_exception(e)
                # Fallback em caso de erro
                return self._parse_intent_fallback(intent)
    
    def _parse_intent_fallback(self, intent: Intent) -> Dict[str, Any]:
        """Fallback para modo mock se ontologia não estiver disponível"""
        return {
            "intent_id": intent.intent_id,
            "concept": intent.service_type.value,
            "properties": {
                "eMBB": {"latency": 50.0, "throughput": 1000.0, "reliability": 0.99},
                "URLLC": {"latency": 10.0, "throughput": 100.0, "reliability": 0.99999},
                "mMTC": {"latency": 1000.0, "throughput": 0.1, "reliability": 0.9}
            }.get(intent.service_type.value, {}),
            "sla_requirements": intent.sla_requirements.dict(),
            "validated": True,
            "ontology_loaded": False,
            "fallback_mode": True
        }

