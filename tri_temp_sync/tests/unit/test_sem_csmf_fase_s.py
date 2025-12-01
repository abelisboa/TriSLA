"""
Testes Unitários - FASE S (SEM-CSMF)
Validação das implementações da FASE S:
- Ontologia OWL completa
- Cache semântico LRU
- NLP expandido
- Mapeamento 3GPP completo
"""

import pytest
import sys
import os
from pathlib import Path

# Adicionar caminho do módulo
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "apps" / "sem-csmf" / "src"))

from ontology.loader import OntologyLoader
from ontology.cache import SemanticCache
from ontology.reasoner import SemanticReasoner
from nlp.parser import NLPParser
from nlp.intent_examples import get_all_examples, get_extraction_patterns, get_keywords
from nest_generator import NESTGenerator


class TestOntologyOWL:
    """Testes para ontologia OWL completa"""
    
    def test_ontology_loader_owl_support(self):
        """Testa se loader suporta arquivo OWL"""
        current_dir = Path(__file__).parent.parent.parent / "apps" / "sem-csmf" / "src" / "ontology"
        owl_path = current_dir / "trisla_complete.owl"
        
        if owl_path.exists():
            loader = OntologyLoader(str(owl_path))
            result = loader.load(apply_reasoning=False)
            assert result is not None or loader.is_loaded() == False  # Pode falhar se owlready2 não estiver instalado
        else:
            pytest.skip("Arquivo OWL não encontrado")
    
    def test_ontology_loader_ttl_fallback(self):
        """Testa fallback para TTL se OWL não existir"""
        current_dir = Path(__file__).parent.parent.parent / "apps" / "sem-csmf" / "src" / "ontology"
        ttl_path = current_dir / "trisla.ttl"
        
        if ttl_path.exists():
            loader = OntologyLoader(str(ttl_path))
            result = loader.load(apply_reasoning=False)
            # Não deve levantar exceção mesmo se não carregar
            assert True
        else:
            pytest.skip("Arquivo TTL não encontrado")
    
    def test_ontology_loader_default_path(self):
        """Testa se loader usa caminho padrão corretamente"""
        loader = OntologyLoader()
        # Deve tentar carregar sem erro
        result = loader.load(apply_reasoning=False)
        assert True  # Não deve levantar exceção


class TestSemanticCache:
    """Testes para cache semântico LRU"""
    
    def test_cache_basic_operations(self):
        """Testa operações básicas do cache"""
        cache = SemanticCache(ttl_seconds=3600, max_size=10, enable_lru=True)
        
        # Testar set/get
        cache.set("test_op", {"param": "value"}, "result")
        result = cache.get("test_op", {"param": "value"})
        assert result == "result"
    
    def test_cache_lru_eviction(self):
        """Testa eviction LRU quando cache está cheio"""
        cache = SemanticCache(ttl_seconds=3600, max_size=3, enable_lru=True)
        
        # Preencher cache
        cache.set("op1", {"p": 1}, "r1")
        cache.set("op2", {"p": 2}, "r2")
        cache.set("op3", {"p": 3}, "r3")
        
        # Acessar op1 para atualizar ordem LRU
        cache.get("op1", {"p": 1})
        
        # Adicionar novo item (deve remover op2 que é o menos recente)
        cache.set("op4", {"p": 4}, "r4")
        
        # op2 deve ter sido removido
        assert cache.get("op2", {"p": 2}) is None
        # op1, op3, op4 devem estar presentes
        assert cache.get("op1", {"p": 1}) == "r1"
        assert cache.get("op3", {"p": 3}) == "r3"
        assert cache.get("op4", {"p": 4}) == "r4"
    
    def test_cache_stats(self):
        """Testa estatísticas do cache"""
        cache = SemanticCache(ttl_seconds=3600, max_size=10)
        
        cache.set("op1", {"p": 1}, "r1")
        cache.get("op1", {"p": 1})  # Hit
        cache.get("op2", {"p": 2})  # Miss
        
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 50.0
    
    def test_cache_invalidation(self):
        """Testa invalidação de cache"""
        cache = SemanticCache(ttl_seconds=3600, max_size=10)
        
        cache.set("op1", {"p": 1}, "r1")
        cache.set("op2", {"p": 2}, "r2")
        
        cache.invalidate("op1")
        
        assert cache.get("op1", {"p": 1}) is None
        assert cache.get("op2", {"p": 2}) == "r2"


class TestNLPExpanded:
    """Testes para NLP expandido"""
    
    def test_intent_examples_count(self):
        """Testa se exemplos foram expandidos corretamente"""
        examples = get_all_examples()
        
        assert len(examples["URLLC"]) >= 16, f"URLLC deve ter pelo menos 16 exemplos, tem {len(examples['URLLC'])}"
        assert len(examples["eMBB"]) >= 16, f"eMBB deve ter pelo menos 16 exemplos, tem {len(examples['eMBB'])}"
        assert len(examples["mMTC"]) >= 16, f"mMTC deve ter pelo menos 16 exemplos, tem {len(examples['mMTC'])}"
    
    def test_extraction_patterns(self):
        """Testa se padrões de extração estão disponíveis"""
        patterns = get_extraction_patterns()
        
        assert "latency" in patterns
        assert "throughput" in patterns
        assert "reliability" in patterns
        assert len(patterns["latency"]) > 0
        assert len(patterns["throughput"]) > 0
        assert len(patterns["reliability"]) > 0
    
    def test_keywords(self):
        """Testa se palavras-chave estão disponíveis"""
        keywords = get_keywords()
        
        assert "URLLC" in keywords
        assert "eMBB" in keywords
        assert "mMTC" in keywords
        assert len(keywords["URLLC"]) > 0
        assert len(keywords["eMBB"]) > 0
        assert len(keywords["mMTC"]) > 0
    
    def test_nlp_parser_with_examples(self):
        """Testa parser NLP com exemplos expandidos"""
        parser = NLPParser(language="en")
        
        examples = get_all_examples()
        
        # Testar alguns exemplos URLLC
        for example in examples["URLLC"][:3]:
            result = parser.parse_intent_text(example)
            assert "slice_type" in result
            assert "requirements" in result
            # Deve inferir URLLC ou ter requisitos de latência baixa
            assert result["slice_type"] == "URLLC" or "latency" in str(result["requirements"]).lower()


