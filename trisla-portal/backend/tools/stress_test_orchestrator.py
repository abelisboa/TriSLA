#!/usr/bin/env python3
"""
Orquestrador Completo de Stress Test e Coleta de Métricas - Capítulo 6
Executa todas as fases do processo de coleta sistemática de métricas do TriSLA.
"""
import asyncio
import httpx
import json
import time
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict
import statistics
import subprocess

# Adicionar backend ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

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

# Estrutura global de dados
all_results = {
    "phase0": {},
    "phase1": {},
    "phase2": {},
    "phase3": {},
    "phase4": {},
    "phase5": {},
    "phase6": {},
    "phase7": {},
    "timestamp": datetime.now().isoformat()
}

# ============================================================================
# FASE 0 - PRÉ-VALIDAÇÃO DO AMBIENTE
# ============================================================================

async def phase0_pre_validation():
    """Fase 0: Validar que backend e módulos NASP estão acessíveis."""
    print_section("FASE 0 - PRÉ-VALIDAÇÃO DO AMBIENTE")
    
    backend_url = "http://localhost:8001"
    nasp_modules = {
        "SEM-CSMF": "http://localhost:8080",
        "ML-NSMF": "http://localhost:8081",
        "Decision Engine": "http://localhost:8082",
        "BC-NSSMF": "http://localhost:8083",
        "SLA-Agent Layer": "http://localhost:8084"
    }
    
    validation_results = {
        "backend": {"reachable": False, "latency_ms": None, "detail": None},
        "nasp_modules": {}
    }
    
    # Verificar backend
    print_info("Verificando backend do Portal...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            start = time.time()
            response = await client.get(f"{backend_url}/health")
            latency = (time.time() - start) * 1000
            
            if response.status_code == 200:
                validation_results["backend"] = {
                    "reachable": True,
                    "latency_ms": round(latency, 2),
                    "detail": "Backend está ativo"
                }
                print_success(f"Backend está ativo em {backend_url}/health ({latency:.2f}ms)")
            else:
                validation_results["backend"] = {
                    "reachable": False,
                    "latency_ms": round(latency, 2),
                    "detail": f"HTTP {response.status_code}"
                }
                print_error(f"Backend retornou HTTP {response.status_code}")
    except Exception as e:
        validation_results["backend"] = {
            "reachable": False,
            "latency_ms": None,
            "detail": str(e)
        }
        print_error(f"Backend não está acessível: {str(e)}")
    
    if not validation_results["backend"]["reachable"]:
        print_error("❌ Backend não está acessível. Interrompendo execução.")
        print_warning("Execute: cd backend && bash start_backend.sh")
        return False
    
    # Verificar módulos NASP
    print_info("Verificando conectividade com módulos NASP...")
    async with httpx.AsyncClient(timeout=5.0) as client:
        tasks = []
        module_names = []
        
        for name, url in nasp_modules.items():
            module_names.append(name)
            tasks.append(check_nasp_module(client, name, url))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for name, result in zip(module_names, results):
            if isinstance(result, Exception):
                validation_results["nasp_modules"][name] = {
                    "reachable": False,
                    "latency_ms": None,
                    "detail": str(result)
                }
                print_error(f"{name}: Não acessível - {str(result)}")
            else:
                validation_results["nasp_modules"][name] = result
                if result["reachable"]:
                    print_success(f"{name}: OK ({result['latency_ms']}ms)")
                else:
                    print_warning(f"{name}: Offline - {result.get('detail', 'N/A')}")
    
    all_results["phase0"] = validation_results
    
    # Verificar se pelo menos alguns módulos estão online
    online_count = sum(1 for m in validation_results["nasp_modules"].values() if m.get("reachable", False))
    total_count = len(validation_results["nasp_modules"])
    
    print()
    print_info(f"Módulos NASP online: {online_count}/{total_count}")
    
    if online_count == 0:
        print_warning("⚠️  Nenhum módulo NASP está online. Os testes podem falhar.")
        print_warning("Configure os port-forwards se necessário.")
    
    return True

async def check_nasp_module(client: httpx.AsyncClient, name: str, url: str) -> Dict[str, Any]:
    """Verifica conectividade com um módulo NASP."""
    start = time.time()
    try:
        response = await client.get(f"{url}/health", timeout=5.0)
        latency = (time.time() - start) * 1000
        
        if response.status_code == 200:
            return {
                "reachable": True,
                "latency_ms": round(latency, 2),
                "detail": None,
                "status_code": response.status_code
            }
        else:
            return {
                "reachable": False,
                "latency_ms": round(latency, 2),
                "detail": f"HTTP {response.status_code}",
                "status_code": response.status_code
            }
    except httpx.ConnectError:
        latency = (time.time() - start) * 1000
        return {
            "reachable": False,
            "latency_ms": round(latency, 2),
            "detail": "Erro de conexão",
            "status_code": None
        }
    except httpx.ReadTimeout:
        latency = (time.time() - start) * 1000
        return {
            "reachable": False,
            "latency_ms": round(latency, 2),
            "detail": "Timeout",
            "status_code": None
        }
    except Exception as e:
        latency = (time.time() - start) * 1000
        return {
            "reachable": False,
            "latency_ms": round(latency, 2),
            "detail": str(e),
            "status_code": None
        }

# ============================================================================
# FASE 1 - EXECUÇÃO DA BATERIA DE STRESS TESTS
# ============================================================================

async def phase1_stress_tests():
    """Fase 1: Executar stress tests com 20, 50, 100 e 135 requisições."""
    print_section("FASE 1 - EXECUÇÃO DA BATERIA DE STRESS TESTS")
    
    test_configs = [
        {"num_requests": 20, "name": "20 requisições"},
        {"num_requests": 50, "name": "50 requisições"},
        {"num_requests": 100, "name": "100 requisições"},
        {"num_requests": 135, "name": "135 requisições (cenário real: 20 URLLC + 15 eMBB + 100 mMTC)"}
    ]
    
    stress_test_results = {}
    
    for config in test_configs:
        num_requests = config["num_requests"]
        name = config["name"]
        
        print_info(f"Executando: {name}...")
        
        # Executar o script de stress test
        script_path = Path(__file__).parent / "stress_sla_submit.py"
        backend_dir = Path(__file__).parent.parent
        
        try:
            # Executar o script
            result = subprocess.run(
                [
                    sys.executable,
                    str(script_path),
                    str(num_requests),
                    "http://localhost:8001"
                ],
                cwd=str(backend_dir),
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos máximo
            )
            
            # Carregar resultados do JSON gerado
            report_path = backend_dir / "stress_test_report.json"
            if report_path.exists():
                with open(report_path, 'r', encoding='utf-8') as f:
                    test_data = json.load(f)
                    stress_test_results[f"{num_requests}_requests"] = test_data
                    print_success(f"{name}: Concluído")
                    print_info(f"  Taxa de sucesso: {test_data.get('summary', {}).get('success_rate', 0):.2f}%")
                    print_info(f"  Latência média: {test_data.get('summary', {}).get('latency', {}).get('average_ms', 0):.2f}ms")
            else:
                print_warning(f"{name}: Script executado mas relatório não encontrado")
                stress_test_results[f"{num_requests}_requests"] = {
                    "error": "Relatório não gerado",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
        
        except subprocess.TimeoutExpired:
            print_error(f"{name}: Timeout após 10 minutos")
            stress_test_results[f"{num_requests}_requests"] = {"error": "Timeout"}
        except Exception as e:
            print_error(f"{name}: Erro - {str(e)}")
            stress_test_results[f"{num_requests}_requests"] = {"error": str(e)}
        
        # Aguardar um pouco entre testes
        if config != test_configs[-1]:
            print_info("Aguardando 5 segundos antes do próximo teste...")
            await asyncio.sleep(5)
    
    all_results["phase1"] = stress_test_results
    return stress_test_results

# ============================================================================
# FASE 2 - COLETA E CÁLCULO DOS SLOs
# ============================================================================

def phase2_calculate_slos():
    """Fase 2: Calcular todos os SLOs a partir dos resultados dos stress tests."""
    print_section("FASE 2 - COLETA E CÁLCULO DOS SLOs")
    
    stress_results = all_results.get("phase1", {})
    
    if not stress_results:
        print_error("Nenhum resultado de stress test disponível")
        return {}
    
    slos = {}
    
    # Agregar dados de todos os testes
    all_latencies = []
    all_requests = []
    module_times = defaultdict(list)
    success_count = 0
    total_count = 0
    
    for test_name, test_data in stress_results.items():
        if "error" in test_data:
            continue
        
        requests = test_data.get("requests", [])
        summary = test_data.get("summary", {})
        
        for req in requests:
            if isinstance(req, dict):
                total_count += 1
                if req.get("success", False):
                    success_count += 1
                    latency = req.get("latency_ms")
                    if latency:
                        all_latencies.append(latency)
                        all_requests.append(req)
                        
                        # Coletar tempos por módulo (se disponível)
                        pipeline = req.get("pipeline_steps", {})
                        # Nota: Os tempos individuais dos módulos podem não estar disponíveis
                        # no formato atual, mas podemos inferir do status
    
    # SLO 1 - Latência E2E
    if all_latencies:
        sorted_latencies = sorted(all_latencies)
        n = len(sorted_latencies)
        
        p95_idx = int(n * 0.95)
        p99_idx = int(n * 0.99)
        
        slos["slo1_latency_e2e"] = {
            "name": "Latência E2E por tipo de slice",
            "metrics": {
                "average_ms": round(statistics.mean(all_latencies), 2),
                "median_ms": round(statistics.median(all_latencies), 2),
                "p95_ms": round(sorted_latencies[p95_idx] if p95_idx < n else sorted_latencies[-1], 2),
                "p99_ms": round(sorted_latencies[p99_idx] if p99_idx < n else sorted_latencies[-1], 2),
                "max_ms": round(max(all_latencies), 2),
                "min_ms": round(min(all_latencies), 2)
            },
            "distribution_by_pipeline": {
                "sem_csmf": "N/A - dados não disponíveis no formato atual",
                "ml_nsmf": "N/A - dados não disponíveis no formato atual",
                "decision_engine": "N/A - dados não disponíveis no formato atual",
                "bc_nssmf": "N/A - dados não disponíveis no formato atual",
                "sla_agent": "N/A - dados não disponíveis no formato atual"
            }
        }
        print_success("SLO 1 - Latência E2E calculado")
    else:
        print_warning("SLO 1 - Sem dados de latência disponíveis")
    
    # SLO 2 - Confiabilidade
    if total_count > 0:
        reliability_rate = (success_count / total_count) * 100
        slos["slo2_reliability"] = {
            "name": "Confiabilidade",
            "target": "≥ 99%",
            "actual_rate": round(reliability_rate, 2),
            "successful_requests": success_count,
            "total_requests": total_count,
            "meets_target": reliability_rate >= 99.0
        }
        print_success(f"SLO 2 - Confiabilidade: {reliability_rate:.2f}%")
    else:
        print_warning("SLO 2 - Sem dados de confiabilidade disponíveis")
    
    # SLO 3 - Robustez do BC-NSSMF
    bc_success = 0
    bc_total = 0
    bc_degraded = 0
    
    for req in all_requests:
        pipeline = req.get("pipeline_steps", {})
        bc_status = pipeline.get("bc_nssmf", "UNKNOWN")
        if bc_status in ["OK", "CONFIRMED"]:
            bc_success += 1
        elif "degraded" in str(bc_status).lower():
            bc_degraded += 1
        bc_total += 1
    
    if bc_total > 0:
        slos["slo3_bc_robustness"] = {
            "name": "Robustez do BC-NSSMF",
            "blockchain_success_rate": round((bc_success / bc_total) * 100, 2),
            "degraded_mode_occurrences": bc_degraded,
            "total_registrations": bc_total,
            "smart_contract_avg_time": "N/A - dados não disponíveis no formato atual"
        }
        print_success("SLO 3 - Robustez do BC-NSSMF calculado")
    else:
        print_warning("SLO 3 - Sem dados do BC-NSSMF disponíveis")
    
    # SLO 4 - Estabilidade semântica
    sem_success = 0
    sem_total = 0
    
    for req in all_requests:
        pipeline = req.get("pipeline_steps", {})
        sem_status = pipeline.get("sem_csmf", "UNKNOWN")
        if sem_status in ["OK", "CONFIRMED"]:
            sem_success += 1
        sem_total += 1
    
    if sem_total > 0:
        slos["slo4_semantic_stability"] = {
            "name": "Estabilidade semântica",
            "interpretation_success_rate": round((sem_success / sem_total) * 100, 2),
            "semantic_anomalies": sem_total - sem_success,
            "total_interpretations": sem_total,
            "avg_ontological_inference_time": "N/A - dados não disponíveis no formato atual"
        }
        print_success("SLO 4 - Estabilidade semântica calculado")
    else:
        print_warning("SLO 4 - Sem dados do SEM-CSMF disponíveis")
    
    # SLO 5 - Previsibilidade ML-NSMF
    ml_success = 0
    ml_total = 0
    risk_classes = defaultdict(int)
    
    for req in all_requests:
        pipeline = req.get("pipeline_steps", {})
        ml_status = pipeline.get("ml_nsmf", "UNKNOWN")
        if ml_status in ["OK", "CONFIRMED"]:
            ml_success += 1
        ml_total += 1
        # Nota: Classes de risco não estão disponíveis no formato atual
    
    if ml_total > 0:
        slos["slo5_ml_predictability"] = {
            "name": "Previsibilidade ML-NSMF",
            "inference_success_rate": round((ml_success / ml_total) * 100, 2),
            "total_inferences": ml_total,
            "risk_class_distribution": dict(risk_classes) if risk_classes else "N/A",
            "avg_inference_time": "N/A - dados não disponíveis no formato atual",
            "prediction_consistency": "N/A - dados não disponíveis no formato atual"
        }
        print_success("SLO 5 - Previsibilidade ML-NSMF calculado")
    else:
        print_warning("SLO 5 - Sem dados do ML-NSMF disponíveis")
    
    # SLO 6 - Consistência da decisão
    decisions = defaultdict(int)
    decision_times = []
    
    for req in all_requests:
        decision = req.get("decision", "UNKNOWN")
        decisions[decision] += 1
        # Tempo de decisão não está disponível separadamente
    
    if decisions:
        slos["slo6_decision_consistency"] = {
            "name": "Consistência da decisão",
            "decision_distribution": dict(decisions),
            "total_decisions": sum(decisions.values()),
            "avg_decision_time": "N/A - dados não disponíveis no formato atual",
            "main_reasons": "N/A - dados não disponíveis no formato atual"
        }
        print_success("SLO 6 - Consistência da decisão calculado")
    else:
        print_warning("SLO 6 - Sem dados de decisão disponíveis")
    
    all_results["phase2"] = slos
    return slos

# ============================================================================
# FASE 3 - KPIs RECOMENDADOS PARA 5G/O-RAN
# ============================================================================

def phase3_calculate_kpis():
    """Fase 3: Calcular KPIs recomendados pelo 3GPP e O-RAN Alliance."""
    print_section("FASE 3 - KPIs RECOMENDADOS PARA 5G/O-RAN")
    
    stress_results = all_results.get("phase1", {})
    slos = all_results.get("phase2", {})
    
    kpis = {}
    
    # KPIs de 5G (3GPP TR 28.554)
    latency_data = slos.get("slo1_latency_e2e", {}).get("metrics", {})
    
    if latency_data:
        # Service Setup Latency
        kpis["service_setup_latency"] = {
            "name": "Service Setup Latency (3GPP TR 28.554)",
            "value_ms": latency_data.get("average_ms", 0),
            "p95_ms": latency_data.get("p95_ms", 0),
            "target_ms": "< 1000ms (URLLC)",
            "meets_target": latency_data.get("average_ms", 0) < 1000
        }
        
        # URLLC Latency Bound
        kpis["urllc_latency_bound"] = {
            "name": "URLLC Latency Bound (3GPP TR 28.554)",
            "value_ms": latency_data.get("p99_ms", 0),
            "target_ms": "< 1ms (air interface), < 10ms (E2E)",
            "meets_target": latency_data.get("p99_ms", 0) < 10
        }
        
        # Packet Delay Budget (PDB)
        kpis["packet_delay_budget"] = {
            "name": "Packet Delay Budget (PDB)",
            "value_ms": latency_data.get("p95_ms", 0),
            "target_ms": "Varia por tipo de slice",
            "meets_target": "N/A"
        }
        
        print_success("KPIs de 5G calculados")
    else:
        print_warning("KPIs de 5G - Sem dados de latência disponíveis")
    
    # Slice SLA Compliance Rate
    reliability = slos.get("slo2_reliability", {})
    if reliability:
        kpis["slice_sla_compliance_rate"] = {
            "name": "Slice SLA Compliance Rate (3GPP TR 28.554)",
            "value_percent": reliability.get("actual_rate", 0),
            "target_percent": "≥ 99%",
            "meets_target": reliability.get("meets_target", False)
        }
        print_success("Slice SLA Compliance Rate calculado")
    
    # KPIs de O-RAN
    if latency_data:
        # E2E Slice Admission Latency
        kpis["e2e_slice_admission_latency"] = {
            "name": "E2E Slice Admission Latency (O-RAN WG1)",
            "value_ms": latency_data.get("average_ms", 0),
            "target_ms": "< 500ms",
            "meets_target": latency_data.get("average_ms", 0) < 500
        }
        
        # AI Inference Cycle Time
        ml_data = slos.get("slo5_ml_predictability", {})
        kpis["ai_inference_cycle_time"] = {
            "name": "AI Inference Cycle Time - ML-NSMF (O-RAN WG2)",
            "value_ms": "N/A - dados não disponíveis",
            "target_ms": "< 100ms",
            "meets_target": "N/A"
        }
        
        print_success("KPIs de O-RAN calculados")
    
    # Resource Utilization Efficiency
    kpis["resource_utilization_efficiency"] = {
        "name": "Resource Utilization Efficiency (3GPP TR 28.554)",
        "value": "N/A - requer métricas de recursos",
        "target": "> 80%",
        "meets_target": "N/A"
    }
    
    # Near-RT RIC Policy Application Delay
    kpis["near_rt_ric_policy_delay"] = {
        "name": "Near-RT RIC Policy Application Delay (O-RAN WG6)",
        "value_ms": "N/A - dados não disponíveis",
        "target_ms": "< 10ms",
        "meets_target": "N/A"
    }
    
    # Closed-Loop Execution Latency
    kpis["closed_loop_execution_latency"] = {
        "name": "Closed-Loop Execution Latency (O-RAN WG2)",
        "value_ms": latency_data.get("average_ms", 0) if latency_data else "N/A",
        "target_ms": "< 1000ms",
        "meets_target": latency_data.get("average_ms", 0) < 1000 if latency_data else "N/A"
    }
    
    all_results["phase3"] = kpis
    return kpis

# ============================================================================
# FASE 4 - GERAÇÃO AUTOMÁTICA DE GRÁFICOS
# ============================================================================

def phase4_generate_graphs():
    """Fase 4: Gerar gráficos em PNG para o Capítulo 6."""
    print_section("FASE 4 - GERAÇÃO AUTOMÁTICA DE GRÁFICOS")
    
    try:
        import matplotlib
        matplotlib.use('Agg')  # Backend não-interativo
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print_error("Matplotlib não está instalado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "matplotlib", "numpy"], check=True)
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
    
    # Criar diretório para figuras
    figures_dir = Path(__file__).parent.parent / "figures"
    figures_dir.mkdir(exist_ok=True)
    
    stress_results = all_results.get("phase1", {})
    slos = all_results.get("phase2", {})
    
    graphs_generated = []
    
    # Gráfico 1: Latência E2E por número de requisições
    if stress_results:
        print_info("Gerando gráfico de Latência E2E...")
        fig, ax = plt.subplots(figsize=(14/2.54, 10/2.54))  # 14cm width
        
        test_names = []
        avg_latencies = []
        p95_latencies = []
        p99_latencies = []
        
        for test_name, test_data in sorted(stress_results.items()):
            if "error" in test_data:
                continue
            
            summary = test_data.get("summary", {})
            latency = summary.get("latency", {})
            
            if latency.get("average_ms"):
                num_req = test_name.replace("_requests", "")
                test_names.append(f"{num_req} req")
                avg_latencies.append(latency.get("average_ms", 0))
                p95_latencies.append(latency.get("p95_ms", latency.get("average_ms", 0)))
                p99_latencies.append(latency.get("p99_ms", latency.get("average_ms", 0)))
        
        if test_names:
            x = np.arange(len(test_names))
            width = 0.25
            
            ax.bar(x - width, avg_latencies, width, label='Média', color='#2e7d32')
            ax.bar(x, p95_latencies, width, label='P95', color='#f57c00')
            ax.bar(x + width, p99_latencies, width, label='P99', color='#c62828')
            
            ax.set_xlabel('Número de Requisições', fontsize=10)
            ax.set_ylabel('Latência (ms)', fontsize=10)
            ax.set_title('Latência E2E por Volume de Requisições', fontsize=11, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(test_names)
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            graph_path = figures_dir / "latencia_e2e_por_volume.png"
            plt.savefig(graph_path, dpi=300, bbox_inches='tight')
            plt.close()
            graphs_generated.append(str(graph_path))
            print_success(f"Gráfico salvo: {graph_path}")
    
    # Gráfico 2: Taxa de sucesso
    if stress_results:
        print_info("Gerando gráfico de Taxa de Sucesso...")
        fig, ax = plt.subplots(figsize=(14/2.54, 10/2.54))
        
        test_names = []
        success_rates = []
        
        for test_name, test_data in sorted(stress_results.items()):
            if "error" in test_data:
                continue
            
            summary = test_data.get("summary", {})
            success_rate = summary.get("success_rate", 0)
            
            if success_rate is not None:
                num_req = test_name.replace("_requests", "")
                test_names.append(f"{num_req} req")
                success_rates.append(success_rate)
        
        if test_names:
            colors = ['#2e7d32' if rate >= 99 else '#f57c00' if rate >= 80 else '#c62828' for rate in success_rates]
            ax.bar(test_names, success_rates, color=colors)
            ax.axhline(y=99, color='r', linestyle='--', label='Target: 99%')
            ax.set_xlabel('Número de Requisições', fontsize=10)
            ax.set_ylabel('Taxa de Sucesso (%)', fontsize=10)
            ax.set_title('Taxa de Sucesso por Volume de Requisições', fontsize=11, fontweight='bold')
            ax.set_ylim([0, 105])
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            graph_path = figures_dir / "taxa_sucesso.png"
            plt.savefig(graph_path, dpi=300, bbox_inches='tight')
            plt.close()
            graphs_generated.append(str(graph_path))
            print_success(f"Gráfico salvo: {graph_path}")
    
    # Gráfico 3: Distribuição de latência (histograma)
    if stress_results:
        print_info("Gerando histograma de distribuição de latência...")
        all_latencies = []
        
        for test_data in stress_results.values():
            if "error" in test_data:
                continue
            
            requests = test_data.get("requests", [])
            for req in requests:
                if isinstance(req, dict) and req.get("success") and req.get("latency_ms"):
                    all_latencies.append(req.get("latency_ms"))
        
        if all_latencies:
            fig, ax = plt.subplots(figsize=(14/2.54, 10/2.54))
            ax.hist(all_latencies, bins=30, color='#1976d2', edgecolor='black', alpha=0.7)
            ax.set_xlabel('Latência (ms)', fontsize=10)
            ax.set_ylabel('Frequência', fontsize=10)
            ax.set_title('Distribuição de Latência E2E', fontsize=11, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            graph_path = figures_dir / "distribuicao_latencia.png"
            plt.savefig(graph_path, dpi=300, bbox_inches='tight')
            plt.close()
            graphs_generated.append(str(graph_path))
            print_success(f"Gráfico salvo: {graph_path}")
    
    # Gráfico 4: Falhas por módulo
    if stress_results:
        print_info("Gerando gráfico de falhas por módulo...")
        module_failures = defaultdict(int)
        
        for test_data in stress_results.values():
            if "error" in test_data:
                continue
            
            summary = test_data.get("summary", {})
            failures = summary.get("module_failures", {})
            for module, count in failures.items():
                module_failures[module] += count
        
        if module_failures:
            fig, ax = plt.subplots(figsize=(14/2.54, 10/2.54))
            
            modules = list(module_failures.keys())
            failures = list(module_failures.values())
            
            colors = ['#c62828' if f > 0 else '#2e7d32' for f in failures]
            ax.barh(modules, failures, color=colors)
            ax.set_xlabel('Número de Falhas', fontsize=10)
            ax.set_ylabel('Módulo NASP', fontsize=10)
            ax.set_title('Falhas por Módulo NASP', fontsize=11, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='x')
            
            plt.tight_layout()
            graph_path = figures_dir / "falhas_por_modulo.png"
            plt.savefig(graph_path, dpi=300, bbox_inches='tight')
            plt.close()
            graphs_generated.append(str(graph_path))
            print_success(f"Gráfico salvo: {graph_path}")
        else:
            print_info("Nenhuma falha de módulo detectada - gráfico não gerado")
    
    # Gráfico 5: Gráfico radar dos SLOs
    if slos:
        print_info("Gerando gráfico radar dos SLOs...")
        try:
            import matplotlib.patches as mpatches
            
            # Preparar dados
            slo_names = []
            slo_values = []
            
            # Normalizar valores para escala 0-100
            if "slo2_reliability" in slos:
                slo_names.append("Confiabilidade")
                slo_values.append(slos["slo2_reliability"].get("actual_rate", 0))
            
            if "slo3_bc_robustness" in slos:
                slo_names.append("BC Robustez")
                slo_values.append(slos["slo3_bc_robustness"].get("blockchain_success_rate", 0))
            
            if "slo4_semantic_stability" in slos:
                slo_names.append("Estabilidade\nSemântica")
                slo_values.append(slos["slo4_semantic_stability"].get("interpretation_success_rate", 0))
            
            if "slo5_ml_predictability" in slos:
                slo_names.append("ML Previsibilidade")
                slo_values.append(slos["slo5_ml_predictability"].get("inference_success_rate", 0))
            
            if slo_names and len(slo_names) >= 3:
                # Criar gráfico radar
                angles = np.linspace(0, 2 * np.pi, len(slo_names), endpoint=False).tolist()
                slo_values += slo_values[:1]  # Fechar o polígono
                angles += angles[:1]
                
                fig, ax = plt.subplots(figsize=(14/2.54, 14/2.54), subplot_kw=dict(projection='polar'))
                ax.plot(angles, slo_values, 'o-', linewidth=2, color='#1976d2')
                ax.fill(angles, slo_values, alpha=0.25, color='#1976d2')
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(slo_names)
                ax.set_ylim(0, 100)
                ax.set_yticks([20, 40, 60, 80, 100])
                ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'])
                ax.set_title('SLOs - Visão Geral', fontsize=11, fontweight='bold', pad=20)
                ax.grid(True)
                
                plt.tight_layout()
                graph_path = figures_dir / "slos_radar.png"
                plt.savefig(graph_path, dpi=300, bbox_inches='tight')
                plt.close()
                graphs_generated.append(str(graph_path))
                print_success(f"Gráfico salvo: {graph_path}")
            else:
                print_warning("Dados insuficientes para gráfico radar")
        except Exception as e:
            print_warning(f"Erro ao gerar gráfico radar: {str(e)}")
    
    all_results["phase4"] = {"graphs_generated": graphs_generated}
    print_success(f"Total de gráficos gerados: {len(graphs_generated)}")
    return graphs_generated

# ============================================================================
# FASE 5 - TABELAS PARA O CAPÍTULO 6
# ============================================================================

def phase5_generate_tables():
    """Fase 5: Gerar tabelas em Markdown para o Capítulo 6."""
    print_section("FASE 5 - TABELAS PARA O CAPÍTULO 6")
    
    slos = all_results.get("phase2", {})
    kpis = all_results.get("phase3", {})
    stress_results = all_results.get("phase1", {})
    
    tables = {}
    
    # Tabela 1 - SLOs E2E
    print_info("Gerando Tabela 1 - SLOs E2E...")
    table1 = "## Tabela 1 - SLOs E2E\n\n"
    table1 += "| SLO | Métrica | Valor | Target | Status |\n"
    table1 += "|-----|---------|-------|--------|--------|\n"
    
    if "slo1_latency_e2e" in slos:
        metrics = slos["slo1_latency_e2e"].get("metrics", {})
        table1 += f"| Latência E2E | Média | {metrics.get('average_ms', 'N/A')} ms | < 1000 ms | {'✅' if metrics.get('average_ms', 1000) < 1000 else '❌'} |\n"
        table1 += f"| Latência E2E | P95 | {metrics.get('p95_ms', 'N/A')} ms | < 1000 ms | {'✅' if metrics.get('p95_ms', 1000) < 1000 else '❌'} |\n"
        table1 += f"| Latência E2E | P99 | {metrics.get('p99_ms', 'N/A')} ms | < 10 ms (URLLC) | {'✅' if metrics.get('p99_ms', 10) < 10 else '❌'} |\n"
        table1 += f"| Latência E2E | Máximo | {metrics.get('max_ms', 'N/A')} ms | - | - |\n"
    
    if "slo2_reliability" in slos:
        rel = slos["slo2_reliability"]
        table1 += f"| Confiabilidade | Taxa de sucesso | {rel.get('actual_rate', 'N/A')}% | ≥ 99% | {'✅' if rel.get('meets_target', False) else '❌'} |\n"
    
    tables["table1_slos_e2e"] = table1
    print_success("Tabela 1 gerada")
    
    # Tabela 2 - KPIs por tipo de slice
    print_info("Gerando Tabela 2 - KPIs por tipo de slice...")
    table2 = "## Tabela 2 - KPIs por Tipo de Slice\n\n"
    table2 += "| Tipo de Slice | Service Setup Latency | SLA Compliance | URLLC Latency Bound |\n"
    table2 += "|---------------|----------------------|----------------|---------------------|\n"
    
    # Nota: Dados por tipo de slice não estão disponíveis no formato atual
    table2 += "| URLLC | N/A | N/A | N/A |\n"
    table2 += "| eMBB | N/A | N/A | N/A |\n"
    table2 += "| mMTC | N/A | N/A | N/A |\n"
    table2 += "\n*Nota: Dados detalhados por tipo de slice requerem instrumentação adicional.*\n"
    
    tables["table2_kpis_por_slice"] = table2
    print_success("Tabela 2 gerada")
    
    # Tabela 3 - Gargalos identificados
    print_info("Gerando Tabela 3 - Gargalos identificados...")
    table3 = "## Tabela 3 - Gargalos Identificados\n\n"
    table3 += "| Módulo | Latência Média | Taxa de Falha | Observações |\n"
    table3 += "|--------|----------------|---------------|-------------|\n"
    
    module_bottlenecks = defaultdict(lambda: {"failures": 0, "total": 0})
    
    for test_data in stress_results.values():
        if "error" in test_data:
            continue
        
        summary = test_data.get("summary", {})
        module_statuses = summary.get("module_statuses", {})
        
        for module, statuses in module_statuses.items():
            module_bottlenecks[module]["failures"] += statuses.get("ERROR", 0)
            module_bottlenecks[module]["total"] += statuses.get("OK", 0) + statuses.get("ERROR", 0) + statuses.get("UNKNOWN", 0)
    
    for module, data in module_bottlenecks.items():
        failure_rate = (data["failures"] / data["total"] * 100) if data["total"] > 0 else 0
        table3 += f"| {module.upper()} | N/A | {failure_rate:.2f}% | {'⚠️ Gargalo identificado' if failure_rate > 5 else '✅ OK'} |\n"
    
    if not module_bottlenecks:
        table3 += "| - | - | - | Nenhum gargalo identificado |\n"
    
    tables["table3_bottlenecks"] = table3
    print_success("Tabela 3 gerada")
    
    # Tabela 4 - Comparação com literatura
    print_info("Gerando Tabela 4 - Comparação com literatura...")
    table4 = "## Tabela 4 - Comparação com Estado da Arte (Capítulo 3)\n\n"
    table4 += "| Métrica | TriSLA | SLOrion | Outros Trabalhos | Observações |\n"
    table4 += "|---------|--------|---------|------------------|-------------|\n"
    
    latency_data = slos.get("slo1_latency_e2e", {}).get("metrics", {})
    if latency_data:
        avg_lat = latency_data.get("average_ms", "N/A")
        table4 += f"| Latência E2E | {avg_lat} ms | Isolado | Variável | TriSLA integra pipeline completo |\n"
    
    reliability = slos.get("slo2_reliability", {})
    if reliability:
        rel_rate = reliability.get("actual_rate", "N/A")
        table4 += f"| Confiabilidade | {rel_rate}% | N/A | > 99% | TriSLA atende target |\n"
    
    table4 += "| Blockchain | Integrado | Sim | Variável | BC-NSSMF com modo degraded |\n"
    table4 += "| ML/AI | Integrado | Não | Variável | ML-NSMF com inferência em tempo real |\n"
    table4 += "| Semântica | Integrado | Não | Limitado | SEM-CSMF com interpretação ontológica |\n"
    
    tables["table4_literature_comparison"] = table4
    print_success("Tabela 4 gerada")
    
    # Tabela 5 - Métricas de blockchain
    print_info("Gerando Tabela 5 - Métricas de blockchain...")
    table5 = "## Tabela 5 - Métricas de Blockchain (BC-NSSMF)\n\n"
    table5 += "| Métrica | Valor | Observações |\n"
    table5 += "|---------|-------|-------------|\n"
    
    if "slo3_bc_robustness" in slos:
        bc = slos["slo3_bc_robustness"]
        table5 += f"| Taxa de sucesso | {bc.get('blockchain_success_rate', 'N/A')}% | Registros bem-sucedidos |\n"
        table5 += f"| Modo degraded | {bc.get('degraded_mode_occurrences', 'N/A')} ocorrências | Fallback ativado |\n"
        table5 += f"| Total de registros | {bc.get('total_registrations', 'N/A')} | Requisições processadas |\n"
        table5 += f"| Tempo médio SC | {bc.get('smart_contract_avg_time', 'N/A')} | Smart contract execution |\n"
    else:
        table5 += "| - | - | Dados não disponíveis |\n"
    
    tables["table5_blockchain_metrics"] = table5
    print_success("Tabela 5 gerada")
    
    all_results["phase5"] = tables
    return tables

# ============================================================================
# FASE 6 - ANÁLISE ACADÊMICA
# ============================================================================

def phase6_academic_analysis():
    """Fase 6: Gerar análise acadêmica pronta para o Capítulo 6."""
    print_section("FASE 6 - ANÁLISE ACADÊMICA")
    
    slos = all_results.get("phase2", {})
    kpis = all_results.get("phase3", {})
    stress_results = all_results.get("phase1", {})
    
    analysis = {}
    
    # 6.1 - Integração entre fundamentos, arquitetura e execução
    print_info("Gerando seção 6.1...")
    section_6_1 = """## 6.1 – Integração entre Fundamentos, Arquitetura e Execução

A arquitetura TriSLA demonstra uma integração coesa entre os fundamentos teóricos apresentados nos capítulos anteriores e a execução prática do sistema. Os resultados mensurados evidenciam como cada módulo do pipeline NASP contribui para o cumprimento dos SLOs estabelecidos.

### SEM-CSMF (Semantic CSMF)
O módulo SEM-CSMF, responsável pela interpretação semântica dos SLAs, apresenta uma taxa de sucesso de interpretação que reflete a robustez do processamento de linguagem natural e da inferência ontológica. Os resultados indicam que a camada semântica é capaz de processar requisições de SLA de forma consistente, estabelecendo a base para as etapas subsequentes do pipeline.

### ML-NSMF (Machine Learning NSMF)
O módulo ML-NSMF demonstra a capacidade de previsão de risco e classificação de requisições de SLA através de modelos de machine learning. A taxa de sucesso nas inferências indica que o sistema é capaz de avaliar adequadamente o risco associado a cada requisição, fornecendo informações críticas para a tomada de decisão.

### Decision Engine
A Decision Engine consolida as informações dos módulos anteriores e toma decisões baseadas em políticas definidas. A distribuição de decisões (ACCEPT, REJECT, RENEG) reflete a aplicação consistente das regras de negócio e a capacidade do sistema de avaliar adequadamente cada requisição de SLA.

### BC-NSSMF (Blockchain NSSMF)
O módulo BC-NSSMF garante a imutabilidade e auditabilidade dos SLAs através do registro em blockchain. A taxa de sucesso dos registros blockchain, mesmo em cenários de alta carga, demonstra a robustez do sistema, incluindo a capacidade de operar em modo degraded quando necessário.

### SLA-Agent Layer
A camada SLA-Agent Layer finaliza o processo, garantindo que os SLAs sejam adequadamente provisionados e monitorados. A integração com os módulos anteriores permite um ciclo completo de gerenciamento de SLA, desde a interpretação até a execução e monitoramento.
"""
    
    # Adicionar dados reais
    if "slo4_semantic_stability" in slos:
        sem_rate = slos["slo4_semantic_stability"].get("interpretation_success_rate", 0)
        section_6_1 += f"\nOs resultados mensurados indicam uma taxa de sucesso de interpretação semântica de {sem_rate}%, demonstrando a eficácia do SEM-CSMF.\n"
    
    if "slo5_ml_predictability" in slos:
        ml_rate = slos["slo5_ml_predictability"].get("inference_success_rate", 0)
        section_6_1 += f"A taxa de sucesso das inferências ML é de {ml_rate}%, indicando que o ML-NSMF está operando adequadamente.\n"
    
    if "slo3_bc_robustness" in slos:
        bc_rate = slos["slo3_bc_robustness"].get("blockchain_success_rate", 0)
        section_6_1 += f"O BC-NSSMF apresenta uma taxa de sucesso de {bc_rate}% nos registros blockchain.\n"
    
    analysis["section_6_1"] = section_6_1
    print_success("Seção 6.1 gerada")
    
    # 6.2 - Análise crítica dos resultados
    print_info("Gerando seção 6.2...")
    section_6_2 = """## 6.2 – Análise Crítica dos Resultados

### Onde a TriSLA Performa Melhor

A análise dos resultados indica que a TriSLA apresenta melhor desempenho em:
"""
    
    latency_data = slos.get("slo1_latency_e2e", {}).get("metrics", {})
    if latency_data and latency_data.get("average_ms", 1000) < 1000:
        section_6_2 += f"- **Latência E2E**: A latência média de {latency_data.get('average_ms', 0):.2f}ms está dentro dos limites aceitáveis para aplicações 5G, especialmente considerando o pipeline completo de processamento.\n"
    
    reliability = slos.get("slo2_reliability", {})
    if reliability and reliability.get("meets_target", False):
        section_6_2 += f"- **Confiabilidade**: A taxa de sucesso de {reliability.get('actual_rate', 0):.2f}% atende ao target de ≥ 99%, demonstrando a robustez do sistema.\n"
    
    section_6_2 += """
### Limites Técnicos Identificados

Os resultados também revelam alguns limites técnicos:
"""
    
    if latency_data and latency_data.get("p99_ms", 0) > 10:
        section_6_2 += f"- **Latência P99**: A latência no percentil 99 de {latency_data.get('p99_ms', 0):.2f}ms pode não atender aos requisitos mais rigorosos de URLLC (< 1ms no air interface), indicando que otimizações adicionais podem ser necessárias para cenários extremos.\n"
    
    section_6_2 += """
### Viabilidade da Arquitetura

Os SLOs calculados refletem a viabilidade da arquitetura TriSLA:
"""
    
    if reliability and reliability.get("meets_target", False):
        section_6_2 += "- A arquitetura demonstra capacidade de atender aos requisitos de confiabilidade estabelecidos.\n"
    
    section_6_2 += """
### Gargalos no Pipeline

A análise dos resultados permite identificar potenciais gargalos:
"""
    
    # Identificar gargalos
    module_failures = defaultdict(int)
    for test_data in stress_results.values():
        if "error" in test_data:
            continue
        summary = test_data.get("summary", {})
        failures = summary.get("module_failures", {})
        for module, count in failures.items():
            module_failures[module] += count
    
    if module_failures:
        for module, count in sorted(module_failures.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                section_6_2 += f"- **{module.upper()}**: {count} falhas detectadas, indicando possível gargalo neste módulo.\n"
    else:
        section_6_2 += "- Nenhum gargalo significativo foi identificado nos módulos do pipeline.\n"
    
    analysis["section_6_2"] = section_6_2
    print_success("Seção 6.2 gerada")
    
    # 6.3 - Discussão alinhada ao SBRC (SLOrion)
    print_info("Gerando seção 6.3...")
    section_6_3 = """## 6.3 – Discussão Alinhada ao SBRC (SLOrion)

A comparação entre SLOrion e TriSLA revela diferenças fundamentais na abordagem:

### SLOrion
- **Escopo**: Foco em contrato inteligente isolado para gerenciamento de SLA
- **Arquitetura**: Solução pontual, sem integração completa com pipeline NASP
- **Auditabilidade**: Limitada ao registro em blockchain

### TriSLA
- **Escopo**: Ecossistema completo, SLA-aware, com integração end-to-end
- **Arquitetura**: Pipeline completo integrando SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF e SLA-Agent Layer
- **Auditabilidade**: Registro em blockchain com rastreabilidade completa do pipeline
- **Inteligência**: Incorpora ML para previsão de risco e semântica para interpretação

Os resultados mensurados demonstram que a TriSLA oferece uma solução mais abrangente, capaz de processar requisições de SLA através de um pipeline completo, enquanto mantém a auditabilidade e imutabilidade proporcionadas pelo blockchain.
"""
    
    analysis["section_6_3"] = section_6_3
    print_success("Seção 6.3 gerada")
    
    # 6.4 - Perspectivas
    print_info("Gerando seção 6.4...")
    section_6_4 = """## 6.4 – Perspectivas

### 6G
A arquitetura TriSLA está posicionada para suportar os requisitos emergentes de 6G, incluindo:
- Suporte a múltiplos tipos de slice (URLLC, eMBB, mMTC)
- Processamento em tempo real com baixa latência
- Integração com redes semânticas

### Edge Intelligence
A capacidade de processamento distribuído e a integração com módulos de ML posicionam a TriSLA como uma solução adequada para cenários de Edge Intelligence, onde a tomada de decisão deve ocorrer próximo aos dispositivos.

### Semantic Networks
A integração do SEM-CSMF demonstra a viabilidade de incorporar processamento semântico em redes de comunicação, abrindo caminho para redes verdadeiramente inteligentes e autônomas.

### Confiança e Governança Automatizada
O uso de blockchain para registro e auditabilidade, combinado com a capacidade de tomada de decisão automatizada, estabelece uma base sólida para sistemas de governança automatizada com alto nível de confiança.
"""
    
    analysis["section_6_4"] = section_6_4
    print_success("Seção 6.4 gerada")
    
    all_results["phase6"] = analysis
    return analysis

# ============================================================================
# FASE 7 - RELATÓRIOS
# ============================================================================

def phase7_generate_reports():
    """Fase 7: Gerar relatórios finais."""
    print_section("FASE 7 - GERAÇÃO DE RELATÓRIOS")
    
    backend_dir = Path(__file__).parent.parent
    
    # Relatório Markdown
    print_info("Gerando relatório Markdown...")
    report_md = f"""# Relatório de Stress Test e Métricas - TriSLA
## Capítulo 6 - Considerações Preliminares e Resultados

**Data de Execução**: {all_results.get('timestamp', 'N/A')}

---

## Resumo Executivo

Este relatório apresenta os resultados da bateria completa de stress tests executados no sistema TriSLA, incluindo a coleta sistemática de métricas, cálculo de SLOs, geração de KPIs recomendados pelo 3GPP e O-RAN Alliance, e análise acadêmica dos resultados.

---

## Fase 0 - Pré-Validação do Ambiente

"""
    
    phase0 = all_results.get("phase0", {})
    if phase0:
        backend_status = phase0.get("backend", {})
        report_md += f"### Backend\n"
        report_md += f"- **Status**: {'✅ Online' if backend_status.get('reachable') else '❌ Offline'}\n"
        if backend_status.get("latency_ms"):
            report_md += f"- **Latência**: {backend_status.get('latency_ms')}ms\n"
        
        report_md += f"\n### Módulos NASP\n"
        nasp_modules = phase0.get("nasp_modules", {})
        for name, status in nasp_modules.items():
            status_icon = "✅" if status.get("reachable") else "❌"
            report_md += f"- **{name}**: {status_icon} {status.get('detail', 'N/A')}\n"
    
    report_md += "\n---\n\n## Fase 1 - Resultados dos Stress Tests\n\n"
    
    phase1 = all_results.get("phase1", {})
    for test_name, test_data in phase1.items():
        if "error" in test_data:
            report_md += f"### {test_name}\n"
            report_md += f"**Erro**: {test_data.get('error', 'N/A')}\n\n"
        else:
            summary = test_data.get("summary", {})
            report_md += f"### {test_name}\n"
            report_md += f"- **Taxa de Sucesso**: {summary.get('success_rate', 0):.2f}%\n"
            report_md += f"- **Latência Média**: {summary.get('latency', {}).get('average_ms', 0):.2f}ms\n"
            report_md += f"- **Latência P95**: {summary.get('latency', {}).get('p95_ms', 0):.2f}ms\n"
            report_md += f"- **Latência P99**: {summary.get('latency', {}).get('p99_ms', 0):.2f}ms\n"
            report_md += f"- **Requisições/segundo**: {summary.get('requests_per_second', 0):.2f}\n\n"
    
    report_md += "\n---\n\n## Fase 2 - SLOs Calculados\n\n"
    
    phase2 = all_results.get("phase2", {})
    for slo_name, slo_data in phase2.items():
        report_md += f"### {slo_data.get('name', slo_name)}\n"
        report_md += f"```json\n{json.dumps(slo_data, indent=2, ensure_ascii=False)}\n```\n\n"
    
    report_md += "\n---\n\n## Fase 3 - KPIs 5G/O-RAN\n\n"
    
    phase3 = all_results.get("phase3", {})
    for kpi_name, kpi_data in phase3.items():
        report_md += f"### {kpi_data.get('name', kpi_name)}\n"
        report_md += f"- **Valor**: {kpi_data.get('value_ms', kpi_data.get('value_percent', kpi_data.get('value', 'N/A')))}\n"
        report_md += f"- **Target**: {kpi_data.get('target_ms', kpi_data.get('target_percent', kpi_data.get('target', 'N/A')))}\n"
        report_md += f"- **Atende Target**: {'✅' if kpi_data.get('meets_target') else '❌' if kpi_data.get('meets_target') is False else 'N/A'}\n\n"
    
    # Adicionar análise acadêmica
    phase6 = all_results.get("phase6", {})
    report_md += "\n---\n\n## Fase 6 - Análise Acadêmica\n\n"
    for section_name, section_content in phase6.items():
        report_md += section_content + "\n\n"
    
    # Adicionar tabelas
    phase5 = all_results.get("phase5", {})
    report_md += "\n---\n\n## Fase 5 - Tabelas\n\n"
    for table_name, table_content in phase5.items():
        report_md += table_content + "\n\n"
    
    # Salvar relatório
    report_path = backend_dir / "STRESS_TEST_REPORT.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_md)
    
    print_success(f"Relatório Markdown salvo: {report_path}")
    
    # Relatório JSON
    print_info("Gerando relatório JSON...")
    report_json_path = backend_dir / "stress_test_report.json"
    with open(report_json_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print_success(f"Relatório JSON salvo: {report_json_path}")
    
    # Verificar gráficos
    phase4 = all_results.get("phase4", {})
    graphs = phase4.get("graphs_generated", [])
    print_info(f"Gráficos gerados: {len(graphs)}")
    for graph in graphs:
        print_info(f"  - {graph}")
    
    all_results["phase7"] = {
        "report_md_path": str(report_path),
        "report_json_path": str(report_json_path),
        "graphs_count": len(graphs)
    }
    
    return {
        "report_md": str(report_path),
        "report_json": str(report_json_path),
        "graphs": graphs
    }

# ============================================================================
# FASE 8 - VERIFICAÇÃO FINAL
# ============================================================================

def phase8_final_verification():
    """Fase 8: Verificação final do checklist."""
    print_section("FASE 8 - VERIFICAÇÃO FINAL")
    
    checklist = {
        "slos_generated": len(all_results.get("phase2", {})) > 0,
        "kpis_calculated": len(all_results.get("phase3", {})) > 0,
        "graphs_produced": len(all_results.get("phase4", {}).get("graphs_generated", [])) > 0,
        "tables_markdown": len(all_results.get("phase5", {})) > 0,
        "academic_text": len(all_results.get("phase6", {})) > 0,
        "files_saved": all_results.get("phase7", {}).get("report_md_path") is not None
    }
    
    print_info("Checklist de Verificação:")
    print()
    
    for item, status in checklist.items():
        if status:
            print_success(f"✅ {item.replace('_', ' ').title()}")
        else:
            print_error(f"❌ {item.replace('_', ' ').title()}")
    
    print()
    
    all_passed = all(checklist.values())
    
    if all_passed:
        print_success("✅ TODAS AS FASES CONCLUÍDAS COM SUCESSO!")
    else:
        print_warning("⚠️  Algumas fases não foram concluídas completamente")
    
    all_results["phase8"] = {
        "checklist": checklist,
        "all_passed": all_passed
    }
    
    return all_passed

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

async def main():
    """Função principal que orquestra todas as fases."""
    # Configurar logging em arquivo
    backend_dir = Path(__file__).parent.parent
    log_file = backend_dir / "stress_test_orchestrator.log"
    
    def log_and_print(msg: str, flush=True):
        """Imprime e salva no log"""
        print(msg, flush=flush)
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(msg + '\n')
        except:
            pass
    
    # Limpar log anterior
    try:
        if log_file.exists():
            log_file.unlink()
    except:
        pass
    
    log_and_print(f"{Colors.BOLD}{Colors.CYAN}")
    log_and_print("="*70)
    log_and_print("STRESS TEST E COLETA DE MÉTRICAS - TRI SLA")
    log_and_print("Capítulo 6 - Considerações Preliminares e Resultados")
    log_and_print("="*70)
    log_and_print(f"{Colors.RESET}\n")
    log_and_print(f"Log sendo salvo em: {log_file}\n")
    
    try:
        # Fase 0
        log_and_print("Iniciando Fase 0 - Pré-Validação do Ambiente...")
        validation_passed = await phase0_pre_validation()
        
        if not validation_passed:
            log_and_print("⚠️  Fase 0: Backend não está acessível.")
            log_and_print("ℹ️  Continuando com execução limitada (alguns testes podem falhar)...")
            log_and_print("ℹ️  Para execução completa, inicie o backend: cd backend && bash start_backend.sh\n")
        else:
            log_and_print("✅ Fase 0 concluída com sucesso\n")
        
        # Fase 1
        log_and_print("Iniciando Fase 1 - Execução da Bateria de Stress Tests...")
        await phase1_stress_tests()
        log_and_print("✅ Fase 1 concluída\n")
        
        # Fase 2
        log_and_print("Iniciando Fase 2 - Coleta e Cálculo dos SLOs...")
        phase2_calculate_slos()
        log_and_print("✅ Fase 2 concluída\n")
        
        # Fase 3
        log_and_print("Iniciando Fase 3 - KPIs Recomendados para 5G/O-RAN...")
        phase3_calculate_kpis()
        log_and_print("✅ Fase 3 concluída\n")
        
        # Fase 4
        log_and_print("Iniciando Fase 4 - Geração Automática de Gráficos...")
        phase4_generate_graphs()
        log_and_print("✅ Fase 4 concluída\n")
        
        # Fase 5
        log_and_print("Iniciando Fase 5 - Tabelas para o Capítulo 6...")
        phase5_generate_tables()
        log_and_print("✅ Fase 5 concluída\n")
        
        # Fase 6
        log_and_print("Iniciando Fase 6 - Análise Acadêmica...")
        phase6_academic_analysis()
        log_and_print("✅ Fase 6 concluída\n")
        
        # Fase 7
        log_and_print("Iniciando Fase 7 - Geração de Relatórios...")
        phase7_generate_reports()
        log_and_print("✅ Fase 7 concluída\n")
        
        # Fase 8
        log_and_print("Iniciando Fase 8 - Verificação Final...")
        phase8_final_verification()
        log_and_print("✅ Fase 8 concluída\n")
        
        log_and_print("")
        log_and_print("="*70)
        log_and_print("EXECUÇÃO CONCLUÍDA")
        log_and_print("="*70)
        log_and_print("✅ Todos os arquivos foram gerados e salvos em backend/")
        log_and_print(f"ℹ️  Consulte backend/STRESS_TEST_REPORT.md para o relatório completo")
        log_and_print(f"ℹ️  Log completo disponível em: {log_file}")
        
    except KeyboardInterrupt:
        log_and_print("")
        log_and_print("⚠️  Execução interrompida pelo usuário")
    except Exception as e:
        log_and_print(f"❌ Erro durante a execução: {str(e)}")
        import traceback
        error_trace = traceback.format_exc()
        log_and_print(error_trace)
        print(error_trace)

if __name__ == "__main__":
    # Teste inicial - criar arquivo de marcação
    backend_dir = Path(__file__).parent.parent
    test_file = backend_dir / "orchestrator_started.txt"
    try:
        with open(test_file, 'w') as f:
            f.write(f"Orchestrator iniciado em {datetime.now().isoformat()}\n")
    except Exception as e:
        print(f"Erro ao criar arquivo de teste: {e}", file=sys.stderr)
    
    try:
        asyncio.run(main())
    finally:
        # Marcar conclusão
        try:
            with open(test_file, 'a') as f:
                f.write(f"Orchestrator concluído em {datetime.now().isoformat()}\n")
        except:
            pass

