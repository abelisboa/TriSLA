"""
Testes unitários para OntologyParser
"""

import pytest
import sys
import os

# Adicionar caminho do módulo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps/sem-csmf/src"))

from models.intent import Intent, SliceType, SLARequirements
from ontology.parser import OntologyParser


@pytest.fixture
def ontology_parser():
    """Fixture para criar parser de ontologia"""
    return OntologyParser()


@pytest.fixture
def sample_intent():
    """Fixture para criar intent de teste"""
    return Intent(
        intent_id="test-intent-001",
        tenant_id="test-tenant",
        service_type=SliceType.URLLC,
        sla_requirements=SLARequirements(
            latency="10ms",
            throughput="100Mbps",
            reliability=0.99999
        )
    )


@pytest.mark.asyncio
async def test_parse_intent_basic(ontology_parser, sample_intent):
    """Testa parsing básico de intent"""
    result = await ontology_parser.parse_intent(sample_intent)
    
    assert result is not None
    assert result["intent_id"] == "test-intent-001"
    assert result["concept"] == "URLLC"
    assert "properties" in result
    assert "sla_requirements" in result


@pytest.mark.asyncio
async def test_parse_intent_fallback(ontology_parser):
    """Testa fallback quando ontologia não está disponível"""
    intent = Intent(
        intent_id="test-intent-002",
        service_type=SliceType.EMBB,
        sla_requirements=SLARequirements()
    )
    
    result = await ontology_parser.parse_intent(intent)
    
    assert result is not None
    assert "fallback_mode" in result or "ontology_loaded" in result


@pytest.mark.asyncio
async def test_parse_intent_all_slice_types(ontology_parser):
    """Testa parsing para todos os tipos de slice"""
    slice_types = [SliceType.EMBB, SliceType.URLLC, SliceType.MMTC]
    
    for slice_type in slice_types:
        intent = Intent(
            intent_id=f"test-{slice_type.value}",
            service_type=slice_type,
            sla_requirements=SLARequirements()
        )
        
        result = await ontology_parser.parse_intent(intent)
        assert result is not None
        assert result["concept"] == slice_type.value or result.get("fallback_mode", False)

