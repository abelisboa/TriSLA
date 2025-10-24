# SESSION_WU005_INIT.md  
### Fase: WU-005 — Avaliação Experimental TriSLA@NASP  
**Autor:** Abel Lisboa  
**Ambiente:** NASP Kubernetes (node1/node2 – Dell R430)  
**Data:** 2025-10-22  
**Versão:** 2025.10 – Fase Experimental  

---

## 🎯 OBJETIVO GERAL
Executar a **avaliação experimental da arquitetura TriSLA** no ambiente NASP, validando o comportamento integrado dos módulos SEM-NSMF, ML-NSMF e BC-NSSMF em cenários controlados de requisição, decisão e enforcement de SLAs em redes 5G/O-RAN.

---

## 🧩 CONTEXTO OPERACIONAL
O ambiente NASP encontra-se estabilizado e auditado (vide `/tmp/nasp_env_final_report.txt`), com:
- Kubernetes 1.28.15 (node1) e 1.31.1 (node2) operacionais;  
- CRI-O + Multus + Calico ativos;  
- Namespaces ativos: `trisla-nsp`, `nonrtric`, `semantic`, `open5gs`, `monitoring`;  
- Pods TriSLA executando (AI-Layer, Blockchain-Layer, Integration-Layer, Semantic-Layer, Monitoring-Layer).  

---

## ⚙️ ARQUITETURA EXPERIMENTAL
A Fase WU-005 executará experimentos com base em três eixos:
1. **SLA Awareness** — entrada semântica via módulo SEM-NSMF e ontologia TriSLA.  
2. **Decision Intelligence** — predição e validação com ML-NSMF (LSTM, XAI, federated reasoning).  
3. **Smart Enforcement** — verificação de conformidade e logging por contratos inteligentes (BC-NSSMF).  

Os experimentos seguem as recomendações dos Apêndices A, E e H da proposta técnica.  

---

## 🧠 RECURSOS E ESTRUTURA

```
trisla-nsp/
 ├── automation/             → scripts de auditoria e validação
 │    ├── supervisor_check.py
 │    └── deploy_watcher.py  *(a ser criado nesta WU)*
 ├── PROMPTS/                → templates de execução
 │    ├── SESSION_TEMPLATE.md
 │    ├── HELM_DEPLOY_TEMPLATE.md
 │    └── TESTS_CONTRACT_TEMPLATE.md *(novo)*
 ├── STATE/                  → estado e resultados por WU
 │    └── WU-005_Avaliacao_Experimental.md *(a ser gerado)*
 ├── docs/evidencias/        → relatórios JSON e gráficos de métricas
 └── helm/                   → charts de atualização incremental
```

---

## 🔍 ETAPAS DE EXECUÇÃO

| Etapa | Script | Função |
|-------|---------|--------|
| 1️⃣ | `automation/supervisor_check.py` | Valida integridade do ambiente TriSLA |
| 2️⃣ | `automation/deploy_watcher.py` | Monitora pods e coleta logs/métricas |
| 3️⃣ | `automation/auto_validator.py` | Executa testes e gera relatório comparativo |
| 4️⃣ | `helm upgrade --install` | Atualiza módulos TriSLA com parâmetros de teste |
| 5️⃣ | `STATE/WU-005_Avaliacao_Experimental.md` | Registra resultados e análises finais |

---

## 🧭 MODO DE OPERAÇÃO (no Cursor IDE)

1. **Abrir o repositório local** (`trisla-deploy/`) no Cursor.  
2. Colar este arquivo **SESSION_WU005_INIT.md** na raiz do projeto.  
3. Em seguida, colar o conteúdo completo do **Prompt Mestre Unificado (TriSLA@NASP)**.  
4. O agente IA interpretará automaticamente este contexto e iniciará a execução da WU-005.  

---

## 📘 RESULTADOS ESPERADOS
- Logs estruturados (`deploy_watch_log.json`, `validation_report.json`);  
- Métricas de latência e disponibilidade (RTT, SLA compliance %);  
- Evidência da execução ontológica e inferência semântica (SEM-NSMF);  
- Validação de predições via LSTM e explicabilidade (ML-NSMF);  
- Auditoria de contratos inteligentes e estados de conformidade (BC-NSSMF).  

---

## 🧩 CRITÉRIOS DE ACEITE (DoD)
- Todos os pods TriSLA em estado **Running**.  
- Dashboard de observabilidade ativo no namespace `monitoring`.  
- Geração de relatórios JSON e Markdown no diretório `docs/evidencias/`.  
- Registro de decisão semântica → predição → enforcement em pipeline único.  
- Hash de auditoria verificado via `automation/supervisor_check.py`.

---

## 🧾 PRÓXIMO PASSO
Após colar este arquivo e o Prompt Mestre no Cursor IDE:
- A IA executará leitura automática do estado `WU-004 → WU-005`;
- Validará a integridade estrutural (`supervisor_check.py`);
- Criará o `WU-005_Avaliacao_Experimental.md` com plano técnico inicial;
- E solicitará sua confirmação antes de qualquer operação real no NASP.

---

🧠 *TriSLA@NASP — Fase Experimental conduzida por Abel Lisboa*  
📍 *UNISINOS – PPGCA – 2025*  
