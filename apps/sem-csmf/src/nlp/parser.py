"""
NLP Parser - SEM-CSMF
Parser de linguagem natural para extração de requisitos de intent
"""

from typing import Dict, Any, Optional, List
from opentelemetry import trace
import re

try:
    import spacy
    from spacy import displacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None

tracer = trace.get_tracer(__name__)


class NLPParser:
    """Parser de linguagem natural para intents"""
    
    def __init__(self, language: str = "en"):
        """
        Inicializa parser NLP
        
        Args:
            language: Idioma ("en" para inglês, "pt" para português)
        """
        self.language = language
        self.nlp = None
        self._initialized = False
        
        if SPACY_AVAILABLE:
            self._load_model()
    
    def _load_model(self):
        """Carrega modelo spaCy"""
        try:
            if self.language == "pt":
                model_name = "pt_core_news_sm"
            else:
                model_name = "en_core_web_sm"
            
            self.nlp = spacy.load(model_name)
            self._initialized = True
        except OSError:
            # Modelo não instalado, usar fallback
            try:
                current_tracer = trace.get_tracer(__name__)
                with current_tracer.start_as_current_span("nlp_fallback") as span:
                    span.set_attribute("fallback.reason", f"Modelo {model_name} não encontrado")
            except Exception:
                pass  # Se tracer falhar, continuar sem tracing
            self._initialized = False
    
    def parse_intent_text(self, intent_text: str) -> Dict[str, Any]:
        """
        Parse de texto em linguagem natural para extrair requisitos
        
        Args:
            intent_text: Texto do intent em linguagem natural
            
        Returns:
            Dicionário com requisitos extraídos
        """
        with tracer.start_as_current_span("parse_intent_text") as span:
            span.set_attribute("intent_text.length", len(intent_text))
            
            # Extrair requisitos usando regex (funciona mesmo sem spaCy)
            requirements = self._extract_requirements_regex(intent_text)
            
            # Se spaCy estiver disponível, usar para melhorar extração
            if self._initialized and self.nlp:
                requirements = self._extract_requirements_spacy(intent_text, requirements)
            
            # Inferir tipo de slice
            slice_type = self._infer_slice_type(intent_text, requirements)
            
            result = {
                "slice_type": slice_type,
                "requirements": requirements,
                "original_text": intent_text,
                "nlp_available": self._initialized
            }
            
            span.set_attribute("extracted.slice_type", slice_type)
            span.set_attribute("extracted.requirements_count", len(requirements))
            
            return result
    
    def _extract_requirements_regex(self, text: str) -> Dict[str, Any]:
        """Extrai requisitos usando regex (fallback se spaCy não estiver disponível)"""
        requirements = {}
        text_lower = text.lower()
        
        # Extrair latência
        latency_patterns = [
            r'lat[êe]ncia\s*(?:m[áa]xima|max)?\s*(?:de|of)?\s*(\d+(?:\.\d+)?)\s*ms',
            r'latency\s*(?:max|maximum)?\s*(?:of)?\s*(\d+(?:\.\d+)?)\s*ms',
            r'(\d+(?:\.\d+)?)\s*ms\s*(?:de\s*)?lat[êe]ncia',
            r'(\d+(?:\.\d+)?)\s*ms\s*(?:of\s*)?latency'
        ]
        for pattern in latency_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                requirements["latency"] = f"{match.group(1)}ms"
                break
        
        # Extrair throughput
        throughput_patterns = [
            r'throughput\s*(?:m[íi]nimo|min|minimum)?\s*(?:de|of)?\s*(\d+(?:\.\d+)?)\s*(?:mbps|gbps|kbps)',
            r'(\d+(?:\.\d+)?)\s*(?:mbps|gbps|kbps)\s*(?:de\s*)?throughput',
            r'largura\s*de\s*banda\s*(?:m[íi]nima|min)?\s*(?:de|of)?\s*(\d+(?:\.\d+)?)\s*(?:mbps|gbps|kbps)',
            r'bandwidth\s*(?:min|minimum)?\s*(?:of)?\s*(\d+(?:\.\d+)?)\s*(?:mbps|gbps|kbps)'
        ]
        for pattern in throughput_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                unit = re.search(r'(mbps|gbps|kbps)', text_lower, re.IGNORECASE)
                unit_str = unit.group(1).upper() if unit else "Mbps"
                requirements["throughput"] = f"{match.group(1)}{unit_str}"
                break
        
        # Extrair confiabilidade
        reliability_patterns = [
            r'confiabilidade\s*(?:de|of)?\s*(\d+(?:\.\d+)?)%',
            r'reliability\s*(?:of)?\s*(\d+(?:\.\d+)?)%',
            r'(\d+(?:\.\d+)?)%\s*(?:de\s*)?confiabilidade',
            r'(\d+(?:\.\d+)?)%\s*(?:of\s*)?reliability'
        ]
        for pattern in reliability_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                reliability_value = float(match.group(1)) / 100.0
                requirements["reliability"] = reliability_value
                break
        
        # Extrair jitter
        jitter_patterns = [
            r'jitter\s*(?:m[áa]ximo|max|maximum)?\s*(?:de|of)?\s*(\d+(?:\.\d+)?)\s*ms',
            r'(\d+(?:\.\d+)?)\s*ms\s*(?:de\s*)?jitter'
        ]
        for pattern in jitter_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                requirements["jitter"] = f"{match.group(1)}ms"
                break
        
        # Extrair cobertura
        coverage_patterns = [
            r'cobertura\s*(?:de|of)?\s*(urbana|rural|urban|rural)',
            r'coverage\s*(?:of)?\s*(urbana|rural|urban|rural)'
        ]
        for pattern in coverage_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                requirements["coverage"] = match.group(1).capitalize()
                break
        
        return requirements
    
    def _extract_requirements_spacy(self, text: str, existing_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Melhora extração usando spaCy"""
        if not self.nlp:
            return existing_requirements
        
        doc = self.nlp(text)
        requirements = existing_requirements.copy()
        
        # Usar Named Entity Recognition (NER) para encontrar valores numéricos
        for ent in doc.ents:
            if ent.label_ in ["CARDINAL", "QUANTITY"]:
                # Verificar contexto para determinar tipo de métrica
                context = doc[max(0, ent.start-3):min(len(doc), ent.end+3)].text.lower()
                
                if "latency" in context or "latência" in context:
                    if "ms" in context:
                        requirements["latency"] = f"{ent.text}ms"
                elif "throughput" in context or "bandwidth" in context:
                    if any(unit in context for unit in ["mbps", "gbps", "kbps"]):
                        requirements["throughput"] = ent.text
                elif "reliability" in context or "confiabilidade" in context:
                    if "%" in context:
                        try:
                            reliability_value = float(ent.text.replace("%", "")) / 100.0
                            requirements["reliability"] = reliability_value
                        except ValueError:
                            pass
        
        return requirements
    
    def _infer_slice_type(self, text: str, requirements: Dict[str, Any]) -> Optional[str]:
        """Infere tipo de slice baseado em texto e requisitos"""
        text_lower = text.lower()
        
        # Palavras-chave para cada tipo
        embb_keywords = ["embb", "enhanced mobile broadband", "broadband", "banda larga", "video", "streaming"]
        urllc_keywords = ["urllc", "ultra reliable", "low latency", "ultra confiável", "baixa latência", "surgery", "cirurgia"]
        mmtc_keywords = ["mmtc", "massive", "iot", "internet das coisas", "sensores", "sensors"]
        
        # Verificar palavras-chave
        if any(keyword in text_lower for keyword in urllc_keywords):
            return "URLLC"
        elif any(keyword in text_lower for keyword in mmtc_keywords):
            return "mMTC"
        elif any(keyword in text_lower for keyword in embb_keywords):
            return "eMBB"
        
        # Inferir baseado em requisitos
        latency = requirements.get("latency")
        if latency:
            latency_value = float(re.search(r'(\d+(?:\.\d+)?)', str(latency)).group(1))
            if latency_value <= 10:
                return "URLLC"
            elif latency_value <= 50:
                return "eMBB"
            else:
                return "mMTC"
        
        throughput = requirements.get("throughput")
        if throughput:
            throughput_value = float(re.search(r'(\d+(?:\.\d+)?)', str(throughput)).group(1))
            if "gbps" in str(throughput).lower():
                return "eMBB"
            elif throughput_value >= 100:
                return "eMBB"
            elif throughput_value < 1:
                return "mMTC"
        
        reliability = requirements.get("reliability")
        if reliability and reliability >= 0.999:
            return "URLLC"
        
        return None

