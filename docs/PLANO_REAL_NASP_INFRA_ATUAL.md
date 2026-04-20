# Plano real da infra NASP em `/home/porvir5g/gtp5g` — PROMPT_16.2_v2

**PROMPT_ID:** PROMPT_16.2_v2  
**Base:** PROMPT_15.1  
**Tipo:** engenharia reversa da infra **real** + plano de ativação — **sem execução** (sem clone, instalação, deploy ou alteração de cluster).  
**Data (UTC):** 2026-04-01  
**Evidências:** `evidencias/prompt16_2_20260401T171739Z/` (tree `gtp5g`, `find` de scripts/yaml, `kubectl` completo, greps dirigidos).

---

## 1) Arquitetura real detectada

### 1.1 O diretório base `/home/porvir5g/gtp5g`

Alto nível (ver `estrutura_gtp5g.txt` e `dirs_gtp5g.txt`):

- **`NASP/`** — código do protótipo (Flask `nasp`, `helm_charts`, `data/db`, `README` académico).
- **`trisla/`** — stack TriSLA atual (apps, `docs`, `PROMPTS`, Helm/kube, etc.).
- **`kubespray/`** — tooling de cluster (Ansible); script auxiliar `nasp_env_final_audit.sh` (checklist host/k8s, **não** provisiona ONOS/OAI).
- **`trisla-portal/`** — portal legado/paralelo com `docker-compose`, `nasp/`, playbooks (histórico de integração).
- **Arquivos e snapshots** (`ARCHIVE_*`, `trisla_snapshot_*`, `backups/`) — cópias pontuais; não substituem o estado do cluster.

Conclusão: a “infra NASP” no disco é sobretudo **código + histórico + automação Kubernetes**; **não** existe árvore dedicada tipo `onos-mininet/` ou `oai-5g/` pronta e isolada nesta amostra de três níveis.

### 1.2 O cluster Kubernetes (snapshot)

Ficheiros: `pods_full.txt`, `svc_full.txt`, `deploy_full.txt`, `pods_filtered_nasp.txt`.

Domínios **observados**:

| Domínio   | Evidência no cluster |
| --------- | -------------------- |
| **CORE**  | NFs **Free5GC** em `ns-1274485` (AMF, SMF, UPF, NRF, NSSF, PCF, UDM, UDR, AUSF, WebUI). |
| **RAN**   | **My5G-RANTester** — `rantester-0` no mesmo namespace; Grafana associada em `ran-test`. |
| **TRANSPORT (SDN)** | **Sem** pods ou serviços cujo nome sugira **ONOS** ou **Mininet** na filtragem efetuada. |

Alinhamento com `docs/AUDITORIA_PROMPT15_1_NASP_FULL_STACK.md`: o ambiente continua **2/3 domínios** no sentido estrito NASP (Core + gerador RAN), **sem** camada TRANSPORT nativa visível.

---

## 2) Componentes existentes

| Componente | Onde está | Função |
| ---------- | --------- | ------ |
| Free5GC | Cluster `ns-1274485` + charts em `NASP/helm_charts/*` | Core 5G |
| RANTester | Cluster + chart `NASP/helm_charts/rantester` | Tráfego / teste RAN↔AMF |
| NASP app | `NASP/nasp/` | Orquestração lógica, Helm installs, hooks para transporte (legado) |
| TriSLA | `trisla/` | Pipeline SLA, observabilidade, integração com NASP via APIs |

**RANTester → Core (configuração declarada):** o `config.yaml` do chart aponta o AMF para o serviço Kubernetes interno:

```yaml
amfif:
  ip: amf-free5gc-amf-amf-0.amf-service
  port: 38412
```

Isto indica ligação **direta UE/RANTester – AMF** sobre a rede do cluster, **sem** referência a dataplane ONOS neste ficheiro.

---

## 3) Componentes ausentes (face ao modelo NASP documental)

