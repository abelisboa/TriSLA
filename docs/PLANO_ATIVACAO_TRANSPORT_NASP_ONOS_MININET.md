# Plano de ativação do domínio TRANSPORT do NASP (ONOS + Mininet) — PROMPT_16.3

**PROMPT_ID:** PROMPT_16.3  
**Base:** PROMPT_15.1 + PROMPT_16.2_v2  
**Tipo:** planeamento operacional **sem execução** (sem instalação, deploy ou alteração de cluster/TriSLA).  
**Data (UTC):** 2026-04-01  
**Evidências congeladas:** `evidencias/prompt16_3_20260401T174211Z/` (`pods_before.txt`, `services_before.txt`, `deployments_before.txt`, `onos_paths.txt`, `mininet_paths.txt`, greps `kubectl_*_transport.txt`).

---

## 1) Artefactos encontrados

### 1.1 No repositório NASP (`/home/porvir5g/gtp5g/NASP`)

| Artefacto | Descrição |
|-----------|-----------|
| `nasp/src/services/helm_deployments.py` | Lógica **Transport**: `deploy_transport_network`, `deploy_onos_intents`, `delete_onos_intents`; chamada ao fluxo principal **comentada**; URLs e credenciais **fixas**. |
| `nasp/tests/test_nsmf_service.py` | Teste unitário com **mock** de `requests.post` para intents (sem infra real). |
| `README.md` | Arquitectura: **Transport NSSMF** ↔ **ONOS REST** sobre infra **Mininet** virtualizada. |
| `nasp/web/static/onos-topology.png` | Recurso estático (UX) — não substitui manifests. |

**Não encontrado** em `helm_charts` nem como paths `*onos*` / `*mininet*` úteis (para além de documentação e ruído tipo *apconos* no Ansible): **charts Kubernetes para ONOS ou Mininet**, **topologias Mininet** (`.mn`, scripts Python), **docker-compose** dedicado ao par ONOS+Mininet no âmbito NASP.

### 1.2 Na árvore `/home/porvir5g/gtp5g` (amostra `find` com prune de `node_modules` / `.git`)

- Matches `*onos*`: sobretudo **falsos positivos** (`apconos` em coleções Ansible), **PROMPTS**, evidências de auditorias anteriores, **`NASP/nasp/web/static/onos-topology.png`**.
- Matches `*mininet*`: sobretudo **ficheiros de prompt** e **evidências** — **nenhum** runtime Mininet versionado como parte do protótipo NASP nesta amostra.

### 1.3 Cluster (snapshot `kubectl`)

- **Pods / Services / ConfigMaps / Secrets** com `onos` ou `mininet` no nome: **vazios** nos filtros registados (`kubectl_pods_transport.txt`, etc.).
- **Conclusão:** não há implantação parcial óbvia do domínio TRANSPORT no cluster no momento do congelamento.

---

## 2) Arquitectura operacional esperada do TRANSPORT (reconstrução)

### 2.1 Pela documentação (README)

- Plataforma orquestrada em **Kubernetes**; funções SMO em contentores.
- **Transport NSSMF** deve falar com o **controlador WAN SDN** via **REST do ONOS**, sobre uma infra-estrutura **Mininet** virtualizada (topologia programável, tráfego através de switches controlados por OpenFlow).

### 2.2 Pelo código (`helm_deployments.py`)

1. **ONOS** expõe API REST (caminho típico `/onos/v1/intents` na porta **8181** no código legado).
2. **Intents** do tipo `PointToPointIntent` com `ingressPoint` / `egressPoint` em **dispositivos OpenFlow** (`of:...`) e **portas** — coerente com **Mininet** ou topo física/emulada com DPIDs conhecidos.
3. O **fluxo de slice** que instala RAN/Core **não invoca** `deploy_transport_network` na versão lida (**linha comentada**), pelo que o Transport **nunca** é activado no pipeline actual.
4. **Atraso / jitter** (`create_delay`, `delete_delay`): uso de **`tc qdisc`** via **SSH** para **hosts com IPs fixos** — indica desenho de **laboratório** (máquinas externas ao modelo declarativo puro em Kubernetes), não um único chart “Mininet-in-Pod” documentado aqui.

### 2.3 Onde o ONOS “deveria” correr?

| Opção | Coerência com evidências |
| ----- | ------------------------- |
| **Externo (VM/bare-metal)** | **Alta** — URL IP literal `67.205.130.238` e SSH para outros IPs em `create_delay`. |
| **Kubernetes (Service + Pod)** | **Possível** no futuro — substitui o IP por **DNS interno** e alinha com o resto do stack; **não** está implementado nos artefactos actuais. |
| **Só contentor Docker fora do cluster** | **Possível** — equivalência operacional a “externo” com rede alcançável pelo NASP. |

### 2.4 Onde o Mininet “deveria” correr?

