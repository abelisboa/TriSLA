"""
Reasoner - SEM-CSMF
Motor de reasoning semântico usando ontologia OWL
"""

from typing import Dict, Any, List, Optional
from opentelemetry import trace

try:
    from owlready2 import sync_reasoner_pellet, World
except ImportError:
    sync_reasoner_pellet = None
    World = None

from .loader import OntologyLoader
from .cache import SemanticCache

tracer = trace.get_tracer(__name__)


class SemanticReasoner:
    """Motor de reasoning semântico"""
    
    def __init__(self, ontology_loader: OntologyLoader, cache: Optional[SemanticCache] = None):
        """
        Inicializa reasoner
        
        Args:
            ontology_loader: Carregador de ontologia
            cache: Cache semântico (opcional, cria novo se None)
        """
        self.ontology_loader = ontology_loader
        self.ontology = None
        self.world = None
        self.cache = cache if cache is not None else SemanticCache()
    
    def initialize(self):
        """Inicializa reasoner com ontologia carregada"""
        try:
            if not self.ontology_loader.is_loaded():
                result = self.ontology_loader.load(apply_reasoning=True)
                if result is None:
                    # Ontologia não pôde ser carregada, usar modo degraded
                    self.ontology = None
                    self.world = None
                    return
            
            self.ontology = self.ontology_loader.ontology
            self.world = self.ontology_loader.world
        except Exception as e:
            # Fallback robusto: continuar sem ontologia
            self.ontology = None
            self.world = None
    
    def infer_slice_type(self, intent_data: Dict[str, Any]) -> Optional[str]:
        """
        Infere tipo de slice baseado em requisitos do intent
        
        Args:
            intent_data: Dados do intent (SLA requirements)
            
        Returns:
            Tipo de slice inferido (eMBB, URLLC, mMTC) ou None
        """
        with tracer.start_as_current_span("infer_slice_type") as span:
            # Verificar cache primeiro
            cached_result = self.cache.get("infer_slice_type", intent_data)
            if cached_result is not None:
                span.set_attribute("cache.hit", True)
                return cached_result
            
            span.set_attribute("cache.hit", False)
            
            try:
                if not self.ontology:
                    self.initialize()
                
                # Se ontologia não foi carregada, usar inferência simplificada
                if not self.ontology:
                    result = self._infer_slice_type_fallback(intent_data)
                    # Cachear resultado mesmo do fallback
                    if result:
                        self.cache.set("infer_slice_type", intent_data, result)
                    return result
                # Extrair requisitos
                latency = self._parse_latency(intent_data.get("latency"))
                throughput = self._parse_throughput(intent_data.get("throughput"))
                reliability = intent_data.get("reliability")
                
                # Query SPARQL para encontrar slice type compatível
                query = f"""
                PREFIX : <http://trisla.org/ontology#>
                SELECT ?sliceType ?latency ?throughput ?reliability
                WHERE {{
                    ?sliceType a :SliceType .
                    ?sliceType :hasLatency ?latency .
                    ?sliceType :hasThroughput ?throughput .
                    ?sliceType :hasReliability ?reliability .
                }}
                """
                
                results = list(self.ontology_loader.query(query))
                
                # Encontrar melhor match
                best_match = None
                best_score = 0.0
                
                for result in results:
                    slice_type = str(result[0]).split("#")[-1]
                    ont_latency = float(result[1]) if result[1] else None
                    ont_throughput = float(result[2]) if result[2] else None
                    ont_reliability = float(result[3]) if result[3] else None
                    
                    score = self._calculate_match_score(
                        latency, throughput, reliability,
                        ont_latency, ont_throughput, ont_reliability
                    )
                    
                    if score > best_score:
                        best_score = score
                        best_match = slice_type
                
                if best_match:
                    # Remover sufixo _Type se presente
                    slice_type = best_match.replace("_Type", "").replace("_Slice", "")
                    span.set_attribute("inferred.slice_type", slice_type)
                    span.set_attribute("inferred.score", best_score)
                    # Cachear resultado
                    self.cache.set("infer_slice_type", intent_data, slice_type)
                    return slice_type
                
                return None
                
            except Exception as e:
                span.record_exception(e)
                # Fallback para inferência simplificada
                return self._infer_slice_type_fallback(intent_data)
    
    def _infer_slice_type_fallback(self, intent_data: Dict[str, Any]) -> Optional[str]:
        """Inferência simplificada quando ontologia não está disponível"""
        latency = intent_data.get("latency")
        throughput = intent_data.get("throughput")
        reliability = intent_data.get("reliability")
        
        # Inferência baseada em valores típicos
        if latency:
            try:
                latency_val = float(str(latency).replace("ms", "").strip())
                if latency_val <= 10:
                    return "URLLC"
                elif latency_val <= 50:
                    return "eMBB"
            except (ValueError, AttributeError):
                pass
        
        if reliability and float(reliability) >= 0.999:
            return "URLLC"
        
        if throughput:
            try:
                throughput_str = str(throughput).upper()
                if "GBPS" in throughput_str:
                    return "eMBB"
                elif "MBPS" in throughput_str:
                    val = float(throughput_str.replace("MBPS", "").strip())
                    if val >= 100:
                        return "eMBB"
            except (ValueError, AttributeError):
                pass
        
        return "eMBB"  # Padrão
    
    def validate_sla_requirements(self, slice_type: str, sla_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida requisitos de SLA contra ontologia
        
        Args:
            slice_type: Tipo de slice (eMBB, URLLC, mMTC)
            sla_requirements: Requisitos de SLA
            
        Returns:
            Dicionário com validação e detalhes
        """
        with tracer.start_as_current_span("validate_sla_requirements") as span:
            # Verificar cache primeiro
            cache_params = {"slice_type": slice_type, **sla_requirements}
            cached_result = self.cache.get("validate_sla_requirements", cache_params)
            if cached_result is not None:
                span.set_attribute("cache.hit", True)
                return cached_result
            
            span.set_attribute("cache.hit", False)
            
            if not self.ontology:
                self.initialize()
            
            try:
                # Buscar indivíduo do tipo de slice
                slice_type_individual = None
                try:
                    if slice_type == "eMBB":
                        slice_type_individual = self.ontology_loader.get_individual("eMBB_Type")
                    elif slice_type == "URLLC":
                        slice_type_individual = self.ontology_loader.get_individual("URLLC_Type")
                    elif slice_type == "mMTC":
                        slice_type_individual = self.ontology_loader.get_individual("mMTC_Type")
                except ValueError:
                    pass
                
                validation_result = {
                    "valid": True,
                    "violations": [],
                    "warnings": []
                }
                
                if slice_type_individual:
                    # Validar latência
                    if "latency" in sla_requirements:
                        req_latency = self._parse_latency(sla_requirements["latency"])
                        ont_latency = getattr(slice_type_individual, "hasLatency", [None])[0]
                        
                        if ont_latency and req_latency:
                            if req_latency > ont_latency:
                                validation_result["valid"] = False
                                validation_result["violations"].append(
                                    f"Latência requerida ({req_latency}ms) excede máximo da ontologia ({ont_latency}ms)"
                                )
                    
                    # Validar throughput
                    if "throughput" in sla_requirements:
                        req_throughput = self._parse_throughput(sla_requirements["throughput"])
                        ont_throughput = getattr(slice_type_individual, "hasThroughput", [None])[0]
                        
                        if ont_throughput and req_throughput:
                            if req_throughput < ont_throughput:
                                validation_result["valid"] = False
                                validation_result["violations"].append(
                                    f"Throughput requerido ({req_throughput}Mbps) abaixo do mínimo da ontologia ({ont_throughput}Mbps)"
                                )
                    
                    # Validar confiabilidade
                    if "reliability" in sla_requirements:
                        req_reliability = float(sla_requirements["reliability"])
                        ont_reliability = getattr(slice_type_individual, "hasReliability", [None])[0]
                        
                        if ont_reliability and req_reliability:
                            if req_reliability < ont_reliability:
                                validation_result["valid"] = False
                                validation_result["violations"].append(
                                    f"Confiabilidade requerida ({req_reliability}) abaixo do mínimo da ontologia ({ont_reliability})"
                                )
                
                span.set_attribute("validation.valid", validation_result["valid"])
                span.set_attribute("validation.violations_count", len(validation_result["violations"]))
                
                # Cachear resultado
                self.cache.set("validate_sla_requirements", cache_params, validation_result)
                
                return validation_result
                
            except Exception as e:
                span.record_exception(e)
                return {
                    "valid": False,
                    "violations": [f"Erro na validação: {str(e)}"],
                    "warnings": []
                }
    
    def _parse_latency(self, latency_str: Optional[str]) -> Optional[float]:
        """Parse de string de latência para float (ms)"""
        if not latency_str:
            return None
        
        try:
            # Remover "ms" e converter
            latency_str = latency_str.replace("ms", "").strip()
            return float(latency_str)
        except (ValueError, AttributeError):
            return None
    
    def _parse_throughput(self, throughput_str: Optional[str]) -> Optional[float]:
        """Parse de string de throughput para float (Mbps)"""
        if not throughput_str:
            return None
        
        try:
            # Converter para Mbps
            throughput_str = throughput_str.upper()
            if "GBPS" in throughput_str:
                value = float(throughput_str.replace("GBPS", "").strip())
                return value * 1000  # Gbps para Mbps
            elif "MBPS" in throughput_str:
                return float(throughput_str.replace("MBPS", "").strip())
            elif "KBPS" in throughput_str:
                value = float(throughput_str.replace("KBPS", "").strip())
                return value / 1000  # Kbps para Mbps
            elif "BPS" in throughput_str:
                value = float(throughput_str.replace("BPS", "").strip())
                return value / 1000000  # bps para Mbps
            else:
                # Tentar parse direto
                return float(throughput_str)
        except (ValueError, AttributeError):
            return None
    
    def _calculate_match_score(self, req_latency, req_throughput, req_reliability,
                              ont_latency, ont_throughput, ont_reliability) -> float:
        """Calcula score de match entre requisitos e ontologia"""
        score = 0.0
        factors = 0
        
        if req_latency and ont_latency:
            # Latência menor é melhor - score baseado em quão próximo está
            if req_latency <= ont_latency:
                score += 1.0
            else:
                # Penalizar se exceder
                score += max(0.0, 1.0 - (req_latency - ont_latency) / ont_latency)
            factors += 1
        
        if req_throughput and ont_throughput:
            # Throughput maior é melhor
            if req_throughput >= ont_throughput:
                score += 1.0
            else:
                score += max(0.0, req_throughput / ont_throughput)
            factors += 1
        
        if req_reliability and ont_reliability:
            # Confiabilidade maior é melhor
            if req_reliability >= ont_reliability:
                score += 1.0
            else:
                score += max(0.0, req_reliability / ont_reliability)
            factors += 1
        
        return score / factors if factors > 0 else 0.0

