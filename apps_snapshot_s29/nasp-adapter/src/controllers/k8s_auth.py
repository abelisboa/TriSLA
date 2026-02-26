"""
Kubernetes Authentication Utilities
FASE C3-C3.2 FIX B: Hardening do client Kubernetes com logs explícitos
"""

import os
import logging
from kubernetes import config, client

logger = logging.getLogger(__name__)


def load_incluster_config_with_validation():
    """
    Carrega configuração in-cluster do Kubernetes com validação e logs explícitos
    FASE C3-C3.2 FIX B: Hardening - nunca usar kubeconfig local
    
    Returns:
        tuple: (ApiClient, token_present, namespace, apiserver_host)
    """
    # Verificar existência do token
    token_path = "/var/run/secrets/kubernetes.io/serviceaccount/token"
    token_present = os.path.exists(token_path)
    
    # Verificar namespace
    namespace_path = "/var/run/secrets/kubernetes.io/serviceaccount/namespace"
    namespace = "default"
    if os.path.exists(namespace_path):
        try:
            with open(namespace_path, 'r') as f:
                namespace = f.read().strip()
        except Exception as e:
            logger.warning(f"[K8S-AUTH] Erro ao ler namespace: {e}")
    
    # Carregar configuração in-cluster (sempre, sem fallback)
    try:
        config.load_incluster_config()
        logger.info("✅ [K8S-AUTH] in-cluster config loaded")
    except Exception as e:
        logger.error(f"❌ [K8S-AUTH] Falha ao carregar in-cluster config: {e}")
        raise RuntimeError("Failed to load in-cluster Kubernetes configuration") from e
    
    # Criar ApiClient após load_incluster_config
    api_client = client.ApiClient()
    
    # Obter informações do apiserver (host:port)
    apiserver_host = "unknown"
    try:
        # Tentar obter do configuration
        configuration = client.Configuration.get_default_copy()
        if configuration:
            apiserver_host = f"{configuration.host or 'unknown'}"
    except Exception as e:
        logger.warning(f"[K8S-AUTH] Não foi possível obter apiserver host: {e}")
    
    # Log explícito de evidência
    logger.info(f"✅ [K8S-AUTH] token_present={token_present} namespace={namespace} apiserver={apiserver_host}")
    
    return api_client, token_present, namespace, apiserver_host

