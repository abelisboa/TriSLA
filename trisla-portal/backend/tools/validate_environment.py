#!/usr/bin/env python3
"""Script para validar ambiente antes de executar stress tests"""
import httpx
import asyncio
import sys
from typing import Dict, Any

async def check_endpoint(name: str, url: str, timeout: float = 5.0) -> Dict[str, Any]:
    """Verifica se um endpoint está acessível"""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            return {
                "name": name,
                "url": url,
                "reachable": True,
                "status_code": response.status_code,
                "healthy": response.status_code == 200
            }
    except httpx.ConnectError:
        return {
            "name": name,
            "url": url,
            "reachable": False,
            "status_code": None,
            "healthy": False,
            "error": "Connection error"
        }
    except httpx.ReadTimeout:
        return {
            "name": name,
            "url": url,
            "reachable": False,
            "status_code": None,
            "healthy": False,
            "error": "Timeout"
        }
    except Exception as e:
        return {
            "name": name,
            "url": url,
            "reachable": False,
            "status_code": None,
            "healthy": False,
            "error": str(e)
        }

async def main():
    """Valida todo o ambiente"""
    import sys
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    
    from pathlib import Path
    log_file = Path(__file__).parent.parent / "validation_log.txt"
    
    def log(msg):
        print(msg, flush=True)
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(msg + '\n')
        except:
            pass
    
    log("="*70)
    log("VALIDAÇÃO DO AMBIENTE - FASE 0")
    log("="*70)
    log("")
    
    # 0.1 Validar Portal
    log("0.1 Validando Portal (http://localhost:8001/health)...")
    portal_status = await check_endpoint("Portal", "http://localhost:8001/health")
    
    if portal_status["healthy"]:
        log(f"✅ Portal está ativo (HTTP {portal_status['status_code']})")
    else:
        log(f"❌ Portal NÃO está ativo")
        log(f"   Erro: {portal_status.get('error', 'Unknown')}")
        log("")
        log("⚠️  AÇÃO NECESSÁRIA:")
        log("   Execute: cd backend && bash start_backend.sh")
        sys.exit(1)
    
    log("")
    
    # 0.2 Validar módulos NASP
    log("0.2 Validando módulos NASP (port-forwards)...")
    nasp_modules = [
        ("SEM-CSMF", "http://localhost:8080/health"),
        ("ML-NSMF", "http://localhost:8081/health"),
        ("Decision Engine", "http://localhost:8082/health"),
        ("BC-NSSMF", "http://localhost:8083/health"),
        ("SLA-Agent Layer", "http://localhost:8084/health")
    ]
    
    results = await asyncio.gather(*[
        check_endpoint(name, url) for name, url in nasp_modules
    ])
    
    all_healthy = True
    for result in results:
        if result["healthy"]:
            log(f"✅ {result['name']}: OK (HTTP {result['status_code']})")
        else:
            log(f"⚠️  {result['name']}: Offline - {result.get('error', 'Unknown')}")
            all_healthy = False
    
    log("")
    
    # 0.3 Validar acesso real ao NASP (BC-NSSMF)
    log("0.3 Validando acesso real ao BC-NSSMF...")
    bc_status = await check_endpoint("BC-NSSMF", "http://localhost:8083/health")
    
    if bc_status["healthy"]:
        # Tentar obter resposta JSON
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("http://localhost:8083/health")
                if response.status_code == 200:
                    try:
                        data = response.json()
                        status = data.get("status", "unknown")
                        if status == "healthy":
                            log(f"✅ BC-NSSMF está healthy")
                        else:
                            log(f"⚠️  BC-NSSMF status: {status}")
                            all_healthy = False
                    except:
                        log(f"✅ BC-NSSMF responde (mas resposta não é JSON)")
        except Exception as e:
            log(f"⚠️  Erro ao verificar status do BC-NSSMF: {e}")
            all_healthy = False
    else:
        log(f"❌ BC-NSSMF não está acessível")
        all_healthy = False
    
    log("")
    log("="*70)
    
    if portal_status["healthy"] and all_healthy:
        log("✅ AMBIENTE VALIDADO - Todos os serviços estão online")
        log("")
        log("Pronto para executar FASE 1 - Battery Test")
        sys.exit(0)
    elif portal_status["healthy"]:
        log("⚠️  AMBIENTE PARCIALMENTE VALIDADO")
        log("   Portal está online, mas alguns módulos NASP estão offline")
        log("   Os testes continuarão, mas podem apresentar falhas")
        log("")
        log("Pronto para executar FASE 1 - Battery Test (com limitações)")
        sys.exit(0)
    else:
        log("❌ AMBIENTE NÃO VALIDADO")
        log("   Portal não está acessível")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

