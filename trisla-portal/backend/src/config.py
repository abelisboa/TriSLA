"""
Configuração centralizada do Portal TriSLA.

Todas as URLs dos serviços NASP são configuráveis via variáveis de ambiente,
com defaults alinhados ao cenário de port-forward local (localhost:8080-8084).

Variáveis de ambiente suportadas (prioridade):
1. SEM_CSMF_URL, ML_NSMF_URL, DECISION_ENGINE_URL, BC_NSSMF_URL, SLA_AGENT_URL (formato Helm/NASP)
2. NASP_SEM_CSMF_URL, NASP_ML_NSMF_URL, NASP_DECISION_URL, NASP_BC_NSSMF_URL, NASP_SLA_AGENT_URL (formato legado)

No cenário NASP remoto + port-forward local, usar localhost:8080-8084.
Em outros cenários, apontar para o IP/hostname do NASP.
"""
from pydantic_settings import BaseSettings
from pydantic import Field, model_validator
from typing import List
import os


class Settings(BaseSettings):
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8001
    api_reload: bool = True

    # NASP - TODOS os Módulos Reais TriSLA (Port-Forward Localhost)
    # Suporta ambos os formatos: SEM_CSMF_URL (prioridade) ou NASP_SEM_CSMF_URL (fallback)
    nasp_sem_csmf_url: str = Field(
        default="http://localhost:8080",
        description="URL do módulo SEM-CSMF do NASP"
    )
    nasp_ml_nsmf_url: str = Field(
        default="http://localhost:8081",
        description="URL do módulo ML-NSMF do NASP"
    )
    nasp_decision_url: str = Field(
        default="http://localhost:8082",
        description="URL do módulo Decision Engine do NASP"
    )
    nasp_bc_nssmf_url: str = Field(
        default="http://localhost:8083",
        description="URL do módulo BC-NSSMF do NASP"
    )
    nasp_sla_agent_url: str = Field(
        default="http://localhost:8084",
        description="URL do módulo SLA-Agent Layer do NASP"
    )

    @model_validator(mode='after')
    def resolve_env_vars(self):
        """Resolve environment variables with priority: SEM_CSMF_URL > NASP_SEM_CSMF_URL"""
        # SEM-CSMF
        if sem_url := os.getenv('SEM_CSMF_URL'):
            self.nasp_sem_csmf_url = sem_url
        elif nasp_sem_url := os.getenv('NASP_SEM_CSMF_URL'):
            self.nasp_sem_csmf_url = nasp_sem_url
        
        # ML-NSMF
        if ml_url := os.getenv('ML_NSMF_URL'):
            self.nasp_ml_nsmf_url = ml_url
        elif nasp_ml_url := os.getenv('NASP_ML_NSMF_URL'):
            self.nasp_ml_nsmf_url = nasp_ml_url
        
        # Decision Engine
        if de_url := os.getenv('DECISION_ENGINE_URL'):
            self.nasp_decision_url = de_url
        elif nasp_de_url := os.getenv('NASP_DECISION_URL'):
            self.nasp_decision_url = nasp_de_url
        
        # BC-NSSMF
        if bc_url := os.getenv('BC_NSSMF_URL'):
            self.nasp_bc_nssmf_url = bc_url
        elif nasp_bc_url := os.getenv('NASP_BC_NSSMF_URL'):
            self.nasp_bc_nssmf_url = nasp_bc_url
        
        # SLA-Agent
        if sla_url := os.getenv('SLA_AGENT_URL'):
            self.nasp_sla_agent_url = sla_url
        elif nasp_sla_url := os.getenv('NASP_SLA_AGENT_URL'):
            self.nasp_sla_agent_url = nasp_sla_url
        
        return self

    # Aliases para compatibilidade com código existente
    @property
    def ml_nsmf_url(self) -> str:
        """Alias para nasp_ml_nsmf_url - compatibilidade"""
        return self.nasp_ml_nsmf_url

    @property
    def decision_engine_url(self) -> str:
        """Alias para nasp_decision_url - compatibilidade"""
        return self.nasp_decision_url

    @property
    def bc_nssmf_url(self) -> str:
        """Alias para nasp_bc_nssmf_url - compatibilidade"""
        return self.nasp_bc_nssmf_url

    @property
    def sla_agent_layer_url(self) -> str:
        """Alias para nasp_sla_agent_url - compatibilidade"""
        return self.nasp_sla_agent_url

    # CORS - Permitir todas as origens para desenvolvimento
    cors_origins: List[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