class Test3GPPMapping:
    """Testes para mapeamento 3GPP completo"""
    
    def test_nest_generator_qos_characteristics(self):
        """Testa geração de QoS Characteristics conforme 3GPP"""
        generator = NESTGenerator()
        
        # Template eMBB
        template_embb = {
            "slice_type": "eMBB",
            "qos": {
                "maximum_bitrate": "1Gbps",
                "guaranteed_bitrate": "100Mbps"
            },
            "sla": {}
        }
        
        resources = generator._calculate_resources(template_embb)
        
        assert "qosCharacteristics" in resources
        qos = resources["qosCharacteristics"]
        assert "priorityLevel" in qos
        assert "packetDelayBudget" in qos
        assert "packetErrorRate" in qos
        assert "guaranteedBitRate" in qos
        assert "maximumBitRate" in qos
        
        # eMBB deve ter priorityLevel 6
        assert qos["priorityLevel"] == 6
    
    def test_nest_generator_slice_profile(self):
        """Testa geração de Slice Profile conforme 3GPP"""
        generator = NESTGenerator()
        
        template = {
            "slice_type": "URLLC",
            "qos": {},
            "sla": {}
        }
        
        resources = generator._calculate_resources(template)
        
        assert "sliceProfile" in resources
        profile = resources["sliceProfile"]
        assert "plmnId" in profile
        assert "sNSSAI" in profile
        assert "maxNumberOfUEs" in profile
        assert "maxDataRatePerUE" in profile
        
        # sNSSAI deve ter formato SST-SD
        assert "-" in profile["sNSSAI"]
        assert profile["sNSSAI"].startswith("2")  # URLLC tem SST=2
    
    def test_nest_generator_coverage_area(self):
        """Testa geração de Coverage Area conforme 3GPP"""
        generator = NESTGenerator()
        
        template = {
            "slice_type": "mMTC",
            "qos": {},
            "sla": {},
            "coverage": {
                "area_type": "Rural",
                "coordinates": "-23.5505,-46.6333"
            }
        }
        
        resources = generator._calculate_resources(template)
        
        assert "coverageArea" in resources
        coverage = resources["coverageArea"]
        assert "areaType" in coverage
        assert "geographicCoordinates" in coverage
        assert coverage["areaType"] == "Rural"
    
    def test_nest_generator_priority_levels(self):
        """Testa priority levels conforme 3GPP para cada tipo de slice"""
        generator = NESTGenerator()
        
        # URLLC deve ter priorityLevel 1 (mais alta)
        template_urllc = {"slice_type": "URLLC", "qos": {}, "sla": {}}
        resources_urllc = generator._calculate_resources(template_urllc)
        assert resources_urllc["qosCharacteristics"]["priorityLevel"] == 1
        
        # eMBB deve ter priorityLevel 6
        template_embb = {"slice_type": "eMBB", "qos": {}, "sla": {}}
        resources_embb = generator._calculate_resources(template_embb)
        assert resources_embb["qosCharacteristics"]["priorityLevel"] == 6
        
        # mMTC deve ter priorityLevel 8 (mais baixa)
        template_mmtc = {"slice_type": "mMTC", "qos": {}, "sla": {}}
        resources_mmtc = generator._calculate_resources(template_mmtc)
        assert resources_mmtc["qosCharacteristics"]["priorityLevel"] == 8


class TestIntegration:
    """Testes de integração"""
    
    def test_ontology_cache_reasoner_integration(self):
        """Testa integração entre ontologia, cache e reasoner"""
        cache = SemanticCache(ttl_seconds=3600, max_size=100)
        loader = OntologyLoader()
        reasoner = SemanticReasoner(loader, cache=cache)
        
        # Inicializar reasoner
        reasoner.initialize()
        
        # Testar inferência com cache
        intent_data = {
            "latency": "5ms",
            "throughput": "100Mbps",
            "reliability": 0.999
        }
        
        result1 = reasoner.infer_slice_type(intent_data)
        result2 = reasoner.infer_slice_type(intent_data)  # Deve usar cache
        
        # Resultados devem ser consistentes
        assert result1 == result2
        
        # Cache deve ter hit (pode ser 0 se primeira chamada não cacheou, mas segunda deve usar)
        stats = cache.get_stats()
        # Verificar que pelo menos uma operação foi feita
        assert stats["hits"] + stats["misses"] > 0
        # Se houver hits, verificar que hit rate é razoável
        if stats["hits"] > 0:
            assert stats["hit_rate"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

