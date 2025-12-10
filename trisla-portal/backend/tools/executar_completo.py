#!/usr/bin/env python3
"""
Script de Execução Completa - Stress Test e Coleta de Métricas
Capítulo 6 - Considerações Preliminares e Resultados

Executa todas as fases conforme especificação:
- FASE 0: Validação do Ambiente
- FASE 1: Battery Test (20, 50, 100, 135 requisições)
- FASE 2: Orquestrador Completo (SLOs, KPIs, Gráficos, Tabelas)
- FASE 3-7: Validação e Finalização
"""
import asyncio
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

# Configurar encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

backend_dir = Path(__file__).parent.parent
log_file = backend_dir / "execucao_completa.log"
results_file = backend_dir / "execucao_completa_results.json"

def log(msg, also_print=True):
    """Log para arquivo e console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {msg}"
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    except:
        pass
    if also_print:
        print(log_msg, flush=True)

def log_section(title):
    """Log de seção"""
    log("")
    log("="*70)
    log(title)
    log("="*70)
    log("")

# Resultados globais
execution_results = {
    "timestamp": datetime.now().isoformat(),
    "fase0": {},
    "fase1": {},
    "fase2": {},
    "fase3": {},
    "fase4": {},
    "fase5": {},
    "fase6": {},
    "fase7": {}
}

# Limpar log anterior
if log_file.exists():
    log_file.unlink()

log_section("INICIANDO EXECUÇÃO COMPLETA - STRESS TEST TRI-SLA")
log("Capítulo 6 - Considerações Preliminares e Resultados")
log("")

# ============================================================================
# FASE 0 - VALIDAÇÃO DO AMBIENTE
# ============================================================================
log_section("FASE 0 - VALIDAÇÃO DO AMBIENTE")

try:
    # Executar script de validação
    result = subprocess.run(
        [sys.executable, str(backend_dir / "tools" / "validate_environment.py")],
        cwd=str(backend_dir),
        capture_output=True,
        text=True,
        timeout=30
    )
    
    log(f"Validação executada (exit code: {result.returncode})")
    if result.stdout:
        log(f"STDOUT: {result.stdout[:500]}")
    if result.stderr:
        log(f"STDERR: {result.stderr[:500]}")
    
    execution_results["fase0"] = {
        "exit_code": result.returncode,
        "validated": result.returncode == 0 or result.returncode == 0  # Mesmo se parcial
    }
    
    if result.returncode != 0:
        log("⚠️  Validação falhou, mas continuando execução...")
        log("   (Alguns módulos podem estar offline)")
    
except Exception as e:
    log(f"❌ Erro na validação: {e}")
    execution_results["fase0"] = {"error": str(e)}
    log("⚠️  Continuando execução mesmo com erro de validação...")

log("")

# ============================================================================
# FASE 1 - BATTERY TEST
# ============================================================================
log_section("FASE 1 - EXECUTAR BATTERY TEST")

test_configs = [
    {"num": 20, "name": "20 requisições"},
    {"num": 50, "name": "50 requisições"},
    {"num": 100, "name": "100 requisições"},
    {"num": 135, "name": "135 requisições (cenário real: 20 URLLC + 15 eMBB + 100 mMTC)"}
]

fase1_results = {}

for config in test_configs:
    num = config["num"]
    name = config["name"]
    
    log(f"Executando: {name}...")
    
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(backend_dir / "tools" / "stress_sla_submit.py"),
                str(num),
                "http://localhost:8001"
            ],
            cwd=str(backend_dir),
            capture_output=True,
            text=True,
            timeout=600  # 10 minutos
        )
        
        log(f"  Exit code: {result.returncode}")
        
        # Verificar se relatório foi gerado
        report_path = backend_dir / "stress_test_report.json"
        if report_path.exists():
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    test_data = json.load(f)
                    fase1_results[f"{num}_requests"] = {
                        "success": True,
                        "summary": test_data.get("summary", {})
                    }
                    success_rate = test_data.get("summary", {}).get("success_rate", 0)
                    avg_latency = test_data.get("summary", {}).get("latency", {}).get("average_ms", 0)
                    log(f"  ✅ Concluído - Taxa de sucesso: {success_rate:.2f}%, Latência média: {avg_latency:.2f}ms")
            except Exception as e:
                log(f"  ⚠️  Relatório gerado mas erro ao ler: {e}")
                fase1_results[f"{num}_requests"] = {"success": False, "error": str(e)}
        else:
            log(f"  ⚠️  Relatório não encontrado após execução")
            fase1_results[f"{num}_requests"] = {"success": False, "error": "Relatório não gerado"}
        
        # Aguardar entre testes
        if config != test_configs[-1]:
            log("  Aguardando 5 segundos...")
            import time
            time.sleep(5)
    
    except subprocess.TimeoutExpired:
        log(f"  ❌ Timeout após 10 minutos")
        fase1_results[f"{num}_requests"] = {"success": False, "error": "Timeout"}
    except Exception as e:
        log(f"  ❌ Erro: {e}")
        fase1_results[f"{num}_requests"] = {"success": False, "error": str(e)}

execution_results["fase1"] = fase1_results
log("")

# ============================================================================
# FASE 2 - ORQUESTRADOR COMPLETO
# ============================================================================
log_section("FASE 2 - ORQUESTRADOR COMPLETO (SLOs, KPIs, Gráficos, Tabelas)")

try:
    log("Executando stress_test_orchestrator.py...")
    result = subprocess.run(
        [sys.executable, str(backend_dir / "tools" / "stress_test_orchestrator.py")],
        cwd=str(backend_dir),
        capture_output=True,
        text=True,
        timeout=1800  # 30 minutos
    )
    
    log(f"Orquestrador executado (exit code: {result.returncode})")
    
    if result.stdout:
        # Salvar output em arquivo separado
        output_file = backend_dir / "orchestrator_output.log"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result.stdout)
        log(f"Output completo salvo em: {output_file}")
    
    execution_results["fase2"] = {
        "exit_code": result.returncode,
        "success": result.returncode == 0
    }
    
except subprocess.TimeoutExpired:
    log("❌ Timeout após 30 minutos")
    execution_results["fase2"] = {"success": False, "error": "Timeout"}
except Exception as e:
    log(f"❌ Erro: {e}")
    execution_results["fase2"] = {"success": False, "error": str(e)}

log("")

# ============================================================================
# FASE 3 - VALIDAR SLOs E KPIs
# ============================================================================
log_section("FASE 3 - VALIDAR SLOs E KPIs")

# Verificar se relatório foi gerado
report_path = backend_dir / "STRESS_TEST_REPORT.md"
json_report_path = backend_dir / "stress_test_report.json"

slos_validated = False
kpis_validated = False

if json_report_path.exists():
    try:
        with open(json_report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        # Verificar SLOs
        phase2_data = report_data.get("phase2", {})
        if phase2_data:
            slo_count = len(phase2_data)
            log(f"✅ {slo_count} SLOs encontrados no relatório")
            slos_validated = True
        else:
            log("⚠️  Nenhum SLO encontrado no relatório")
        
        # Verificar KPIs
        phase3_data = report_data.get("phase3", {})
        if phase3_data:
            kpi_count = len(phase3_data)
            log(f"✅ {kpi_count} KPIs encontrados no relatório")
            kpis_validated = True
        else:
            log("⚠️  Nenhum KPI encontrado no relatório")
    
    except Exception as e:
        log(f"❌ Erro ao validar relatório JSON: {e}")
else:
    log("⚠️  Relatório JSON não encontrado")

execution_results["fase3"] = {
    "slos_validated": slos_validated,
    "kpis_validated": kpis_validated,
    "report_exists": report_path.exists(),
    "json_report_exists": json_report_path.exists()
}

log("")

# ============================================================================
# FASE 4 - VALIDAR GRÁFICOS
# ============================================================================
log_section("FASE 4 - VALIDAR GRÁFICOS")

figures_dir = backend_dir / "figures"
expected_graphs = [
    "latencia_e2e_por_volume.png",
    "taxa_sucesso.png",
    "distribuicao_latencia.png",
    "falhas_por_modulo.png",
    "slos_radar.png"
]

graphs_found = []
if figures_dir.exists():
    for graph in expected_graphs:
        graph_path = figures_dir / graph
        if graph_path.exists():
            graphs_found.append(graph)
            log(f"✅ {graph}")
        else:
            log(f"⚠️  {graph} não encontrado")
else:
    log("⚠️  Diretório figures/ não existe")

execution_results["fase4"] = {
    "graphs_found": graphs_found,
    "total_expected": len(expected_graphs),
    "total_found": len(graphs_found)
}

log("")

# ============================================================================
# FASE 5 - VALIDAR TEXTO ACADÊMICO
# ============================================================================
log_section("FASE 5 - VALIDAR TEXTO ACADÊMICO")

if report_path.exists():
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            report_content = f.read()
        
        sections = {
            "6.1": "6.1" in report_content or "Integração entre fundamentos" in report_content,
            "6.2": "6.2" in report_content or "Análise crítica" in report_content,
            "6.3": "6.3" in report_content or "SLOrion" in report_content,
            "6.4": "6.4" in report_content or "Perspectivas" in report_content
        }
        
        for section, found in sections.items():
            if found:
                log(f"✅ Seção {section} encontrada")
            else:
                log(f"⚠️  Seção {section} não encontrada")
        
        execution_results["fase5"] = {
            "report_exists": True,
            "sections": sections,
            "all_sections": all(sections.values())
        }
    except Exception as e:
        log(f"❌ Erro ao validar relatório: {e}")
        execution_results["fase5"] = {"error": str(e)}
else:
    log("⚠️  Relatório Markdown não encontrado")
    execution_results["fase5"] = {"report_exists": False}

log("")

# ============================================================================
# FASE 6 - CHECKLIST FINAL
# ============================================================================
log_section("FASE 6 - CHECKLIST FINAL")

checklist = {
    "STRESS_TEST_REPORT.md": report_path.exists(),
    "stress_test_report.json": json_report_path.exists(),
    "graficos_png": len(graphs_found) > 0,
    "tabelas_markdown": report_path.exists() and "Tabela" in (open(report_path, 'r', encoding='utf-8').read() if report_path.exists() else ""),
    "texto_academico": execution_results.get("fase5", {}).get("all_sections", False),
    "kpis": kpis_validated,
    "slos": slos_validated
}

for item, status in checklist.items():
    if status:
        log(f"✅ {item}")
    else:
        log(f"❌ {item}")

execution_results["fase6"] = checklist
log("")

# ============================================================================
# FASE 7 - FINALIZAÇÃO
# ============================================================================
log_section("FASE 7 - FINALIZAÇÃO")

# Salvar resultados
with open(results_file, 'w', encoding='utf-8') as f:
    json.dump(execution_results, f, indent=2, ensure_ascii=False)

log("Resultados salvos em: " + str(results_file))
log("")

# Resumo final
log("="*70)
log("RESUMO FINAL")
log("="*70)
log("")

all_passed = all(checklist.values())
if all_passed:
    log("✅ TODAS AS FASES CONCLUÍDAS COM SUCESSO!")
else:
    log("⚠️  ALGUMAS FASES NÃO FORAM CONCLUÍDAS COMPLETAMENTE")
    log("")
    log("Itens faltando:")
    for item, status in checklist.items():
        if not status:
            log(f"  - {item}")

log("")
log("="*70)
log("CONCLUSÃO EXECUTIVA PARA CAPÍTULO 6")
log("="*70)
log("")

# Gerar conclusão executiva
if all_passed:
    log("O processo completo de stress test e coleta de métricas foi executado com sucesso.")
    log("Todos os arquivos necessários para o Capítulo 6 foram gerados:")
    log("")
    log("1. Relatório completo (STRESS_TEST_REPORT.md)")
    log("2. Dados estruturados (stress_test_report.json)")
    log("3. Gráficos acadêmicos (figures/*.png)")
    log("4. Tabelas em Markdown (prontas para LaTeX)")
    log("5. Análise acadêmica completa (seções 6.1-6.4)")
    log("6. SLOs e KPIs calculados")
    log("")
    log("Os arquivos estão prontos para envio ao Overleaf e incorporação ao Capítulo 6.")
else:
    log("O processo foi executado, mas alguns itens não foram gerados completamente.")
    log("Verifique os logs acima para identificar o que precisa ser corrigido.")

log("")
log("="*70)
log(f"Execução concluída em: {datetime.now().isoformat()}")
log("="*70)



