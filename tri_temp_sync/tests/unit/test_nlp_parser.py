"""
Testes unitários para NLPParser
"""

import pytest
import sys
import os

# Adicionar caminho do módulo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../apps/sem-csmf/src"))

from nlp.parser import NLPParser


@pytest.fixture
def nlp_parser():
    """Fixture para criar parser NLP"""
    return NLPParser(language="en")


def test_parse_intent_text_urllc(nlp_parser):
    """Testa parsing de texto URLLC"""
    text = "I need a URLLC slice with maximum latency of 10ms and reliability of 99.999%"
    result = nlp_parser.parse_intent_text(text)
    
    assert result is not None
    assert result["slice_type"] == "URLLC"
    assert "requirements" in result
    assert "latency" in result["requirements"]
    assert "reliability" in result["requirements"]


def test_parse_intent_text_embb(nlp_parser):
    """Testa parsing de texto eMBB"""
    text = "I need an eMBB slice with minimum throughput of 1Gbps"
    result = nlp_parser.parse_intent_text(text)
    
    assert result is not None
    assert result["slice_type"] in ["eMBB", None]  # Pode inferir ou não
    assert "requirements" in result


def test_parse_intent_text_mmtc(nlp_parser):
    """Testa parsing de texto mMTC"""
    text = "I need a massive IoT slice for sensors"
    result = nlp_parser.parse_intent_text(text)
    
    assert result is not None
    assert result["slice_type"] in ["mMTC", None]
    assert "requirements" in result


def test_extract_latency(nlp_parser):
    """Testa extração de latência"""
    text = "latency maximum 10ms"
    result = nlp_parser.parse_intent_text(text)
    
    assert "latency" in result["requirements"]
    assert "10" in result["requirements"]["latency"]


def test_extract_throughput(nlp_parser):
    """Testa extração de throughput"""
    text = "throughput minimum 100Mbps"
    result = nlp_parser.parse_intent_text(text)
    
    assert "throughput" in result["requirements"]


def test_extract_reliability(nlp_parser):
    """Testa extração de confiabilidade"""
    text = "reliability 99.999%"
    result = nlp_parser.parse_intent_text(text)
    
    assert "reliability" in result["requirements"]
    assert result["requirements"]["reliability"] > 0.99

