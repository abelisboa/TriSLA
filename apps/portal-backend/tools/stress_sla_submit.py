#!/usr/bin/env python3
"""
Stress Test - Submissão de SLA
Executa 20 requisições paralelas ao endpoint /api/v1/sla/submit
e coleta métricas de performance, taxa de sucesso e comportamentos de retry.
"""
import asyncio
import httpx
import time
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict
import statistics

# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")

def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")

def print_section(title: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

# Resultados globais
results = {
    "timestamp": datetime.now().isoformat(),
    "total_requests": 20,
    "requests": [],
    "summary": {}
}

async def submit_sla(
    client: httpx.AsyncClient,
    request_id: int,
    backend_url: str
) -> Dict[str, Any]:
    """
    Submete um SLA e retorna métricas detalhadas.
    """
    payload = {
        "template_id": "urllc-template-001",
        "tenant_id": "default",
        "form_values": {
            "type": "URLLC",
            "latency": 10,
            "reliability": 99.99,
            "availability": 99.99,
            "throughput_dl": 100,
            "throughput_ul": 50,
            "device_count": 10,
            "coverage_area": "urban",
            "mobility": "low",
            "duration": 3600,
            "priority": "high"
        }
    }
    
    result = {
        "request_id": request_id,
        "status": "pending",
        "status_code": None,
        "latency_ms": None,
        "success": False,
        "pipeline_steps": {},
        "errors": [],
        "retry_detected": False,
        "timestamp": datetime.now().isoformat()
    }
    
    start_time = time.time()
    
    try:
        response = await client.post(
            f"{backend_url}/api/v1/sla/submit",
            json=payload,
            timeout=60.0
        )
        
        elapsed_time = (time.time() - start_time) * 1000
        result["latency_ms"] = round(elapsed_time, 2)
        result["status_code"] = response.status_code
        
        if response.status_code == 200:
            data = response.json()
            result["success"] = True
            result["status"] = "success"
            
            # Coletar status da pipeline
            result["pipeline_steps"] = {
                "sem_csmf": data.get("sem_csmf_status", "UNKNOWN"),
                "ml_nsmf": data.get("ml_nsmf_status", "UNKNOWN"),
                "decision_engine": data.get("decision", "UNKNOWN"),
                "bc_nssmf": data.get("bc_status", "UNKNOWN"),
                "sla_agent": data.get("sla_agent_status", "UNKNOWN")
            }
            
            # Detectar possíveis retries (latência alta pode indicar retries)
            if elapsed_time > 10000:  # Mais de 10 segundos
                result["retry_detected"] = True
            
            # Coletar informações adicionais
            result["sla_id"] = data.get("sla_id")
            result["tx_hash"] = data.get("tx_hash") or data.get("blockchain_tx_hash")
            result["decision"] = data.get("decision")
            
        elif response.status_code == 503:
            result["status"] = "service_unavailable"
            try:
                error_data = response.json()
                detail = error_data.get("detail", {})
                if isinstance(detail, dict):
                    result["error_reason"] = detail.get("reason", "unknown")
                    result["error_phase"] = detail.get("phase", "unknown")
                    result["errors"].append(f"{detail.get('reason', 'unknown')}: {detail.get('detail', 'N/A')}")
                else:
                    result["errors"].append(str(detail))
            except:
                result["errors"].append(response.text[:200])
        else:
            result["status"] = "error"
            try:
                error_data = response.json()
                result["errors"].append(error_data.get("detail", response.text[:200]))
            except:
                result["errors"].append(response.text[:200])
                
    except httpx.ConnectError as e:
        result["status"] = "connection_error"
        result["errors"].append(f"Erro de conexão: {str(e)}")
        result["latency_ms"] = (time.time() - start_time) * 1000
    except httpx.ReadTimeout as e:
        result["status"] = "timeout"
        result["errors"].append(f"Timeout: {str(e)}")
        result["latency_ms"] = (time.time() - start_time) * 1000
        result["retry_detected"] = True  # Timeout pode indicar retries
    except Exception as e:
        result["status"] = "exception"
        result["errors"].append(f"Exceção: {str(e)}")
        result["latency_ms"] = (time.time() - start_time) * 1000
    
    return result

async def run_stress_test(num_requests: int = 20, backend_url: str = "http://localhost:8001"):
    """
    Executa o stress test com N requisições paralelas.
    """
    print_section("STRESS TEST - Submissão de SLA")
    print_info(f"Executando {num_requests} requisições paralelas...")
    print_info(f"Backend URL: {backend_url}\n")
    
    start_time = time.time()
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Executar todas as requisições em paralelo
        tasks = [
            submit_sla(client, i+1, backend_url)
            for i in range(num_requests)
        ]
        
        results["requests"] = await asyncio.gather(*tasks, return_exceptions=True)
    
    total_time = time.time() - start_time
    
    # Processar resultados
    process_results(total_time)

def process_results(total_time: float):
    """
    Processa os resultados e gera estatísticas.
    """
    print_section("PROCESSANDO RESULTADOS")
    
    # Filtrar exceções
    valid_results = [r for r in results["requests"] if isinstance(r, dict)]
    exceptions = [r for r in results["requests"] if not isinstance(r, dict)]
    
    if exceptions:
        print_warning(f"{len(exceptions)} requisições geraram exceções")
    
    total_valid = len(valid_results)
    successful = [r for r in valid_results if r.get("success", False)]
    failed = [r for r in valid_results if not r.get("success", False)]
    
    # Taxa de sucesso
    success_rate = (len(successful) / total_valid * 100) if total_valid > 0 else 0
    
    # Latências
    latencies = [r["latency_ms"] for r in valid_results if r.get("latency_ms")]
    avg_latency = statistics.mean(latencies) if latencies else 0
    median_latency = statistics.median(latencies) if latencies else 0
    min_latency = min(latencies) if latencies else 0
    max_latency = max(latencies) if latencies else 0
    
    # Falhas por módulo
    module_failures = defaultdict(int)
    module_statuses = defaultdict(lambda: {"OK": 0, "ERROR": 0, "UNKNOWN": 0})
    
    for result in valid_results:
        pipeline = result.get("pipeline_steps", {})
        for module, status in pipeline.items():
            if status in ["OK", "CONFIRMED", "ACCEPT"]:
                module_statuses[module]["OK"] += 1
            elif status in ["ERROR", "REJECT", "FAILED"]:
                module_statuses[module]["ERROR"] += 1
                module_failures[module] += 1
            else:
                module_statuses[module]["UNKNOWN"] += 1
    
    # Comportamentos de retry
    retries_detected = [r for r in valid_results if r.get("retry_detected", False)]
    retry_rate = (len(retries_detected) / total_valid * 100) if total_valid > 0 else 0
    
    # Erros por tipo
    error_types = defaultdict(int)
    for result in failed:
        status = result.get("status", "unknown")
        error_types[status] += 1
        if result.get("error_reason"):
            error_types[f"{status}_{result['error_reason']}"] += 1
    
    # Salvar resultados
    results["summary"] = {
        "total_requests": results["total_requests"],
        "valid_requests": total_valid,
        "successful_requests": len(successful),
        "failed_requests": len(failed),
        "success_rate": round(success_rate, 2),
        "total_time_seconds": round(total_time, 2),
        "requests_per_second": round(total_valid / total_time, 2) if total_time > 0 else 0,
        "latency": {
            "average_ms": round(avg_latency, 2),
            "median_ms": round(median_latency, 2),
            "min_ms": round(min_latency, 2),
            "max_ms": round(max_latency, 2)
        },
        "module_failures": dict(module_failures),
        "module_statuses": {k: dict(v) for k, v in module_statuses.items()},
        "retry_rate": round(retry_rate, 2),
        "retries_detected": len(retries_detected),
        "error_types": dict(error_types)
    }
    
    # Exibir resultados
    print_results()

def print_results():
    """
    Exibe os resultados formatados.
    """
    summary = results["summary"]
    
    print_section("RESULTADOS DO STRESS TEST")
    
    # Taxa de sucesso
    print(f"{Colors.BOLD}Taxa de Sucesso:{Colors.RESET}")
    success_rate = summary["success_rate"]
    if success_rate >= 95:
        print_success(f"  {success_rate}% ({summary['successful_requests']}/{summary['valid_requests']})")
    elif success_rate >= 80:
        print_warning(f"  {success_rate}% ({summary['successful_requests']}/{summary['valid_requests']})")
    else:
        print_error(f"  {success_rate}% ({summary['successful_requests']}/{summary['valid_requests']})")
    
    print()
    
    # Latência
    print(f"{Colors.BOLD}Latência:{Colors.RESET}")
    latency = summary["latency"]
    print_info(f"  Média: {latency['average_ms']}ms")
    print_info(f"  Mediana: {latency['median_ms']}ms")
    print_info(f"  Mínima: {latency['min_ms']}ms")
    print_info(f"  Máxima: {latency['max_ms']}ms")
    
    print()
    
    # Throughput
    print(f"{Colors.BOLD}Throughput:{Colors.RESET}")
    print_info(f"  Total de requisições: {summary['valid_requests']}")
    print_info(f"  Tempo total: {summary['total_time_seconds']}s")
    print_info(f"  Requisições/segundo: {summary['requests_per_second']}")
    
    print()
    
    # Falhas por módulo
    if summary["module_failures"]:
        print(f"{Colors.BOLD}Falhas por Módulo:{Colors.RESET}")
        for module, count in summary["module_failures"].items():
            print_error(f"  {module.upper()}: {count} falhas")
    else:
        print_success("Nenhuma falha de módulo detectada")
    
    print()
    
    # Status por módulo
    if summary["module_statuses"]:
        print(f"{Colors.BOLD}Status por Módulo:{Colors.RESET}")
        for module, statuses in summary["module_statuses"].items():
            ok = statuses.get("OK", 0)
            error = statuses.get("ERROR", 0)
            unknown = statuses.get("UNKNOWN", 0)
            total = ok + error + unknown
            if total > 0:
                ok_rate = (ok / total * 100) if total > 0 else 0
                if ok_rate >= 95:
                    print_success(f"  {module.upper()}: {ok} OK, {error} ERROR, {unknown} UNKNOWN ({ok_rate:.1f}% OK)")
                elif ok_rate >= 80:
                    print_warning(f"  {module.upper()}: {ok} OK, {error} ERROR, {unknown} UNKNOWN ({ok_rate:.1f}% OK)")
                else:
                    print_error(f"  {module.upper()}: {ok} OK, {error} ERROR, {unknown} UNKNOWN ({ok_rate:.1f}% OK)")
    
    print()
    
    # Comportamentos de retry
    print(f"{Colors.BOLD}Comportamentos de Retry:{Colors.RESET}")
    retry_rate = summary["retry_rate"]
    retries_count = summary["retries_detected"]
    if retries_count > 0:
        print_warning(f"  Retries detectados: {retries_count} ({retry_rate}%)")
        print_info("  (Retries são detectados quando latência > 10s ou timeout ocorre)")
    else:
        print_success(f"  Nenhum retry detectado ({retry_rate}%)")
    
    print()
    
    # Tipos de erro
    if summary["error_types"]:
        print(f"{Colors.BOLD}Tipos de Erro:{Colors.RESET}")
        for error_type, count in summary["error_types"].items():
            print_error(f"  {error_type}: {count} ocorrências")
    
    print()
    
    # Detalhes das requisições
    print_section("DETALHES DAS REQUISIÇÕES")
    
    successful = [r for r in results["requests"] if isinstance(r, dict) and r.get("success")]
    failed = [r for r in results["requests"] if isinstance(r, dict) and not r.get("success")]
    
    if successful:
        print_success(f"Requisições bem-sucedidas ({len(successful)}):")
        for result in successful[:5]:  # Mostrar apenas as primeiras 5
            print(f"  Request #{result['request_id']}: {result['latency_ms']}ms - SLA ID: {result.get('sla_id', 'N/A')}")
        if len(successful) > 5:
            print_info(f"  ... e mais {len(successful) - 5} requisições bem-sucedidas")
    
    print()
    
    if failed:
        print_error(f"Requisições falhadas ({len(failed)}):")
        for result in failed[:5]:  # Mostrar apenas as primeiras 5
            status = result.get("status", "unknown")
            errors = result.get("errors", [])
            error_msg = errors[0] if errors else "N/A"
            print(f"  Request #{result['request_id']}: {status} - {error_msg[:80]}")
        if len(failed) > 5:
            print_info(f"  ... e mais {len(failed) - 5} requisições falhadas")
    
    # Salvar relatório JSON
    save_report()

def save_report():
    """
    Salva relatório detalhado em JSON.
    """
    report_path = "backend/stress_test_report.json"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print()
    print_info(f"Relatório detalhado salvo em: {report_path}")

async def main():
    """
    Função principal.
    """
    import sys
    
    num_requests = 20
    backend_url = "http://localhost:8001"
    
    # Parse argumentos
    if len(sys.argv) > 1:
        try:
            num_requests = int(sys.argv[1])
        except ValueError:
            print_warning(f"Argumento inválido: {sys.argv[1]}. Usando padrão: 20")
    
    if len(sys.argv) > 2:
        backend_url = sys.argv[2]
    
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("="*70)
    print("STRESS TEST - Portal TriSLA")
    print("Submissão de SLA em Paralelo")
    print("="*70)
    print(f"{Colors.RESET}\n")
    
    try:
        await run_stress_test(num_requests, backend_url)
    except KeyboardInterrupt:
        print()
        print_warning("Teste interrompido pelo usuário")
    except Exception as e:
        print_error(f"Erro ao executar stress test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())




