# AUDITORIA PROMPT_14.1 — NASP RAN ALIGNMENT (OAI + My5G-RANTester + Free5GC)

## Escopo e metodo

- Auditoria somente leitura (sem deploy, sem alteracao de codigo/cluster).
- Fontes: repositorio `NASP`, manifests/charts/scripts do NASP, estado real do cluster Kubernetes.

## 1) Arquitetura oficial do NASP (evidencias)

### 1.1 O que o README declara

- `NASP/README.md` cita explicitamente:
  - uso de **OpenAirInterface** para modulos RAN;
  - uso de **My5G-RANTester** para simulacao/geracao no dominio RAN;
  - uso de **Free5GC** para Core.

### 1.2 O que o repositorio realmente entrega em artefatos de deploy

- Estrutura de `NASP/helm_charts` contem:
  - Core NFs (`amf`, `smf`, `upf`, `nrf`, etc.);
  - `rantester`;
  - **nao** contem chart `oai`/`openair`.
- Caminhos internos de dados/servicos apontam para:
  - `RNFs = ["rantester"]` em `nasp/src/services/helm_deployments.py`;
  - `nsst_ran.json` com paths inconsistentes (`../helm_charts/ran/rantester`), mas sem diretório `helm_charts/ran`.
- O chart de `rantester` usa imagem:
  - `baleeiro17/my5grantester:1.0.1` (`helm_charts/rantester/values.yaml`).

Conclusao estrutural do repo:

- Core: claramente **Free5GC**.
- RAN no plano de deploy atual do NASP: **My5G-RANTester** (como bloco RAN/UE simulado).
- OAI aparece como intencao arquitetural no README, mas **nao aparece como chart operacional direto** no snapshot auditado.

## 2) Estado atual do cluster (evidencias)

### 2.1 Core

- Pods `free5gc-*` ativos no namespace `ns-1274485`:
  - `amf`, `ausf`, `nrf`, `nssf`, `pcf`, `smf`, `udm`, `udr`, `upf`, `webui`.

### 2.2 RAN / trafego

- Encontrados:
  - `rantester-0` (namespace `ns-1274485`) Running;
  - `ran-rantester-grafana-*` (namespace `ran-test`) Running;
  - `ueransim-singlepod-*` (namespace `ueransim`) Running;
  - `srsenb-*` (namespace `srsran`) Running.
- Nao encontrado:
  - pod/servico com nome `oai`, `openair`, `openairinterface`.

### 2.3 Servicos RAN relacionados

- `rantester-service` em `ns-1274485`;
- `ueransim-gnb` em `ueransim`;
- `srsenb` em `srsran`.

## 3) Comparacao NASP vs ambiente atual

| Componente | NASP esperado (por artefatos) | Cluster atual | Status |
| ---------- | ----------------------------- | ------------- | ------ |
| RAN        | RANTester (deploy), OAI (README conceitual) | `srsenb` + `UERANSIM` + `rantester` | Divergente/misto |
| Core       | Free5GC                       | Free5GC (`ns-1274485`) | Alinhado |
| Trafego    | My5G-RANTester                | `rantester-0` ativo | Alinhado parcial |
| Telemetria | Prometheus                    | stack Prometheus ativa | Alinhado |

## 4) Divergencias e lacunas

1. **Divergencia de pilha RAN**:
   - ambiente roda `srsenb`/`UERANSIM` fora do fluxo declarativo principal do NASP;
   - repo NASP operacionaliza `rantester`, nao um chart OAI explicito.
2. **Lacuna de OAI operacional**:
   - inexistencia de artefato claro de deploy OAI em `helm_charts`.
3. **Inconsistencia de paths internos NASP**:
   - referencias a `../helm_charts/ran/rantester`, mas pasta `helm_charts/ran` inexistente no snapshot.
4. **Ambiente hibrido**:
   - coexistencia de `srsenb`, `UERANSIM` e `rantester` sem uma trilha unica de RAN oficial operacional.

## 5) Fluxo operacional esperado (NASP) vs real

### Fluxo esperado (objetivo arquitetural)

`RAN (OAI ou bloco RAN oficial) -> Core (Free5GC) -> Trafego (My5G-RANTester) -> Metricas -> Prometheus -> TriSLA`

### Fluxo observado no cluster

`srsenb/UERANSIM + rantester (paralelos) -> Free5GC -> Prometheus/TriSLA`

Conclusao:

- o fluxo real esta **misturado** e sem alinhamento unico com um "RAN oficial NASP" claramente implantado.

## 6) Classificacao (fase 9)

- **CASO C — OAI nao e usado no ambiente atual (como stack operacional principal)**.

Justificativa:

- sem pods/servicos OAI no cluster;
- sem chart OAI direto no caminho de deploy auditado;
- RAN ativa atual baseada em `srsenb`/`UERANSIM` + `rantester`.

## 7) Respostas finais (criterio do prompt)

### QUAL E A PILHA RAN CORRETA PARA O NASP?

- Pelo repositorio auditado, a pilha operacional efetivamente entregue e:
  - **Free5GC + My5G-RANTester** (com RAN modelada no fluxo de templates/servicos),
  - enquanto **OAI aparece como referencia arquitetural** no README, nao como deploy direto comprovado no snapshot atual.

### O AMBIENTE ATUAL ESTA ALINHADO? (SIM/NAO)

- **NAO**.

### O QUE PRECISA SER FEITO?

1. Definir SSOT da pilha RAN alvo (unica): `OAI` **ou** `srsRAN/UERANSIM`, sem mistura operacional.
2. Se a decisao for OAI, introduzir/validar artefatos de deploy OAI reais no NASP (chart/manifests) antes de qualquer nova correcao de telemetria.
3. Se a decisao for manter srsRAN, atualizar o NASP para refletir oficialmente essa escolha (remover ambiguidade OAI vs srsRAN nos artefatos operacionais).
4. Depois do alinhamento arquitetural, executar ativacao RAN e somente entao retomar PRB/telemetria.
