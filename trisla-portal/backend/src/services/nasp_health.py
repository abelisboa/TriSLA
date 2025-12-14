"""
Módulo de diagnóstico de saúde dos serviços NASP.

Verifica a conectividade e disponibilidade de todos os módulos NASP usados pelo Portal.
Utilizado pelo endpoint /nasp/diagnostics para expor o estado dos serviços.
"""
import httpx
import asyncio
import time
from typing import Dict, Any, Optional
from src.config import settings
import logging

logger = logging.getLogger(__name__)

# Timeout padrão para health checks (3-5 segundos conforme especificação)
HEALTH_CHECK_TIMEOUT = 5.0


async def check_sem_csmf() -> Dict[str, Any]:
    """
    Verifica conectividade com o módulo SEM-CSMF do NASP.
    
    Retorna:
        {
            "reachable": bool,
            "latency_ms": Optional[float],
            "detail": Optional[str],
            "status_code": Optional[int]
        }
    """
    start_time = time.time()
    try:
        async with httpx.AsyncClient() as client:
            # Tentar endpoint /health ou uma chamada leve
            url = f"{settings.nasp_sem_csmf_url}/health"
            response = await client.get(url, timeout=HEALTH_CHECK_TIMEOUT)
            latency_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return {
                    "reachable": True,
                    "latency_ms": round(latency_ms, 2),
                    "detail": None,
                    "status_code": response.status_code
                }
            else:
                return {
                    "reachable": False,
                    "latency_ms": round(latency_ms, 2),
                    "detail": f"HTTP {response.status_code}: {response.text[:100]}",
                    "status_code": response.status_code
                }
    except httpx.ConnectError as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "reachable": False,
            "latency_ms": round(latency_ms, 2),
            "detail": f"Erro de conexão: {str(e)}",
            "status_code": None
        }
    except httpx.ReadTimeout as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "reachable": False,
            "latency_ms": round(latency_ms, 2),
            "detail": f"Timeout ao conectar: {str(e)}",
            "status_code": None
        }
    except httpx.HTTPStatusError as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "reachable": False,
            "latency_ms": round(latency_ms, 2),
            "detail": f"Erro HTTP {e.response.status_code}: {e.response.text[:100]}",
            "status_code": e.response.status_code
        }
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        logger.error(f"Erro inesperado ao verificar SEM-CSMF: {type(e).__name__}: {str(e)}")
        return {
            "reachable": False,
            "latency_ms": round(latency_ms, 2),
            "detail": f"Erro inesperado: {str(e)}",
            "status_code": None
        }


async def check_ml_nsmf() -> Dict[str, Any]:
    """
    Verifica conectividade com o módulo ML-NSMF do NASP.
    """
    start_time = time.time()
    try:
        async with httpx.AsyncClient() as client:
            url = f"{settings.nasp_ml_nsmf_url}/health"
            response = await client.get(url, timeout=HEALTH_CHECK_TIMEOUT)
            latency_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return {
                    "reachable": True,
                    "latency_ms": round(latency_ms, 2),
                    "detail": None,
                    "status_code": response.status_code
                }
            else:
                return {
                    "reachable": False,
                    "latency_ms": round(latency_ms, 2),
                    "detail": f"HTTP {response.status_code}: {response.text[:100]}",
                    "status_code": response.status_code
                }
    except httpx.ConnectError as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "reachable": False,
            "latency_ms": round(latency_ms, 2),
            "detail": f"Erro de conexão: {str(e)}",
            "status_code": None
        }
    except httpx.ReadTimeout as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "reachable": False,
            "latency_ms": round(latency_ms, 2),
            "detail": f"Timeout ao conectar: {str(e)}",
            "status_code": None
        }
    except httpx.HTTPStatusError as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "reachable": False,
            "latency_ms": round(latency_ms, 2),
            "detail": f"Erro HTTP {e.response.status_code}: {e.response.text[:100]}",
            "status_code": e.response.status_code
        }
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        logger.error(f"Erro inesperado ao verificar ML-NSMF: {type(e).__name__}: {str(e)}")
        return {
            "reachable": False,
            "latency_ms": round(latency_ms, 2),
            "detail": f"Erro inesperado: {str(e)}",
            "status_code": None
        }


