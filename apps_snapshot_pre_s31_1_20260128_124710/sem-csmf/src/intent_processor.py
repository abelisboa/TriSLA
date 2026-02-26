"""
Processador de Intents - SEM-CSMF
Pipeline: Intent → Ontology → GST
"""

from typing import Dict, Any, Optional
from opentelemetry import trace

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.intent import Intent, SLARequirements
from ontology.parser import OntologyParser
from ontology.matcher import SemanticMatcher

try:
    from nlp.parser import NLPParser
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
    NLPParser = None

tracer = trace.get_tracer(__name__)


class IntentProcessor:
    """Processa intents através do pipeline semântico"""
    
    def __init__(self):
        self.ontology_parser = OntologyParser()
        self.semantic_matcher = SemanticMatcher(
            ontology_loader=self.ontology_parser.ontology_loader
        )
        if NLP_AVAILABLE:
            self.nlp_parser = NLPParser()
        else:
            self.nlp_parser = None
    
    async def validate_semantic(self, intent: Intent, intent_text: Optional[str] = None) -> Intent:
        """
        Valida intent semanticamente usando ontologias
        Intent → Ontology
        
        Args:
            intent: Intent a ser validado
            intent_text: Texto em linguagem natural (opcional, para NLP)
        """
        with tracer.start_as_current_span("validate_semantic") as span:
            span.set_attribute("intent.id", intent.intent_id)
            
            # Se texto em linguagem natural fornecido, processar com NLP
            if intent_text and self.nlp_parser:
                try:
                    nlp_result = self.nlp_parser.parse_intent_text(intent_text)
                    
                    # Atualizar intent com informações extraídas do NLP
                    if nlp_result.get("slice_type") and not intent.service_type.value:
                        from models.intent import SliceType
                        try:
                            intent.service_type = SliceType[nlp_result["slice_type"].upper()]
                        except (KeyError, AttributeError):
                            pass
                    
                    # Atualizar requisitos de SLA se extraídos
                    if nlp_result.get("requirements"):
                        req = nlp_result["requirements"]
                        if "latency" in req and not intent.sla_requirements.latency:
                            intent.sla_requirements.latency = req["latency"]
                        if "throughput" in req and not intent.sla_requirements.throughput:
                            intent.sla_requirements.throughput = req["throughput"]
                        if "reliability" in req and not intent.sla_requirements.reliability:
                            intent.sla_requirements.reliability = req["reliability"]
                        if "jitter" in req and not intent.sla_requirements.jitter:
                            intent.sla_requirements.jitter = req["jitter"]
                        if "coverage" in req and not intent.sla_requirements.coverage:
                            intent.sla_requirements.coverage = req["coverage"]
                    
                    span.set_attribute("nlp.processed", True)
                except Exception as e:
                    span.set_attribute("nlp.error", str(e))
                    span.set_attribute("nlp.processed", False)
            
            # Parse da ontologia
            ontology = await self.ontology_parser.parse_intent(intent)
            
            # Match semântico
            validated = await self.semantic_matcher.match(ontology, intent)
            
            span.set_attribute("validation.status", "success")
            return validated
    
    async def generate_gst(self, intent: Intent) -> Dict[str, Any]:
        """
        Gera GST (Generation Service Template) a partir do intent validado
        Ontology → GST
        """
        with tracer.start_as_current_span("generate_gst") as span:
            span.set_attribute("intent.id", intent.intent_id)
            
            gst = {
                "gst_id": f"gst-{intent.intent_id}",
                "intent_id": intent.intent_id,
                "service_type": intent.service_type.value,
                "sla_requirements": intent.sla_requirements.model_dump(),
                "template": self._create_gst_template(intent)
            }
            
            span.set_attribute("gst.id", gst["gst_id"])
            return gst
    
    def _create_gst_template(self, intent: Intent) -> Dict[str, Any]:
        """Cria template GST baseado no tipo de slice"""
        base_template = {
            "slice_type": intent.service_type.value,
            "sla": intent.sla_requirements.model_dump()
        }
        
        # Templates específicos por tipo
        if intent.service_type.value == "eMBB":
            base_template.update({
                "priority": "high_throughput",
                "qos": {
                    "guaranteed_bitrate": "100Mbps",
                    "maximum_bitrate": "1Gbps"
                }
            })
        elif intent.service_type.value == "URLLC":
            base_template.update({
                "priority": "low_latency",
                "qos": {
                    "latency": "1ms",
                    "reliability": "0.99999"
                }
            })
        elif intent.service_type.value == "mMTC":
            base_template.update({
                "priority": "high_density",
                "qos": {
                    "device_density": "1000000/km²",
                    "data_rate": "160bps"
                }
            })
        
        return base_template
    
    async def generate_metadata(self, intent: Intent, nest) -> Dict[str, Any]:
        """
        Gera metadados para envio ao Decision Engine via I-01
        Metadados → I-01 → Decision Engine
        """
        from models.nest import NEST
        
        with tracer.start_as_current_span("generate_metadata") as span:
            # nest pode ser um objeto NEST ou um dict
            if isinstance(nest, NEST):
                nest_id = nest.nest_id
                nest_status = nest.status.value if hasattr(nest.status, 'value') else str(nest.status)
            else:
                nest_id = nest.get("nest_id") if isinstance(nest, dict) else None
                nest_status = nest.get("status") if isinstance(nest, dict) else None
            
            metadata = {
                "intent_id": intent.intent_id,
                "nest_id": nest_id,
                "tenant_id": intent.tenant_id,
                "service_type": intent.service_type.value,
                "sla_requirements": intent.sla_requirements.model_dump(),
                "nest_status": nest_status,
                "timestamp": self._get_timestamp()
            }
            
            span.set_attribute("metadata.intent_id", intent.intent_id)
            return metadata
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp atual em ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

