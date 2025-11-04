import os
from typing import List, Optional
import yaml
from pydantic import BaseModel

class ServerConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = False

class PrometheusConfig(BaseModel):
    url: str = "http://localhost:9090"

class SemNsmfConfig(BaseModel):
    url: str = "http://localhost:8000"
    token: Optional[str] = None

class CorsConfig(BaseModel):
    allowed_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

class AppConfig(BaseModel):
    server: ServerConfig = ServerConfig()
    prometheus: PrometheusConfig = PrometheusConfig()
    sem_nsmf: SemNsmfConfig = SemNsmfConfig()
    cors: CorsConfig = CorsConfig()

def load_config() -> AppConfig:
    """Load configuration from environment variables or config file"""
    
    # Default configuration
    config = AppConfig()
    
    # Try to load from config.yaml if it exists
    config_file = os.getenv("CONFIG_FILE", "config.yaml")
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                yaml_config = yaml.safe_load(f)
                
            if yaml_config:
                # Update server config
                if "server" in yaml_config:
                    for key, value in yaml_config["server"].items():
                        setattr(config.server, key, value)
                
                # Update prometheus config
                if "prometheus" in yaml_config:
                    for key, value in yaml_config["prometheus"].items():
                        setattr(config.prometheus, key, value)
                
                # Update sem_nsmf config
                if "sem_nsmf" in yaml_config:
                    for key, value in yaml_config["sem_nsmf"].items():
                        setattr(config.sem_nsmf, key, value)
                
                # Update cors config
                if "cors" in yaml_config and "allowed_origins" in yaml_config["cors"]:
                    config.cors.allowed_origins = yaml_config["cors"]["allowed_origins"]
        except Exception as e:
            print(f"Error loading config file: {e}")
    
    # Override with environment variables if provided
    if os.getenv("PORT"):
        config.server.port = int(os.getenv("PORT"))
    
    if os.getenv("HOST"):
        config.server.host = os.getenv("HOST")
    
    if os.getenv("DEBUG"):
        config.server.debug = os.getenv("DEBUG").lower() in ("true", "1", "yes")
    
    if os.getenv("PROMETHEUS_URL"):
        config.prometheus.url = os.getenv("PROMETHEUS_URL")
    
    if os.getenv("SEM_NSMF_URL"):
        config.sem_nsmf.url = os.getenv("SEM_NSMF_URL")
    
    if os.getenv("SEM_NSMF_TOKEN"):
        config.sem_nsmf.token = os.getenv("SEM_NSMF_TOKEN")
    
    if os.getenv("ALLOWED_ORIGINS"):
        config.cors.allowed_origins = os.getenv("ALLOWED_ORIGINS").split(",")
    
    return config

# Create a singleton config instance
config = load_config()



