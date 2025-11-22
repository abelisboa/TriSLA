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

tracer = trace.get_tracer(__name__)


class IntentProcessor:
    """Processa intents através do pipeline semântico"""
    
    def __init__(self, ontology_path: Optional[str] = None):
        """
        Inicializa processador de intents com ontologia OWL real
        
        Args:
            ontology_path: Caminho para arquivo .owl (opcional, usa padrão se None)
        """
        self.ontology_parser = OntologyParser(ontology_path=ontology_path)
        self.semantic_matcher = SemanticMatcher(ontology_parser=self.ontology_parser)
    
    async def validate_semantic(self, intent: Intent) -> Intent:
        """
        Valida intent semanticamente usando ontologias
        Intent → Ontology
        """
        with tracer.start_as_current_span("validate_semantic") as span:
            span.set_attribute("intent.id", intent.intent_id)
            
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
                "sla_requirements": intent.sla_requirements.dict(),
                "template": self._create_gst_template(intent)
            }
            
            span.set_attribute("gst.id", gst["gst_id"])
            return gst
    
    def _create_gst_template(self, intent: Intent) -> Dict[str, Any]:
        """
        Cria template GST baseado no tipo de slice e requisitos validados
        Usa informações da ontologia OWL para gerar template correto
        """
        base_template = {
            "slice_type": intent.service_type.value,
            "sla": intent.sla_requirements.dict()
        }
        
        # Mapear tipo de slice para SST conforme 3GPP TS 28.541
        sst_map = {
            "eMBB": 1,
            "URLLC": 2,
            "mMTC": 3
        }
        
        sst = sst_map.get(intent.service_type.value, 0)
        base_template["sst"] = sst
        base_template["sd"] = f"{intent.service_type.value.lower()}-{intent.intent_id}"
        
        # Templates específicos por tipo baseados na ontologia
        sla = intent.sla_requirements
        
        if intent.service_type.value == "eMBB":
            base_template.update({
                "priority": "high_throughput",
                "qos": {
                    "guaranteed_bitrate": sla.throughput or "100Mbps",
                    "maximum_bitrate": "1Gbps",
                    "latency": sla.latency or "50ms"
                }
            })
        elif intent.service_type.value == "URLLC":
            base_template.update({
                "priority": "low_latency",
                "qos": {
                    "latency": sla.latency or "1ms",
                    "reliability": sla.reliability or 0.99999,
                    "jitter": sla.jitter or "1ms"
                }
            })
        elif intent.service_type.value == "mMTC":
            base_template.update({
                "priority": "high_density",
                "qos": {
                    "device_density": "1000000/km²",
                    "data_rate": "160bps",
                    "latency": sla.latency or "1000ms"
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
                "sla_requirements": intent.sla_requirements.dict(),
                "nest_status": nest_status,
                "timestamp": self._get_timestamp()
            }
            
            span.set_attribute("metadata.intent_id", intent.intent_id)
            return metadata
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp atual em ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"