| Componente | Repo AWS / charts | Cluster |
| ---------- | ----------------- | ------- |
| **OpenAirInterface (OAI)** | Mencionado no `NASP/README.md`; **sem** chart OAI em `NASP/helm_charts` na auditoria anterior (PROMPT_15.1) | **Sem** pods OAI |
| **ONOS** | Sem chart em `helm_charts`; **código Python** assume controlador **externo** | **Sem** ONOS in-cluster |
| **Mininet** | Apenas texto no README; shaping em código usa `tc` via **SSH para hosts externos** (não Mininet local no repo analisado) | **Sem** Mininet |

---

## 4) Gaps (tabela consolidada)

| Domínio   | Esperado (NASP README / dissertação) | Atual (infra real) | Gap |
| --------- | ------------------------------------ | ------------------- | --- |
| RAN       | OAI + RANTester                      | RANTester apenas   | **OAI ausente**; RAN “real” OAI não operacionalizado |
| TRANSPORT | ONOS + Mininet                       | Não implantado; intents ONOS desactivados no fluxo principal | **Gap total** no cluster; legado **HTTP fixo** no código |
| CORE      | Free5GC                              | Free5GC            | **OK** |

### 4.1 Detalhe crítico: integração ONOS no código NASP

Em `NASP/nasp/src/services/helm_deployments.py`:

- O método `deploy_transport_network()` existe e chamaria `deploy_onos_intents()`, com **URL hardcoded** `http://67.205.130.238:8181/onos/v1/intents` e credenciais Basic em claro.
- No fluxo principal de deploy (`install_slice` / caminho observado nas linhas ~95–109), a linha que activaria o transporte está **comentada**: `#self.deploy_transport_network(low_latency=False)`.
- Há ainda `create_delay()` com **SSH** para IPs externos e `tc qdisc` — padrão de **laboratório remoto**, não de pods Kubernetes actuais.

Interpretação: o protótipo **previu** Transport via ONOS/Mininet ou análogo, mas a **instanciação actual** do serviço NASP no cluster **não** activa esse caminho; o ONOS referenciado é **endpoint legado**, não um Service do cluster actual.

---

## 5) Integração actual (respostas da Fase 6)

```text
Como RANTester envia tráfego?
  → Conforme chart: aplicação My5G-RANTester no Pod, configuração aponta para
    amf-free5gc-amf-amf-0.amf-service:38412 (N2 lógico / stack de teste).

Como Free5GC recebe?
  → AMF (e demais NFs) no namespace ns-1274485; tráfego de controlo/dados de teste
    conforme topologia Helm Free5GC + RANTester.

Existe camada intermediária real (ONOS/Mininet) no caminho?
  → Não evidenciada no cluster nem na config do RANTester analisada;
    o código NASP teria de chamá-la explicitamente (hoje comentada / URL externa).
```

---

## 6) Plano realista de ativação (somente desenho — não executado)

### Fase A — Transport (ONOS + topologia)

1. **Decisão:** ONOS **in-cluster** (StatefulSet/Helm oficial ou custom) **vs.** VM/bare-metal dedicada (espelhar o IP legado com modernização).
2. **Rede:** Garantir que o dataplane entre vários nós/workloads (UPF, RANTester, bridges) pode ser encaminhado por switches OpenFlow **ou** documentar um **equivalente** (por exemplo Cilium + políticas) **com aceitação formal** no runbook (já previsto em PROMPT_15.1 para “equivalente funcional”).
3. **Código:** Substituir `67.205.130.238` por **Service DNS** + Secret; reactivar `deploy_transport_network()` só após controlador e topologia **reais** existirem.
4. **Mininet:** Se necessário ao protótipo, orquestrar como Job/privileged ou nó dedicado — **alto risco operacional** (capabilities, root); frequentemente o protótipo migra para **treinço SDN simplificado** ou emulador externo.

### Fase B — RAN (OAI)

