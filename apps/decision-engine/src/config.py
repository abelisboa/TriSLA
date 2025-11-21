"""
Configurações centralizadas - Decision Engine
Centraliza URLs, endpoints e flags de ambiente
"""

import os
from pydantic import BaseModel
from typing import Optional


class DecisionEngineConfig(BaseModel):
    """
    Configurações do Decision Engine
    Alinha URLs e endpoints com SEM-CSMF, ML-NSMF e BC-NSSMF
    """
    
    # Ambiente
    environment: str = os.getenv("TRISLA_ENV", "dev")
    
    # SEM-CSMF (Interface I-01 - gRPC)
    sem_csmf_grpc_host: str = os.getenv("SEM_CSMF_GRPC_HOST", "localhost")
    sem_csmf_grpc_port: int = int(os.getenv("SEM_CSMF_GRPC_PORT", "50051"))
    sem_csmf_http_url: str = os.getenv("SEM_CSMF_HTTP_URL", "http://127.0.0.1:8080")
    
    # ML-NSMF (Interface I-05 - HTTP REST)
    ml_nsmf_http_url: str = os.getenv("ML_NSMF_HTTP_URL", "http://127.0.0.1:8081")
    
    # BC-NSSMF (Interface I-06 - Blockchain)
    bc_nssmf_rpc_url: str = os.getenv("TRISLA_RPC_URL", "http://127.0.0.1:8545")
    bc_nssmf_contract_path: str = os.getenv(
        "BC_CONTRACT_PATH",
        os.path.join(os.path.dirname(__file__), "../../../bc-nssmf/src/contracts/contract_address.json")
    )
    bc_nssmf_chain_id: int = int(os.getenv("TRISLA_CHAIN_ID", "1337"))
    
    # Decision Engine
    decision_engine_grpc_port: int = int(os.getenv("GRPC_PORT", "50051"))
    decision_engine_http_port: int = int(os.getenv("HTTP_PORT", "8082"))
    
    # OTLP Collector (OpenTelemetry)
    otlp_endpoint: str = os.getenv("OTLP_ENDPOINT", "http://localhost:4318")
    otlp_endpoint_grpc: str = os.getenv("OTLP_ENDPOINT_GRPC", "http://localhost:4317")
    
    # Kafka (para comunicação assíncrona, se necessário)
    kafka_bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    use_kafka: bool = os.getenv("USE_KAFKA", "false").lower() == "true"
    
    @property
    def sem_csmf_grpc_endpoint(self) -> str:
        """Endpoint gRPC completo do SEM-CSMF"""
        return f"{self.sem_csmf_grpc_host}:{self.sem_csmf_grpc_port}"
    
    @property
    def decision_engine_grpc_endpoint(self) -> str:
        """Endpoint gRPC completo do Decision Engine"""
        return f"0.0.0.0:{self.decision_engine_grpc_port}"


# Instância global de configuração
config = DecisionEngineConfig()

