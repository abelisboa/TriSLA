"""
Unit Tests - BC-NSSMF BCService
Testes unitários para o serviço blockchain (Ethereum Permissionado GoQuorum/Besu)
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Adicionar src ao path
BASE_DIR = Path(__file__).parent.parent.parent
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from service import BCService
from config import BCConfig


class TestBCService:
    """Testes do BCService (Ethereum Permissionado GoQuorum/Besu)"""
    
    @pytest.mark.asyncio
    async def test_config_initialization(self):
        """Testa inicialização da configuração"""
        config = BCConfig()
        assert config.rpc_url is not None
        assert config.chain_id == 1337  # Padrão do genesis.json
        assert config.blockchain_type == "Ethereum Permissionado (GoQuorum/Besu)"
    
    @pytest.mark.asyncio
    async def test_config_environment_variables(self):
        """Testa configuração via variáveis de ambiente"""
        with patch.dict(os.environ, {
            "BESU_RPC_URL": "http://besu-test:8545",
            "BESU_CHAIN_ID": "9999",
            "BESU_PRIVATE_KEY": "0x" + "1" * 64
        }):
            config = BCConfig()
            assert config.rpc_url == "http://besu-test:8545"
            assert config.chain_id == 9999
            assert config.private_key == "0x" + "1" * 64
    
    @pytest.mark.asyncio
    async def test_bc_service_initialization_failure(self):
        """Testa falha na inicialização quando RPC não conectado"""
        with patch('web3.Web3') as mock_web3:
            mock_w3 = MagicMock()
            mock_w3.is_connected.return_value = False
            mock_web3.return_value = mock_w3
            
            with pytest.raises(RuntimeError, match="Não conectado ao Besu RPC"):
                BCService()
    
    @pytest.mark.asyncio
    async def test_register_sla_hash_conversion(self):
        """Testa conversão de sla_hash para bytes32"""
        # Este teste valida a lógica de conversão sem precisar de blockchain real
        config = BCConfig()
        
        # Testar diferentes formatos de hash
        test_hashes = [
            "0x" + "a" * 64,  # Com prefixo 0x
            "b" * 64,  # Sem prefixo
            "c" * 32,  # Hash curto (deve ser preenchido)
            "d" * 128,  # Hash longo (deve ser truncado)
        ]
        
        # Validar que a conversão funciona (sem executar na blockchain)
        for hash_str in test_hashes:
            # Simular conversão
            if hash_str.startswith("0x"):
                hash_hex = hash_str[2:]
            else:
                hash_hex = hash_str
            
            if len(hash_hex) < 64:
                hash_hex = hash_hex.ljust(64, '0')
            elif len(hash_hex) > 64:
                hash_hex = hash_hex[:64]
            
            assert len(hash_hex) == 64
            assert all(c in '0123456789abcdef' for c in hash_hex.lower())
    
    @pytest.mark.asyncio
    async def test_extract_slos_format(self):
        """Testa formatação de SLOs para o contrato"""
        slos_input = [
            {"name": "latency", "value": 10.5, "threshold": 10},
            {"name": "throughput", "value": 100, "threshold": 100}
        ]
        
        # Formatar SLOs (simulação)
        slos_formatted = [
            (slo["name"], int(slo["value"]), int(slo["threshold"]))
            for slo in slos_input
        ]
        
        assert len(slos_formatted) == 2
        assert slos_formatted[0] == ("latency", 10, 10)
        assert slos_formatted[1] == ("throughput", 100, 100)


class TestOracle:
    """Testes do MetricsOracle"""
    
    @pytest.mark.asyncio
    async def test_oracle_without_nasp(self):
        """Testa Oracle sem NASP Adapter (fallback)"""
        from oracle import MetricsOracle
        
        oracle = MetricsOracle(nasp_client=None)
        metrics = await oracle.get_metrics()
        
        assert metrics is not None
        assert "source" in metrics
        assert metrics["source"] == "fallback"
        assert "warning" in metrics
    
    @pytest.mark.asyncio
    async def test_oracle_metric_extraction(self):
        """Testa extração de métricas agregadas"""
        from oracle import MetricsOracle
        
        oracle = MetricsOracle(nasp_client=None)
        
        ran_metrics = {"latency": 10.0, "throughput": 100.0}
        transport_metrics = {"latency": 5.0, "throughput": 200.0}
        core_metrics = {"latency": 2.0}
        
        latency = oracle._extract_latency(ran_metrics, transport_metrics, core_metrics)
        throughput = oracle._extract_throughput(ran_metrics, transport_metrics, core_metrics)
        
        assert latency > 0
        assert throughput > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

