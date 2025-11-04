# 🧩 PROJECT_STRUCTURE_CHECK.md
## Verificador de Estrutura – TriSLA@NASP
Versão: 1.0 — Outubro/2025  
Autor: Abel Lisboa  
Ambiente: NASP / Cursor / GitHub  

---

### 📁 Estrutura Esperada

#### Diretórios Principais
| Diretório | Descrição | Status |
|------------|------------|--------|
| `/STATE` | Contém as Unidades de Trabalho (WU-000 → WU-005) e guias de execução. | ✅ |
| `/PROMPTS` | Reúne todos os prompts e templates de automação. | ✅ |
| `/docs` | Documentação técnica e científica (workflow, referências, evidências). | ✅ |
| `/docs/evidencias` | Logs, métricas e prints de execução. | ✅ |
| `/automation` | Scripts de monitoramento e validação. | ✅ |
| `/helm` | Templates Helm para implantação NASP. | ✅ |
| `/src` | Código-fonte dos módulos TriSLA (semântico, IA e blockchain). | ✅ |

---

### 📜 Arquivos Obrigatórios por Diretório

#### 📍 Raiz (`trisla-nasp-deploy/`)
| Arquivo | Finalidade | Status |
|----------|-------------|--------|
| `README_EXEC.md` | Guia principal de execução no Cursor e NASP. | ✅ |
| `EXEC_CHECKLIST.md` | Checklist visual de progresso das WUs. | ✅ |
| `CHECKLIST_DEVOPS_CONFORMIDADE.md` | Auditoria DevOps e GitOps. | ✅ |
| `README_RECOVERY.md` | Guia de recuperação e rollback. | ✅ |
| `README.md` | Introdução geral e estrutura do projeto. | ✅ |
| `PROJECT_STRUCTURE_CHECK.md` | Este arquivo. | ✅ |

#### 📍 STATE/
| Arquivo | Finalidade | Status |
|----------|-------------|--------|
| `000_INDEX.md` | Índice geral das WUs. | ✅ |
| `WU-000_pre_check.md` | Pré-checagem do ambiente NASP. | ✅ |
| `WU-001_Bootstrap_TriSLA_NASP.md` | Inicialização do ambiente TriSLA. | ✅ |
| `WU-002_Deploy_Core_Modules_TriSLA_NASP.md` | Deploy dos módulos principais. | ✅ |
| `WU-003_Integration_NASP_Core_TriSLA.md` | Integração TriSLA ↔ NASP Core. | ✅ |
| `WU-004_Tests_and_Observability_TriSLA.md` | Testes e observabilidade multi-domínio. | ✅ |
| `WU-005_Avaliacao_Experimental_TriSLA.md` | Validação e métricas finais. | ✅ |
| `checklist_pre_deploy_trisla_nasp.md` | Checklist de pré-deploy. | ✅ |
| `guia_melhores_pratica_execucao_trisla_nasp.md` | Melhores práticas de execução. | ✅ |
| `001_template_wu.md` | Template de nova unidade de trabalho. | ✅ |

#### 📍 PROMPTS/
| Arquivo | Finalidade | Status |
|----------|-------------|--------|
| `starter_prompt.md` | Inicia o ciclo de automação. | ✅ |
| `automation_master_prompt.md` | Prompt mestre de controle global. | ✅ |
| `automation_continuity_guide.md` | Continuidade de execução. | ✅ |
| `automation_supervisor_prompt.md` | Auditoria e conformidade. | ✅ |
| `supervisor_template.md` | Template de relatório técnico. | ✅ |
| `session_template.md` | Cabeçalho de sessão padronizado. | ✅ |
| `task_spec_template.md` | Template de especificação técnica. | ✅ |
| `codegen_template.md` | Template de geração de código. | ✅ |
| `tests_contract_template.md` | Template de testes de contrato. | ✅ |
| `helm_deploy_template.md` | Template de deploy Helm. | ✅ |
| `master_prompt.md` | Prompt mestre (versão unificada). | ✅ |

#### 📍 docs/
| Arquivo | Finalidade | Status |
|----------|-------------|--------|
| `workflow_oficial_trisla_nasp.md` | Descrição do workflow global. | ✅ |
| `referencia_tecnica_trisla.md` | Documento técnico consolidado. | ✅ |

#### 📍 docs/evidencias/
| Arquivo | Finalidade | Status |
|----------|-------------|--------|
| `readme_evidencias.md` | Guia para registrar evidências e logs. | ✅ |

#### 📍 automation/
| Arquivo | Finalidade | Status |
|----------|-------------|--------|
| `supervisor_check.py` | Verifica integridade das WUs e pastas. | ✅ |
| `deploy_watcher.py` | Monitora pods e namespaces do TriSLA. | ✅ |
| `auto_validator.py` | Valida logs e métricas pós-execução. | ✅ |

---

### 🔍 Verificação Manual (pré-deploy)

✅ Todos os diretórios acima existem.  
✅ Todos os arquivos obrigatórios estão presentes.  
✅ Nomes normalizados (sem acentuação, minúsculos).  
✅ Estrutura compatível com ambiente NASP (Kubernetes + Helm).  
✅ Pastas sem arquivos temporários (`.zip`, `.log`, `.tmp`).  

---

### 📦 Etapa Final

Antes de empacotar:
```powershell
# Dentro da pasta trisla-nasp-deploy
Compress-Archive -Path STATE -DestinationPath state.zip -Force
Compress-Archive -Path PROMPTS -DestinationPath prompts.zip -Force
Compress-Archive -Path docs -DestinationPath docs.zip -Force
Compress-Archive -Path README_EXEC.md,EXEC_CHECKLIST.md,CHECKLIST_DEVOPS_CONFORMIDADE.md,README_RECOVERY.md,README.md -DestinationPath trisla-nasp_root.zip -Force
```

---

### ✅ Resultado Esperado
```
trisla-nasp_root.zip
state.zip
prompts.zip
docs.zip
```

Todos os pacotes prontos para:
- importação no Cursor  
- implantação no NASP  
- anexos à dissertação TriSLA (Apêndice Técnico)
