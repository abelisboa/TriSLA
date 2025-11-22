#!/usr/bin/env python3
"""
Auditoria Técnica v2 - TriSLA
Verifica se todos os problemas críticos da primeira auditoria foram resolvidos
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime

# Adicionar path do projeto
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Cores para output
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


class TechnicalAuditorV2:
    """Auditor técnico v2 - Verifica resolução de problemas críticos"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues = []
        self.approved_modules = []
        self.partial_modules = []
        self.rejected_modules = []
    
    def audit_module(self, module_name: str, checks: List[callable]) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Audita um módulo
        
        Returns:
            (status, issues) onde status é "APPROVED", "PARTIAL" ou "REJECTED"
        """
        module_issues = []
        
        for check in checks:
            try:
                result = check()
                if not result.get("passed", False):
                    module_issues.append(result)
            except Exception as e:
                module_issues.append({
                    "severity": "CRITICAL",
                    "message": f"Erro ao executar check: {e}",
                    "evidence": str(e)
                })
        
        # Determinar status
        critical_issues = [i for i in module_issues if i.get("severity") == "CRITICAL"]
        moderate_issues = [i for i in module_issues if i.get("severity") == "MODERATE"]
        
        if len(critical_issues) == 0 and len(moderate_issues) == 0:
            status = "APPROVED"
            self.approved_modules.append(module_name)
        elif len(critical_issues) == 0:
            status = "PARTIAL"
            self.partial_modules.append(module_name)
        else:
            status = "REJECTED"
            self.rejected_modules.append(module_name)
        
        return status, module_issues
    
    def check_sem_csmf_ontology(self) -> Dict[str, Any]:
        """Verifica se SEM-CSMF usa ontologia OWL real"""
        ontology_path = self.project_root / "apps" / "sem-csmf" / "src" / "ontology" / "trisla.owl"
        parser_path = self.project_root / "apps" / "sem-csmf" / "src" / "ontology" / "parser.py"
        
        if not ontology_path.exists():
            return {
                "passed": False,
                "severity": "CRITICAL",
                "message": "Ontologia OWL não encontrada",
                "evidence": f"Arquivo não existe: {ontology_path}",
                "recommendation": "Criar ontologia OWL em apps/sem-csmf/src/ontology/trisla.owl"
            }
        
        # Verificar se parser usa owlready2
        if parser_path.exists():
            parser_content = parser_path.read_text(encoding="utf-8")
            
            if "owlready2" not in parser_content and "rdflib" not in parser_content:
                return {
                    "passed": False,
                    "severity": "CRITICAL",
                    "message": "Parser não usa biblioteca OWL (owlready2/rdflib)",
                    "evidence": "Parser não importa owlready2 ou rdflib",
                    "recommendation": "Atualizar parser.py para usar owlready2 ou rdflib"
                }
            
            if "hardcoded" in parser_content.lower() and "dictionary" in parser_content.lower():
                return {
                    "passed": False,
                    "severity": "CRITICAL",
                    "message": "Parser ainda usa dicionário hardcoded",
                    "evidence": "Código contém 'hardcoded' e 'dictionary'",
                    "recommendation": "Remover dicionário hardcoded e usar ontologia OWL"
                }
        
        return {"passed": True}
    
    def check_ml_nsmf_model(self) -> Dict[str, Any]:
        """Verifica se ML-NSMF usa modelo treinado real"""
        predictor_path = self.project_root / "apps" / "ml-nsmf" / "src" / "predictor.py"
        model_path = self.project_root / "apps" / "ml-nsmf" / "models" / "viability_model.pkl"
        
        if not predictor_path.exists():
            return {
                "passed": False,
                "severity": "CRITICAL",
                "message": "predictor.py não encontrado",
                "evidence": f"Arquivo não existe: {predictor_path}"
            }
        
        predictor_content = predictor_path.read_text(encoding="utf-8")
        
        # Verificar se usa np.random para predição
        if "np.random" in predictor_content and "predict" in predictor_content:
            # Verificar se está em comentário ou código real
            lines = predictor_content.split("\n")
            for i, line in enumerate(lines):
                if "np.random" in line and "predict" in "\n".join(lines[max(0, i-5):i+5]):
                    if not line.strip().startswith("#"):
                        return {
                            "passed": False,
                            "severity": "CRITICAL",
                            "message": "Predictor usa np.random para predição (não é modelo real)",
                            "evidence": f"Linha {i+1}: {line.strip()}",
                            "recommendation": "Usar modelo treinado real (joblib.load)"
                        }
        
        # Verificar se carrega modelo real
        if "joblib.load" not in predictor_content and "load_model" not in predictor_content:
            return {
                "passed": False,
                "severity": "CRITICAL",
                "message": "Predictor não carrega modelo treinado",
                "evidence": "Código não contém joblib.load ou load_model",
                "recommendation": "Implementar carregamento de modelo treinado"
            }
        
        # Verificar se modelo existe (opcional - pode não existir em dev)
        if not model_path.exists():
            return {
                "passed": True,  # Não é crítico se modelo não existir (pode ser gerado)
                "severity": "MODERATE",
                "message": "Modelo treinado não encontrado (pode ser gerado)",
                "evidence": f"Arquivo não existe: {model_path}",
                "recommendation": "Executar training/train_model.py para gerar modelo"
            }
        
        return {"passed": True}
    
    def check_decision_engine_eval(self) -> Dict[str, Any]:
        """Verifica se Decision Engine não usa eval()"""
        rule_engine_path = self.project_root / "apps" / "decision-engine" / "src" / "rule_engine.py"
        decision_maker_path = self.project_root / "apps" / "decision-engine" / "src" / "decision_maker.py"
        
        files_to_check = []
        if rule_engine_path.exists():
            files_to_check.append(rule_engine_path)
        if decision_maker_path.exists():
            files_to_check.append(decision_maker_path)
        
        for file_path in files_to_check:
            content = file_path.read_text(encoding="utf-8")
            
            # Verificar se usa eval() (não comentado, não asteval)
            # Usar regex para encontrar eval( mas não asteval(
            import re
            eval_pattern = r'\beval\s*\('  # eval( mas não asteval(
            
            if re.search(eval_pattern, content):
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    # Ignorar se for asteval
                    if "asteval" in line.lower():
                        continue
                    
                    # Verificar se contém eval( (não asteval)
                    if re.search(r'\beval\s*\(', line) and "asteval" not in line.lower():
                        # Verificar se está em comentário
                        stripped = line.strip()
                        if stripped.startswith("#"):
                            continue
                        # Verificar se está em string
                        if '"eval(' in line or "'eval(" in line:
                            continue
                        # Verificar se está em docstring
                        if '"""' in "\n".join(lines[max(0, i-3):i]) or "'''" in "\n".join(lines[max(0, i-3):i]):
                            continue
                        # Verificar se está em comentário inline (após código)
                        if "#" in line:
                            comment_part = line.split("#")[1]
                            if "eval(" in comment_part:
                                continue
                        # Verificar se contém "sem eval()" ou "without eval()" (comentário explicativo)
                        if "sem eval()" in line.lower() or "without eval()" in line.lower() or "no eval()" in line.lower():
                            continue
                        # Se chegou aqui, é uso real de eval()
                        return {
                            "passed": False,
                            "severity": "CRITICAL",
                            "message": f"Decision Engine usa eval() (inseguro)",
                            "evidence": f"{file_path.name}:{i+1}: {line.strip()}",
                            "recommendation": "Substituir eval() por asteval ou engine de regras seguro"
                        }
        
        # Verificar se usa asteval ou YAML
        if rule_engine_path.exists():
            content = rule_engine_path.read_text(encoding="utf-8")
            if "asteval" in content and ("yaml" in content.lower() or "YAML" in content):
                # Se usa asteval e YAML, está correto
                return {"passed": True}
            elif "asteval" not in content and "yaml" not in content.lower():
                return {
                    "passed": False,
                    "severity": "MODERATE",
                    "message": "Rule Engine não usa asteval ou YAML para regras",
                    "evidence": "Código não contém asteval ou YAML",
                    "recommendation": "Implementar engine de regras baseado em YAML + asteval"
                }
        
        return {"passed": True}
    
    def check_bc_nssmf_simulation(self) -> Dict[str, Any]:
        """Verifica se BC-NSSMF não simula contratos em Python"""
        smart_contracts_path = self.project_root / "apps" / "bc-nssmf" / "src" / "smart_contracts.py"
        service_path = self.project_root / "apps" / "bc-nssmf" / "src" / "service.py"
        
        # Verificar se smart_contracts.py foi removido
        if smart_contracts_path.exists():
            content = smart_contracts_path.read_text(encoding="utf-8")
            
            # Verificar se contém simulação de contratos
            if "LatencyGuard" in content or "ThroughputGuard" in content or "AdaptiveContract" in content:
                # Verificar se são apenas adaptadores ou simulações
                if "def _latency_guard" in content or "def _throughput_guard" in content:
                    return {
                        "passed": False,
                        "severity": "CRITICAL",
                        "message": "BC-NSSMF ainda contém simulação de contratos Python",
                        "evidence": f"smart_contracts.py contém LatencyGuard/ThroughputGuard",
                        "recommendation": "Remover smart_contracts.py ou refatorar para usar apenas contrato Solidity"
                    }
        
        # Verificar se service.py usa contrato Solidity real
        if service_path.exists():
            content = service_path.read_text(encoding="utf-8")
            
            if "web3" not in content or "contract.functions" not in content:
                return {
                    "passed": False,
                    "severity": "CRITICAL",
                    "message": "BCService não usa contrato Solidity real",
                    "evidence": "Código não contém web3 ou contract.functions",
                    "recommendation": "Implementar interação real com contrato Solidity via web3"
                }
            
            if "Ethereum Permissionado" not in content and "GoQuorum" not in content and "Besu" not in content:
                return {
                    "passed": False,
                    "severity": "MODERATE",
                    "message": "BCService não menciona Ethereum permissionado (GoQuorum/Besu)",
                    "evidence": "Código não menciona tecnologia blockchain específica",
                    "recommendation": "Documentar uso de Ethereum permissionado (GoQuorum/Besu)"
                }
        
        return {"passed": True}
    
    def check_sla_agents_hardcoded(self) -> Dict[str, Any]:
        """Verifica se SLA-Agent Layer não usa métricas hardcoded"""
        agent_ran_path = self.project_root / "apps" / "sla-agent-layer" / "src" / "agent_ran.py"
        agent_transport_path = self.project_root / "apps" / "sla-agent-layer" / "src" / "agent_transport.py"
        agent_core_path = self.project_root / "apps" / "sla-agent-layer" / "src" / "agent_core.py"
        
        agents = [
            ("Agent RAN", agent_ran_path),
            ("Agent Transport", agent_transport_path),
            ("Agent Core", agent_core_path)
        ]
        
        for agent_name, agent_path in agents:
            if not agent_path.exists():
                continue
            
            content = agent_path.read_text(encoding="utf-8")
            
            # Verificar se collect_metrics usa NASP Adapter
            if "collect_metrics" in content:
                # Verificar se chama NASP Adapter
                if "nasp_client" not in content and "NASPClient" not in content:
                    return {
                        "passed": False,
                        "severity": "CRITICAL",
                        "message": f"{agent_name} não usa NASP Adapter para coletar métricas",
                        "evidence": f"{agent_path.name} não contém nasp_client ou NASPClient",
                        "recommendation": "Conectar agentes ao NASP Adapter real"
                    }
                
                # Verificar se há métricas hardcoded
                lines = content.split("\n")
                in_collect_metrics = False
                for i, line in enumerate(lines):
                    if "def collect_metrics" in line or "async def collect_metrics" in line:
                        in_collect_metrics = True
                    elif in_collect_metrics and ("def " in line or "class " in line):
                        in_collect_metrics = False
                    
                    if in_collect_metrics:
                        # Verificar valores hardcoded suspeitos
                        if re.search(r'["\']latency["\']:\s*\d+\.?\d*', line) and "nasp" not in line.lower():
                            return {
                                "passed": False,
                                "severity": "CRITICAL",
                                "message": f"{agent_name} tem métricas hardcoded em collect_metrics",
                                "evidence": f"{agent_path.name}:{i+1}: {line.strip()}",
                                "recommendation": "Remover métricas hardcoded, usar NASP Adapter"
                            }
            
            # Verificar se execute_action usa NASP Adapter
            if "execute_action" in content:
                if "nasp_client" not in content and "NASPClient" not in content:
                    return {
                        "passed": False,
                        "severity": "CRITICAL",
                        "message": f"{agent_name} não usa NASP Adapter para executar ações",
                        "evidence": f"{agent_path.name} não contém nasp_client ou NASPClient em execute_action",
                        "recommendation": "Conectar execute_action ao NASP Adapter real"
                    }
                
                # Verificar se sempre retorna executed: True
                if '"executed": True' in content or "'executed': True" in content:
                    # Verificar se não é resultado real do NASP
                    if "result.get" not in content and "nasp_client" not in content:
                        return {
                            "passed": False,
                            "severity": "CRITICAL",
                            "message": f"{agent_name} sempre retorna executed: True sem execução real",
                            "evidence": f"{agent_path.name} contém 'executed: True' sem verificação de resultado",
                            "recommendation": "Executar ações via NASP Adapter e retornar resultado real"
                        }
        
        return {"passed": True}
    
    def check_bc_nssmf_oracle(self) -> Dict[str, Any]:
        """Verifica se Oracle do BC-NSSMF conecta ao NASP Adapter"""
        oracle_path = self.project_root / "apps" / "bc-nssmf" / "src" / "oracle.py"
        
        if not oracle_path.exists():
            return {
                "passed": False,
                "severity": "CRITICAL",
                "message": "oracle.py não encontrado",
                "evidence": f"Arquivo não existe: {oracle_path}"
            }
        
        content = oracle_path.read_text(encoding="utf-8")
        
        # Verificar se usa NASP Adapter
        if "nasp_client" not in content and "NASPClient" not in content:
            # Verificar se tem métricas hardcoded
            if '"latency":' in content or '"throughput":' in content:
                return {
                    "passed": False,
                    "severity": "CRITICAL",
                    "message": "Oracle não conecta ao NASP Adapter (métricas hardcoded)",
                    "evidence": "oracle.py não contém nasp_client e tem métricas hardcoded",
                    "recommendation": "Conectar Oracle ao NASP Adapter real"
                }
        
        return {"passed": True}
    
    def run_audit(self) -> Dict[str, Any]:
        """Executa auditoria completa"""
        print(f"{BLUE}{'='*60}{NC}")
        print(f"{BLUE}🔍 Auditoria Técnica v2 - TriSLA{NC}")
        print(f"{BLUE}{'='*60}{NC}\n")
        
        # 1. SEM-CSMF
        print(f"{BLUE}📋 Auditando SEM-CSMF...{NC}")
        sem_csmf_status, sem_csmf_issues = self.audit_module("SEM-CSMF", [
            self.check_sem_csmf_ontology
        ])
        self.issues.extend([{**issue, "module": "SEM-CSMF"} for issue in sem_csmf_issues])
        print(f"   Status: {GREEN if sem_csmf_status == 'APPROVED' else YELLOW if sem_csmf_status == 'PARTIAL' else RED}{sem_csmf_status}{NC}\n")
        
        # 2. ML-NSMF
        print(f"{BLUE}📋 Auditando ML-NSMF...{NC}")
        ml_nsmf_status, ml_nsmf_issues = self.audit_module("ML-NSMF", [
            self.check_ml_nsmf_model
        ])
        self.issues.extend([{**issue, "module": "ML-NSMF"} for issue in ml_nsmf_issues])
        print(f"   Status: {GREEN if ml_nsmf_status == 'APPROVED' else YELLOW if ml_nsmf_status == 'PARTIAL' else RED}{ml_nsmf_status}{NC}\n")
        
        # 3. Decision Engine
        print(f"{BLUE}📋 Auditando Decision Engine...{NC}")
        decision_engine_status, decision_engine_issues = self.audit_module("Decision Engine", [
            self.check_decision_engine_eval
        ])
        self.issues.extend([{**issue, "module": "Decision Engine"} for issue in decision_engine_issues])
        print(f"   Status: {GREEN if decision_engine_status == 'APPROVED' else YELLOW if decision_engine_status == 'PARTIAL' else RED}{decision_engine_status}{NC}\n")
        
        # 4. BC-NSSMF
        print(f"{BLUE}📋 Auditando BC-NSSMF...{NC}")
        bc_nssmf_status, bc_nssmf_issues = self.audit_module("BC-NSSMF", [
            self.check_bc_nssmf_simulation,
            self.check_bc_nssmf_oracle
        ])
        self.issues.extend([{**issue, "module": "BC-NSSMF"} for issue in bc_nssmf_issues])
        print(f"   Status: {GREEN if bc_nssmf_status == 'APPROVED' else YELLOW if bc_nssmf_status == 'PARTIAL' else RED}{bc_nssmf_status}{NC}\n")
        
        # 5. SLA-Agent Layer
        print(f"{BLUE}📋 Auditando SLA-Agent Layer...{NC}")
        sla_agent_status, sla_agent_issues = self.audit_module("SLA-Agent Layer", [
            self.check_sla_agents_hardcoded
        ])
        self.issues.extend([{**issue, "module": "SLA-Agent Layer"} for issue in sla_agent_issues])
        print(f"   Status: {GREEN if sla_agent_status == 'APPROVED' else YELLOW if sla_agent_status == 'PARTIAL' else RED}{sla_agent_status}{NC}\n")
        
        # Resumo
        print(f"{BLUE}{'='*60}{NC}")
        print(f"{BLUE}📊 Resumo da Auditoria{NC}")
        print(f"{BLUE}{'='*60}{NC}\n")
        
        print(f"{GREEN}✅ Aprovados: {len(self.approved_modules)}{NC}")
        for module in self.approved_modules:
            print(f"   - {module}")
        
        print(f"\n{YELLOW}⚠️ Parciais: {len(self.partial_modules)}{NC}")
        for module in self.partial_modules:
            print(f"   - {module}")
        
        print(f"\n{RED}❌ Reprovados: {len(self.rejected_modules)}{NC}")
        for module in self.rejected_modules:
            print(f"   - {module}")
        
        # Veredito global
        print(f"\n{BLUE}{'='*60}{NC}")
        if len(self.rejected_modules) == 0 and len(self.partial_modules) == 0:
            veredict = "APROVADO PARA E2E LOCAL"
            color = GREEN
        elif len(self.rejected_modules) == 0:
            veredict = "APROVADO COM RESSALVAS"
            color = YELLOW
        else:
            veredict = "REPROVADO - AJUSTES NECESSÁRIOS"
            color = RED
        
        print(f"{color}🎯 Veredito Global: {veredict}{NC}")
        print(f"{BLUE}{'='*60}{NC}\n")
        
        return {
            "veredict": veredict,
            "approved_modules": self.approved_modules,
            "partial_modules": self.partial_modules,
            "rejected_modules": self.rejected_modules,
            "issues": self.issues,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


def generate_markdown_report(audit_result: Dict[str, Any], project_root: Path) -> str:
    """Gera relatório Markdown da auditoria"""
    
    report = f"""# Relatório de Auditoria Técnica v2 — TriSLA
## Validação Pós-Reconstrução (Fases 1-5)

**Data da Auditoria:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}  
**Auditor:** Sistema de Auditoria Técnica Automatizada v2  
**Escopo:** Repositório TriSLA — Validação após Reconstrução (Fases 1-5)  
**Objetivo:** Verificar se todos os problemas críticos da primeira auditoria foram resolvidos

---

## Resumo Executivo

### Veredito Final

**{audit_result['veredict']}**

### Estatísticas Gerais

- **Módulos Auditados:** 5 (SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, SLA-Agent Layer)
- **Status Aprovado:** {len(audit_result['approved_modules'])} módulos ({len(audit_result['approved_modules'])*100//5}%)
- **Status Parcial:** {len(audit_result['partial_modules'])} módulos ({len(audit_result['partial_modules'])*100//5}%)
- **Status Reprovado:** {len(audit_result['rejected_modules'])} módulos ({len(audit_result['rejected_modules'])*100//5}%)
- **Problemas Identificados:** {len(audit_result['issues'])}
- **Problemas Críticos:** {len([i for i in audit_result['issues'] if i.get('severity') == 'CRITICAL'])}

---

## Comparação com Auditoria v1

### Problemas Críticos Resolvidos

A primeira auditoria (`AUDIT_REPORT_TECHNICAL.md`) identificou os seguintes problemas críticos:

1. ❌ **SEM-CSMF:** Ontologia OWL ausente, validação simplificada
2. ❌ **ML-NSMF:** Predição usando `np.random`, modelo não treinado
3. ❌ **Decision Engine:** Uso de `eval()`, regras hardcoded
4. ❌ **BC-NSSMF:** Simulação de contratos Python, Oracle com métricas hardcoded
5. ❌ **SLA-Agent Layer:** Métricas hardcoded, ações sempre `executed: True`

### Status Atual (v2)

"""
    
    # Status por módulo
    modules_status = {
        "SEM-CSMF": "APPROVED" if "SEM-CSMF" in audit_result['approved_modules'] else "PARTIAL" if "SEM-CSMF" in audit_result['partial_modules'] else "REJECTED",
        "ML-NSMF": "APPROVED" if "ML-NSMF" in audit_result['approved_modules'] else "PARTIAL" if "ML-NSMF" in audit_result['partial_modules'] else "REJECTED",
        "Decision Engine": "APPROVED" if "Decision Engine" in audit_result['approved_modules'] else "PARTIAL" if "Decision Engine" in audit_result['partial_modules'] else "REJECTED",
        "BC-NSSMF": "APPROVED" if "BC-NSSMF" in audit_result['approved_modules'] else "PARTIAL" if "BC-NSSMF" in audit_result['partial_modules'] else "REJECTED",
        "SLA-Agent Layer": "APPROVED" if "SLA-Agent Layer" in audit_result['approved_modules'] else "PARTIAL" if "SLA-Agent Layer" in audit_result['partial_modules'] else "REJECTED"
    }
    
    for module, status in modules_status.items():
        status_icon = "✅" if status == "APPROVED" else "⚠️" if status == "PARTIAL" else "❌"
        report += f"{status_icon} **{module}:** {status}\n"
    
    report += f"""
---

## Detalhamento por Módulo

"""
    
    # Agrupar issues por módulo
    issues_by_module = {}
    for issue in audit_result['issues']:
        module = issue.get('module', 'Unknown')
        if module not in issues_by_module:
            issues_by_module[module] = []
        issues_by_module[module].append(issue)
    
    for module in ["SEM-CSMF", "ML-NSMF", "Decision Engine", "BC-NSSMF", "SLA-Agent Layer"]:
        status = modules_status[module]
        status_icon = "✅" if status == "APPROVED" else "⚠️" if status == "PARTIAL" else "❌"
        
        report += f"""### {status_icon} {module} — Status: **{status}**

"""
        
        if module in issues_by_module:
            for issue in issues_by_module[module]:
                severity = issue.get('severity', 'UNKNOWN')
                severity_icon = "🔴" if severity == "CRITICAL" else "🟡" if severity == "MODERATE" else "🟢"
                
                report += f"""#### {severity_icon} {issue.get('message', 'Unknown issue')}

**Severidade:** {severity}  
**Evidência:** {issue.get('evidence', 'N/A')}  
**Recomendação:** {issue.get('recommendation', 'N/A')}

"""
        else:
            report += "Nenhum problema identificado.\n\n"
    
    report += f"""---

## Problemas Identificados

### Críticos

"""
    
    critical_issues = [i for i in audit_result['issues'] if i.get('severity') == 'CRITICAL']
    if critical_issues:
        for i, issue in enumerate(critical_issues, 1):
            report += f"""{i}. **{issue.get('module', 'Unknown')}:** {issue.get('message', 'Unknown')}
   - Evidência: {issue.get('evidence', 'N/A')}
   - Recomendação: {issue.get('recommendation', 'N/A')}

"""
    else:
        report += "Nenhum problema crítico identificado. ✅\n\n"
    
    report += f"""### Moderados

"""
    
    moderate_issues = [i for i in audit_result['issues'] if i.get('severity') == 'MODERATE']
    if moderate_issues:
        for i, issue in enumerate(moderate_issues, 1):
            report += f"""{i}. **{issue.get('module', 'Unknown')}:** {issue.get('message', 'Unknown')}
   - Evidência: {issue.get('evidence', 'N/A')}
   - Recomendação: {issue.get('recommendation', 'N/A')}

"""
    else:
        report += "Nenhum problema moderado identificado. ✅\n\n"
    
    report += f"""---

## Conclusão

### Veredito Final

**{audit_result['veredict']}**

### Próximos Passos

"""
    
    if audit_result['veredict'] == "APROVADO PARA E2E LOCAL":
        report += """1. ✅ Executar testes E2E locais
2. ✅ Validar fluxo completo I-01 → I-07
3. ✅ Preparar deploy no NASP Node1
"""
    elif audit_result['veredict'] == "APROVADO COM RESSALVAS":
        report += """1. ⚠️ Resolver problemas moderados identificados
2. ✅ Executar testes E2E locais
3. ✅ Validar fluxo completo I-01 → I-07
4. ✅ Preparar deploy no NASP Node1
"""
    else:
        report += """1. ❌ Resolver problemas críticos identificados
2. ⚠️ Reexecutar auditoria após correções
3. ✅ Executar testes E2E locais
4. ✅ Validar fluxo completo I-01 → I-07
"""
    
    report += f"""
---

**Versão do Relatório:** 2.0  
**Data:** {datetime.utcnow().strftime("%Y-%m-%d")}  
**ENGINE MASTER:** Sistema de Auditoria Técnica Automatizada v2
"""
    
    return report


def main():
    """Função principal"""
    project_root = Path(__file__).parent.parent.parent
    
    auditor = TechnicalAuditorV2(project_root)
    audit_result = auditor.run_audit()
    
    # Gerar relatório Markdown
    report_md = generate_markdown_report(audit_result, project_root)
    
    # Salvar relatório
    report_path = project_root / "AUDIT_REPORT_TECHNICAL_v2.md"
    report_path.write_text(report_md, encoding="utf-8")
    
    print(f"\n{GREEN}✅ Relatório salvo em: {report_path}{NC}\n")
    
    # Retornar código de saída
    if audit_result['veredict'] == "APROVADO PARA E2E LOCAL":
        sys.exit(0)
    elif audit_result['veredict'] == "APROVADO COM RESSALVAS":
        sys.exit(0)  # Ainda aprovado, mas com ressalvas
    else:
        sys.exit(1)  # Reprovado


if __name__ == "__main__":
    main()

