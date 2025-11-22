"""
Parser de Ontologias - SEM-CSMF
Processa intents usando ontologia OWL real
"""

from typing import Dict, Any, Optional
from opentelemetry import trace
import os
import sys

# Adicionar owlready2 para manipulação de ontologia OWL
try:
    from owlready2 import get_ontology, sync_reasoner_pellet, World
except ImportError:
    # Fallback para rdflib se owlready2 não estiver disponível
    from rdflib import Graph, Namespace, RDF, RDFS, OWL
    owlready2_available = False
else:
    owlready2_available = True

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.intent import Intent

tracer = trace.get_tracer(__name__)


class OntologyParser:
    """Parser de ontologias OWL para validação semântica REAL"""
    
    def __init__(self, ontology_path: Optional[str] = None):
        """
        Inicializa parser com ontologia OWL real
        
        Args:
            ontology_path: Caminho para arquivo .owl (padrão: trisla.owl no diretório atual)
        """
        if ontology_path is None:
            # Caminho padrão: arquivo trisla.owl no mesmo diretório
            current_dir = os.path.dirname(os.path.abspath(__file__))
            ontology_path = os.path.join(current_dir, "trisla.owl")
        
        if not os.path.exists(ontology_path):
            raise FileNotFoundError(
                f"Ontologia OWL não encontrada em: {ontology_path}. "
                "Certifique-se de que o arquivo trisla.owl existe."
            )
        
        self.ontology_path = ontology_path
        self.ontology = self._load_ontology()
        self._apply_reasoning()
    
    def _load_ontology(self):
        """
        Carrega ontologia OWL real do arquivo
        Usa owlready2 (preferencial) ou rdflib como fallback
        """
        with tracer.start_as_current_span("load_ontology") as span:
            span.set_attribute("ontology.path", self.ontology_path)
            
            if owlready2_available:
                try:
                    # Carregar ontologia usando owlready2
                    onto = get_ontology(f"file://{os.path.abspath(self.ontology_path)}").load()
                    span.set_attribute("ontology.loader", "owlready2")
                    span.set_attribute("ontology.loaded", True)
                    return onto
                except Exception as e:
                    span.record_exception(e)
                    raise RuntimeError(f"Erro ao carregar ontologia com owlready2: {e}")
            else:
                # Fallback para rdflib
                try:
                    graph = Graph()
                    graph.parse(self.ontology_path, format="xml")
                    span.set_attribute("ontology.loader", "rdflib")
                    span.set_attribute("ontology.loaded", True)
                    return graph
                except Exception as e:
                    span.record_exception(e)
                    raise RuntimeError(f"Erro ao carregar ontologia com rdflib: {e}")
    
    def _apply_reasoning(self):
        """Aplica reasoning semântico na ontologia"""
        with tracer.start_as_current_span("apply_reasoning") as span:
            if owlready2_available and hasattr(self.ontology, 'sync_reasoner_pellet'):
                try:
                    # Aplicar reasoner Pellet (se disponível)
                    sync_reasoner_pellet(self.ontology, infer_property_values=True, infer_data_property_values=True)
                    span.set_attribute("reasoning.applied", True)
                    span.set_attribute("reasoner", "pellet")
                except Exception as e:
                    # Se Pellet não estiver disponível, continuar sem reasoning
                    span.set_attribute("reasoning.applied", False)
                    span.set_attribute("reasoning.warning", "Pellet não disponível, continuando sem reasoning")
            else:
                span.set_attribute("reasoning.applied", False)
                span.set_attribute("reasoning.note", "Reasoning não disponível com rdflib")
    
    def _get_slice_class(self, slice_type: str):
        """Obtém classe OWL correspondente ao tipo de slice"""
        if owlready2_available:
            # Usar owlready2
            slice_type_map = {
                "eMBB": getattr(self.ontology, "eMBBSlice", None),
                "URLLC": getattr(self.ontology, "URLLCSlice", None),
                "mMTC": getattr(self.ontology, "mMTCSlice", None),
            }
            return slice_type_map.get(slice_type)
        else:
            # Usar rdflib
            TRISLA = Namespace("http://www.semanticweb.org/trisla/ontologies/2025/trisla#")
            slice_type_map = {
                "eMBB": TRISLA.eMBBSlice,
                "URLLC": TRISLA.URLLCSlice,
                "mMTC": TRISLA.mMTCSlice,
            }
            return slice_type_map.get(slice_type)
    
    def _extract_properties_from_ontology(self, slice_class) -> Dict[str, Any]:
        """Extrai propriedades da classe de slice da ontologia"""
        properties = {}
        
        if owlready2_available:
            # Usar owlready2 para extrair propriedades
            if slice_class:
                # Obter restrições da classe
                for restriction in slice_class.is_a:
                    if hasattr(restriction, 'property') and hasattr(restriction, 'value'):
                        prop_name = restriction.property.name
                        prop_value = restriction.value
                        properties[prop_name] = prop_value
        else:
            # Usar rdflib para consultar propriedades
            if slice_class:
                TRISLA = Namespace("http://www.semanticweb.org/trisla/ontologies/2025/trisla#")
                # Consultar propriedades usando SPARQL ou navegação RDF
                # Por enquanto, retornar estrutura básica
                properties = {
                    "hasLatency": None,
                    "hasThroughput": None,
                    "hasReliability": None,
                }
        
        return properties
    
    async def parse_intent(self, intent: Intent) -> Dict[str, Any]:
        """
        Parse do intent usando ontologia OWL REAL
        Retorna representação ontológica do intent baseada na ontologia carregada
        """
        with tracer.start_as_current_span("parse_intent_ontology") as span:
            span.set_attribute("intent.id", intent.intent_id)
            span.set_attribute("intent.type", intent.service_type.value)
            
            # Obter classe de slice correspondente da ontologia
            slice_class = self._get_slice_class(intent.service_type.value)
            
            if slice_class is None:
                raise ValueError(
                    f"Tipo de slice '{intent.service_type.value}' não encontrado na ontologia. "
                    "Tipos suportados: eMBB, URLLC, mMTC"
                )
            
            # Extrair propriedades da ontologia
            ontology_properties = self._extract_properties_from_ontology(slice_class)
            
            # Construir representação ontológica
            ontology_representation = {
                "intent_id": intent.intent_id,
                "concept": intent.service_type.value,
                "slice_class_iri": str(slice_class) if hasattr(slice_class, '__str__') else None,
                "properties": ontology_properties,
                "sla_requirements": intent.sla_requirements.dict(),
                "validated": False  # Será validado pelo SemanticMatcher
            }
            
            span.set_attribute("ontology.concept", intent.service_type.value)
            span.set_attribute("ontology.class_found", slice_class is not None)
            
            return ontology_representation
    
    def get_ontology(self):
        """Retorna a ontologia carregada para uso externo"""
        return self.ontology

