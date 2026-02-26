from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8001
    api_reload: bool = True

    # NASP - TODOS os Módulos Reais TriSLA (Port-Forward Localhost)
    nasp_sem_csmf_url: str = "http://localhost:8080"
    ml_nsmf_url: str = "http://localhost:8081"
    decision_engine_url: str = "http://localhost:8082"
    bc_nssmf_url: str = "http://localhost:8083"
    sla_agent_layer_url: str = "http://localhost:8084"

    # CORS - Permitir todas as origens para desenvolvimento
    cors_origins: List[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
