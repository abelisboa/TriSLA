from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Core TriSLA modules
    sem_csmf_url: str = "http://trisla-sem-csmf:8080"
    ml_nsmf_url: str = "http://trisla-ml-nsmf:8081"
    decision_engine_url: str = "http://trisla-decision-engine:8082"
    bc_nssmf_url: str = "http://trisla-bc-nssmf:8083"
    sla_agent_url: str = "http://trisla-sla-agent-layer:8084"

    # Observability
    prometheus_url: str = "http://prometheus-operated.monitoring:9090"
    loki_url: str = "http://loki.monitoring:3100"
    tempo_url: str = "http://tempo.monitoring:3200"

    # Portal
    backend_host: str = "0.0.0.0"
    backend_port: int = 8001

    class Config:
        env_file = ".env"


settings = Settings()
