# AUDITORIA PROMPT_15.1 — PILHA OFICIAL DO PROTÓTIPO NASP + ALINHAMENTO AO RUNBOOK

**PROMPT_ID:** PROMPT_15.1  
**Tipo:** auditoria documental e de cluster apenas (sem deploy, sem correção, sem coleta, sem alteração de código).  
**Base:** PROMPT_15 (SSOT parcial `RANTester + Free5GC`).  
**Timestamp da coleta (UTC):** 2026-04-01T17:00Z (aprox.).  
**Evidências brutas:** `evidencias/prompt15_1_20260401T170031Z/`

---

## 1) Estado por domínio (objetivo NASP vs realidade)

### 1.1 Arquitetura alvo (documental — NASP)

O `NASP/README.md` declara três domínios e ferramentas associadas:

- **RAN:** OpenAirInterface (“Radio Access modules”) e integração com **My5G-RANTester** para simulação NG-RAN.
- **TRANSPORT:** **ONOS** como controlador SDN sobre um ambiente **Mininet** virtualizado; Transport NSSMF projetado para REST do ONOS (intents, topologia, fluxos).
- **CORE:** **Free5GC**.

Referência textual consolidada (conceito):

`RAN (OpenAirInterface / RANTester) → TRANSPORT (ONOS + Mininet) → CORE (Free5GC) → funções SMO / orquestração`

### 1.2 O que o repositório NASP entrega em artefatos (`helm_charts`)

| Domínio   | Esperado (README) | Presente em `helm_charts` (auditoria) |
| --------- | ----------------- | ---------------------------------------- |
| CORE      | Free5GC           | **Sim** — charts `amf`, `smf`, `upf`, `nrf`, etc. |
| RAN       | OAI + RANTester   | **Parcial** — chart **`rantester`** (imagem `baleeiro17/my5grantester`); **sem** chart OAI/OpenAirInterface sob `helm_charts` (grep em `*.yaml`: sem matches). |
| TRANSPORT | ONOS + Mininet    | **Não** — sem matches de `onos` / `mininet` em `helm_charts/*.yaml` (auditoria orientada a manifests). |

Estrutura de alto nível arquivada em `audit_repo_structure.txt` (tree L=3).

### 1.3 Estado do cluster Kubernetes (amostra vivo)

Comandos conforme prompt: `kubectl get pods -A` filtrado.

| Domínio   | Critério de busca        | Resultado (snapshot) |
| --------- | ------------------------ | -------------------- |
| RAN       | `oai`, `openair`, `ran`  | **Sem** pods OAI/OpenAirInterface; **sim** `rantester-0` e `ran-rantester-grafana-*` (namespace `ran-test`). Não há `ueransim` / `srsran` na listagem completa atual — alinhado à limpeza PROMPT_15. |
| TRANSPORT | `onos`, `mininet`        | **Nenhum** pod; **nenhum** Service com nome ONOS (`kubectl get svc -A \| grep -i onos` vazio). |
| CORE      | `free5g`                 | **Sim** — NFs Free5GC em `ns-1274485` (amf, smf, upf, nrf, nssf, pcf, udm, udr, ausf, webui, etc.). |
| RANTester | `rantester`              | **Sim** — `rantester-0` em `ns-1274485` (Running). |

Listagem completa: `kubectl_pods_all.txt`.

---

## 2) Existência explícita (checklist)

| Componente        | No repo NASP (deploy direto) | No cluster (ativo) |
| ----------------- | ---------------------------- | ------------------ |
| OpenAirInterface  | Não (só menção README)       | Não                |
| ONOS              | Não (só menção README)       | Não                |
| Mininet           | Não (só menção README)       | Não                |
| Free5GC           | Sim (charts)                 | Sim                |
| My5G-RANTester    | Sim (`helm_charts/rantester`)| Sim (`rantester-0`) |

---

## 3) Integração entre domínios (evidência e limites)

### 3.1 RAN → Core

- **Evidência indireta forte:** `rantester-0` e pods Free5GC **no mesmo namespace operacional** (`ns-1274485`), consistente com o desenho de protótipo colocado junto ao core.
- **Limitação:** esta auditoria **não** executou captura de pacotes nem testes de sinalização para provar UE attach fim-a-fim; afirma-se apenas **coexistência e coerência de namespace** com tráfego RANTester documentado em campanhas anteriores.

### 3.2 TRANSPORT (ONOS) no caminho

- **Não observado:** ausência de pods/serviços ONOS ou Mininet.
- **Conclusão:** o domínio **TRANSPORT “real” NASP (ONOS + Mininet) não está ativo** neste cluster; qualquer métrica de “transporte” usada pelo TriSLA em vias paralelas (por exemplo *blackbox* / *probe* sobre caminhos IP) é **proxy de transporte**, não substitui o controlador ONOS documentado no NASP.

### 3.3 RANTester, core e intents ONOS

- RANTester **pode** gerar carga direcionada ao stack 5G conforme configuração interna; **não há evidência nesta auditoria** de intents/flows ativos no ONOS (componente inexistente no snapshot).

### 3.4 Telemetria por domínio (mapeamento conceitual)

