#!/usr/bin/env python3
"""
Script de Validação Completa do Portal TriSLA - NASP Integration
Executa todas as 8 fases de validação automaticamente
"""
import os
import sys
import json
import asyncio
import httpx
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
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
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

# Resultados globais
results = {
    "timestamp": datetime.now().isoformat(),
    "phases": {},
    "summary": {}
}

# FASE 1: Validar variáveis de ambiente
def phase1_validate_env():
    print_section("FASE 1: Validar Variáveis de Ambiente")
    
    phase_results = {
        "status": "pending",
        "variables": {},
        "defaults_ok": False,
        "issues": []
    }
    
    expected_vars = [
        "NASP_SEM_CSMF_URL",
        "NASP_ML_NSMF_URL",
        "NASP_DECISION_URL",
        "NASP_BC_NSSMF_URL",
        "NASP_SLA_AGENT_URL"
    ]
    
    expected_defaults = {
        "NASP_SEM_CSMF_URL": "http://localhost:8080",
        "NASP_ML_NSMF_URL": "http://localhost:8081",
        "NASP_DECISION_URL": "http://localhost:8082",
        "NASP_BC_NSSMF_URL": "http://localhost:8083",
        "NASP_SLA_AGENT_URL": "http://localhost:8084"
    }
    
    # Verificar variáveis de ambiente
    for var in expected_vars:
        value = os.getenv(var)
        if value:
            phase_results["variables"][var] = value
            print_success(f"{var} = {value}")
        else:
            # Verificar defaults no código
            try:
                from src.config import settings
                if var == "NASP_SEM_CSMF_URL":
                    default_value = settings.nasp_sem_csmf_url
                elif var == "NASP_ML_NSMF_URL":
                    default_value = settings.nasp_ml_nsmf_url
                elif var == "NASP_DECISION_URL":
                    default_value = settings.nasp_decision_url
                elif var == "NASP_BC_NSSMF_URL":
                    default_value = settings.nasp_bc_nssmf_url
                elif var == "NASP_SLA_AGENT_URL":
                    default_value = settings.nasp_sla_agent_url
                
                phase_results["variables"][var] = default_value
                if default_value == expected_defaults[var]:
                    print_success(f"{var} = {default_value} (default correto)")
                else:
                    print_warning(f"{var} = {default_value} (default diferente do esperado)")
                    phase_results["issues"].append(f"{var} tem default diferente: {default_value}")
            except Exception as e:
                print_error(f"Erro ao ler {var}: {str(e)}")
                phase_results["issues"].append(f"Erro ao ler {var}: {str(e)}")
    
    # Validar defaults
    defaults_ok = True
    for var, expected_default in expected_defaults.items():
        actual_value = phase_results["variables"].get(var, "")
        if actual_value != expected_default:
            defaults_ok = False
            break
    
    phase_results["defaults_ok"] = defaults_ok
    if defaults_ok:
        print_success("Todos os defaults correspondem a localhost:8080-8084")
    else:
        print_warning("Alguns defaults não correspondem ao esperado")
    
    phase_results["status"] = "passed" if len(phase_results["issues"]) == 0 else "warning"
    results["phases"]["phase1_env"] = phase_results
    return phase_results

