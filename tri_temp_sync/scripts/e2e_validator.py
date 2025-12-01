#!/usr/bin/env python3
"""
TriSLA - END-TO-END VALIDATION ORCHESTRATOR

Script que consolida a validação fim-a-fim do TriSLA, executando testes
e gerando relatórios consolidados de validação.

Saídas:
- docs/VALIDACAO_FINAL_TRI-SLA.md
- docs/METRICAS_VALIDACAO_FINAL.json
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
READY_REPORT_JSON = DOCS_DIR / "READY_STATUS_TRI-SLA_v1.json"


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="TriSLA End-to-End Validation Orchestrator"
    )
    parser.add_argument(
        "--mode",
        choices=["local", "nasp"],
        default="local",
        help="Modo de validação: local ou nasp (default: local)",
    )
    parser.add_argument(
        "--output-md",
        type=str,
        default=str(DOCS_DIR / "VALIDACAO_FINAL_TRI-SLA.md"),
        help="Caminho do relatório Markdown (default: docs/VALIDACAO_FINAL_TRI-SLA.md)",
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default=str(DOCS_DIR / "METRICAS_VALIDACAO_FINAL.json"),
        help="Caminho do JSON de métricas (default: docs/METRICAS_VALIDACAO_FINAL.json)",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Apenas consolidar resultados existentes, sem reexecutar testes",
    )
    return parser.parse_args()


def run_pytest(test_path: str) -> Dict:
    """Executa pytest em um caminho específico e retorna resultados"""
    try:
        result = subprocess.run(
            ["pytest", test_path, "-q", "--tb=no"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        
        # Tentar extrair contagem de testes do stdout
        passed = 0
        failed = 0
        for line in result.stdout.splitlines():
            if "passed" in line.lower():
                # Tentar extrair número (ex: "5 passed")
                parts = line.split()
                for part in parts:
                    if part.isdigit():
                        passed = int(part)
                        break
            if "failed" in line.lower():
                parts = line.split()
                for part in parts:
                    if part.isdigit():
                        failed = int(part)
                        break
        
        return {
            "executado": True,
            "return_code": result.returncode,
            "passed": passed,
            "failed": failed,
            "output": result.stdout[:500],  # Limitar tamanho
        }
    except subprocess.TimeoutExpired:
        return {
            "executado": True,
            "return_code": -1,
            "passed": 0,
            "failed": 0,
            "output": "Timeout após 300s",
        }
    except Exception as e:
        return {
            "executado": False,
            "return_code": -1,
            "passed": 0,
            "failed": 0,
            "output": f"Erro ao executar: {type(e).__name__}: {e}",
        }


def load_ready_report() -> Optional[Dict]:
    """Carrega o READY REPORT JSON se existir"""
    if READY_REPORT_JSON.exists():
        try:
            with open(READY_REPORT_JSON, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[TriSLA] ⚠️  Erro ao carregar READY REPORT: {e}")
            return None
    return None


def calculate_global_status(tests: Dict, ready_report: Optional[Dict]) -> str:
    """
    Calcula status global baseado em testes e READY REPORT.
    
    Lógica:
    - HEALTHY: Todos os testes OK (return_code=0) e READY REPORT HEALTHY
    - DEGRADED: Alguns testes falharam, mas maioria OK ou READY DEGRADED
    - ERROR: Testes críticos falharam ou READY ERROR
    """
    # Contar testes executados e bem-sucedidos
    total_executados = 0
    total_passou = 0
    critical_failed = False
    
    for test_name, test_result in tests.items():
        if test_result.get("executado", False):
            total_executados += 1
            if test_result.get("return_code") == 0:
                total_passou += 1
            else:
                # E2E é considerado crítico
                if test_name == "e2e":
                    critical_failed = True
    
    # Verificar READY REPORT
    ready_status = None
    if ready_report:
        ready_status = ready_report.get("overall_status", "UNKNOWN")
    
    # Decidir status global
    if total_executados == 0:
        return "ERROR"  # Nenhum teste foi executado
    
    if critical_failed:
        return "ERROR"
    
    if ready_status == "ERROR":
        return "ERROR"
    
    # Taxa de sucesso
    success_rate = total_passou / total_executados if total_executados > 0 else 0
    
    if success_rate == 1.0 and ready_status == "HEALTHY":
        return "HEALTHY"
    elif success_rate >= 0.7 or ready_status == "DEGRADED":
        return "DEGRADED"
    else:
        return "ERROR"


def execute_tests(summary_only: bool) -> Dict:
    """Executa testes ou retorna resultados vazios se summary_only=True"""
    tests = {
        "unit": {"executado": False, "return_code": -1},
        "integration": {"executado": False, "return_code": -1},
        "e2e": {"executado": False, "return_code": -1},
        "load": {"executado": False, "return_code": -1},
    }
    
    if summary_only:
        print("[TriSLA] Modo --summary-only: não reexecutando testes.")
        return tests
    
    # Executar testes unitários
    test_unit_path = REPO_ROOT / "tests" / "unit"
    if test_unit_path.exists() and list(test_unit_path.glob("*.py")):
        print("[TriSLA] Executando testes unitários...")
        tests["unit"] = run_pytest(str(test_unit_path))
    else:
        print("[TriSLA] ⚠️  Nenhum teste unitário encontrado.")
    
    # Executar testes de integração
    test_integration_path = REPO_ROOT / "tests" / "integration"
    if test_integration_path.exists() and list(test_integration_path.glob("*.py")):
        print("[TriSLA] Executando testes de integração...")
        tests["integration"] = run_pytest(str(test_integration_path))
    else:
        print("[TriSLA] ⚠️  Nenhum teste de integração encontrado.")
    
    # Executar testes E2E
    test_e2e_path = REPO_ROOT / "tests" / "e2e"
    if test_e2e_path.exists() and list(test_e2e_path.glob("*.py")):
        print("[TriSLA] Executando testes E2E...")
        tests["e2e"] = run_pytest(str(test_e2e_path))
    else:
        print("[TriSLA] ⚠️  Nenhum teste E2E encontrado.")
    
    # Executar testes de carga (opcional)
    test_load_path = REPO_ROOT / "tests" / "load"
    if test_load_path.exists() and list(test_load_path.glob("*.py")):
        print("[TriSLA] Executando testes de carga...")
        tests["load"] = run_pytest(str(test_load_path))
    else:
        print("[TriSLA] ⚠️  Nenhum teste de carga encontrado (opcional).")
    
    return tests


def generate_markdown(
    timestamp: str,
    mode: str,
    status_global: str,
    tests: Dict,
    ready_report: Optional[Dict],
) -> str:
    """Gera relatório Markdown"""
    lines = []
    lines.append("# Validação Final TriSLA — Fase H")
    lines.append("")
    lines.append(f"- **Gerado em:** `{timestamp}` (UTC)")
    lines.append(f"- **Modo:** `{mode}`")
    lines.append(f"- **Status global:** **{status_global}**")
    lines.append("")
    
    lines.append("## Resumo dos Testes")
    lines.append("")
    lines.append("| Tipo de teste | Executado | Código de retorno | Passou | Falhou |")
    lines.append("|---------------|-----------|-------------------|--------|--------|")
    
    for test_name, test_result in tests.items():
        executado = "✅ Sim" if test_result.get("executado") else "❌ Não"
        return_code = test_result.get("return_code", -1)
        passed = test_result.get("passed", 0)
        failed = test_result.get("failed", 0)
        
        status_icon = "✅" if return_code == 0 else "❌" if return_code > 0 else "⚠️"
        lines.append(
            f"| {test_name.title()} | {executado} | {status_icon} {return_code} | {passed} | {failed} |"
        )
    
    lines.append("")
    lines.append("## READY REPORT")
    lines.append("")
    
    if ready_report:
        ready_status = ready_report.get("overall_status", "UNKNOWN")
        ready_timestamp = ready_report.get("timestamp", "N/A")
        lines.append(f"- **Status:** **{ready_status}**")
        lines.append(f"- **Timestamp:** `{ready_timestamp}`")
        lines.append(f"- **Arquivo:** `{READY_REPORT_JSON}`")
    else:
        lines.append("- ⚠️ **READY REPORT não encontrado ou não foi gerado ainda.**")
    
    lines.append("")
    lines.append("## Interpretação do Status")
    lines.append("")
    
    if status_global == "HEALTHY":
        lines.append("✅ **HEALTHY:** TriSLA está pronto para:")
        lines.append("- Publicação no GitHub")
        lines.append("- Deploy no NASP")
        lines.append("- Uso como evidência na dissertação")
    elif status_global == "DEGRADED":
        lines.append("⚠️ **DEGRADED:** TriSLA pode ser usado, mas com ressalvas:")
        lines.append("- Revisar módulos degradados antes de publicação")
        lines.append("- Documentar limitações conhecidas")
        lines.append("- Priorizar correções em módulos críticos")
    else:
        lines.append("❌ **ERROR:** TriSLA NÃO está pronto para:")
        lines.append("- Publicação no GitHub")
        lines.append("- Deploy no NASP")
        lines.append("- Uso como evidência na dissertação")
        lines.append("")
        lines.append("**Ações necessárias:**")
        lines.append("- Corrigir problemas críticos")
        lines.append("- Reexecutar validação após correções")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("> Relatório gerado automaticamente pelo `scripts/e2e_validator.py` (TriSLA DevOps - FASE H).")
    
    return "\n".join(lines)


def main():
    """Função principal"""
    args = parse_arguments()
    
    # Garantir que diretório docs existe
    DOCS_DIR.mkdir(exist_ok=True)
    
    timestamp = datetime.now(timezone.utc).isoformat()
    
    print(f"[TriSLA] FASE H — Iniciando validação fim-a-fim (modo: {args.mode})...")
    
    # Executar testes
    tests = execute_tests(args.summary_only)
    
    # Carregar READY REPORT
    ready_report = load_ready_report()
    
    # Calcular status global
    status_global = calculate_global_status(tests, ready_report)
    
    # Preparar dados JSON
    json_data = {
        "timestamp": timestamp,
        "mode": args.mode,
        "status_global": status_global,
        "tests": tests,
        "ready_report": {
            "arquivo_json": str(READY_REPORT_JSON),
            "status": ready_report.get("overall_status", "NOT_FOUND")
            if ready_report
            else "NOT_FOUND",
        },
    }
    
    # Gerar Markdown
    md_content = generate_markdown(timestamp, args.mode, status_global, tests, ready_report)
    
    # Salvar arquivos
    output_md_path = Path(args.output_md)
    output_json_path = Path(args.output_json)
    
    output_md_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    # Mensagem final
    print(f"[TriSLA] FASE H — Validação concluída com status: {status_global}")
    print(f"[TriSLA] Relatório Markdown: {output_md_path}")
    print(f"[TriSLA] Métricas JSON: {output_json_path}")
    
    # Retornar código de saída apropriado
    if status_global == "HEALTHY":
        sys.exit(0)
    elif status_global == "DEGRADED":
        sys.exit(1)  # Aviso, mas não crítico
    else:
        sys.exit(2)  # Erro crítico


if __name__ == "__main__":
    main()