1. **Viabilidade:** OAI em Kubernetes é **complexa** (SRIOU/VNF, sincronismo, licenças de RF virtual); frequentemente sai do escopo “só Helm” do NASP actual.
2. **Opções:** (i) chart OAI da comunidade + Multus + hugepages; (ii) manter **RANTester** como RAN de protótipo e declarar OAI como **roadmap**; (iii) integração com outro gNB comercial/emulado **explicitamente** nomeado na SSOT.

### Fase C — Integração multi-domínio

1. Ordem sugerida: **Transport observável** (métricas ONOS / flows) → **ligação nominal** RANTester–Core mantida → **provas** (ping, sessão, intents) → **TriSLA** ler telemetria por domínio (sem proxy único).
2. Actualizar `docs/TRISLA_MASTER_RUNBOOK.md` após cada marco (regra já estabelecida em PROMPT_15.1).

---

## 7) Viabilidade e complexidade

| Domínio faltante | Base no ambiente? | Esforço relativo | Notas |
| ----------------- | ----------------- | ---------------- | ----- |
| TRANSPORT (ONOS) | **Código** e testes existem; **infra** não | Médio–Alto | Limpeza de secrets, networking SDN, reactivar código com segurança |
|_mininet_        | README + `tc` SSH legado | Alto se “puro Mininet” | Avaliar substituição por topologia equivalente documentada |
| RAN (OAI)        | Só documentação | Alto | Alternativa: manter RANTester + roadmap OAI |

---

## 8) Riscos

1. **Dependência de IPs e credenciais fixos** no código NASP — risco de segurança e de falha quando o laboratório mudar.
2. **Transport desligado por comentário** — risco de **falsa sensação** de NASP “completo” quando apenas Core+RAN estão activos.
3. **OAI** — risco de sobrecarga operacional e de **regressão** na estabilidade do cluster já validada (Free5GC + RANTester).
4. **Conflito SSOT:** exigir “3 domínios” para ciência vs. continuar campanhas no **modelo actual** — deve ficar **explícito** em cada dataset (PROMPT_15.1 / `CURSOR_WORKFLOW_RULES.md` §11).

---

## 9) Recomendação final

- **Curto prazo (ciência e estabilidade):** manter o **modelo actual** **Free5GC + RANTester** como **SSOT operacional** **desde que** todos os artefactos declarem **claramente** que o domínio **TRANSPORT NASP integral** e **OAI** **não** estão activos (evitar claims “NASP 100%” nas teses).
- **Médio prazo (alinhamento arquitectural):** projecto dedicado **PROMPT futuro** só para **Transport**: ONOS servido em ambiente controlado + remoção de IPs hardcoded + métricas + teste de intents; **em paralelo** decisão explícita sobre **OAI vs. RANTester-only**.

---

## 10) Critério final (respostas obrigatórias)

```text
NASP COMPLETO EXISTE NO AMBIENTE? NÃO

O QUE FALTA?
  - Domínio TRANSPORT (ONOS + Mininet ou equivalente aceite) no cluster e integrado.
  - RAN OAI operacional (hoje: apenas RANTester como carga RAN declarada nos charts).
  - Remoção da dependência de endpoints ONOS legados e reactivação segura do fluxo de transporte no código NASP.

É VIÁVEL ATIVAR?
  SIM, de forma incremental e com projecto próprio — Transport primeiro, OAI como decisão estratégica separada.
  Não é “plug-and-play” apenas a partir dos artefactos Helm actuais do NASP.

QUAL ESTRATÉGIA RECOMENDADA?
  (1) Documentar e usar o modelo Core+RANTester como baseline científica honesta.
  (2) Planear activação CONTROLADA do Transport (ONOS + rede + secrets + métricas).
  (3) Só então reavaliar OAI ou equivalente RAN “pesado” sem regressão no core.
```

---

**Fim do documento PROMPT_16.2_v2.**