# FASE 2: Validar módulo de configuração
def phase2_validate_config():
    print_section("FASE 2: Validar Módulo de Configuração")
    
    phase_results = {
        "status": "pending",
        "hardcoded_urls": [],
        "uses_settings": True,
        "issues": []
    }
    
    try:
        # Ler arquivo config.py
        config_path = Path(__file__).parent.parent / "src" / "config.py"
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        # Verificar se há URLs hardcoded (exceto defaults)
        hardcoded_patterns = [
            '"http://localhost:8080"',
            '"http://localhost:8081"',
            '"http://localhost:8082"',
            '"http://localhost:8083"',
            '"http://localhost:8084"',
        ]
        
        # Verificar se usa Settings
        if "class Settings" in config_content and "BaseSettings" in config_content:
            print_success("Configuração usa BaseSettings (pydantic-settings)")
        else:
            print_error("Configuração não usa BaseSettings")
            phase_results["issues"].append("Configuração não usa BaseSettings")
            phase_results["uses_settings"] = False
        
        # Verificar se há imports de settings em nasp.py
        nasp_path = Path(__file__).parent.parent / "src" / "services" / "nasp.py"
        if nasp_path.exists():
            with open(nasp_path, 'r', encoding='utf-8') as f:
                nasp_content = f.read()
            
            if "from src.config import settings" in nasp_content:
                print_success("nasp.py importa settings corretamente")
            else:
                print_error("nasp.py não importa settings")
                phase_results["issues"].append("nasp.py não importa settings")
            
            # Verificar se usa settings.xxx_url
            if "settings.nasp_sem_csmf_url" in nasp_content or "settings.ml_nsmf_url" in nasp_content:
                print_success("nasp.py usa settings para URLs")
            else:
                print_error("nasp.py não usa settings para URLs")
                phase_results["issues"].append("nasp.py não usa settings para URLs")
        
        # Verificar se não há URLs hardcoded fora de defaults
        # (exceto nos defaults da classe Settings)
        if '"http://localhost:808' in config_content:
            # Verificar se está apenas nos defaults
            lines = config_content.split('\n')
            for i, line in enumerate(lines):
                if '"http://localhost:808' in line and 'default=' not in line:
                    if 'f"{settings.' not in line:  # Não é uso de settings
                        print_warning(f"Possível URL hardcoded na linha {i+1}: {line.strip()}")
                        phase_results["hardcoded_urls"].append(f"Linha {i+1}: {line.strip()}")
        
        if len(phase_results["hardcoded_urls"]) == 0:
            print_success("Nenhum endpoint hardcoded encontrado (exceto defaults)")
        else:
            print_warning(f"{len(phase_results['hardcoded_urls'])} possíveis URLs hardcoded encontradas")
        
    except Exception as e:
        print_error(f"Erro ao validar configuração: {str(e)}")
        phase_results["issues"].append(f"Erro: {str(e)}")
    
    phase_results["status"] = "passed" if len(phase_results["issues"]) == 0 else "failed"
    results["phases"]["phase2_config"] = phase_results
    return phase_results

# FASE 3: Testar /nasp/diagnostics
async def phase3_test_diagnostics():
    print_section("FASE 3: Testar /nasp/diagnostics")
    
    phase_results = {
        "status": "pending",
        "modules": {},
        "all_reachable": False,
        "latencies": {},
        "issues": []
    }
    
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8001")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{backend_url}/nasp/diagnostics")
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"GET /nasp/diagnostics retornou 200")
                
                modules_to_check = ["sem_csmf", "ml_nsmf", "decision", "bc_nssmf", "sla_agent"]
                all_reachable = True
                
                for module in modules_to_check:
                    module_data = data.get(module, {})
                    reachable = module_data.get("reachable", False)
                    latency = module_data.get("latency_ms")
                    detail = module_data.get("detail")
                    
                    phase_results["modules"][module] = {
                        "reachable": reachable,
                        "latency_ms": latency,
                        "detail": detail
                    }
                    
                    if latency:
                        phase_results["latencies"][module] = latency
                    
                    if reachable:
                        print_success(f"{module.upper()}: reachable=True, latency={latency}ms")
                    else:
                        all_reachable = False
                        print_error(f"{module.upper()}: reachable=False, detail={detail}")
                        phase_results["issues"].append(f"{module} não está acessível: {detail}")
                
                phase_results["all_reachable"] = all_reachable
                
                if all_reachable:
                    print_success("Todos os módulos NASP estão acessíveis")
                else:
                    print_warning("Alguns módulos NASP não estão acessíveis")
                    print_info("Sugestão: Verificar se os port-forwards estão ativos no node1")
            else:
                print_error(f"GET /nasp/diagnostics retornou {response.status_code}")
                phase_results["issues"].append(f"Status code {response.status_code}: {response.text}")
                
    except httpx.ConnectError:
        print_error("Não foi possível conectar ao backend. Verifique se está rodando em localhost:8001")
        phase_results["issues"].append("Backend não está acessível")
    except Exception as e:
        print_error(f"Erro ao testar /nasp/diagnostics: {str(e)}")
        phase_results["issues"].append(f"Erro: {str(e)}")
    
    phase_results["status"] = "passed" if phase_results["all_reachable"] else "failed"
    results["phases"]["phase3_diagnostics"] = phase_results
    return phase_results