| Opção | Coerência |
| ----- |----------|
| **Host/VM com kernel namespace** (modo clássico) | **Alta** — Mininet depende de **network namespaces** e frequentemente de **privilégios**; é o padrão da literatura e compatível com switches Open vSwitch ligados ao ONOS. |
| **Pod Kubernetes não privilegiado** | **Baixa** para topo completa — sem `CAP_NET_ADMIN` / `/sys` / módulos, Mininet é limitado ou inviável. |
| **Pod privileged / DaemonSet** | **Média** — viável em clusters onde política de segurança permita; requer revisão explícita de **PSA/PSS** e política da equipa. |

### 2.5 Ligação ONOS ↔ Mininet (esperada)

- Controlador **ONOS** estabelece sessões **OpenFlow** com switches da topologia **Mininet** (ou OVS externos).
- O **NASP** não instancia essa topologia nos artefactos analisados; assume que **DPIDs e portas** dos intents (`of:0000000000000001`, etc.) **já correspondem** à topologia real/carregada no laboratório.

### 2.6 Integração ao fluxo de orquestração NASP

- No fluxo `install`/deploy de slice: após condições de RAN/Core, deveria existir fase **“Deploying Transport”** que chama `deploy_transport_network(...)` **ou** equivalente parametrizado.
- Limpeza: `clear_environment` chama `delete_onos_intents()` e manipula **delay** via SSH — Transport participa do **ciclo de vida** apenas se ONOS e hosts `tc` existirem.

---

## 3) Dependências reais de ativação

### 3.1 ONOS

| Item | Detalhe |
| ---- | ------- |
| Imagem / pacote | A definir (ex.: imagem Docker oficial ONOS 2.x ou build personalizado). |
| Versão | Compatível com API **`/onos/v1/intents`** e tipo `PointToPointIntent` usado no código. |
| Portas | **8181** (REST UI/API típica); validar versão. |
| Credenciais | Hoje **Basic** em claro no código (`onos`/`rocks` — **remover** e mover para **Secret**). |
| Endpoint | **Configurável** (env/config): `ONOS_REST_URL` em vez de IP fixo. |
| Deploy | **VM**, **systemd**, **Docker** ou **Kubernetes** — desde que URL seja estável para o pod NASP/API que chama o REST. |

### 3.2 Mininet

| Item | Detalhe |
| ---- | ------- |
| Dependências | Linux, Open vSwitch (ou kernel compatível), Python Mininet; frequentemente root/privileged. |
| Topologia | **Ficheiro ou script** que reproduza os **DPIDs/portas** que os intents esperam **ou** gerar intents a partir da topologia descoberta (refactor futuro). |
| Execução | **Recomendado:** VM ou nó dedicado; alternativa **privileged** Kubernetes após aprovação de segurança. |
| Integração ONOS | Switches registados no ONOS; conectividade IP entre controlador e dataplane. |

### 3.3 Integração NASP (código / config)

| Item | Detalhe |
| ---- | ------- |
| Variáveis | `ONOS_BASE_URL`, `ONOS_USER`, `ONOS_PASSWORD` (Secret), flag `TRANSPORT_ENABLED=true`. |
| Serviços consumidores | Processo que corre `HelmDeployments` / NASP API **no cluster** deve resolver DNS para o ONOS. |
| Refactor mínimo | Descomentar e condicionar chamada a `deploy_transport_network`; **nunca** manter credenciais no Git. |

---

## 4) Gaps atuais

1. **Nenhum** manifesto de deploy ONOS/Mininet na linha oficial NASP analisada.  
2. **Transport desligado** no fluxo principal (`#self.deploy_transport_network`).  
3. **Endpoint e credenciais** hardcoded — incompatível com produção e com cluster actual.  
4. **`create_delay`** depende de **SSH + IPs estáticos** — mapping para o ambiente actual **inexistente** no plano de rede documentado.  
5. **Cluster:** zero pods/serviços Transport — sem observabilidade de domínio.  
6. **Correspondência intent ↔ topologia:** não há prova versionada de que os `of:...` do código casam com uma Mininet real.

---

## 5) Plano de ativação por fases (**não executado** neste prompt)

### FASE A — Pré-requisitos

- Definir **namespace** (ex. `nasp-transport` ou VM fora do cluster).
- Obter **imagens** ONOS (digest) e baseline Mininet (SO base).
- Criar **Secrets** para credenciais ONOS; remover literais do repositório num prompt de implementação futuro.
- Mapear **conectividade**: NASP → ONOS; ONOS ↔ dataplane; dataplane ↔ caminhos relevantes ao **Free5GC/UPF** (se o desenho exigir tráfego através do Transport).
- **Portas / NetworkPolicy:** permitir 8181 (ou TLS terminado) conforme arquitectura.

### FASE B — Ativação do ONOS

- Subir ONOS (VM ou K8s).
- **Validação:** `GET` health/API; autenticação; lista de dispositivos OpenFlow **não vazia** após Mininet/pré-config.
- **Healthcheck** para Prometheus (métrica JMX/HTTP conforme versão) ou *blackbox* mínimo.

