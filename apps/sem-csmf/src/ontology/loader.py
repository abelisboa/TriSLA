"""
Ontology Loader - SEM-CSMF
Carrega ontologia OWL usando owlready2
"""

from typing import Optional
from opentelemetry import trace
import os

try:
    from owlready2 import get_ontology, sync_reasoner_pellet, World
except ImportError:
    # Fallback se owlready2 não estiver disponível
    get_ontology = None
    sync_reasoner_pellet = None
    World = None

tracer = trace.get_tracer(__name__)


class OntologyLoader:
    """Carregador de ontologia OWL"""
    
    def __init__(self, ontology_path: Optional[str] = None):
        """
        Inicializa carregador de ontologia
        
        Args:
            ontology_path: Caminho para arquivo .ttl ou .owl. 
                          Se None, usa caminho padrão.
        """
        if ontology_path is None:
            # Caminho padrão relativo ao módulo
            current_dir = os.path.dirname(os.path.abspath(__file__))
            ontology_path = os.path.join(current_dir, "trisla.ttl")
        
        self.ontology_path = ontology_path
        self.ontology = None
        self.world = None
        self._loaded = False
    
    def load(self, apply_reasoning: bool = True):
        """
        Carrega ontologia OWL
        
        Args:
            apply_reasoning: Se True, aplica reasoning semântico
        """
        with tracer.start_as_current_span("load_ontology") as span:
            if get_ontology is None:
                raise ImportError(
                    "owlready2 não está instalado. "
                    "Instale com: pip install owlready2"
                )
            
            try:
                span.set_attribute("ontology.path", self.ontology_path)
                
                # Carregar ontologia (owlready2 gerencia o mundo automaticamente)
                ontology_uri = f"file://{os.path.abspath(self.ontology_path)}"
                self.ontology = get_ontology(ontology_uri)
                self.ontology.load()
                
                # Obter mundo da ontologia
                self.world = self.ontology.world
                
                span.set_attribute("ontology.loaded", True)
                
                # Aplicar reasoning se solicitado
                if apply_reasoning:
                    try:
                        sync_reasoner_pellet(self.world, infer_property_values=True, infer_data_property_values=True)
                        span.set_attribute("ontology.reasoning_applied", True)
                    except Exception as e:
                        # Se Pellet não estiver disponível, continuar sem reasoning
                        span.set_attribute("ontology.reasoning_applied", False)
                        span.set_attribute("ontology.reasoning_error", str(e))
                
                self._loaded = True
                
                return self.ontology
                
            except Exception as e:
                span.record_exception(e)
                span.set_attribute("ontology.loaded", False)
                raise
    
    def get_class(self, class_name: str):
        """Obtém classe da ontologia"""
        if not self._loaded:
            raise RuntimeError("Ontologia não foi carregada. Chame load() primeiro.")
        
        try:
            return getattr(self.ontology, class_name)
        except AttributeError:
            raise ValueError(f"Classe '{class_name}' não encontrada na ontologia")
    
    def get_individual(self, individual_name: str):
        """Obtém indivíduo da ontologia"""
        if not self._loaded:
            raise RuntimeError("Ontologia não foi carregada. Chame load() primeiro.")
        
        try:
            return getattr(self.ontology, individual_name)
        except AttributeError:
            raise ValueError(f"Indivíduo '{individual_name}' não encontrado na ontologia")
    
    def query(self, sparql_query: str):
        """
        Executa query SPARQL na ontologia
        
        Args:
            sparql_query: Query SPARQL
            
        Returns:
            Resultados da query
        """
        if not self._loaded:
            raise RuntimeError("Ontologia não foi carregada. Chame load() primeiro.")
        
        with tracer.start_as_current_span("sparql_query") as span:
            try:
                results = self.world.sparql(sparql_query)
                span.set_attribute("query.results_count", len(list(results)))
                return results
            except Exception as e:
                span.record_exception(e)
                raise
    
    def is_loaded(self) -> bool:
        """Verifica se ontologia foi carregada"""
        return self._loaded

