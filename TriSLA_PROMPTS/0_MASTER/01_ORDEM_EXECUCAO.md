# 01 – ORDEM DE EXECUÇÃO

Sequência oficial de execução dos prompts TriSLA.
# ORDEM OFICIAL DE EXECUÇÃO DOS PROMPTS TRI-SLA

Esta ordem garante que o desenvolvimento siga dependências técnicas e fluxo lógico do projeto.

> **⚠️ IMPORTANTE**: Antes de iniciar, leia o documento `03_ESTRATEGIA_EXECUCAO.md` para entender **onde** (local vs servidor NASP) cada prompt deve ser executado.

1) 00_PROMPT_MASTER_PLANEJAMENTO  
2) 10_INFRA_NASP  
3) 11_ANSIBLE_INVENTORY  
4) 12_PRE_FLIGHT  
5) 20_SEM_CSMF  
6) 21_ML_NSMF  
7) 22_DECISION_ENGINE  
8) 23_BC_NSSMF  
9) 24_SLA_AGENT_LAYER  
10) 25_INTERFACES_I_01_I_07  
11) 26_ADAPTER_NASP  
12) 27_UI_DASHBOARD  
13) 30_OBSERVABILITY_OTLP  
14) 31_SLO_REPORTS  
15) 32_DASHBOARDS_GRAFANA  
16) 40_UNIT_TESTS  
17) 41_INTEGRATION_TESTS  
18) 42_E2E_TESTS  
19) 50_MASTER_CICD_QUALITY_GATES  
20) 51_GITHUB_ACTIONS  
21) 52_PR_RULES  
22) 53_GHCR_PACKAGING  
23) 60_HELM_CHART  
24) 61_HELM_VALIDATION  
25) 62_DEPLOY_STAGE  
26) 63_DEPLOY_QA  
27) 64_DEPLOY_NASP  
28) 65_ROLLBACK_STRATEGY  
29) 66_PRODUCAO_REAL  

Iniciar sempre da fase 0 até a fase 6.  
Nunca executar prompts fora de ordem.

---

## 📍 RESUMO: ONDE EXECUTAR CADA PROMPT

> **⚠️ IMPORTANTE**: **TODOS os 29 prompts são executados LOCALMENTE**. Eles geram código, playbooks Ansible e instruções que são publicados no GitHub e depois usados para deploy no NASP em **PRODUÇÃO REAL**.

| # | Prompt | Ambiente | O que gera | Publicado em |
|---|--------|----------|------------|--------------|
| 1 | `00_PROMPT_MASTER_PLANEJAMENTO` | 🖥️ **Local** | Documentação | GitHub `/docs` |
| 2 | `10_INFRA_NASP` | 🖥️ **Local** | Scripts auto-config | GitHub `/scripts` |
| 3 | `11_ANSIBLE_INVENTORY` | 🖥️ **Local** | Inventory + playbooks | GitHub `/ansible` |
| 4 | `12_PRE_FLIGHT` | 🖥️ **Local** | Scripts validação | GitHub `/scripts` |
| 5-11 | `20_SEM_CSMF` até `26_ADAPTER_NASP` | 🖥️ **Local** | Código módulos | GitHub `/apps` |
| 12 | `27_UI_DASHBOARD` | 🖥️ **Local** | Interface web completa | GitHub `/apps/ui-dashboard` |
| 13-15 | `30_OBSERVABILITY_OTLP` até `32_DASHBOARDS_GRAFANA` | 🖥️ **Local** | Configs observabilidade | GitHub `/monitoring` |
| 16-18 | `40_UNIT_TESTS` até `42_E2E_TESTS` | 🖥️ **Local** | Testes automatizados | GitHub `/tests` |
| 19-22 | `50_*` até `53_*` | 🖥️ **Local** | Workflows CI/CD | GitHub `/.github/workflows` |
| 23 | `60_HELM_CHART` | 🖥️ **Local** | Helm charts | GitHub `/helm` |
| 24 | `61_HELM_VALIDATION` | 🖥️ **Local** | Scripts validação | GitHub `/scripts` |
| 25-27 | `62_DEPLOY_*` até `64_DEPLOY_NASP` | 🖥️ **Local** | **Playbooks + Instruções** | GitHub `/ansible`, `/docs` |
| 28 | `65_ROLLBACK_STRATEGY` | 🖥️ **Local** | Scripts rollback | GitHub `/scripts` |
| 29 | `66_PRODUCAO_REAL` | 🖥️ **Local** | **Configuração produção REAL** | GitHub `/docs`, `/configs` |

**Fluxo:**
1. ✅ **Executar prompts localmente** (todos os 29)
2. ✅ **Publicar no GitHub**: https://github.com/abelisboa/TriSLA
3. ✅ **Deploy no NASP**: Usar playbooks Ansible ou instruções manuais do GitHub

**Legenda:**
- 🖥️ **Local**: Todos os prompts executados na máquina de desenvolvimento
- 📦 **GitHub**: Código gerado é publicado no repositório público
- 🚀 **NASP**: Deploy feito a partir do GitHub (node1/node2)

> Para detalhes completos sobre o fluxo Local → GitHub → NASP, consulte `03_ESTRATEGIA_EXECUCAO.md`