### FASE C — Ativação do Mininet

- Instalar topologia **mínima** (2–4 switches) com DPIDs **alinhados** aos intents do código **ou** ajustar intents ao descobrir DPIDs.
- Garantir que o controlador vê **links** e **hosts**; teste `pingall` (ou equivalente) **antes** de intents NASP.

### FASE D — Integração com NASP (Transport NSSMF)

- Parametrizar URL e credenciais.  
- Reactivar **chamada** a `deploy_transport_network` atrás de feature flag e testes em ambiente de **staging**.  
- Validar `clear_environment` / `delete_onos_intents` sem erro.  
- **Substituir** ou **desactivar** `create_delay` até existirem hosts equivalentes ou novo mecanismo (por exemplo *netem* num namespace controlado).

### FASE E — Observabilidade

- **ONOS:** intents activos, fluxos, topologia (REST ou exportador).  
- **Dataplane:** contadores, latência ponta-a-ponta entre hosts Mininet.  
- **Prometheus:** job scrape (PodMonitor/ServiceMonitor) ou integração via NASP/Pushgateway **documentada**.  
- **TriSLA** (fora do escopo deste prompt): só depois de métricas estáveis — alinhar com runbook multi-domínio.

### FASE F — *Gate* final

O domínio TRANSPORT só é dado como **activo** quando, com evidência objectiva:

- ONOS responde por **REST** autenticado.  
- Mininet (ou equivalente aceite no runbook) está **operacional**.  
- **Intents/fluxos** são criados e reflectidos no controlador / dataplane.  
- **Tráfego** de teste atravessa o domínio conforme desenho.  
- **Métricas** mínimas do transporte estão disponíveis para auditoria.

---

## 6) Critérios de sucesso (checklist)

- [ ] `ONOS_REST_URL` configurável; Secrets aplicados; código sem passwords em texto claro.  
- [ ] `deploy_transport_network` invocado **só** quando Transport está saudável.  
- [ ] Intents aplicam-se sem erro 4xx/5xx; topologia ONOS mostra caminhos.  
- [ ] Mininet (ou alternativa aprovada) comprovada com teste de conectividade.  
- [ ] `kubectl`/inventário com **recursos nomeados** Transport ou documentação de **VM** equivalente.  
- [ ] Runbook actualizado com “TRANSPORT activo” e *links* para evidências.

---

## 7) Complexidade e risco (resumo)

| Fase | Dificuldade | Risco regressão | Bloqueadores típicos |
|------|------------|-----------------|----------------------|
| A — Pré-requisitos | Média | Baixo | Acordo de rede / firewall / ausência de IPs |
| B — ONOS | Média–Alta | Médio | Imagem, memória, versão API |
| C — Mininet | Alta | Alto | Privilégios, kernel, alinhamento DPID |
| D — NASP código | Média | Alto | Reactivar fluxo sem quebrar deploys actuais |
| E — Observabilidade | Média | Baixo | Falta de exporter oficial |
| F — Gate | — | — | Qualquer falha acima |

**Dependências externas:** conectividade de laboratório, possível VM fora do cluster, política de segurança para contentores privilegiados.

---

## 8) Decisão recomendada

1. **Não** activar Transport “à bruta” com o código legado (IP + password em claro + SSH `tc`).  
2. **Sim** investir em **ONOS primeiro** (API estável, observável), depois **Mininet em VM** alinhada aos intents **ou** regenerar intents a partir da topologia real.  
3. Só então **reintroduzir** a chamada no fluxo NASP com **feature flag** e **duas fases** (staging → produção de protótipo).  
4. Manter **TriSLA** em modo “dois domínios” até o *gate* F ser passado — coerente com PROMPT_15.1.

---

## 9) Critério final (respostas obrigatórias)

```text
EXISTEM ARTEFATOS SUFICIENTES PARA ATIVAR O TRANSPORT? NÃO
  (há lógica parcial e documentação; faltam manifests, topologia Mininet,
   parametrização segura e integração activa no fluxo)

ONOS É VIÁVEL NO AMBIENTE ATUAL? SIM
  (viável com projecto de deploy VM ou Kubernetes + secrets + networking)

MININET É VIÁVEL NO AMBIENTE ATUAL? NÃO
  (no snapshot congelado não há Mininet nem política/pods privilegiados;
   é viável numa fase seguinte com VM/nó dedicado ou contentores privilegiados
   aprovados — ver Fases A–C)

QUAL É O PLANO CORRETO DE ATIVAÇÃO?
  Pré-requisitos (rede + secrets) → ONOS operacional e testado por REST
  → Mininet (ou equivalente) com DPIDs alinhados → integração NASP por env/flag
  → métricas → gate final; só depois fechar o terceiro domínio para o TriSLA.
```

---

**Fim do documento PROMPT_16.3** — *não executa deploy; apenas define o plano para a etapa seguinte.*