| Domínio   | Métricas / observações esperadas (NASP) | Estado atual (TriSLA / Prometheus) |
| --------- | ---------------------------------------- | ----------------------------------- |
| RAN       | Carga RAN, sessões, tráfego UE           | SSOT recente usa **proxy de carga** (`ran_load`, sessões `kube_pod_status_phase`, latência de *probe*) — ver PROMPT_16 / 16.1. |
| TRANSPORT | Latência, jitter, caminhos, flows ONOS   | **Sem ONOS:** não há métricas de intent/flow ONOS; jitter/latência podem existir como KPIs genéricos (`trisla_transport_*`) se instrumentados. |
| CORE      | Sessões, UPF, AMF/SMF                    | Core Free5GC ativo; métricas kube/Prometheus podem refletir pods do core. |

---

## 4) Lacunas identificadas

1. **TRANSPORT ausente:** alvo arquitetural NASP (ONOS + Mininet) **não implantado** no cluster auditado e **sem chart** correspondente localizado em `helm_charts`.
2. **OAI ausente:** mencionado no README, **sem** artefato Helm operacional evidente e **sem** pods OAI.
3. **SSOT operacional anterior (PROMPT_15)** correta para **RANTester + Core**, mas **incompleta** face ao **modelo de três domínios** do próprio NASP.
4. **Validação E2E “100% NASP”** continua **bloqueada** até o domínio TRANSPORT (e, se exigido, OAI) estar presente e integrado.

---

## 5) Definição final da SSOT (governança — alvo vs atual)

### 5.1 SSOT **alvo** (alinhamento com documentação NASP)

O TriSLA deve visar operar com **três domínios obrigatórios**:

- **RAN:** OpenAirInterface **ou** equivalente validado pelo projeto + **My5G-RANTester** como gerador de carga.
- **TRANSPORT:** **ONOS** + **Mininet** (ou equivalente funcional explicitamente aceite no runbook).
- **CORE:** **Free5GC**.

### 5.2 SSOT **atual** (snapshot 2026-04-01)

- **Implementado e ativo:** **Free5GC + RANTester**.
- **Não implementado no cluster:** **ONOS, Mininet, OAI** (como acima).
- **Interpretação:** o ambiente é **parcialmente alinhado** ao NASP; cumpre **2 de 3** domínios no sentido estrito do prompt.

---

## 6) Fluxo E2E oficial do TriSLA (formalização — documento de referência)

1. Entrada SLA (Portal / PNL / Template).  
2. SEM-CSMF (interpretação semântica).  
3. ML-NSMF (predição de risco).  
4. Decision Engine (decisão SLA-aware).  
5. **Verificação multi-domínio:** RAN, TRANSPORT, CORE (cada um deve estar **ativo e observável** para experimentos válidos).  
6. Se **ACCEPT:** orquestração NASP → encadeamento NSSMF (RAN, Transport/ONOS, Core/Free5GC) conforme contratos do protótipo.  
7. Execução real da slice / tráfego.  
8. Observabilidade: Prometheus + telemetria multi-domínio.  
9. Feedback contínuo (ML / decisão / closed loops).

---

## 7) Regras obrigatórias (governança — espelhadas no runbook)

1. Proibido ambiente híbrido não declarado (pilhas paralelas não SSOT).  
2. Proibido ignorar o domínio **TRANSPORT** em desenhos experimentais quando a arquitetura NASP for a referência.  
3. Proibido coleta científica final sem E2E completo **nos três domínios** quando a hipótese experimental exige NASP integral.  
4. Proibido substituir métricas reais de domínio por simulação **sem** registo explícito de limitação no manifesto de evidências.  
5. Obrigatório telemetria real por domínio ativo (sem “buracos” silenciosos).  
6. Obrigatório deploy por **digest** quando imagens forem usadas em produção de evidências.  
7. Obrigatório atualizar o runbook após cada fase que altere SSOT ou integrações.

---

## 8) Critério final (respostas obrigatórias)

```text
RAN REAL PRESENTE? SIM (My5G-RANTester; OAI/OpenAirInterface NÃO)
TRANSPORT REAL PRESENTE? NÃO (ONOS/Mininet ausentes no cluster)
CORE REAL PRESENTE? SIM (Free5GC)

AMBIENTE COMPLETO NASP? NÃO (falta domínio TRANSPORT real; OAI não operacional)

PRONTO PARA ATIVAÇÃO COMPLETA? NÃO (requer implantação e integração TRANSPORT + decisão sobre OAI conforme SSOT alvo)
```

---

## 9) Próximos passos recomendados (somente planeamento — fora do escopo de execução deste prompt)

1. Inventariar ou produzir charts/manifests **ONOS + Mininet** (ou equivalente aceite) e plano de namespace / conectividade com Free5GC e RANTester.  
2. Decidir se **OAI** é obrigatório para a linha de evidência ou se **RANTester isolado** permanece como RAN “oficial” até migração OAI — documentar no runbook.  
3. Reauditar Prometheus para métricas **por domínio** após TRANSPORT ativo (flows, latência controlada SDN, etc.).

---

**Fim do relatório PROMPT_15.1.**