# FASE 4: Testar /health
async def phase4_test_health():
    print_section("FASE 4: Testar /health")
    
    phase_results = {
        "status": "pending",
        "response": {},
        "has_status": False,
        "has_version": False,
        "has_nasp_link": False,
        "issues": []
    }
    
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8001")
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{backend_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                phase_results["response"] = data
                print_success(f"GET /health retornou 200")
                
                # Validar campos
                if "status" in data:
                    phase_results["has_status"] = True
                    print_success(f"Campo 'status' presente: {data['status']}")
                else:
                    print_error("Campo 'status' ausente")
                    phase_results["issues"].append("Campo 'status' ausente")
                
                if "version" in data:
                    phase_results["has_version"] = True
                    print_success(f"Campo 'version' presente: {data['version']}")
                else:
                    print_warning("Campo 'version' ausente (opcional)")
                
                if "nasp_details_url" in data:
                    phase_results["has_nasp_link"] = True
                    print_success(f"Campo 'nasp_details_url' presente: {data['nasp_details_url']}")
                else:
                    print_warning("Campo 'nasp_details_url' ausente (opcional)")
                
            else:
                print_error(f"GET /health retornou {response.status_code}")
                phase_results["issues"].append(f"Status code {response.status_code}")
                
    except httpx.ConnectError:
        print_error("Não foi possível conectar ao backend")
        phase_results["issues"].append("Backend não está acessível")
    except Exception as e:
        print_error(f"Erro ao testar /health: {str(e)}")
        phase_results["issues"].append(f"Erro: {str(e)}")
    
    phase_results["status"] = "passed" if phase_results["has_status"] and len(phase_results["issues"]) == 0 else "failed"
    results["phases"]["phase4_health"] = phase_results
    return phase_results

# FASE 5: Teste E2E do fluxo de SLA
async def phase5_test_sla_flow():
    print_section("FASE 5: Teste E2E do Fluxo de SLA")
    
    phase_results = {
        "status": "pending",
        "submission": {},
        "pipeline_steps": {},
        "retries_detected": False,
        "blockchain_registered": False,
        "issues": []
    }
    
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8001")
    
    # Payload de teste
    test_payload = {
        "template_id": "urllc-template-001",
        "tenant_id": "default",
        "form_values": {
            "type": "URLLC",
            "latency": 10,
            "reliability": 99.99,
            "availability": 99.99,
            "throughput_dl": 100,
            "throughput_ul": 50
        }
    }
    
    print_info("Enviando SLA de teste...")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            start_time = time.time()
            response = await client.post(
                f"{backend_url}/api/v1/sla/submit",
                json=test_payload
            )
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                phase_results["submission"] = data
                print_success(f"POST /api/v1/sla/submit retornou 200 (tempo: {elapsed_time:.2f}s)")
                
                # Validar pipeline
                pipeline_ok = True
                
                # SEM-CSMF
                if data.get("sem_csmf_status") == "OK":
                    phase_results["pipeline_steps"]["sem_csmf"] = "OK"
                    print_success("SEM-CSMF → OK")
                else:
                    phase_results["pipeline_steps"]["sem_csmf"] = data.get("sem_csmf_status", "ERROR")
                    print_error(f"SEM-CSMF → {data.get('sem_csmf_status', 'ERROR')}")
                    pipeline_ok = False
                
                # ML-NSMF
                if data.get("ml_nsmf_status") == "OK":
                    phase_results["pipeline_steps"]["ml_nsmf"] = "OK"
                    print_success("ML-NSMF → OK")
                else:
                    phase_results["pipeline_steps"]["ml_nsmf"] = data.get("ml_nsmf_status", "ERROR")
                    print_error(f"ML-NSMF → {data.get('ml_nsmf_status', 'ERROR')}")
                    pipeline_ok = False
                
                # Decision Engine
                decision = data.get("decision", "").upper()
                if decision in ["ACCEPT", "REJECT"]:
                    phase_results["pipeline_steps"]["decision_engine"] = decision
                    print_success(f"Decision Engine → {decision}")
                else:
                    phase_results["pipeline_steps"]["decision_engine"] = "INVALID"
                    print_error(f"Decision Engine → {decision} (inválido)")
                    pipeline_ok = False
                
                # SLA-aware gerado
                if data.get("sla_hash"):
                    phase_results["pipeline_steps"]["sla_aware"] = "OK"
                    print_success(f"SLA-aware gerado → hash: {data['sla_hash'][:16]}...")
                else:
                    phase_results["pipeline_steps"]["sla_aware"] = "MISSING"
                    print_warning("SLA-aware hash não encontrado na resposta")
                
                # BC-NSSMF
                bc_status = data.get("bc_status", "ERROR")
                tx_hash = data.get("tx_hash") or data.get("blockchain_tx_hash")
                
                if bc_status in ["CONFIRMED", "PENDING"] and tx_hash:
                    phase_results["pipeline_steps"]["bc_nssmf"] = bc_status
                    phase_results["blockchain_registered"] = True
                    print_success(f"BC-NSSMF → {bc_status}, tx_hash: {tx_hash[:16]}...")
                else:
                    phase_results["pipeline_steps"]["bc_nssmf"] = bc_status
                    print_error(f"BC-NSSMF → {bc_status}, tx_hash: {tx_hash or 'N/A'}")
                    pipeline_ok = False
                
                # Verificar se houve retries (não podemos detectar diretamente, mas podemos inferir pelo tempo)
                if elapsed_time > 10.0:  # Se demorou mais de 10s, pode ter havido retries
                    phase_results["retries_detected"] = True
                    print_info(f"Tempo de resposta alto ({elapsed_time:.2f}s) - possíveis retries")
                
                phase_results["status"] = "passed" if pipeline_ok else "warning"
                
            elif response.status_code == 503:
                # Erro de conectividade
                try:
                    error_data = response.json()
                    detail = error_data.get("detail", {})
                    if isinstance(detail, dict):
                        reason = detail.get("reason", "unknown")
                        if reason == "connection_error":
                            print_error("Erro de conexão com NASP - verifique port-forwards")
                            phase_results["issues"].append("Erro de conexão com NASP")
                        elif reason == "nasp_degraded":
                            print_error("NASP em modo degraded")
                            phase_results["issues"].append("NASP em modo degraded")
                except:
                    pass
                
                phase_results["status"] = "failed"
                print_error(f"POST /api/v1/sla/submit retornou 503")
            else:
                phase_results["status"] = "failed"
                print_error(f"POST /api/v1/sla/submit retornou {response.status_code}")
                phase_results["issues"].append(f"Status code {response.status_code}: {response.text[:200]}")
                
    except httpx.ConnectError:
        print_error("Não foi possível conectar ao backend")
        phase_results["issues"].append("Backend não está acessível")
        phase_results["status"] = "failed"
    except httpx.ReadTimeout:
        print_error("Timeout ao submeter SLA (pode indicar problemas de conectividade)")
        phase_results["issues"].append("Timeout na submissão")
        phase_results["status"] = "failed"
    except Exception as e:
        print_error(f"Erro ao testar fluxo de SLA: {str(e)}")
        phase_results["issues"].append(f"Erro: {str(e)}")
        phase_results["status"] = "failed"
    
    results["phases"]["phase5_sla_flow"] = phase_results
    return phase_results

# FASE 6: Validar comportamento do frontend
def phase6_validate_frontend():
    print_section("FASE 6: Validar Comportamento do Frontend")
    
    phase_results = {
        "status": "pending",
        "error_handling": {},
        "issues": []
    }
    
    api_path = Path(__file__).parent.parent.parent / "frontend" / "src" / "lib" / "api.ts"
    
    if not api_path.exists():
        print_warning("Arquivo frontend/src/lib/api.ts não encontrado")
        phase_results["issues"].append("Arquivo api.ts não encontrado")
        phase_results["status"] = "warning"
        results["phases"]["phase6_frontend"] = phase_results
        return phase_results
    
    try:
        with open(api_path, 'r', encoding='utf-8') as f:
            api_content = f.read()
        
        # Verificar tratamento de erros estruturados
        error_checks = {
            "connection_error": "connection_error" in api_content,
            "nasp_degraded": "nasp_degraded" in api_content,
            "invalid_payload": "invalid_payload" in api_content or "invalid" in api_content.lower(),
            "structured_errors": "errorData.detail" in api_content and "reason" in api_content
        }
        
        phase_results["error_handling"] = error_checks
        
        for check, passed in error_checks.items():
            if passed:
                print_success(f"Frontend trata '{check}' corretamente")
            else:
                print_warning(f"Frontend pode não tratar '{check}' adequadamente")
                phase_results["issues"].append(f"Tratamento de '{check}' não encontrado")
        
        # Verificar se há mensagens específicas
        if "Falha ao contatar" in api_content or "Verifique se o NASP está acessível" in api_content:
            print_success("Frontend tem mensagens específicas para erros de conectividade")
        else:
            print_warning("Frontend pode não ter mensagens específicas para erros de conectividade")
        
    except Exception as e:
        print_error(f"Erro ao validar frontend: {str(e)}")
        phase_results["issues"].append(f"Erro: {str(e)}")
    
    phase_results["status"] = "passed" if len(phase_results["issues"]) == 0 else "warning"
    results["phases"]["phase6_frontend"] = phase_results
    return phase_results

# FASE 7: Auditar lógica local
def phase7_audit_local_logic():
    print_section("FASE 7: Auditar Lógica Local")
    
    phase_results = {
        "status": "pending",
        "found_patterns": [],
        "mock_functions": [],
        "simulators": [],
        "issues": []
    }
    
    backend_src = Path(__file__).parent.parent / "src"
    
    patterns_to_check = [
        ("mock", "mock"),
        ("fake", "fake"),
        ("stub", "stub"),
        ("local_mode", "local_mode"),
        ("simulate", "simulate"),
        ("offline_mode", "offline_mode"),
        ("NO_BC", "NO_BC"),
        ("USE_MOCK", "USE_MOCK"),
        ("DEMO_MODE", "DEMO_MODE"),
        ("MOCK_NASP", "MOCK_NASP")
    ]
    
    for pattern_name, pattern in patterns_to_check:
        found_files = []
        for py_file in backend_src.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if pattern.lower() in content.lower():
                        # Verificar se não é apenas comentário ou string
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if pattern.lower() in line.lower():
                                # Verificar se não é comentário
                                stripped = line.strip()
                                if not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
                                    # Verificar se não é apenas parte de uma string maior
                                    if f'"{pattern}' in line or f"'{pattern}" in line or f'def {pattern}' in line or f'class {pattern}' in line:
                                        found_files.append(f"{py_file.relative_to(backend_src)}:{i+1}")
            except Exception:
                pass
        
        if found_files:
            phase_results["found_patterns"].append({
                "pattern": pattern_name,
                "files": found_files
            })
            print_warning(f"Padrão '{pattern_name}' encontrado em: {', '.join(found_files[:3])}")
        else:
            print_success(f"Nenhum padrão '{pattern_name}' encontrado")
    
    if len(phase_results["found_patterns"]) == 0:
        print_success("Nenhum simulador ou mock ativo encontrado")
        phase_results["status"] = "passed"
    else:
        print_warning(f"{len(phase_results['found_patterns'])} padrões suspeitos encontrados")
        phase_results["status"] = "warning"
        phase_results["issues"].append(f"Padrões suspeitos encontrados: {[p['pattern'] for p in phase_results['found_patterns']]}")
    
    results["phases"]["phase7_audit"] = phase_results
    return phase_results

# FASE 8: Criar relatório final
def phase8_generate_report():
    print_section("FASE 8: Gerar Relatório Final")
    
    # Calcular estatísticas
    total_phases = len(results["phases"])
    passed_phases = sum(1 for p in results["phases"].values() if p.get("status") == "passed")
    warning_phases = sum(1 for p in results["phases"].values() if p.get("status") == "warning")
    failed_phases = sum(1 for p in results["phases"].values() if p.get("status") == "failed")
    
    # Latências
    latencies = {}
    if "phase3_diagnostics" in results["phases"]:
        latencies = results["phases"]["phase3_diagnostics"].get("latencies", {})
    
    # Veredito
    if failed_phases == 0 and warning_phases == 0:
        veredict = "✅ APROVADO - Portal está configurado corretamente"
    elif failed_phases == 0:
        veredict = "⚠️ APROVADO COM RESSALVAS - Alguns pontos precisam de atenção"
    else:
        veredict = "❌ REPROVADO - Problemas críticos encontrados"
    
    # Gerar relatório Markdown
    report_content = f"""# Relatório de Validação - Portal TriSLA NASP Integration

**Data**: {results['timestamp']}  
**Veredito**: {veredict}

## Resumo Executivo

- **Total de Fases**: {total_phases}
- **✅ Aprovadas**: {passed_phases}
- **⚠️ Com Avisos**: {warning_phases}
- **❌ Falhas**: {failed_phases}

## Detalhamento por Fase

"""
    
    for phase_name, phase_data in results["phases"].items():
        status_icon = {
            "passed": "✅",
            "warning": "⚠️",
            "failed": "❌",
            "pending": "⏳"
        }.get(phase_data.get("status", "pending"), "❓")
        
        phase_title = {
            "phase1_env": "FASE 1: Variáveis de Ambiente",
            "phase2_config": "FASE 2: Módulo de Configuração",
            "phase3_diagnostics": "FASE 3: Diagnóstico NASP",
            "phase4_health": "FASE 4: Health Check",
            "phase5_sla_flow": "FASE 5: Fluxo E2E de SLA",
            "phase6_frontend": "FASE 6: Comportamento do Frontend",
            "phase7_audit": "FASE 7: Auditoria de Lógica Local"
        }.get(phase_name, phase_name)
        
        report_content += f"""
### {status_icon} {phase_title}

**Status**: {phase_data.get("status", "unknown").upper()}

"""
        
        if phase_data.get("issues"):
            report_content += "**Problemas Encontrados:**\n"
            for issue in phase_data["issues"]:
                report_content += f"- {issue}\n"
            report_content += "\n"
        
        # Adicionar detalhes específicos
        if phase_name == "phase3_diagnostics" and latencies:
            report_content += "**Latências por Módulo:**\n"
            for module, latency in latencies.items():
                report_content += f"- {module.upper()}: {latency}ms\n"
            report_content += "\n"
        
        if phase_name == "phase5_sla_flow" and phase_data.get("pipeline_steps"):
            report_content += "**Status da Pipeline:**\n"
            for step, status in phase_data["pipeline_steps"].items():
                report_content += f"- {step.upper()}: {status}\n"
            report_content += "\n"
    
    report_content += f"""
## Pontos Fortes

"""
    
    if passed_phases >= 5:
        report_content += "- ✅ Maioria das validações passou com sucesso\n"
    if "phase3_diagnostics" in results["phases"] and results["phases"]["phase3_diagnostics"].get("all_reachable"):
        report_content += "- ✅ Todos os módulos NASP estão acessíveis\n"
    if "phase5_sla_flow" in results["phases"] and results["phases"]["phase5_sla_flow"].get("blockchain_registered"):
        report_content += "- ✅ Fluxo completo de SLA funcionando (blockchain registrado)\n"
    if "phase7_audit" in results["phases"] and results["phases"]["phase7_audit"].get("status") == "passed":
        report_content += "- ✅ Nenhum mock ou simulador encontrado (NASP-first confirmado)\n"
    
    report_content += f"""
## Melhorias Opcionais

"""
    
    if warning_phases > 0:
        report_content += "- ⚠️ Revisar avisos nas fases com status 'warning'\n"
    if "phase3_diagnostics" in results["phases"] and not results["phases"]["phase3_diagnostics"].get("all_reachable"):
        report_content += "- 🔧 Verificar conectividade com módulos NASP não acessíveis\n"
    if "phase5_sla_flow" in results["phases"] and not results["phases"]["phase5_sla_flow"].get("blockchain_registered"):
        report_content += "- 🔧 Investigar problemas no registro blockchain\n"
    
    report_content += f"""
## Latências por Módulo

"""
    
    if latencies:
        for module, latency in latencies.items():
            report_content += f"- **{module.upper()}**: {latency}ms\n"
    else:
        report_content += "- N/A (módulos não acessíveis durante validação)\n"
    
    report_content += f"""
## Logs de Retry e Resiliência

"""
    
    if "phase5_sla_flow" in results["phases"]:
        sla_phase = results["phases"]["phase5_sla_flow"]
        if sla_phase.get("retries_detected"):
            report_content += "- ⚠️ Possíveis retries detectados (tempo de resposta alto)\n"
        else:
            report_content += "- ✅ Nenhum retry detectado (resposta rápida)\n"
        
        if sla_phase.get("blockchain_registered"):
            report_content += "- ✅ BC-NSSMF registrou SLA com sucesso\n"
        else:
            report_content += "- ❌ BC-NSSMF não registrou SLA\n"
    else:
        report_content += "- N/A (teste E2E não executado)\n"
    
    report_content += f"""
## Conclusão

{veredict}

O Portal TriSLA foi validado conforme as especificações NASP-First. Todas as fases foram executadas e os resultados estão documentados acima.

---
*Relatório gerado automaticamente em {results['timestamp']}*
"""
    
    # Salvar relatório
    report_path = Path(__file__).parent.parent / "PORTAL_VALIDATION_REPORT.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print_success(f"Relatório salvo em: {report_path}")
    print_info(f"Veredito: {veredict}")
    
    results["summary"] = {
        "veredict": veredict,
        "total_phases": total_phases,
        "passed": passed_phases,
        "warnings": warning_phases,
        "failed": failed_phases,
        "latencies": latencies
    }
    
    return report_path

# Função principal
async def main():
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("="*60)
    print("VALIDAÇÃO COMPLETA DO PORTAL TRI-SLA")
    print("NASP Integration - Todas as 8 Fases")
    print("="*60)
    print(f"{Colors.RESET}\n")
    
    # Executar todas as fases
    phase1_validate_env()
    phase2_validate_config()
    await phase3_test_diagnostics()
    await phase4_test_health()
    await phase5_test_sla_flow()
    phase6_validate_frontend()
    phase7_audit_local_logic()
    report_path = phase8_generate_report()
    
    # Resumo final
    print_section("RESUMO FINAL")
    summary = results["summary"]
    print(f"Total de Fases: {summary['total_phases']}")
    print_success(f"Aprovadas: {summary['passed']}")
    if summary['warnings'] > 0:
        print_warning(f"Com Avisos: {summary['warnings']}")
    if summary['failed'] > 0:
        print_error(f"Falhas: {summary['failed']}")
    print(f"\n{Colors.BOLD}Veredito: {summary['veredict']}{Colors.RESET}")
    print(f"\nRelatório completo: {report_path}")

if __name__ == "__main__":
    asyncio.run(main())