async def check_decision_engine() -> Dict[str, Any]:
    """
    Verifica conectividade com o módulo Decision Engine do NASP.
    """
    start_time = time.time()
    try:
        async with httpx.AsyncClient() as client:
            url = f"{settings.nasp_decision_url}/health"
            response = await client.get(url, timeout=HEALTH_CHECK_TIMEOUT)
            latency_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return {
                    "reachable": True,
                    "latency_ms": round(latency_ms, 2),
                    "detail": None,
                    "status_code": response.status_code
                }
            else:
                return {
                    "reachable": False,
                    "latency_ms": round(latency_ms, 2),
                    "detail": f"HTTP {response.status_code}: {response.text[:100]}",
                    "status_code": response.status_code
                }
    except httpx.ConnectError as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "reachable": False,
            "latency_ms": round(latency_ms, 2),
            "detail": f"Erro de conexão: {str(e)}",
            "status_code": None
        }
    except httpx.ReadTimeout as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "reachable": False,
            "latency_ms": round(latency_ms, 2),
            "detail": f"Timeout ao conectar: {str(e)}",
            "status_code": None
        }
    except httpx.HTTPStatusError as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "reachable": False,
            "latency_ms": round(latency_ms, 2),
            "detail": f"Erro HTTP {e.response.status_code}: {e.response.text[:100]}",
            "status_code": e.response.status_code
        }
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        logger.error(f"Erro inesperado ao verificar Decision Engine: {type(e).__name__}: {str(e)}")
        return {
            "reachable": False,
            "latency_ms": round(latency_ms, 2),
            "detail": f"Erro inesperado: {str(e)}",
            "status_code": None
        }


async def check_bc_nssmf() -> Dict[str, Any]:
    """
    Verifica conectividade com o módulo BC-NSSMF do NASP.
    
    Este é um módulo crítico para registro de SLA no blockchain.
    """
    start_time = time.time()
    try:
        async with httpx.AsyncClient() as client:
            # BC-NSSMF tem endpoint /health específico conforme documentação
            url = f"{settings.nasp_bc_nssmf_url}/health"
            response = await client.get(url, timeout=HEALTH_CHECK_TIMEOUT)
            latency_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                # Verificar se a resposta indica que o BC está saudável
                try:
                    health_data = response.json()
                    rpc_connected = health_data.get("rpc_connected", False)
                    status = health_data.get("status", "unknown")
                    
                    if status == "healthy" and rpc_connected:
                        return {
                            "reachable": True,
                            "latency_ms": round(latency_ms, 2),
                            "detail": None,
                            "status_code": response.status_code,
                            "rpc_connected": True
                        }
                    else:
                        return {
                            "reachable": False,
                            "latency_ms": round(latency_ms, 2),
                            "detail": f"BC-NSSMF em modo degraded. Status: {status}, RPC: {rpc_connected}",
                            "status_code": response.status_code,
                            "rpc_connected": rpc_connected
                        }
                except Exception:
                    # Se não conseguir parsear JSON, considerar reachable se status 200
                    return {
                        "reachable": True,
                        "latency_ms": round(latency_ms, 2),
                        "detail": "Resposta não-JSON recebida",
                        "status_code": response.status_code
                    }
            else:
                return {
                    "reachable": False,
                    "latency_ms": round(latency_ms, 2),
                    "detail": f"HTTP {response.status_code}: {response.text[:100]}",
                    "status_code": response.status_code
                }
    except httpx.ConnectError as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "reachable": False,
            "latency_ms": round(latency_ms, 2),
            "detail": f"Erro de conexão: {str(e)}",
            "status_code": None
        }
    except httpx.ReadTimeout as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "reachable": False,
            "latency_ms": round(latency_ms, 2),
            "detail": f"Timeout ao conectar: {str(e)}",
            "status_code": None
        }
    except httpx.HTTPStatusError as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "reachable": False,
            "latency_ms": round(latency_ms, 2),
            "detail": f"Erro HTTP {e.response.status_code}: {e.response.text[:100]}",
            "status_code": e.response.status_code
        }
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        logger.error(f"Erro inesperado ao verificar BC-NSSMF: {type(e).__name__}: {str(e)}")
        return {
            "reachable": False,
            "latency_ms": round(latency_ms, 2),
            "detail": f"Erro inesperado: {str(e)}",
            "status_code": None
        }


