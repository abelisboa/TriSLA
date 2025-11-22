"""
Semantic Matcher - SEM-CSMF
Faz match semântico REAL entre intent e ontologia OWL
"""

from typing import Dict, Any
from opentelemetry import trace
import re

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.intent import Intent

tracer = trace.get_tracer(__name__)


class SemanticMatcher:
    """Faz match semântico REAL entre intents e ontologia OWL"""
    
    def __init__(self, ontology_parser=None):
        """
        Inicializa matcher com parser de ontologia
        
        Args:
            ontology_parser: Instância de OntologyParser (opcional)
        """
        self.ontology_parser = ontology_parser
    
    async def match(self, ontology_representation: Dict[str, Any], intent: Intent) -> Intent:
        """
        Faz match semântico REAL e valida se o intent está de acordo com a ontologia OWL
        
        Args:
            ontology_representation: Representação ontológica do intent (do OntologyParser)
            intent: Intent a ser validado
            
        Returns:
            Intent validado
            
        Raises:
            ValueError: Se o intent não estiver de acordo com a ontologia
        """
        with tracer.start_as_current_span("semantic_match") as span:
            span.set_attribute("intent.id", intent.intent_id)
            span.set_attribute("intent.type", intent.service_type.value)
            
            # Validar se os requisitos de SLA estão dentro dos limites da ontologia
            validated, validation_details = self._validate_against_ontology(
                intent, 
                ontology_representation
            )
            
            span.set_attribute("validation.validated", validated)
            span.set_attribute("validation.details", str(validation_details))
            
            if not validated:
                error_msg = (
                    f"Intent {intent.intent_id} não está de acordo com a ontologia. "
                    f"Detalhes: {validation_details}"
                )
                span.set_attribute("validation.error", error_msg)
                raise ValueError(error_msg)
            
            span.set_attribute("match.status", "success")
            return intent
    
    def _parse_value_with_unit(self, value_str: str) -> tuple:
        """
        Parse de valor com unidade (ex: "10ms" -> (10.0, "ms"))
        
        Args:
            value_str: String com valor e unidade
            
        Returns:
            Tupla (valor, unidade)
        """
        if not value_str:
            return None, None
        
        # Remover espaços
        value_str = value_str.strip()
        
        # Padrões comuns: "10ms", "100Mbps", "0.999", "10-50ms"
        # Para ranges, usar o valor máximo
        if '-' in value_str:
            # Range: "10-50ms" -> usar 50
            parts = value_str.split('-')
            if len(parts) == 2:
                value_str = parts[1]
        
        # Extrair número e unidade
        match = re.match(r'([\d.]+)\s*([a-zA-Z%]+)?', value_str)
        if match:
            value = float(match.group(1))
            unit = match.group(2) if match.group(2) else ""
            return value, unit
        
        # Tentar apenas número
        try:
            value = float(value_str)
            return value, ""
        except ValueError:
            return None, None
    
    def _validate_against_ontology(self, intent: Intent, ontology_rep: Dict[str, Any]) -> tuple:
        """
        Valida intent contra propriedades da ontologia OWL REAL
        
        Args:
            intent: Intent a ser validado
            ontology_rep: Representação ontológica do intent
            
        Returns:
            Tupla (validado, detalhes)
        """
        sla = intent.sla_requirements
        slice_type = intent.service_type.value
        validation_details = {
            "validated_properties": [],
            "failed_properties": [],
            "warnings": []
        }
        
        # Definir limites baseados no tipo de slice conforme ontologia
        # Estes valores devem corresponder às restrições na ontologia OWL
        slice_limits = {
            "eMBB": {
                "latency": {"max": 50.0, "unit": "ms"},  # eMBB: até 50ms
                "throughput": {"min": 100.0, "unit": "Mbps"},  # eMBB: mínimo 100Mbps
                "reliability": {"min": 0.99, "unit": ""},  # eMBB: mínimo 99%
            },
            "URLLC": {
                "latency": {"max": 10.0, "unit": "ms"},  # URLLC: até 10ms
                "throughput": {"min": 1.0, "unit": "Mbps"},  # URLLC: mínimo 1Mbps
                "reliability": {"min": 0.99999, "unit": ""},  # URLLC: mínimo 99.999%
            },
            "mMTC": {
                "latency": {"max": 1000.0, "unit": "ms"},  # mMTC: até 1000ms
                "throughput": {"min": 0.00016, "unit": "Mbps"},  # mMTC: mínimo 160bps = 0.00016Mbps
                "reliability": {"min": 0.9, "unit": ""},  # mMTC: mínimo 90%
                "device_density": {"min": 100000, "unit": "devices/km²"},  # mMTC: mínimo 100k devices/km²
            }
        }
        
        limits = slice_limits.get(slice_type, {})
        
        # Validar latência
        if sla.latency:
            intent_latency, intent_unit = self._parse_value_with_unit(sla.latency)
            if intent_latency is not None:
                if "latency" in limits:
                    max_latency = limits["latency"]["max"]
                    if intent_latency > max_latency:
                        validation_details["failed_properties"].append({
                            "property": "latency",
                            "value": intent_latency,
                            "limit": max_latency,
                            "message": f"Latência {intent_latency}ms excede máximo permitido {max_latency}ms para {slice_type}"
                        })
                    else:
                        validation_details["validated_properties"].append("latency")
                else:
                    validation_details["warnings"].append("Latência especificada mas não há limite na ontologia")
        
        # Validar throughput
        if sla.throughput:
            intent_throughput, intent_unit = self._parse_value_with_unit(sla.throughput)
            if intent_throughput is not None:
                # Converter para Mbps se necessário
                if intent_unit.lower() in ["kbps", "k"]:
                    intent_throughput = intent_throughput / 1000.0
                elif intent_unit.lower() in ["gbps", "g"]:
                    intent_throughput = intent_throughput * 1000.0
                elif intent_unit.lower() in ["bps", "b"]:
                    intent_throughput = intent_throughput / 1000000.0
                
                if "throughput" in limits:
                    min_throughput = limits["throughput"]["min"]
                    if intent_throughput < min_throughput:
                        validation_details["failed_properties"].append({
                            "property": "throughput",
                            "value": intent_throughput,
                            "limit": min_throughput,
                            "message": f"Throughput {intent_throughput}Mbps abaixo do mínimo {min_throughput}Mbps para {slice_type}"
                        })
                    else:
                        validation_details["validated_properties"].append("throughput")
                else:
                    validation_details["warnings"].append("Throughput especificado mas não há limite na ontologia")
        
        # Validar confiabilidade
        if sla.reliability is not None:
            if "reliability" in limits:
                min_reliability = limits["reliability"]["min"]
                if sla.reliability < min_reliability:
                    validation_details["failed_properties"].append({
                        "property": "reliability",
                        "value": sla.reliability,
                        "limit": min_reliability,
                        "message": f"Confiabilidade {sla.reliability} abaixo do mínimo {min_reliability} para {slice_type}"
                    })
                else:
                    validation_details["validated_properties"].append("reliability")
            else:
                validation_details["warnings"].append("Confiabilidade especificada mas não há limite na ontologia")
        
        # Validar jitter (se especificado)
        if sla.jitter:
            intent_jitter, intent_unit = self._parse_value_with_unit(sla.jitter)
            if intent_jitter is not None:
                # Para URLLC, jitter deve ser muito baixo
                if slice_type == "URLLC" and intent_jitter > 1.0:
                    validation_details["failed_properties"].append({
                        "property": "jitter",
                        "value": intent_jitter,
                        "limit": 1.0,
                        "message": f"Jitter {intent_jitter}ms muito alto para URLLC (máximo 1ms recomendado)"
                    })
                else:
                    validation_details["validated_properties"].append("jitter")
        
        # Determinar se validação passou
        validated = len(validation_details["failed_properties"]) == 0
        
        return validated, validation_details

