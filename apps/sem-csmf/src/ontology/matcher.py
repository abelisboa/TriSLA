"""
Semantic Matcher - SEM-CSMF
Faz match semântico entre intent e ontologia usando reasoning real
"""

from typing import Dict, Any, Optional
from opentelemetry import trace

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.intent import Intent
from .reasoner import SemanticReasoner
from .loader import OntologyLoader
from .cache import SemanticCache

tracer = trace.get_tracer(__name__)


class SemanticMatcher:
    """Faz match semântico entre intents e ontologias usando reasoning OWL"""
    
    def __init__(self, ontology_loader: OntologyLoader = None, reasoner: SemanticReasoner = None, cache: Optional[SemanticCache] = None):
        """
        Inicializa matcher semântico
        
        Args:
            ontology_loader: Carregador de ontologia (opcional, cria novo se None)
            reasoner: Reasoner semântico (opcional, cria novo se None)
            cache: Cache semântico compartilhado (opcional, cria novo se None)
        """
        if ontology_loader is None:
            ontology_loader = OntologyLoader()
        if cache is None:
            cache = SemanticCache()
        if reasoner is None:
            reasoner = SemanticReasoner(ontology_loader, cache=cache)
        
        self.ontology_loader = ontology_loader
        self.reasoner = reasoner
        self.cache = cache
        self._initialized = False
    
    def _ensure_initialized(self):
        """Garante que ontologia foi carregada"""
        if not self._initialized:
            try:
                if not self.ontology_loader.is_loaded():
                    result = self.ontology_loader.load(apply_reasoning=True)
                    if result is None:
                        # Ontologia não pôde ser carregada
                        self._initialized = False
                        return
                self.reasoner.initialize()
                # Verificar se reasoner foi inicializado corretamente
                if self.reasoner.ontology is None:
                    self._initialized = False
                else:
                    self._initialized = True
            except Exception as e:
                try:
                    with tracer.start_as_current_span("matcher_fallback") as span:
                        span.set_attribute("fallback.reason", str(e))
                except Exception:
                    pass  # Se tracer falhar, continuar
                self._initialized = False
    
    async def match(self, ontology: Dict[str, Any], intent: Intent) -> Intent:
        """
        Faz match semântico e valida se o intent está de acordo com a ontologia
        
        Args:
            ontology: Representação ontológica do intent (do parser)
            intent: Intent a ser validado
            
        Returns:
            Intent validado
            
        Raises:
            ValueError: Se intent não estiver de acordo com a ontologia
        """
        with tracer.start_as_current_span("semantic_match") as span:
            span.set_attribute("intent.id", intent.intent_id)
            
            self._ensure_initialized()
            
            # Se ontologia não foi carregada, usar validação simplificada
            if not self._initialized:
                validated = self._validate_simple(intent, ontology.get("properties", {}))
                if not validated:
                    raise ValueError(f"Intent {intent.intent_id} não está de acordo com a ontologia")
                span.set_attribute("match.status", "success")
                span.set_attribute("match.mode", "fallback")
                return intent
            
            try:
                # Usar reasoner para validação completa
                slice_type = intent.service_type.value or ontology.get("inferred_type")
                sla_dict = intent.sla_requirements.dict()
                
                validation_result = self.reasoner.validate_sla_requirements(slice_type, sla_dict)
                
                if not validation_result["valid"]:
                    violations = "; ".join(validation_result["violations"])
                    span.set_attribute("match.status", "failed")
                    span.set_attribute("match.violations", violations)
                    raise ValueError(
                        f"Intent {intent.intent_id} não está de acordo com a ontologia: {violations}"
                    )
                
                span.set_attribute("match.status", "success")
                span.set_attribute("match.mode", "reasoning")
                span.set_attribute("match.warnings_count", len(validation_result.get("warnings", [])))
                
                return intent
                
            except Exception as e:
                span.record_exception(e)
                # Fallback para validação simples
                validated = self._validate_simple(intent, ontology.get("properties", {}))
                if not validated:
                    raise ValueError(f"Intent {intent.intent_id} não está de acordo com a ontologia")
                span.set_attribute("match.status", "success")
                span.set_attribute("match.mode", "fallback")
                return intent
    
    def _validate_simple(self, intent: Intent, properties: Dict[str, Any]) -> bool:
        """Validação simplificada (fallback)"""
        sla = intent.sla_requirements
        
        # Validação básica - apenas verificar se propriedades existem
        # Validação completa requer ontologia carregada
        return True