async def check_sla_agent() -> Dict[str, Any]:
    """
    Verifica conectividade com o módulo SLA-Agent Layer do NASP.
    """
    start_time = time.time()
    try:
        async with httpx.AsyncClient() as client:
            # Tentar endpoint /health ou uma chamada leve
            url = f"{settings.nasp_sla_agent_url}/health"
            response = await client.get(url, timeout=HEALTH_CHECK_TIMEOUT)
            latency_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return {
                    "reachable": True,
                    "latency_ms": round(latency_ms, 2),
                    "detail": None,
                    "status_code": response.status_code
                }
            else:
                return {
                    "reachable": False,
                    "latency_ms": round(latency_ms, 2),
                    "detail": f"HTTP {response.status_code}: {response.text[:100]}",
                    "status_code": response.status_code
                }
    except httpx.ConnectError as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "reachable": False,
            "latency_ms": round(latency_ms, 2),
            "detail": f"Erro de conexão: {str(e)}",
            "status_code": None
        }
    except httpx.ReadTimeout as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "reachable": False,
            "latency_ms": round(latency_ms, 2),
            "detail": f"Timeout ao conectar: {str(e)}",
            "status_code": None
        }
    except httpx.HTTPStatusError as e:
        latency_ms = (time.time() - start_time) * 1000
        return {
            "reachable": False,
            "latency_ms": round(latency_ms, 2),
            "detail": f"Erro HTTP {e.response.status_code}: {e.response.text[:100]}",
            "status_code": e.response.status_code
        }
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        logger.error(f"Erro inesperado ao verificar SLA-Agent Layer: {type(e).__name__}: {str(e)}")
        return {
            "reachable": False,
            "latency_ms": round(latency_ms, 2),
            "detail": f"Erro inesperado: {str(e)}",
            "status_code": None
        }


async def check_all_nasp_modules() -> Dict[str, Any]:
    """
    Verifica todos os módulos NASP em paralelo.
    
    Retorna um dicionário com o estado de cada módulo:
    {
        "sem_csmf": {...},
        "ml_nsmf": {...},
        "decision": {...},
        "bc_nssmf": {...},
        "sla_agent": {...}
    }
    """
    # Executar todos os checks em paralelo
    results = await asyncio.gather(
        check_sem_csmf(),
        check_ml_nsmf(),
        check_decision_engine(),
        check_bc_nssmf(),
        check_sla_agent(),
        return_exceptions=True
    )
    
    # Processar resultados
    diagnostics = {
        "sem_csmf": results[0] if not isinstance(results[0], Exception) else {
            "reachable": False,
            "latency_ms": None,
            "detail": f"Erro ao executar check: {str(results[0])}",
            "status_code": None
        },
        "ml_nsmf": results[1] if not isinstance(results[1], Exception) else {
            "reachable": False,
            "latency_ms": None,
            "detail": f"Erro ao executar check: {str(results[1])}",
            "status_code": None
        },
        "decision": results[2] if not isinstance(results[2], Exception) else {
            "reachable": False,
            "latency_ms": None,
            "detail": f"Erro ao executar check: {str(results[2])}",
            "status_code": None
        },
        "bc_nssmf": results[3] if not isinstance(results[3], Exception) else {
            "reachable": False,
            "latency_ms": None,
            "detail": f"Erro ao executar check: {str(results[3])}",
            "status_code": None
        },
        "sla_agent": results[4] if not isinstance(results[4], Exception) else {
            "reachable": False,
            "latency_ms": None,
            "detail": f"Erro ao executar check: {str(results[4])}",
            "status_code": None
        }
    }
    
    # Logar resumo
    all_reachable = all(m.get("reachable", False) for m in diagnostics.values())
    if all_reachable:
        logger.info("✅ Todos os módulos NASP estão acessíveis")
    else:
        unreachable = [name for name, status in diagnostics.items() if not status.get("reachable", False)]
        logger.warning(f"⚠️ Módulos NASP não acessíveis: {', '.join(unreachable)}")
    
    return diagnostics




