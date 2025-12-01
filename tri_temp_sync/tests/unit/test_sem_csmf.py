"""
Unit Tests - SEM-CSMF
"""

import pytest
import sys
from pathlib import Path

# Adiciona os diretórios src ao path (diretórios com hífen não podem ser importados diretamente)
BASE_DIR = Path(__file__).parent.parent.parent
SEM_CSMF_SRC = BASE_DIR / "apps" / "sem-csmf" / "src"
sys.path.insert(0, str(SEM_CSMF_SRC))

from intent_processor import IntentProcessor
from nest_generator import NESTGenerator
from models.intent import Intent, SliceType, SLARequirements


class TestIntentProcessor:
    """Testes do IntentProcessor"""
    
    @pytest.mark.asyncio
    async def test_validate_semantic(self):
        """Testa validação semântica"""
        processor = IntentProcessor()
        intent = Intent(
            intent_id="test-001",
            service_type=SliceType.EMBB,
            sla_requirements=SLARequirements(
                latency="10ms",
                throughput="100Mbps"
            )
        )
        
        result = await processor.validate_semantic(intent)
        assert result is not None
        assert result.intent_id == "test-001"
    
    @pytest.mark.asyncio
    async def test_generate_gst(self):
        """Testa geração de GST"""
        processor = IntentProcessor()
        intent = Intent(
            intent_id="test-001",
            service_type=SliceType.EMBB,
            sla_requirements=SLARequirements(throughput="100Mbps")
        )
        
        gst = await processor.generate_gst(intent)
        assert gst["gst_id"] is not None
        assert gst["service_type"] == "eMBB"


class TestNESTGenerator:
    """Testes do NESTGenerator"""
    
    @pytest.mark.asyncio
    async def test_generate_nest(self):
        """Testa geração de NEST"""
        generator = NESTGenerator()
        gst = {
            "gst_id": "gst-001",
            "intent_id": "intent-001",
            "service_type": "eMBB",
            "template": {}
        }
        
        nest = await generator.generate_nest(gst)
        assert nest.nest_id is not None
        assert len(nest.network_slices) > 0

