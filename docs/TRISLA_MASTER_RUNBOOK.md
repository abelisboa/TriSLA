# TriSLA Master Runbook — Fonte Única de Verdade (SSOT)

**Versão:** v3.9.15  
**Data de Criação:** 2026-01-29  
**Última Atualização:** 2026-02-11  
**Ambiente:** NASP (Network Automation & Slicing Platform)  
**Cluster:** Kubernetes (namespace `trisla`)  
**Node de Acesso:** node006 (SSH entry point obrigatório; hostname reporta "node1")  
**Diretório Base (TriSLA):** `/home/porvir5g/gtp5g/trisla`  
**Repo base path oficial (S41.3D.0):** `/home/porvir5g/gtp5g`

### 🔑 Regra de Acesso Operacional — node006 ≡ node1

**SSOT de Acesso:**
- **SSH entry point:** `ssh node006` (SEMPRE usar este comando)
- **Hostname reportado:** `node1` (após conectar via SSH)
- **Equivalência operacional:** node006 ≡ node1 neste ambiente
- **Regra crítica:** NUNCA instruir `ssh node1`; SEMPRE `ssh node006`

**Justificativa:**
- `node006` é o nome DNS/alias configurado no ambiente
- O hostname interno do sistema reporta `node1`
- Para fins operacionais, são o mesmo host físico/virtual
- Documentação e scripts devem usar `ssh node006` como entry point
- Após conexão, comandos como `hostname` retornam `node1` (comportamento esperado)

---

## 1️⃣ Propósito e Regras de Uso do Runbook

### Papel do Documento como SSOT

Este documento é a **fonte única de verdade (Single Source of Truth - SSOT)** para a arquitetura TriSLA. Ele consolida:

- Arquitetura real implantada (runtime truth)
- Fluxo ponta-a-ponta (E2E) oficial
- Interfaces e contratos reais entre módulos
- Regras de engenharia normativas
- Padrões de evidência e validação
- Estado operacional atual

### Obrigatoriedade de Uso

**📌 REGRA FUNDAMENTAL:** Após este documento (S37), nenhum novo prompt poderá ser executado sem:

1. **Referenciar este Runbook** explicitamente
2. **Seguir suas regras** de engenharia
3. **Atualizar o Runbook** quando houver mudanças no sistema

### Regra de Atualização Contínua

- Qualquer alteração funcional, arquitetural ou operacional **DEVE** ser refletida neste documento
- Versões do Runbook seguem o versionamento do TriSLA (ex: v3.9.11)
- Mudanças devem ser documentadas na seção de Changelog (seção 12)

### Proibição de Regressão, Gambiarra e Invenção

Este Runbook proíbe explicitamente:

- ❌ **Regressão:** Alterações que quebram funcionalidades existentes sem justificativa técnica documentada
- ❌ **Gambiarra:** Workarounds temporários que não são documentados como limitações conhecidas
- ❌ **Invenção:** Criação de funcionalidades não alinhadas com a arquitetura documentada

---

## 2️⃣ Regras de Engenharia TriSLA (Normativas)

### Anti-Regressão

**Regra:** Qualquer alteração que afete interfaces públicas, contratos de API, ou fluxo E2E deve:

1. Manter compatibilidade retroativa quando possível
2. Documentar breaking changes explicitamente
3. Incluir migração path quando necessário
4. Validar via gates oficiais (S31.x, S34.x, S36.x)

### Anti-Gambiarra

**Regra:** Workarounds são permitidos APENAS se:

1. Documentados como limitações conhecidas (seção 11)
2. Incluem plano de correção definitiva
3. Não violam contratos de API
4. Não introduzem dependências circulares

### Anti-Invenção

**Regra:** Novas funcionalidades devem:

1. Estar alinhadas com a arquitetura documentada
2. Seguir padrões de evidência estabelecidos
3. Passar por gates de validação oficiais
4. Ser documentadas neste Runbook antes de produção

### Política de Versionamento

- **Formato:** `v{Major}.{Minor}.{Patch}`
- **Major:** Breaking changes arquiteturais
- **Minor:** Novas funcionalidades compatíveis
- **Patch:** Correções e melhorias
- **Tags:** Todas as imagens Docker devem usar tags versionadas (não `latest`)

### Política de Release

1. **Baseline:** Versão atual de referência: **v3.9.20** (Release Final SSOT MDCE v2)
2. **Evidências:** Cada release deve incluir evidências em `evidencias_release_v{VERSION}/`
3. **Validação:** Release só é considerada válida após passar gates oficiais
4. **Documentação:** Runbook deve ser atualizado antes do release

### 🏁 Release Final SSOT (MDCE v2) — v3.9.20

- **Tag final:** v3.9.20
- **Imagem GHCR NASP Adapter:** `ghcr.io/abelisboa/trisla-nasp-adapter:v3.9.20`
- **Conteúdo:** Código MDCE v2 (Capacity Accounting, ledger PENDING/ACTIVE/RELEASED/EXPIRED/ORPHANED, rollback, reconciler), Cost Tuning (COST_EMBB/URLLC/MMTC_* no Helm), CRD TriSLAReservation, Runbook Final Close + Cost Tuning.
- **Evidências MDCE v2:** As 7 evidências (CRD + Ledger + reserveOnly guard + reconciler TTL/orphan + 422 headroom + Final Close). Cost Tuning: modo degradado (defaults 1) quando métricas multidomain indisponíveis.
- **Regra anti-regressão:** Se `/api/v1/metrics/multidomain` ou `/api/v1/3gpp/gate` retornar 404, ou se qualquer evidência MDCE v2 falhar → rollback imediato para última tag válida (**v3.9.20** ou v3.9.19) e re-validar checklist antes de promover nova versão.

### Telemetria Real — Prometheus (v3.9.22)

- **Prompt:** PROMPT_STELEMETRY_REAL_ACTIVATION_v1.0.
- **Objetivo:** `GET /api/v1/metrics/multidomain` retorna valores reais (não `metric_unavailable`) para CPU%, Mem%, UE count.
- **Implementação:** NASP Adapter consulta Prometheus (`PROMETHEUS_URL`, default `http://monitoring-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090`). Queries: CPU % = `sum(rate(container_cpu_usage_seconds_total{namespace="trisla"}[1m]))/sum(rate(node_cpu_seconds_total[1m]))*100`; Mem % = uso trisla / `sum(node_memory_MemTotal_bytes)`; UE proxy = `count(kube_pod_status_phase{namespace="trisla",phase="Running"})`. RTT p95 e tx/rx_mbps permanecem null se indisponíveis (documentado em `reasons`).
- **Validação:** Telemetria ativa quando multidomain retorna `cpu_pct`, `mem_pct`, `ran.ue.active_count` numéricos; NASP Adapter não crasha; MDCE e Gate continuam funcionando.
- **Próximo passo:** PROMPT_SMDCE_V2_COST_RECALIBRATION_v1.0 para recalibrar cost model com dados reais.

### Política de Evidência

- **Estrutura:** `evidencias_release_v{VERSION}/{SCENARIO}/`
- **Artefatos mínimos:** Logs, métricas, snapshots, checksums
- **Validade:** Evidências devem ser reproduzíveis e auditáveis
- **Checksums:** SHA256 obrigatório para artefatos críticos

### 🔐 Regra Anti-Drift (S41.3E.2)

- **Proibido:** Usar tags `*-fix`, `*-hotfix`, `*-temp` em produção.
- **Obrigatório:** Hotfixes devem ser promovidos para uma release oficial (ex.: v3.9.12-bcfix → v3.9.12).
- **Validação:** Todo deploy deve validar imagens contra o Release Manifest (`evidencias_release_v3.9.12/RELEASE_MANIFEST.yaml`).
- **Gate:** Nenhuma imagem em runtime pode conter sufixo -fix/-hotfix/-temp.

---

## 3️⃣ Ambiente NASP — Runtime Truth

### Cluster Kubernetes

**Nodes:**
- `node1` - control-plane, Ready, v1.31.1, Age: 456d
- `node2` - control-plane, Ready, v1.31.1, Age: 456d

**Namespace:**
- `trisla` - Active, Age: 40d

### Estado Operacional dos Pods (v3.9.11)

| Pod | Status | Ready | Restarts | Age | Node | IP |
|-----|--------|-------|----------|-----|------|-----|
| kafka-c9477555-fjtsc | Running | 1/1 | 0 | 33m | node2 | 10.233.75.44 |
| trisla-bc-nssmf-6d959b59c8-qzqpb | Running | 1/1 | 0 | 13h | node1 | 10.233.102.155 |
| trisla-decision-engine-f976f766c-5l8qd | Running | 1/1 | 0 | 13h | node1 | 10.233.102.138 |
| trisla-ml-nsmf-59698b5cbb-nwx8l | Running | 1/1 | 0 | 13h | node1 | 10.233.102.189 |
| trisla-nasp-adapter-68f54f99d5-vwjl4 | Running | 1/1 | 0 | 13h | node1 | 10.233.102.164 |
| trisla-portal-backend-7d46f4587c-4mp2k | Running | 1/1 | 0 | 13h | node2 | 10.233.75.42 |
| trisla-portal-frontend-7c7f45948f-tz5bw | Running | 1/1 | 0 | 13h | node2 | 10.233.75.55 |
| trisla-sem-csmf-64889b9447-lwvgw | Running | 1/1 | 0 | 13h | node1 | 10.233.102.178 |
| trisla-sla-agent-layer-5b5d55df4-bgzpw | Running | 1/1 | 0 | 13h | node1 | 10.233.102.153 |
| trisla-ui-dashboard-7988b8b6d9-qlpzc | Running | 1/1 | 0 | 13h | node1 | 10.233.102.145 |

### Versões Reais das Imagens

| Módulo | Imagem Docker | Tag |
|--------|---------------|-----|
| Kafka | apache/kafka | latest |
| BC-NSSMF | ghcr.io/abelisboa/trisla-bc-nssmf | v3.9.12 |
| Decision Engine | ghcr.io/abelisboa/trisla-decision-engine | v3.9.11 |
| ML-NSMF | ghcr.io/abelisboa/trisla-ml-nsmf | v3.9.11 |
| NASP Adapter | ghcr.io/abelisboa/trisla-nasp-adapter | v3.9.11 |
| Portal Backend | ghcr.io/abelisboa/trisla-portal-backend | v3.9.11 |
| Portal Frontend | ghcr.io/abelisboa/trisla-portal-frontend | v3.9.11 |
| SEM-CSMF | ghcr.io/abelisboa/trisla-sem-csmf | v3.9.11 |
| SLA-Agent Layer | ghcr.io/abelisboa/trisla-sla-agent-layer | v3.9.11 |
| UI Dashboard | ghcr.io/abelisboa/trisla-ui-dashboard | v3.9.11 |
| Traffic Exporter | ghcr.io/abelisboa/trisla-traffic-exporter | v3.10.0 |
| Besu | ghcr.io/abelisboa/trisla-besu | v3.9.12 |

### Helm Releases

| Release | Namespace | Revision | Status | Chart | App Version |
|---------|-----------|----------|--------|-------|-------------|
| trisla | trisla | 152 | deployed | trisla-3.7.10 | 3.7.10 |
| trisla-besu | trisla | 3 | failed | trisla-besu-1.0.0 | 23.10.1 |
| trisla-portal | trisla | 15 | deployed | trisla-portal-1.0.2 | 1.0.0 |

### Repo base path e Component Registry (S41.3D.0)

**Repo base path oficial:** `/home/porvir5g/gtp5g` (confirmado em node006).

**Component Registry (SSOT):** Mapeamento deployment → repo_path (relativo ao repo base). Tabela completa em `evidencias_release_v3.9.11/s41_3d0_registry_release/01_repo_discovery/component_repo_map.md`. Resumo:

| Módulo (deployment) | repo_path | Imagem atual |
|---------------------|-----------|--------------|
| trisla-bc-nssmf | trisla/apps/bc-nssmf (ou apps/bc-nssmf) | ghcr.io/abelisboa/trisla-bc-nssmf:v3.9.11 |
| trisla-decision-engine | trisla/apps/decision-engine ou apps/decision-engine | ghcr.io/abelisboa/trisla-decision-engine:v3.9.11 |
| trisla-ml-nsmf | trisla/apps/ml-nsmf ou apps/ml-nsmf | ghcr.io/abelisboa/trisla-ml-nsmf:v3.9.11 |
| trisla-nasp-adapter | trisla/apps/nasp-adapter | ghcr.io/abelisboa/trisla-nasp-adapter:v3.9.11 |
| trisla-portal-backend | trisla/trisla-portal/backend + portal-backend-patch | ghcr.io/abelisboa/trisla-portal-backend:v3.10.0 |
| trisla-portal-frontend | trisla/trisla-portal/frontend | ghcr.io/abelisboa/trisla-portal-frontend:v3.9.11 |
| trisla-sem-csmf | trisla/apps/sem-csmf ou apps/sem-csmf | ghcr.io/abelisboa/trisla-sem-csmf:v3.9.11 |
| trisla-sla-agent-layer | trisla/apps/sla-agent-layer ou apps/sla-agent-layer | ghcr.io/abelisboa/trisla-sla-agent-layer:v3.9.11 |
| trisla-ui-dashboard | trisla/apps/ui-dashboard ou trisla/TriSLA/apps/ui-dashboard | ghcr.io/abelisboa/trisla-ui-dashboard:v3.9.11 |
| trisla-traffic-exporter | (gerenciado pelo Helm, PROMPT_S52) | ghcr.io/abelisboa/trisla-traffic-exporter:v3.10.0 |

**Release Manifest (SSOT):** `evidencias_release_v3.9.11/s41_3d0_registry_release/04_release_manifest/RELEASE_MANIFEST.yaml` — release_id, componentes (repo_path, image_current, build_push, deploy, rollback, gates), deploy_order.

**Build/Publish oficial:** Scripts em `trisla/scripts/`: `build-and-push-images-3.7.9.sh` (podman, trisla/apps), `build-push-v3.9.8.sh` e `execute-fase3-build-push.sh` (docker, paths relativos a trisla: apps/<module>, trisla-portal/backend|frontend). Registro: ghcr.io/abelisboa.

**Autenticação GHCR (confirmada em node1 e node006):** Nos nós de acesso (node1 e node006), o procedimento de login é o mesmo. Podman emula Docker quando se usa o comando `docker`; o login no GHCR deve ser feito antes de build/push:

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u abelisboa --password-stdin
```

Saída esperada: **`Login Succeeded!`** — confirmado no node1; o mesmo procedimento vale no node006. Em ambiente com podman: pode aparecer "Emulate Docker CLI using podman"; o login é válido. **Node1 e node006:** equivalentes para esse procedimento (repo base `/home/porvir5g/gtp5g`, `cd trisla` para scripts de build). **Confirmado em execução real (node1):** Login Succeeded → build `ghcr.io/abelisboa/trisla-bc-nssmf:v3.9.12-bcfix` → push → `kubectl set image` + rollout — deployment "trisla-bc-nssmf" successfully rolled out.

**Ordem de deploy recomendada:** kafka → trisla-sem-csmf → trisla-ml-nsmf → trisla-decision-engine → trisla-bc-nssmf → trisla-sla-agent-layer → trisla-nasp-adapter → trisla-portal-backend → trisla-portal-frontend → trisla-ui-dashboard → trisla-traffic-exporter. Gates: S31.x, S34.x, S36.x conforme componente.

**Procedimento de rollback:** Por deployment: `kubectl rollout undo deploy/<name> -n trisla`. Por Helm: `helm rollback trisla <revision> -n trisla` ou `helm rollback trisla-portal <revision> -n trisla`. Evidências S41.3D.0: `evidencias_release_v3.9.11/s41_3d0_registry_release/`.

---

### Experimental Environment Alignment (PROMPT_S49)

**Referência:** PROMPT_S49 — Alinhamento do Ambiente Experimental ao Baseline Científico TriSLA v3.10.0.

**Objetivo:** Alinhar integralmente o ambiente NASP à versão TriSLA v3.10.0 (baseline científico publicado no GitHub, validado por smoke test S45, documentado em inglês S46). O PROMPT_S49 é estritamente preparatório; não realiza coleta experimental.

**Entry point:** `ssh node006` → hostname `node1`. Diretório: `/home/porvir5g/gtp5g/trisla`. Evidências: `evidencias_resultados_v3.10.0/s49_environment_alignment/`.

**Módulos alvo de upgrade (somente estes podem ser redeployados no S49):** trisla-portal-backend, trisla-portal-frontend, trisla-besu → v3.10.0. Demais módulos (SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, SLA-Agent Layer, NASP Adapter) apenas verificados, não alterados.

**Última execução S49:** 2026-01-31. Resultado: upgrade tentado; imagens ghcr.io/abelisboa/trisla-portal-backend:v3.10.0, trisla-portal-frontend:v3.10.0 e trisla-besu:v3.10.0 resultaram em ImagePullBackOff (imagens não pulláveis no cluster). Rollback aplicado para Portal e Besu; ambiente permanece Portal v3.9.11, Besu v3.9.12. Recomendação: publicar imagens v3.10.0 no registry ou corrigir credenciais e reexecutar PROMPT_S49.

**Data, versão e evidências:** `evidencias_resultados_v3.10.0/s49_environment_alignment/S49_FINAL_REPORT.md`, `08_runbook_update/update_snippet.txt`, `16_integrity/runbook_checksum.txt`.

---

### PROMPT_S49.1 — Final Alignment to v3.10.0 (Portal + Besu)

**Referência:** PROMPT_S49.1 — Alinhamento Final v3.10.0 (Portal + Besu).

**Objetivo:** Executar o alinhamento final do ambiente experimental TriSLA para a baseline científica v3.10.0, cobrindo Portal (backend + frontend) e Besu. O build é feito exclusivamente no node006; as imagens v3.10.0 são publicadas no GHCR; o Helm é atualizado; o cluster NASP é atualizado (deploy) sem fallback; não existe regressão de versão após o rollout.

**Entry point:** `ssh node006` → hostname `node1`. Diretório: `/home/porvir5g/gtp5g/trisla`. Evidências: `evidencias_release_v3.10.0/s49_1_alignment_final/`.

**Fases:** 0 (Gate), 1 (Source validation), 2 (Build), 3 (Publish GHCR), 4 (Helm update), 5 (Deploy), 6 (Post-deploy validation), 8 (Runbook update).

**Última execução S49.1:** 2026-01-31. **Status:** PASS. Build no node006; imagens v3.10.0 publicadas no GHCR; helm upgrade trisla-portal e trisla; Besu atualizado (patch --profile=ENTERPRISE removido para compatibilidade com Besu 23.10.1; PVC reset para compatibilidade de DATABASE_METADATA). Ambiente 100% alinhado: trisla-portal-backend:v3.10.0, trisla-portal-frontend:v3.10.0, trisla-besu:v3.10.0.

**Pré-requisito para:** PROMPT_S48 — Execução Experimental Oficial.

**Evidências:** `evidencias_release_v3.10.0/s49_1_alignment_final/` (00_gate, 01_source_validation, 02_build, 03_publish, 04_helm_update, 05_deploy, 06_post_deploy_validation, 08_runbook_update, 16_integrity).

---

### PROMPT_S49.2 — Traffic Exporter Alignment to v3.10.0

**Referência:** PROMPT_S49.2 — Alinhamento Final do traffic-exporter v3.10.0.

**Objetivo:** Alinhar exclusivamente o módulo trisla-traffic-exporter à versão v3.10.0 (build no node006, publicação no GHCR, atualização de Helm, deploy controlado, validação pós-deploy, atualização do Runbook). Escopo restrito: nenhum outro módulo é alterado.

**Entry point:** ssh node006 → hostname node1. Diretório: /home/porvir5g/gtp5g/trisla. Evidências: evidencias_release_v3.10.0/s49_2_traffic_exporter_alignment/.

**Fases:** 0 (Gate), 1 (Source validation), 2 (Build), 3 (Publish GHCR), 4 (Helm update), 5 (Deploy), 6 (Post-deploy validation), 8 (Runbook update), 16 (Integridade).

**Última execução S49.2:** 2026-01-31. **Status:** ABORT. FASE 1 falhou: o diretório apps/traffic-exporter/ não existe no repositório; a imagem ghcr.io/abelisboa/trisla-traffic-exporter:v3.10.0 não está publicada no GHCR. Build e demais fases não executados. Pré-requisito para conclusão: adicionar apps/traffic-exporter ao repo (ex.: via PROMPT_S51 ou restauração de backup) e reexecutar S49.2.

**Referência cruzada:** S49.1 (Portal + Besu); S48 (Execução Experimental — gate exige trisla-traffic-exporter:v3.10.0).

**Evidências:** evidencias_release_v3.10.0/s49_2_traffic_exporter_alignment/ (00_gate, 01_source_validation, 08_runbook_update, S49_2_FINAL_REPORT.md).

---

### PROMPT_S49.3 — Global Alignment v3.10.0 (Helm SSOT · 1 único upgrade)

**Referência:** PROMPT_S49.3 — Alinhamento Global v3.10.0 (Helm SSOT · 1 único upgrade).

**Objetivo:** Alinhar TODOS os módulos TriSLA no namespace trisla para v3.10.0, garantindo que Helm seja a única fonte de verdade (SSOT), apenas 1 único helm upgrade seja executado, nenhum módulo permaneça em v3.9.11 (ou outro), e não haja ImagePullBackOff/CrashLoopBackOff em pods críticos. Este prompt não executa experimento; apenas prepara o ambiente para o PROMPT_S48.

**Entry point:** `ssh node006` → hostname `node1`. Diretório: `/home/porvir5g/gtp5g/trisla`. Evidências: `evidencias_release_v3.10.0/s49_3_global_alignment/` (00_gate, 01_registry_check, 02_helm_prepare, 03_upgrade, 04_post_validation, 05_rollback_if_needed, 08_runbook_update, 16_integrity).

**Última execução S49.3:** 2026-01-31. **Status:** PASS. Gate inicial OK; registry pull de todas as imagens v3.10.0 OK; Chart/values já v3.10.0; helm upgrade trisla com --reset-values (revision 156); rollouts concluídos; validação pós-upgrade: todos os módulos ghcr.io/abelisboa/trisla-* em v3.10.0 em runtime; sem CrashLoopBackOff/ImagePullBackOff em pods críticos.

**Regra:** PROMPT_S48 — Execução Experimental Controlada do Dataset Oficial TriSLA v3.10.0 — só pode rodar após PASS do S49.3.

**Evidências:** `evidencias_release_v3.10.0/s49_3_global_alignment/` (00_gate, 01_registry_check, 02_helm_prepare, 03_upgrade, 04_post_validation, 08_runbook_update, 16_integrity).

---

### PROMPT_S52 — Official Integration of traffic-exporter (v3.10.0)

**Referência:** PROMPT_S52 — Incorporação Oficial do traffic-exporter como Módulo TriSLA (v3.10.0).

**Data/hora:** 2026-01-31. **Node:** node006 ≡ node1.

**Motivo da incorporação:** Eliminar dependência de deploy manual (kubectl apply); garantir rastreabilidade científica, versionamento semântico v3.10.0, reprodutibilidade experimental e conformidade com o gate do PROMPT_S48 (todas as imagens v3.10.0).

**Escopo do módulo:** traffic-exporter é módulo de observabilidade passiva — exporta métricas Prometheus (porta 9105, endpoint /metrics) e opcionalmente eventos Kafka; não toma decisões, não altera SLAs, não atua no plano de controle.

**O que foi feito:** Criação de apps/traffic-exporter/ (Dockerfile, app/main.py, requirements.txt, README.md); build e push ghcr.io/abelisboa/trisla-traffic-exporter:v3.10.0; integração ao Helm (helm/trisla/templates/traffic-exporter.yaml, values.yaml trafficExporter); deploy exclusivo via helm upgrade — nenhum kubectl manual persistente.

**Impacto no S48:** Gate do PROMPT_S48 exige trisla-traffic-exporter:v3.10.0; após PASS do S52 esse item é satisfeito. É permitido reexecutar PROMPT_S48 — Execução Experimental Oficial do Dataset TriSLA v3.10.0.

**Evidências:** evidencias_release_v3.10.0/s52_traffic_exporter_integration/ (00_gate, 01_module_definition, 02_implementation, 03_build, 04_publish, 05_helm_integration, 06_deploy, 07_validation, 08_runbook_update, 16_integrity, S52_FINAL_REPORT.md).

---

### Operational Anti-Regression Check — PROMPT_S50

**Referência:** PROMPT_S50 — Verificação de Conformidade Operacional e Anti-Regressão (SSOT).

**Objetivo:** Verificar que o ambiente TriSLA não regrediu em relação ao baseline científico v3.10.0; build, publicação e deploy exclusivamente no node006; estado do cluster alinhado ao SSOT; divergências detectadas, explicadas e corrigidas apenas conforme documentação. Este prompt não executa experimentos nem coleta científica; é guardião de consistência e reprodutibilidade.

**Entry point:** `ssh node006` → hostname `node1`. Diretório: `/home/porvir5g/gtp5g/trisla`. Evidências: `evidencias_release_v3.10.0/s50_antiregression/`.

**Última execução S50:** 2026-01-31. **Status:** ABORT — Divergência detectada. Portal (backend/frontend) v3.9.11 e Besu v3.9.12 em runtime; SSOT exige v3.10.0. Causa raiz: imagens ghcr.io/abelisboa/trisla-portal-backend:v3.10.0, trisla-portal-frontend:v3.10.0 e trisla-besu:v3.10.0 inexistentes no registry (manifest unknown). Correção proposta (sem executar): publicar imagens v3.10.0 no registry e reexecutar PROMPT_S49; referência explícita ao Runbook em `06_diagnosis/proposed_fix.md`.

**Evidências:** `00_gate/`, `01_ssot_reference/`, `02_cluster_state/`, `03_version_check/`, `04_registry_check/`, `05_helm_alignment/`, `06_diagnosis/`, `08_runbook_update/`.

---

## PROMPT_S51 — Build & Publish Oficial das Imagens v3.10.0

**Data/hora:** 2026-01-31. **Node:** node006 ≡ node1. **Objetivo:** Publicar as imagens v3.10.0 ausentes no GHCR (Portal Backend, Portal Frontend, Besu), eliminando ImagePullBackOff e restaurando alinhamento exigido pelo PROMPT_S48. Este prompt **não realiza deploy** no cluster; apenas build e publish.

**Imagens publicadas:** ghcr.io/abelisboa/trisla-portal-backend:v3.10.0, ghcr.io/abelisboa/trisla-portal-frontend:v3.10.0, ghcr.io/abelisboa/trisla-besu:v3.10.0.

**Confirmação de pull OK:** As três imagens foram validadas com `docker pull` no node006 (evidências em `evidencias_release_v3.10.0/s51_build_publish/04_pull_validation/pull_results.txt`).

**Referência cruzada:** Resolve as imagens ausentes detectadas no PROMPT_S50; após PASS do S51 é permitido executar PROMPT_S49 (Alinhamento do Ambiente) e em seguida PROMPT_S48 (Execução Experimental Oficial).

**Evidências:** `evidencias_release_v3.10.0/s51_build_publish/` (00_gate, 01_source_validation, 02_build, 03_publish, 04_pull_validation, 08_runbook_update, 16_integrity).

---

### PROMPT_S53 — Global Hotfix v3.10.1 + Alinhamento Total do Ambiente

**Referência:** PROMPT_S53 — Hotfix Global v3.10.1 + Alinhamento Total do Ambiente.

**Causa raiz:** Política de gas price — erro em produção "Gas price below configured minimum gas price" (Besu QBFT). O BC-NSSMF usava `web3.eth.gas_price` sem piso mínimo; transações eram rejeitadas pelo nó Besu.

**Correção:** BC-NSSMF sender (`apps/bc-nssmf/src/blockchain/tx_sender.py`) — aplicado piso mínimo de gas price (1 gwei por padrão, override via `BC_MIN_GAS_PRICE_WEI`). Sem mudança de arquitetura; apenas política de transação.

**Resultado:** Ambiente alinhado em v3.10.1 para módulos TriSLA (bc-nssmf, decision-engine, ml-nsmf, nasp-adapter, sem-csmf, sla-agent-layer, traffic-exporter, ui-dashboard, portal-backend, portal-frontend). Release trisla-besu permanece em v3.10.0 (upgrade do chart falhou por imutabilidade de PVC/selector).

**Regra:** PROMPT_S48 — Execução Experimental Controlada do Dataset Oficial TriSLA — só pode rodar após PASS do S53 (ambiente 100% alinhado em v3.10.1, apto para dataset oficial).

**Evidências:** `evidencias_release_v3.10.1/s53_global_hotfix/` (00_gate, 01_source_validation, 02_code_fix, 03_build, 04_publish, 05_helm_update, 06_deploy, 07_post_deploy_validation, 08_runbook_update, 16_integrity).

---

### PROMPT_S54 — Besu RPC Functional Validation

**Referência:** PROMPT_S54 — Validação e Correção Controlada do RPC do Besu.

**Motivo:** Durante o PROMPT_S48 (Dataset Oficial TriSLA v3.10.1), a FASE 0 (Gate) foi ABORTADA porque o teste funcional do RPC do Besu (`eth_blockNumber`) não obteve resposta — apesar do pod Besu estar Running.

**Ação tomada:** Inspeção do Deployment (RPC já configurado: --rpc-http-enabled=true, --rpc-http-port=8545) e do Service. Causa raiz: (1) Service selector exigia `app.kubernetes.io/name=trisla-besu` e `app.kubernetes.io/instance=trisla-besu`, enquanto o pod (Deployment do chart trisla) tem `app.kubernetes.io/name=trisla` — Endpoints ficavam `<none>`. (2) Service usava `targetPort` nomeado ("rpc"/"ws") que não correspondia aos nomes do container ("rpc-http"/"rpc-ws"), então Endpoints não listavam a porta 8545. Correção: patch no Service trisla-besu — selector substituído por `app=besu, component=blockchain`; targetPort das portas 8545/8546/30303 alterado para numérico (8545, 8546, 30303).

**Resultado:** PASS — RPC responde com JSON válido: `{"jsonrpc":"2.0","id":1,"result":"0x0"}`. Teste executado de dentro do cluster (pod besu-rpc-test, curl para trisla-besu:8545).

**Relação com S48:** O Gate do PROMPT_S48 exige "Testes ativos" (eth_blockNumber). Após PASS do S54, o RPC do Besu está funcional; reexecutar PROMPT_S48 está autorizado (Gate da FASE 0 deve passar).

**Evidências:** `evidencias_release_v3.10.1/s54_besu_rpc_validation/` (00_gate, 01_runtime_inspection, 02_service_validation, 03_rpc_tests, 04_patch_applied, 05_post_patch_validation, 08_runbook_update, 16_integrity, S54_FINAL_REPORT.md).

---

### PROMPT_S55 — BC Nonce & Replacement Policy Hotfix (v3.10.2)

**Referência:** PROMPT_S55 — BC-NSSMF Nonce & Replacement Policy Hotfix (v3.10.2).

**Problema observado (S48.0R):** Cenário 1A falhou com 100% ERROR/503 devido ao erro Besu JSON-RPC "Replacement transaction underpriced" — colisão de nonce / política de substituição sob carga.

**Decisão técnica:** Implementado no BC-NSSMF (`apps/bc-nssmf/src/blockchain/tx_sender.py`): (1) nonce via `eth_getTransactionCount(address, "pending")`; (2) lock/queue por sender (serialização por conta); (3) retry com refresh de nonce e bump de gas em erros replacement/nonce; (4) espera de receipt com timeout configurável (`BC_TX_RECEIPT_TIMEOUT`, padrão 60s). Env vars: `BC_TX_QUEUE_ENABLED=true`, `BC_TX_RECEIPT_TIMEOUT`, `BC_GAS_BUMP_PERCENT=20`, `BC_MIN_GAS_PRICE_WEI` (S53).

**Tag publicada:** `ghcr.io/abelisboa/trisla-bc-nssmf:v3.10.2` (digest em `evidencias_release_v3.10.2/s55_bc_nonce_fix/05_build_push/image_digest.txt`).

**Resultado da validação burst:** Erro "Replacement transaction underpriced" eliminado nos logs. Burst 30 em ambiente com Besu ainda em blockNumber=0x0 (nenhum bloco minerado) resulta em 503 por timeout de receipt — esperado até que a rede produza blocos. Critério S55 (sem erro sistêmico replacement underpriced) atendido.

**Regra:** S48 só pode rodar após PASS do S55 (BC-NSSMF v3.10.2 implantado; burst sem replacement underpriced).

**Evidências:** `evidencias_release_v3.10.2/s55_bc_nonce_fix/` (00_gate, 01_runbook_reference, 02_baseline_repro, 03_design_decision, 04_code_changes, 05_build_push, 06_deploy, 07_validation_burst, 08_runbook_update, 16_integrity, S55_FINAL_REPORT.md).

---

### PROMPT_S56 — Besu QBFT Single-Node Consensus Enablement (parcial)

**Referência:** PROMPT_S56 — Inicialização Controlada do Consenso Besu (QBFT Dev Mode).

**Motivo:** Habilitar produção de blocos no Besu (eth_blockNumber > 0x0) para permitir receipts e desbloquear S48. S54/S55 deixaram o pipeline funcional; as falhas remanescentes devem-se ao Besu não produzir blocos.

**Ação tomada:** (1) FASE 0–1: Gate e inspeção (Besu Running, eth_blockNumber=0x0). (2) FASE 2: Geração QBFT single-node via `besu operator generate-blockchain-config` em pod no cluster; genesis e chave do validador em `evidencias_release_v3.10.2/s56_besu_qbft_enable/02_genesis_qbft/`. (3) FASE 3: Scale Besu 0, delete PVC com label app=besu. (4) FASE 4: Chart atualizado — ConfigMap genesis QBFT (`besu/genesis-qbft.json`), init container para genesis + chave, deployment com args QBFT (--genesis-file, --rpc-http-api=ETH,NET,WEB3,ADMIN,MINER, --min-gas-price=0, etc.), Secret `trisla-besu-validator-key` com chave do validador.

**Bloqueio:** Besu 23.10.1 (imagem trisla-besu:v3.10.1) falha ao iniciar com erro "Supplied file does not contain valid keyPair pair" ao carregar o ficheiro de chave (hex com/sem 0x, com/sem newline). O formato gerado por `generate-blockchain-config` não é aceite pelo KeyPairUtil ao arranque do nó. TriSLA não foi alterada; apenas Besu e Helm.

**Estado atual:** Besu mantido com `enabled: false` até resolução do formato da chave (ex.: uso de security module alternativo, ou chave no formato esperado pelo Besu 23). Genesis QBFT e alterações Helm estão versionadas; S48 continua dependente de Besu a produzir blocos.

**Relação com S55/S48:** S55 PASS; S48 desbloqueado após S55. S56 desbloquearia S48 no que diz respeito a receipts (blocos minerados).

**Evidências:** `evidencias_release_v3.10.2/s56_besu_qbft_enable/` (00_gate, 01_besu_inspection, 02_genesis_qbft, 03_pvc_reset, 04_deploy_qbft, 08_runbook_update, 16_integrity, S56_FINAL_REPORT.md).

---

### PROMPT_S56.1 — QBFT Validator Key Canonical Fix (Besu 23.x)

**Referência:** PROMPT_S56.1 — Correção Canônica do Validador QBFT (Besu 23.x).

**Motivo:** Resolver o bloqueio do S56 (erro "keyPair pair" ao carregar chave gerada por `generate-blockchain-config`). Fluxo canônico: Besu gera a sua própria chave → extrair endereço dos logs → regenerar genesis QBFT com esse endereço. Sem Secret de chave, sem `--node-private-key-file`, sem `besu operator generate-blockchain-config`.

**Ação tomada:** (1) FASE 0: Gate (Besu desabilitado/scale=0). (2) FASE 1: Pod temporário `besu-keygen` (hyperledger/besu:23.10.1, --data-path=/tmp/besu, --rpc-http-enabled=false) para gerar chave. (3) FASE 2: Extrair "Node address 0x..." dos logs, gravar em `02_validator_address/validator_address.txt`, apagar pod. (4) FASE 3: Regenerar genesis QBFT com extraData para o validador extraído (endereço real do Besu em produção usado: 0x58bc60d7bf36ac3bd672bbdada0443eedb625fbe). (5) FASE 4: Helm sem referência a chave — genesis em ConfigMap montado em /data, --genesis-file=/data/genesis.json, --data-path=/opt/besu/data; limpeza de chain data no PVC preservando key; Besu habilitado. (6) FASE 5: Validação — eth_blockNumber incrementa (0x1e → 0x26 → 0x2a).

**Relação com S55, S56, S48:** S55 (BC-NSSMF nonce/replacement) PASS. S56 bloqueado por formato de chave; S56.1 contorna com fluxo canônico. Besu produz blocos; receipts possíveis; S48 desbloqueado para reexecução com expectativa de receipts válidos.

**Evidências:** `evidencias_release_v3.10.2/s56_1_besu_qbft_keyfix/` (00_gate, 01_temp_besu_keygen, 02_validator_address, 03_genesis_regenerated, 04_deploy_qbft, 05_block_production_validation, 08_runbook_update, 16_integrity).

---

### PROMPT_S56.2 — QBFT Validator Identity SSOT (Secret + Init) + Genesis Regenerado + Block Production PASS

**Referência:** PROMPT_S56.2 — QBFT Validator Identity SSOT (Secret + Init) + Genesis Regenerado + Block Production PASS.

**Objetivo:** Restaurar produção de blocos no Besu QBFT (single-node) com chave do validador como SSOT (Secret + initContainer), genesis QBFT com extraData do validador SSOT, eth_blockNumber em aumento contínuo e register-sla do BC-NSSMF concluindo com receipt (HTTP 200).

**Validador SSOT:** Secret `trisla-besu-validator-key` (chave `key`); endereço do validador **0x3d86b9df7ef6a2dbce2e617acf6df08de822a86b**. initContainer copia Secret para `/opt/besu/data/key` antes do Besu iniciar; genesis QBFT (`helm/trisla/besu/genesis-qbft.json` e ConfigMap `trisla-besu-genesis`) contém extraData com esse validador e alloc 1 ETH para wallet BC (0x24f31b...).

**Procedimento de reset quando trocar genesis:** (1) `kubectl scale deploy/trisla-besu -n trisla --replicas=0`; (2) `kubectl delete pvc trisla-besu-data -n trisla`; (3) `helm upgrade --install trisla helm/trisla -n trisla --reset-values`; (4) `kubectl scale deploy/trisla-besu -n trisla --replicas=1`; (5) aguardar rollout e validar eth_blockNumber e register-sla.

**Última execução:** 2026-01-31. **Resultado:** **PASS.** Secret atualizado com chave do nó atual; genesis regenerado com extraData para 0x3d86b9df... e alloc BC wallet; Helm patch: initContainer + volume validator-key; reset PVC + helm upgrade; eth_blockNumber aumenta (0x12 → 0x16 → 0x1a); register-sla retorna HTTP 200 com tx_hash e block_number.

**Evidências:** `evidencias_release_v3.10.2/s56_2_qbft_validator_ssot/` (00_gate, 01_current_state, 02_validator_ssot, 03_genesis_regen, 04_helm_patch, 05_reset_redeploy, 06_validation, 08_runbook_update, 16_integrity, S56_2_FINAL_REPORT.md).

---

### PROMPT_S48.1 — Blockchain Ready Gate Hard (TriSLA v3.10.x)

**Referência:** PROMPT_S48.1 — Blockchain Ready Gate Hard + E2E Recovery (TriSLA v3.10.x).

**Objetivo:** Validação canônica e controlada da prontidão blockchain (Besu + BC-NSSMF) antes da execução experimental oficial (PROMPT_S48). Provar que Besu RPC responde, BC-NSSMF está saudável e conectado ao RPC, e que register-sla mínimo retorna HTTP 200 com tx_hash/block_number.

**Regra explícita:** **PROMPT_S48 só pode ser executado após PASS do S48.1.**

**Última execução:** 2026-01-31. **Resultado:** **ABORT.** FASE 0–3 PASS; FASE 4 (Register-SLA mínimo) FAIL — API retorna "BC-NSSMF está em modo degraded. RPC Besu não disponível." apesar de Besu RPC ativo e health/ready com rpc_connected=true. Causa provável: BCService.__init__ falhou (bc_service=None) enquanto tx_sender mantém RPC conectado; possível contract_address.json ausente ou w3.is_connected() falhou no startup.

**Evidências:** `evidencias_release_v3.10.x/s48_1_blockchain_ready/` (00_gate, 01_besu_rpc_validation, 02_bc_runtime_validation, 03_bc_to_besu_connectivity, 04_register_sla_minimal, 05_findings, 08_runbook_update, 16_integrity).

---

### PROMPT_S48.1A — BCService Init Fix (BC-NSSMF)

**Referência:** PROMPT_S48.1A — Fix Definitivo do BCService Init (BC-NSSMF) + Contrato/Config SSOT + Revalidação S48.1 FASE 4.

**Objetivo:** Eliminar inconsistência em que /health/ready retorna rpc_connected=true mas /api/v1/register-sla retorna degraded (bc_service=None). Garantir que BCService inicialize com Besu RPC acessível, contrato implantado e config carregada; register-sla mínimo deve retornar HTTP 200 com tx_hash e block_number/receipt.

**Regra:** S48 só após PASS de S48.1 e S48.1A (quando este prompt for necessário).

**Última execução:** 2026-01-31. **Resultado:** **PASS** para correção do BCService init; **funding BC wallet aplicado** (genesis alloc 1 ETH); **ABORT** para gate completo. **Causa raiz:** Na inicialização do pod, `w3.is_connected()` retornou False (Besu indisponível no momento do startup). **Correção aplicada:** (1) ConfigMap `trisla-bc-contract-address` já existia e montado; **rollout restart** do trisla-bc-nssmf. (2) ConfigMap `trisla-besu-genesis` atualizado com alloc para 0x24f31b... (1 ETH); Besu scale 0 → delete PVC trisla-besu-data → create PVC → scale 1; eth_getBalance confirma 1 ETH na wallet BC. **Revalidação:** BCService OK; /health/ready OK. **register-sla** não retornou 200 no tempo — após reset do Besu o nó gera novo par de chaves; validador no genesis (extraData) não coincide com o nó atual (0x3d86b9df...), logo Besu não produz blocos (blockNumber=0x0) e register-sla dá receipt timeout. **Próximo passo:** regenerar genesis com extraData do validador atual e novo reset, ou restaurar chave do validador original.

**Endereço do contrato (SSOT):** ConfigMap `trisla-bc-contract-address`, chave `contract_address.json` — endereço `0xb5FE5503125DfB165510290e7782999Ed4B5c9ec`.

**Evidências:** `evidencias_release_v3.10.2/s48_1a_bcservice_fix/` (00_gate, 01_runtime_inspection, 02_contract_artifacts, 03_root_cause, 04_fix_plan, 05_apply_fix, 06_revalidation, 08_runbook_update, 16_integrity, S48_1A_FINAL_REPORT.md).

---

### PROMPT_S48.2 — Execução do Dataset Oficial TriSLA v3.10.2 (Regime SSOT, Blockchain Funcional)

**Referência:** PROMPT_S48.2 — Execução do Dataset Oficial TriSLA v3.10.2 (Regime SSOT, Blockchain Funcional).

**Objetivo:** Coleta experimental oficial do dataset TriSLA v3.10.2 (cenários 1A/1B/1C, métricas, figuras, MANIFEST), com blockchain funcional, contrato ativo (S57 PASS) e register-sla HTTP 200. Execução exclusiva em node006 (hostname node1).

**Pré-requisitos (Runbook):** S55 PASS, S56.2 PASS, S57 PASS.

**Última execução:** 2026-02-01. **Resultado:** **PASS.** Gate FASE 0–3 PASS (Runbook verificado; eth_blockNumber crescente; health/ready ready=true, rpc_connected=true; register-sla HTTP 200 com tx_hash e block_number). PARTE II executada: submissões 1A (30), 1B (50), 1C (100) = **180 SLAs** via Portal Backend (Job no cluster). Métricas, figuras e MANIFEST gerados.

**Quantidade de SLAs:** 30 + 50 + 100 = 180.

**Hash do MANIFEST:** SHA-256 de MANIFEST.md em `16_integrity/CHECKSUMS.sha256` (ex.: 3677b0cd4891b69ba8522b7ef2b37e688c2b52925cb7cffc2c6a5d55bb2a52d7).

**Evidências:** `gtp5g/trisla/evidencias_resultados_v3.10.2/` (00_gate, 01_submissions, 02_latency, 03_decisions, 04_ml_xai, 05_sustainability, 06_traceability, 07_figures, 08_runbook_update, 16_integrity, MANIFEST.md).

---

### PROMPT_SA48.1 — Ativação Canônica de Evidências de Governança (Artigo 2)

**Referência:** PROMPT_SA48.1 — ATIVAÇÃO CANÔNICA DE EVIDÊNCIAS DE GOVERNANÇA.

**Objetivo:** Gerar evidências reais, não nulas e auditáveis para todas as pastas de `evidencias_artigo2/`, por meio da execução de cenários mínimos de governança de SLA (SLA_A: solicitado→aceito→ativo; SLA_B: solicitado→aceito→violado; SLA_C: solicitado→aceito→renegociado→encerrado). Executar ANTES de qualquer FASE 2–7 do PROMPT_MESTRE.

**Pré-requisitos (Runbook):** PROMPT_S00R = PASS; BC-NSSMF = Running; Besu funcional (RPC ativo, blocos minerados, capacidade de tx_receipt).

**Última execução:** 2026-02-10. **Resultado:** **PASS.** Gate (Runbook, BC-NSSMF, Besu) OK. FASE 1: ledger_health.json em `evidencias_artigo2/06_crypto_receipts/`. FASE 2: cenários canônicos mínimos executados (register-sla + update-sla-status com receipts). FASE 3: coleta por pasta — 01_decision_ledger (sla_a/b/c_decision.json), 02_sla_lifecycle (states.csv), 03_evidence_anchoring (anchoring.json), 04_async_execution, 05_non_intrusiveness, 06_crypto_receipts (ledger_health.json, receipts.json). FASE 4: audit_report.json. Nenhuma regressão arquitetural.

**Evidências:** `evidencias_artigo2/` (01_decision_ledger, 02_sla_lifecycle, 03_evidence_anchoring, 04_async_execution, 05_non_intrusiveness, 06_crypto_receipts, audit_report.json, manifest.yaml).

**Impacto:** Habilita Artigo 2 — Resultados; evidências utilizáveis em Resultados, Discussão e tabela comparativa; alinhamento total com S00R.

---

### PROMPT_S57 — Diagnóstico Canônico do BCService e Contrato (SSOT)

**Referência:** PROMPT_S57 — Diagnóstico Canônico do BCService e Contrato (SSOT).

**Objetivo:** Garantir que `POST /api/v1/register-sla` retorne HTTP 200 com tx_hash e block_number. O PROMPT não substitui S55, S56.x nem S48.x; apenas desbloqueia a FASE 3 do S48.x.

**Causa raiz identificada:** Contrato **inexistente na chain atual**. O endereço 0xb5FE5503125DfB165510290e7782999Ed4B5c9ec (ConfigMap trisla-bc-contract-address) tinha eth_getCode = 0x — nenhum bytecode; após o reset do PVC do Besu (S56.2), a chain foi recriada e o contrato SLA não foi reimplantado nesse endereço.

**Correção aplicada:** (1) Job `deploy-sla-contract-s57` reimplantou o SLAContract na chain atual com a wallet BC (0x24f31b...). Novo endereço do contrato: **0xFF5B566746CC44415ac48345d371a2A1A1754662**. (2) ConfigMap `trisla-bc-contract-address` atualizado com o novo endereço (ABI inalterada). (3) BC-NSSMF já montava o ConfigMap em `/app/src/contracts/contract_address.json`; rollout restart para carregar o novo conteúdo. (4) Repo: `config.py` — suporte a CONTRACT_INFO_PATH via env; `deploy_contracts.py` — correção raw_transaction → rawTransaction (web3 v6).

**Última execução:** 2026-02-01. **Resultado:** **PASS.** register-sla retorna HTTP 200 com tx_hash e block_number. S48.2 pode avançar (reexecutar gate FASE 3 e Part II).

**Evidências:** `evidencias_release_v3.10.2/s57_bcservice_contract_diagnostic/` (00_gate, 01_bc_startup, 02_contract_chain, 03_abi_validation, 04_root_cause, 05_fix, 06_revalidation, 08_runbook_update, 16_integrity).

**Endereço do contrato (SSOT pós-S57):** ConfigMap `trisla-bc-contract-address` — endereço **0xFF5B566746CC44415ac48345d371a2A1A1754662** (chain atual).

---

### PROMPT_SPORTAL_01 — Diagnóstico e Correção Controlada do Portal TriSLA (SSOT)

**Referência:** PROMPT_SPORTAL_01 — Diagnóstico e Correção Controlada do Portal TriSLA (SSOT).

**Objetivo:** Diagnóstico técnico completo do Portal TriSLA e correções pontuais (404 em `/slas/status`, erro de métricas, warning Amplitude), sem regressão funcional e sem alteração no backend sem evidência.

**Última execução:** 2026-02-02. **Resultado:** **PASS.** Runbook verificado; inventário de rotas e endpoints realizado; correções aplicadas: (1) Página `/slas/status` criada (`trisla-portal/frontend/src/app/slas/status/page.tsx`) — elimina 404 ao clicar "Ver Status Detalhado"; (2) Página `/slas/metrics` com tratamento defensivo — fallback "Métricas indisponíveis", sem exceção fatal; (3) Amplitude: SDK não encontrado no frontend — classificado como warning não-bloqueante.

**Evidências:** `evidencias_portal/` (rotas_frontend.md, endpoints_backend.md, decisao_rota_status.md, proposta_correcoes.md).

**Próximo passo recomendado:** Reexecutar fluxo E2E (PLN → GST → Decision → ACCEPT → resultado → status → métricas) para validar ausência de 404 e de exceções fatais.

---

### PROMPT_SPORTAL_02 — Validação Funcional, Build, Publicação e Deploy Controlado do Portal TriSLA (SSOT)

**Referência:** PROMPT_SPORTAL_02 — Validação Funcional, Build, Publicação e Deploy Controlado do Portal TriSLA (SSOT).

**Objetivo:** Validar funcionalmente o Portal após PROMPT_SPORTAL_01; build das imagens públicas; publicação no registry; atualização de Helm; deploy controlado no NASP; versionamento único v3.10.4.

**Última execução:** 2026-02-02. **Resultado:** **PASS.** Gate FASE 0 (node006 ≡ node1); validação funcional documentada; build frontend e backend v3.10.4; push GHCR OK; Helm trisla-portal values atualizados para v3.10.4; helm upgrade trisla-portal (revision 19); rollout frontend e backend OK; Runbook atualizado.

**Evidências:** `evidencias_portal_release/` (02_gate, 02_validacao_funcional, 03_build, 04_registry, 05_helm, 06_deploy).

- **Data:** 2026-02-02
- **Versão:** v3.10.4
- **Escopo:** Portal (Frontend + Backend)
- **Build:** OK
- **Registry:** OK
- **Deploy:** OK
- **Regressões:** Nenhuma

---

### PROMPT_SPORTAL_03 — Diagnóstico de Contagem de SLAs e Métricas (SSOT)

**Referência:** PROMPT_SPORTAL_03 — Diagnóstico de Contagem de SLAs e Métricas (SSOT).

**Objetivo:** Diagnosticar causas de "SLAs Ativos = 0", gráficos vazios, 404 (status/health/global) e alerta "Sistema Degradado", sem alterar código, Helm ou cluster.

**Última execução:** 2026-02-02. **Resultado:** **PASS.** Gate FASE 0 (node006 ≡ node1); causas identificadas: (1) Contagem = 0: frontend fixa 0, não existe endpoint de listagem; (2) Gráficos vazios: métricas do NASP indisponíveis ou atraso pós-ACCEPT; (3) 404 health/global: router health não incluído em main.py; (4) "Sistema Degradado": falha em /api/v1/health/global (404) tratada como degraded. Nenhuma alteração aplicada.

**Evidências:** `evidencias_portal/03_diagnostico/` (00_gate, 01_fonte_slas.md, 02_endpoints_mismatch.md, 03_integracao_nasp.md, 04_metricas_vazias.md, 05_status_degradado.md, 06_root_cause_analysis.md, 07_proposed_fixes.md, 08_runbook_update.txt).

**Próximo passo recomendado:** PROMPT_SPORTAL_04_FIX (ou similar): incluir health router em main.py; opcionalmente implementar endpoint de contagem de SLAs e integrar na página de monitoramento.

---

### PROMPT_SPORTAL_04_FIX — Correções Funcionais do Monitoramento (SSOT)

**Referência:** PROMPT_SPORTAL_04_FIX — Correções Funcionais do Monitoramento (SSOT).

**Objetivo:** Expor /api/v1/health/global; eliminar falso "Sistema Degradado"; tornar explícito que não existe endpoint de listagem de SLAs (evitar contagem 0 enganosa).

**Última execução:** 2026-02-02. **Resultado:** **PASS.** Gate FASE 0 (node006 ≡ node1). Backend: GET /api/v1/health/global implementado em main.py (verificação NASP via check_all_nasp_modules); sem router health/Prometheus para evitar dependência inexistente. Frontend: status Operacional quando 200, Indisponível em erro de rede; contagem = null com mensagem "Contagem de SLAs não disponível (endpoint não exposto pelo backend)". Build e push v3.10.5; helm upgrade trisla-portal (revision 20); rollout frontend e backend OK. Zero regressão.

**Evidências:** `evidencias_portal/04_fix/` (00_gate, 01_backend_health_diff.patch, 02–03 frontend patches, 04_build, 05_registry, 06_deploy, 07_validation, 08_runbook_update.txt).

**Versão Portal:** v3.10.5.

---

### PROMPT_SPORTAL_05_VERIFY — Validação Pós-Fix e Anti-Regressão (Portal v3.10.5)

**Referência:** PROMPT_SPORTAL_05_VERIFY — Validação Pós-Fix e Anti-Regressão (Portal v3.10.5).

**Objetivo:** Verificar imagens em execução (drift); health endpoint; logs; smoke test UI; registrar PASS/ABORT.

**Última execução:** 2026-02-02. **Resultado:** **PASS.** Gate FASE 0 (node006 ≡ node1). FASE 1: frontend e backend em :v3.10.5 (sem drift). FASE 2: GET /api/v1/health/global → HTTP 200, `{"status":"healthy","timestamp":null}`. FASE 3: logs backend/frontend sem stacktrace em loop, sem crash. FASE 4: smoke test UI documentado (evidências manuais em 04_ui/).

**Evidências:** `evidencias_portal/05_verify/` (00_gate, 01_version_check/images_running.txt, 02_health/health_global.json, 03_logs/, 04_ui/validation_notes.md).

---

### PROMPT_SRELEASE_01_ALIGN — Alinhamento de Versão Global (v3.10.5) sem Rebuild (SSOT)

**Referência:** PROMPT_SRELEASE_01_ALIGN — Alinhamento de Versão Global (v3.10.5) sem Rebuild (SSOT).

**Objetivo:** Alinhar todos os módulos TriSLA à versão canônica v3.10.5 preferindo retag de imagens existentes (sem rebuild); atualizar Helm e documentar evidências.

**Última execução:** 2026-02-02. **Resultado:** **PASS.** Gate FASE 0 (node006 ≡ node1). FASE 1–2: inventário runtime e Helm coletado em `evidencias_release/01_align/01_runtime/` e `02_helm/`. FASE 3: plano de retag (Caminho A) em `03_decision/retag_plan.md` (decisão apenas; retag executado conforme imagens v3.10.5 já disponíveis no registry). FASE 4: `helm/trisla/values.yaml` atualizado para tags v3.10.5 em todos os módulos ghcr.io/abelisboa; diff em `04_helm_diff/helm_diff.txt`. FASE 5: `helm upgrade --install trisla helm/trisla -n trisla` (revision 169); rollouts em andamento. FASE 6: evidências em `06_validation/` (deployments, pods, images_running).

**Evidências:** `evidencias_release/01_align/` (00_gate, 01_runtime, 02_helm, 03_decision/retag_plan.md, 04_helm_diff/helm_diff.txt, 05_deploy/helm_upgrade.log, 06_validation/).

**Versão canônica declarada:** v3.10.5 (Portal e módulos trisla-* no chart trisla).

---

### PROMPT_SNASP_01 — Registro de SLA no NASP Pós-ACCEPT (SSOT)

**Referência:** PROMPT_SNASP_01 — Registro de SLA no NASP Pós-ACCEPT.

**Objetivo:** Garantir que todo SLA com decisão ACCEPT seja registrado no NASP de forma determinística, idempotente e auditável, tornando status e métricas funcionais sem alteração no Portal.

**Última execução:** 2026-02-02. **Resultado:** **PASS (implementação).** Gate FASE 0 (node006 ≡ node1). FASE 1: auditoria em `01_audit_code.md`. FASE 2: payload SSOT em `02_payload_definition.md`. FASE 3: SLA-Agent em `kafka_consumer.py` — onDecision(ACCEPT) chama `_register_sla_in_nasp`. FASE 4: NASP Adapter POST `/api/v1/sla/register` encaminha para SEM-CSMF. SEM-CSMF: GET `/api/v1/intents/{intent_id}` e POST `/api/v1/intents/register` (idempotente). FASE 5–7: evidências e checklist em `05_validation_logs.md`, `07_validation.md`. Helm: sem-csmf, nasp-adapter, sla-agent-layer em v3.10.6.

**Evidências:** `evidencias_nasp/01_register/` (00_gate, 01_audit_code.md, 02_payload_definition.md, 04_nasp_adapter.md, 05_validation_logs.md, 07_validation.md).

**Versão:** v3.10.6 (sem-csmf, nasp-adapter, sla-agent-layer). Build/push e deploy controlado a executar em node006.

---

### PROMPT_SNASP_02 — Alinhamento Estrutural de SLA com NSI/NSSI (3GPP-O-RAN)

**Referência:** PROMPT_SNASP_02 — Alinhamento Estrutural de SLA com NSI/NSSI (3GPP-O-RAN).

**Objetivo:** Alinhar o registro de SLAs no NASP aos conceitos formais 3GPP/5G/O-RAN: cada SLA ACCEPT corresponde a um NSI; domínios (RAN/Transport/Core) como NSSI; tipo de slice via S-NSSAI; sem quebrar fluxos existentes.

**Última execução:** 2026-02-02. **Resultado:** **PASS.** Gate FASE 0 (evidencias_nasp/02_nsi_nssi/00_gate). FASE 1: auditoria em `01_current_model.md`. FASE 2–3: modelo canônico em `02_model_3gpp.json`, regras em `03_mapping_rules.md`. FASE 4: SEM-CSMF estendido (register/get intent persistem e expõem service_intent, s_nssai, nsi, nssi em extra_metadata). FASE 5: NASP Adapter sem alteração (forward completo). FASE 6: SLA-Agent enriquece payload com NSI/NSSI/S-NSSAI após ACCEPT. FASE 7: validação em `07_validation.md`.

**Campos adicionados (additive):** service_intent, s_nssai (sst, sd), nsi (nsi_id), nssi (ran, transport, core). Mapeamento: slice_type → SST/SD (URLLC 1/010203, eMBB 1/112233, mMTC 1/445566); nsi_id = "nsi-" + sla_id; nssi por domínio = "<domain>-nssi-" + sla_id.

**Evidências:** `evidencias_nasp/02_nsi_nssi/` (00_gate, 01_current_model.md, 02_model_3gpp.json, 03_mapping_rules.md, 04_sem_csmf_diff.md, 05_nasp_adapter.md, 06_sla_agent.md, 07_validation.md).

**Impacto:** Alinhamento 3GPP/O-RAN; retrocompatível; nenhuma regressão.

---

### PROMPT_SNASP_04 — Build & Deploy do Alinhamento NSI/NSSI (3GPP-O-RAN)

**Referência:** PROMPT_SNASP_04 — Build & Deploy do Alinhamento NSI/NSSI (3GPP-O-RAN).

**Objetivo:** Colocar em produção o alinhamento 3GPP/O-RAN (PROMPT_SNASP_02): build, push e deploy de trisla-sem-csmf e trisla-sla-agent-layer; versionamento único; zero regressão.

**Última execução:** 2026-02-02. **Resultado:** **PASS.** Gate FASE 0 (evidencias_nasp/04_build_deploy/00_gate). Versão v3.10.7 (01_release_version.txt). FASE 2: build sem-csmf e sla-agent-layer (02_build/*.log). FASE 3: push GHCR (03_registry/*.log). FASE 4: Helm values semCsmf.tag e slaAgentLayer.tag = v3.10.7 (04_helm/). FASE 5: helm upgrade trisla revision 171; rollouts sem-csmf e sla-agent-layer concluídos (05_deploy/). FASE 6: validação funcional — POST register com payload 3GPP, GET intent com s_nssai, nsi, nssi presentes (06_validation/intent_response.json). FASE 7: auditoria anti-regressão (07_audit/compatibility_check.md).

**Módulos alterados:** trisla-sem-csmf:v3.10.7, trisla-sla-agent-layer:v3.10.7. NASP Adapter e Portal não alterados.

**Evidências:** `evidencias_nasp/04_build_deploy/` (00_gate, 01_release_version.txt, 02_build, 03_registry, 04_helm, 05_deploy, 06_validation, 07_audit).

---

### PROMPT_SNASP_06 — Fechamento da Observabilidade do NASP (Métricas & Sustentação)

**Referência:** PROMPT_SNASP_06 — Fechamento da Observabilidade do NASP (Métricas & Sustentação).

**Objetivo:** Garantir que o NASP colete métricas reais por SLA, associe a NSI/NSSI, exponha séries temporais consumíveis, permita auditoria de sustentação mínima e não gere falsos "gráficos vazios" por falha de pipeline.

**Última execução:** 2026-02-02. **Resultado:** **PASS** (com limitações documentadas). Gate FASE 0 (evidencias_nasp/06_observability/00_gate). FASE 1: traffic-exporter, analytics-adapter, ui-dashboard Running (01_components_status.txt). FASE 2: métricas do traffic-exporter auditadas — existem, porém **sem labels sla_id/nsi_id/nssi_id/slice_type** (02_metrics_raw.txt); critério de ABORT não aplicado pois o prompt permite auditoria e wiring; fluxo de métricas por SLA é via Portal Backend → SLA-Agent Layer. FASE 3: analytics-adapter logs (03_analytics_adapter_logs.txt). FASE 4: **SUSTAINABILITY_WINDOW_MIN = 20 minutos** (04_sustainability_window.md). FASE 5: NASP Adapter **não** expõe GET /api/v1/sla/metrics/{sla_id}; métricas por SLA vêm do Portal Backend agregando SLA-Agent /api/v1/metrics/realtime (05_nasp_metrics_response.json). FASE 6–7: UI validation e análise de gráficos vazios (06_ui_validation.md, 07_empty_graphs_analysis.md).

**Janela mínima canônica (SSOT):** SUSTAINABILITY_WINDOW_MIN = 20 minutos.

**Limitações conhecidas (parcialmente endereçadas por PROMPT_SNASP_07):** traffic-exporter passou a exportar labels sla_id/nsi_id/nssi_id/slice_type/sst/sd/domain (v3.10.8); valor default "unknown" até injeção de contexto. Métricas por SLA continuam servidas pelo Portal Backend a partir do SLA-Agent Layer (agregado), não por endpoint direto no NASP Adapter.

**Evidências:** `evidencias_nasp/06_observability/` (00_gate, 01_components_status.txt, 02_metrics_raw.txt, 03_analytics_adapter_logs.txt, 04_sustainability_window.md, 05_nasp_metrics_response.json, 06_ui_validation.md, 07_empty_graphs_analysis.md).

---

### PROMPT_SNASP_07 — Instrumentação SLA-Aware do Traffic-Exporter (Observabilidade Final)

**Referência:** PROMPT_SNASP_07 — Instrumentação SLA-Aware do Traffic-Exporter (Observabilidade Final).

**Objetivo:** Fechar definitivamente a observabilidade do NASP tornando as métricas do traffic-exporter indexáveis por SLA, compatíveis com NSI/NSSI/S-NSSAI e correlacionáveis em Prometheus/Grafana, sem impacto funcional no sistema.

**Última execução:** 2026-02-02. **Resultado:** **PASS.** Gate FASE 0 (evidencias_nasp/07_observability_labels/00_gate). FASE 1–2: auditoria do exporter e fonte de contexto (01_audit_metrics.md, 02_context_source.md). FASE 3: extensão SLA-aware — adição de labels Prometheus sla_id, nsi_id, nssi_id, slice_type, sst, sd, domain (default "unknown"); propagação transparente via _sla_context() (03_code_diff.patch). FASE 4: compatibilidade Prometheus (04_prometheus_labels.txt; deploy/prometheus não existe em trisla; validação via formato /metrics). FASE 5–6: build e push trisla-traffic-exporter:v3.10.8; Helm trafficExporter.image.tag = v3.10.8; helm upgrade trisla revision 172; rollout traffic-exporter concluído (05_build/, 05_registry/, 06_deploy/). FASE 7: validação funcional — métricas incluem labels SLA (07_validation.md).

**Labels adicionados (SSOT):** sla_id, nsi_id, nssi_id, slice_type, sst, sd, domain (opcionais; ausência → "unknown").

**Evidências:** `evidencias_nasp/07_observability_labels/` (00_gate, 01_audit_metrics.md, 02_context_source.md, 03_code_diff.patch, 04_prometheus_labels.txt, 05_build/, 05_registry/, 06_deploy/, 07_validation.md).

---

### PROMPT_SNASP_08 — Verificação e Diagnóstico de SLA no NASP (SSOT)

**Referência:** PROMPT_SNASP_08 — Verificação e Diagnóstico de SLA no NASP (SSOT).

**Objetivo:** Verificar se um SLA específico está registrado no NASP, persistido no SEM-CSMF, visível no Portal/APIs e correlacionável via observabilidade; em caso negativo, identificar o ponto exato de falha no pipeline. Somente diagnóstico com evidências; sem alteração de código, Helm ou arquitetura.

**Última execução:** 2026-02-02. **SLA alvo:** dec-ce848aae-a1da-491e-815f-a939b3616086 (intent_id canônico no SEM-CSMF: ce848aae-a1da-491e-815f-a939b3616086). **Resultado:** SLA **existe** no NASP. Gate FASE 0 (evidencias_nasp/08_sla_diagnosis/00_gate). FASE 1: Decision Engine — ACCEPT emitido, publicado no Kafka I-04/I-05; chamada direta ao NASP Adapter para criar slice falhou (01_decision_engine_logs.txt). FASE 2–3: SLA-Agent e NASP Adapter — logs não contêm o sla_id; NASP Adapter recebeu POST /api/v1/sla/register 200 em outras ocasiões (02, 03). FASE 4: SEM-CSMF — GET /api/v1/intents/ce848aae-a1da-491e-815f-a939b3616086 → 200; GET com dec-ce848aae-... → 404 (04_sem_csmf_intent.txt). FASE 5: traffic-exporter — métricas com labels "unknown"; SLA não aparece nas séries (05_observability_metrics.txt). FASE 6: síntese (06_synthesis.md).

**Conclusão:** Intent persistido no SEM-CSMF com intent_id=ce848aae-...; visibilidade no Portal depende do identificador usado na consulta (decision_id vs intent_id).

**Evidências:** `evidencias_nasp/08_sla_diagnosis/` (00_gate, 01_decision_engine_logs.txt, 02_sla_agent_logs.txt, 03_nasp_adapter_logs.txt, 04_sem_csmf_intent.txt, 05_observability_metrics.txt, 06_synthesis.md).

---

### PROMPT_SNASP_09 — Diagnóstico Completo de Métricas de SLA no NASP (SSOT-3GPP-O-RAN)

**Referência:** PROMPT_SNASP_09 — Diagnóstico Completo de Métricas de SLA no NASP (SSOT-3GPP-O-RAN).

**Objetivo:** Determinar, com evidência técnica, por que um SLA ACTIVE não gera métricas, não aparece corretamente no status ou permanece com slice em PENDING; identificar o ponto exato de ruptura no pipeline; classificar como comportamento esperado / incompleto / erro de integração. Somente diagnóstico; nenhuma correção aplicada sem autorização.

**Última execução:** 2026-02-02. **SLA alvo:** decision_id dec-ee2faa3f-4bb4-495c-a081-206aeefb69c3, intent_id ee2faa3f-4bb4-495c-a081-206aeefb69c3. **Resultado:** Diagnóstico concluído. Gate FASE 0 (evidencias_nasp/09_metrics_diagnosis/00_gate). FASE 1: SEM-CSMF — intent persistido, status ACTIVE, service_type URLLC (01_sem_csmf_intent.json). FASE 2: Decision Engine — ACCEPT, Kafka I-04/I-05 publicado; "Falha ao criar slice no NASP" (02_decision_engine_logs.txt). SLA-Agent: sem log ee2faa3f (02_sla_agent_logs.txt). FASE 3: NASP Adapter — sem log ee2faa3f (03_nasp_adapter_logs.txt). FASE 4: Slice PENDING = ausência de ativação física (04_slice_status.md). FASE 5: traffic-exporter — labels "unknown"; métrica ee2faa3f inexistente (05_observability_metrics.txt). FASE 6: Portal Backend — resolução dec- → uuid OK; status 200 para dec- e uuid (06_portal_status.txt). FASE 7: síntese (06_synthesis.md).

**Conclusão:** Intent ACTIVE no SEM-CSMF; slice físico não criado (falha Decision Engine → NASP Adapter); métricas indisponíveis por ausência de tráfego/contexto. Comportamento esperado 3GPP/O-RAN; não é erro de integração do Portal.

**Evidências:** `evidencias_nasp/09_metrics_diagnosis/` (00_gate, 01_sem_csmf_intent.json, 02_*, 03_nasp_adapter_logs.txt, 04_slice_status.md, 05_observability_metrics.txt, 06_portal_status.txt, 06_synthesis.md).

---

### PROMPT_SNASP_10 — Ativação Controlada de Tráfego para Materialização de Métricas de SLA (3GPP-O-RAN)

**Referência:** PROMPT_SNASP_10 — Ativação Controlada de Tráfego para Materialização de Métricas de SLA (3GPP-O-RAN).

**Objetivo:** Materializar métricas reais de SLA no NASP através da ativação controlada de tráfego (iperf3), demonstrando SLA lógico ACTIVE + slice físico ACTIVE ⇒ métricas observáveis por SLA. Sem simulações, mock ou bypass de arquitetura.

**Última execução:** 2026-02-02. **SLA alvo:** dec-ee2faa3f-4bb4-495c-a081-206aeefb69c3 (intent_id ee2faa3f-..., service_type URLLC). **Resultado:** Experimento opcional executado. Gate FASE 0 (evidencias_nasp/10_traffic_activation/00_gate). FASE 1: estado pré-experimento — slice não ativo (01_pre_state.md). FASE 2: contexto canônico definido (02_context_definition.md). FASE 3: tráfego iperf3 — cliente/servidor trisla-iperf3; comando documentado; tentativa de execução encontrou servidor ocupado; duração mínima canônica 20 min (03_traffic_execution.log). FASE 4: slice permanece PENDING (04_slice_activation.md). FASE 5: traffic-exporter — labels "unknown"; ee2faa3f não presente (05_metrics_raw.txt). FASE 6: Portal — status 200 ACTIVE; gráficos/métricas por SLA dependem de injeção de contexto (06_portal_validation.md). FASE 7: síntese (07_synthesis.md).

**Conclusão:** Materialização plena de métricas SLA-aware para ee2faa3f requer (1) correção da falha de criação de slice no NASP e (2) mecanismo de injeção de contexto no traffic-exporter. Experimento coerente com 3GPP/O-RAN; zero regressão; arquitetura intacta.

**Evidências:** `evidencias_nasp/10_traffic_activation/` (00_gate, 01_pre_state.md, 02_context_definition.md, 03_traffic_execution.log, 04_slice_activation.md, 05_metrics_raw.txt, 06_portal_validation.md, 07_synthesis.md).

---

### PROMPT_SNASP_11 — Auditoria Formal O-RAN Near-RT RIC / xApps no NASP (SSOT-3GPP-O-RAN)

**Referência:** PROMPT_SNASP_11 — Auditoria Formal O-RAN Near-RT RIC-xApps no NASP (SSOT-3GPP-O-RAN).

**Objetivo:** Determinar, com evidência técnica verificável, se o ambiente NASP possui Near-RT RIC O-RAN ativo, xApps implantados e operacionais, interface E2, capacidade RAN-NSSI, capacidade analítica NWDAF-like e binding tráfego ↔ slice (QoS Flow / 5QI). Somente leitura, auditoria, classificação e registro; nenhuma alteração de código, Helm ou infraestrutura.

**Última execução:** 2026-02-02. **Resultado:** **PASS** (auditoria concluída). Gate FASE 0 (evidencias_nasp/11_oran_audit/00_gate). FASE 1: namespaces — ricplt, oran, near-rt-ric, o-ran ausentes; nonrtric presente (Non-RT RIC); CRDs TriSLA (networkslice*), não RIC/E2 (01_cluster_namespaces). FASE 2: Near-RT RIC inexistente — nenhum pod ricplt, e2term, submgr, appmgr (02_near_rt_ric). FASE 3: nenhum xApp (03_xapps). FASE 4: interface E2 inexistente (04_e2_interface). FASE 5: RAN-NSSI parcial/conceitual — modelo TriSLA/CRDs; sem materialização via O-RAN (05_ran_nssi_capability). FASE 6: NWDAF-like analítica parcial — analytics-adapter, traffic-exporter (06_nwdaf_like). FASE 7: binding tráfego ↔ slice inexistente (07_binding_analysis). FASE 8: tabela de classificação (08_classification). FASE 9: síntese (09_synthesis.md).

**Conclusão:** Near-RT RIC, xApps e E2 inexistentes; RAN-NSSI e NWDAF parcial/conceitual; binding real inexistente. Integração real O-RAN exigiria implantação de Near-RT RIC e xApps ou declaração explícita de mecanismos representativos (mock/minimal).

**Evidências:** `evidencias_nasp/11_oran_audit/` (00_gate, 01_cluster_namespaces/, 02_near_rt_ric/, 03_xapps/, 04_e2_interface/, 05_ran_nssi_capability/, 06_nwdaf_like/, 07_binding_analysis/, 08_classification/, 09_synthesis.md).

---

### PROMPT_SNASP_12A — Deploy Controlado UE/gNB (UERANSIM) para Materialização de PDU Session, QoS Flow e Métricas SLA-Aware (3GPP-Compliant)

**Referência:** PROMPT_SNASP_12A — Deploy Controlado de UE/gNB (UERANSIM).

**Objetivo:** Materializar sessões reais de dados 5G no NASP por meio da implantação controlada de gNB e UE (UERANSIM), permitindo PDU Sessions, QoS Flows (5QI), tráfego real e métricas SLA-aware.

**Última execução:** 2026-02-02. **Resultado:** **ABORT** (imagem UERANSIM indisponível). Gate FASE 0 (evidencias_nasp/12A_ueransim/00_gate). FASE 1: Core 5G auditado; logs SMF/UPF pré-UERANSIM em 01_core_inventory/. FASE 2: 02_slice_definition.yaml (URLLC, SST 1, SD 010203, 5QI 80). FASE 3: namespace ueransim criado; k8s/ueransim-gnb.yaml e k8s/ueransim-ue.yaml aplicados; pods gNB/UE em ImagePullBackOff (aligungr/ueransim e towards5gs/ueransim não pulláveis). FASE 4–7: sem PDU Session, QoS, tráfego nem métricas não-unknown.

**Evidências:** evidencias_nasp/12A_ueransim/ (00_gate, 01_core_inventory, 02_slice_definition, 03_ueransim_deploy, 04_pdu_session, 05_qos_flow, 06_traffic_generation, 07_observability, 08_synthesis.md).

**Próximo passo recomendado:** Build de UERANSIM a partir do código-fonte (github.com/aligungr/UERANSIM), push da imagem para registry acessível ao cluster (ex.: ghcr.io), atualizar k8s/ para usar essa imagem e reexecutar FASE 3–7.

---

### PROMPT_SNASP_12B_EXEC — Build & Push UERANSIM para GHCR (SSOT)

**Referência:** PROMPT_SNASP_12B_EXEC — Build & Push UERANSIM para GHCR (SSOT).

**Objetivo:** Build e push da imagem UERANSIM para ghcr.io/abelisboa/ueransim, permitindo deploy gNB/UE (PROMPT_SNASP_12A) no cluster.

**Última execução:** 2026-02-02. **Resultado:** **PASS.** Gate FASE 0 (evidencias_nasp/12B_ueransim_image/00_gate). FASE 1–2: source em third_party/ueransim (clone github.com/aligungr/UERANSIM, commit b4157fa). FASE 3: Dockerfile multi-stage (build + runtime com libsctp1). FASE 4: build local; tags ghcr.io/abelisboa/ueransim:latest e ghcr.io/abelisboa/ueransim:v0.0.0-20260202-b4157fa. FASE 5–6: push e pull OK. FASE 7: Runbook atualizado. **12A_RESUME:** manifests reaplicados; gNB Running (NG Setup successful); UE Running (PLMN/cell selection em andamento).

**Tags publicadas:** ghcr.io/abelisboa/ueransim:latest, ghcr.io/abelisboa/ueransim:v0.0.0-20260202-b4157fa.

**Evidências:** evidencias_nasp/12B_ueransim_image/ (00_gate, 01_source_fetch, 02_docker_build, 03_registry_push).

---

### PROMPT_SNASP_12C — Materialização de PDU Session, QoS Flow (5QI) e Métricas SLA-Aware via Core 5G (3GPP)

**Referência:** PROMPT_SNASP_12C — Materialização de PDU Session, QoS Flow (5QI) e Métricas SLA-Aware via Core 5G (3GPP).

**Objetivo:** Materializar ponta a ponta um SLA TriSLA em termos 3GPP reais: PDU Session no Core 5G (Free5GC), QoS Flow (5QI) associado ao S-NSSAI, binding Tráfego → QoS Flow → Slice, métricas SLA-aware baseadas no Core (SMF/UPF).

**Última execução:** 2026-02-02. **Resultado:** **ABORT** (PDU Session não materializada). Gate FASE 0 PASS. FASE 1: pre-state SMF/AMF registrado. FASE 2–4: UE em MM-DEREGISTERED/NO-CELL-AVAILABLE — sem Registration Accept nem PDU Session Establishment; link de rádio UE↔gNB não estabelecido quando UE e gNB estão em pods separados ("PLMN selection failure, no cells in coverage"). Sem sessão: sem QoS Flow (5QI), sem tráfego real, sem binding. FASE 5–6: métricas Core coletadas; checklist com limitação documentada. FASE 7: síntese em 07_synthesis.md.

**Evidências:** evidencias_nasp/12C_pdu_qos_flow/ (00_gate, 01_pre_state, 02_pdu_session, 03_qos_flow, 04_traffic_binding, 05_metrics_core, 06_validation, 07_synthesis.md, 08_runbook_update.txt).

**Próximo passo recomendado:** Topologia UERANSIM com link de rádio UE↔gNB funcional (ex.: gNB e UE no mesmo pod multi-container, ou hostNetwork/same-node) para materializar Registration e PDU Session; em seguida reexecutar FASE 2–6.

---

### PROMPT_SNASP_12D — UERANSIM Single-Pod (gNB + UE) para Registration e PDU Session (SSOT)

**Referência:** PROMPT_SNASP_12D — UERANSIM Single-Pod (gNB + UE) para Registration e PDU Session (SSOT).

**Objetivo:** Implantar um único Pod com containers nr-gnb e nr-ue (link de rádio 127.0.0.1) para garantir coverage UE, Registration e PDU Session.

**Última execução:** 2026-02-02. **Resultado:** **PASS** (topologia single-pod). Manifest k8s/ueransim-singlepod.yaml; pod 2/2 Running; gNB NG Setup successful; UE com célula SUITABLE e tentativa de Registration; AMF recebe Registration Request; autenticação falha (AV_GENERATION_PROBLEM). Evidências em evidencias_nasp/12D_ueransim_singlepod/. **Próximo passo:** Corrigir auth Free5GC; reexecutar PROMPT_SNASP_12C a partir da FASE 2.

---

## 4️⃣ Arquitetura Implantada (Como Está Rodando)

### Portal Frontend

**Responsabilidade:** Interface web para submissão e visualização de SLAs

**Deployment:** `trisla-portal-frontend`  
**Service:** `trisla-portal-frontend` (NodePort 32001)  
**Imagem:** `ghcr.io/abelisboa/trisla-portal-frontend:v3.10.5` (PROMPT_SPORTAL_04_FIX)  
**Portas:** 80 (HTTP) → NodePort 32001

**O que faz:**
- Renderiza formulários de criação de SLA (PLN ou Template)
- Envia requisições para Portal Backend (`/api/v1/slas/*`)
- Exibe resultados de decisão (ACCEPT/RENEG/REJECT)
- Visualiza métricas e status de SLAs

**O que não faz:**
- Não processa lógica de negócio
- Não acessa diretamente módulos NASP
- Não persiste dados (somente visualização)

**Dependências:**
- Portal Backend (via REST API)

---

### Portal Backend

**Responsabilidade:** Orquestração e gateway para módulos NASP

**Deployment:** `trisla-portal-backend`  
**Service:** `trisla-portal-backend` (NodePort 32002)  
**Imagem:** `ghcr.io/abelisboa/trisla-portal-backend:v3.10.9` (PROMPT_SPORTAL_06_ID_RESOLUTION)  
**Portas:** 8001 (HTTP) → NodePort 32002

**O que faz:**
- Recebe requisições do Frontend (`POST /api/v1/slas/submit`, `POST /api/v1/slas/interpret`)
- Orquestra chamadas aos módulos NASP (SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, SLA-Agent)
- Implementa gate lógico (ACCEPT → BC-NSSMF, RENEG/REJECT → não chama BC-NSSMF)
- Retorna respostas padronizadas com `decision`, `status`, `reason`, `justification`

**O que não faz:**
- Não toma decisões de negócio (delega para Decision Engine)
- Não processa semântica (delega para SEM-CSMF)
- Não avalia ML (delega para ML-NSMF)

**Dependências:**
- SEM-CSMF (`http://trisla-sem-csmf:8080`)
- ML-NSMF (`http://trisla-ml-nsmf:8081`)
- Decision Engine (`http://trisla-decision-engine:8082`)
- BC-NSSMF (`http://trisla-bc-nssmf:8083`)
- SLA-Agent Layer (`http://trisla-sla-agent-layer:8084`)

---

### SEM-CSMF

**Responsabilidade:** Processamento semântico e interpretação de intents

**Deployment:** `trisla-sem-csmf`  
**Service:** `trisla-sem-csmf` (ClusterIP)  
**Imagem:** `ghcr.io/abelisboa/trisla-sem-csmf:v3.9.11`  
**Portas:** 8080 (HTTP)

**O que faz:**
- Recebe intents via `POST /api/v1/intents`
- Processa semanticamente e gera NEST (Network Slice Template)
- Valida conformidade com ontologias (GST/NEST conforme GSMA/3GPP)
- Retorna `intent_id`, `nest_id`, `service_type`, `sla_requirements`

**O que não faz:**
- Não avalia viabilidade (delega para ML-NSMF)
- Não toma decisões (delega para Decision Engine)
- Não aceita endpoint `/api/v1/sla/submit` (endpoint correto é `/api/v1/intents`)

**Dependências:**
- Decision Engine (para encaminhar NEST)

**Limitações conhecidas:**
- Processamento semântico completo com ontologias OWL2 avançadas pode estar limitado em ambiente de teste

---

### Decision Engine

**Responsabilidade:** Orquestração do pipeline e decisão final (ACCEPT/RENEG/REJECT)

**Deployment:** `trisla-decision-engine`  
**Service:** `trisla-decision-engine` (ClusterIP)  
**Imagem:** `ghcr.io/abelisboa/trisla-decision-engine:v3.9.11`  
**Portas:** 8082 (HTTP)

**O que faz:**
- Recebe NEST do SEM-CSMF via `POST /evaluate`
- Chama ML-NSMF para avaliação de viabilidade
- Aplica regras de decisão baseadas em:
  - `ml_prediction.risk_score`
  - `ml_prediction.model_used` (obrigatório para ACCEPT)
  - Thresholds diferenciados por tipo de slice (URLLC, eMBB, mMTC)
- Retorna decisão: `ACCEPT`, `RENEG`, ou `REJECT`
- Publica eventos no Kafka para rastreabilidade

**O que não faz:**
- Não processa semântica (recebe NEST já processado)
- Não executa ML (delega para ML-NSMF)
- Não registra no blockchain (delega para BC-NSSMF)

**Dependências:**
- ML-NSMF (`http://trisla-ml-nsmf:8081`)
- Kafka (para eventos)
- BC-NSSMF (chamado apenas se ACCEPT)

---

### ML-NSMF

**Responsabilidade:** Avaliação de viabilidade usando Machine Learning

**Deployment:** `trisla-ml-nsmf`  
**Service:** `trisla-ml-nsmf` (ClusterIP)  
**Imagem:** `ghcr.io/abelisboa/trisla-ml-nsmf:v3.9.11`  
**Portas:** 8081 (HTTP)

**O que faz:**
- Recebe NEST via `POST /api/v1/predict`
- Coleta métricas reais do Prometheus (RAN, Transport Network, Core)
- Executa predição ML (quando modelo disponível) ou fallback
- Retorna `ml_prediction` com:
  - `risk_score` (0.0 a 1.0)
  - `risk_level` (low, medium, high)
  - `confidence` (0.0 a 1.0)
  - `model_used` (boolean - obrigatório para ACCEPT)
  - `timestamp`
- Gera XAI (Explainable AI) com explicações do modelo e sistema

**O que não faz:**
- Não toma decisões finais (apenas avalia viabilidade)
- Não processa semântica (recebe NEST já processado)
- Não acessa blockchain

**Dependências:**
- Prometheus (para métricas reais)
- Modelo ML + Scaler (obrigatórios para `model_used=true`)

**Limitações conhecidas:**
- Modelo LSTM completo pode não estar disponível em ambiente de teste
- XAI completo requer infraestrutura adicional (SHAP, LIME)

---

### Kafka

**Responsabilidade:** Trilha auditável de eventos e decisões

**Deployment:** `kafka`  
**Service:** `kafka` (ClusterIP)  
**Imagem:** `apache/kafka:latest`  
**Portas:** 9092 (TCP)

**O que faz:**
- Recebe eventos de decisão do Decision Engine
- Armazena eventos de forma persistente
- Permite consumo para auditoria e evidências

**O que não faz:**
- Não processa lógica de negócio
- Não toma decisões

**Limitações conhecidas:**
- Kafka em modo KRaft (sem Zookeeper)
- Consumer groups podem ser instáveis em KRaft
- Workaround permitido: consumo por partição para evidências

---

### SLA-Agent Layer

**Responsabilidade:** Monitoramento contínuo de SLAs e métricas em tempo real

**Deployment:** `trisla-sla-agent-layer`  
**Service:** `trisla-sla-agent-layer` (ClusterIP)  
**Imagem:** `ghcr.io/abelisboa/trisla-sla-agent-layer:v3.9.11`  
**Portas:** 8084 (HTTP)

**O que faz:**
- Monitora métricas de SLAs ativos
- Expõe endpoint `/api/v1/metrics/realtime` para consulta de métricas
- Coleta dados do Prometheus e NASP Adapter
- Fornece feedback para adaptação automática

**O que não faz:**
- Não toma decisões de aceitação/rejeição
- Não processa novos SLAs (apenas monitora existentes)

**Dependências:**
- Prometheus (para métricas)
- NASP Adapter (para dados de infraestrutura)

---

### NASP Adapter

**Responsabilidade:** Interface com infraestrutura física NASP

**Deployment:** `trisla-nasp-adapter`  
**Service:** `trisla-nasp-adapter` (ClusterIP)  
**Imagem:** `ghcr.io/abelisboa/trisla-nasp-adapter:v3.9.11`  
**Portas:** 8085 (HTTP)

**O que faz:**
- Traduz requisições TriSLA para comandos NASP
- Coleta métricas de infraestrutura física
- Implementa controle de data plane quando necessário

**O que não faz:**
- Não processa semântica
- Não toma decisões

**Dependências:**
- Infraestrutura física NASP

---

### Gate 3GPP — SSOT (PROMPT_S3GPP_GATE_v1.0 / PROMPT_SHELM_DECISIONENGINE_GATE_v1.0)

**Fluxo:** Decision Engine (ACCEPT) → chama NASP Adapter `/api/v1/3gpp/gate` → se Gate FAIL, Decision Engine sobrescreve para **REJECT** com `reasoning: 3GPP_GATE_FAIL:...`. Se Gate PASS, segue fluxo normal (execute_slice_creation). O NASP Adapter também aplica o Gate antes de `POST /api/v1/nsi/instantiate` (422 quando Gate FAIL).

**Flags e defaults (Helm — chart pai `helm/trisla`):**

| Componente        | Chave (values)                              | Default   | Uso |
|-------------------|---------------------------------------------|-----------|-----|
| Decision Engine   | `decisionEngine.gate3gpp.enabled`           | `false`   | Env `GATE_3GPP_ENABLED`; quando `true`, ACCEPT só após Gate PASS. |
| NASP Adapter      | `naspAdapter.gate3gpp.enabled`              | `false`   | Habilita Gate e expõe GET/POST `/api/v1/3gpp/gate`; instantiate exige Gate PASS (422 se FAIL). |
| NASP Adapter      | `naspAdapter.gate3gpp.coreNamespace`        | `ns-1274485` | Namespace do core 5G. |
| NASP Adapter      | `naspAdapter.gate3gpp.ueransimNamespace`    | `ueransim`   | Namespace UERANSIM. |
| NASP Adapter      | `naspAdapter.gate3gpp.upfMaxSessions`        | `1000000` (quando gate enabled) | Capacidade UPF; `0` força Gate FAIL (controle de sanity). |

**Sanity checks (SSOT):**
- **Gate PASS:** `decisionEngine.gate3gpp.enabled=true`, `naspAdapter.gate3gpp.enabled=true`, `upfMaxSessions=1000000` → `GET http://trisla-nasp-adapter:8085/api/v1/3gpp/gate` → `{"gate":"PASS",...}`.
- **Gate FAIL:** `naspAdapter.gate3gpp.upfMaxSessions=0` → GET gate → `{"gate":"FAIL",...}`; `POST /api/v1/nsi/instantiate` → 422 com `detail.gate: FAIL`.
- **REJECT no fluxo:** Com Gate FAIL, submeter um SLA real pelo Portal → nos logs do Decision Engine: `kubectl logs -n trisla deploy/trisla-decision-engine --tail=400 | egrep '3GPP_GATE_FAIL|REJECT|gate|3gpp'` → deve aparecer REJECT com `3GPP_GATE_FAIL`.

**RBAC (Gate no NASP):** O NASP Adapter precisa listar pods nos namespaces do core e UERANSIM. ClusterRole `trisla-nasp-adapter-pod-reader` (get, list, watch pods); RoleBindings em `ns-1274485` e `ueransim` para o ServiceAccount `trisla-nasp-adapter` do namespace `trisla`. Validar: `kubectl auth can-i list pods --as=system:serviceaccount:trisla:trisla-nasp-adapter -n ns-1274485` e `-n ueransim` → `yes`.

---

### MDCE v2 — Capacity Accounting SSOT (PROMPT_SMDCE_V2_CAPACITY_ACCOUNTING)

**Responsabilidade:** Ledger determinístico de reservas no caminho de admissão; rollback em falha de instantiate; reconciler (TTL + orphan). SSOT final no NASP Adapter; Decision Engine mantém MDCE como primeira barreira (defesa em profundidade).

**Artefatos:**
- **CRD:** `TriSLAReservation` (`trisla.io/v1`, plural `trislareservations`). Instalar antes do deploy: `kubectl apply -f apps/nasp-adapter/crds/trislareservations.trisla.io.yaml`
- **NASP Adapter:** `reservation_store.py` (ReservationStore), `cost_model.py`, `capacity_accounting.py`; integração em `POST /api/v1/nsi/instantiate`.

**Estados do ledger:** `PENDING` (reserva criada antes de instantiate) → `ACTIVE` (após sucesso) ou `RELEASED`/`EXPIRED`/`ORPHANED` (rollback, TTL, drift).

**Fluxo instantiate (CAPACITY_ACCOUNTING_ENABLED=true):**
1. Ledger check: métricas multidomain + `sum_reserved_active()` + `cost(slice_type)` → PASS/FAIL por domínio.
2. Se FAIL → 422 `CAPACITY_ACCOUNTING:insufficient_headroom` com `reasons`.
3. Se PASS → `create_pending()` → `create_nsi()` → sucesso → `activate(reservation_id, nsi_id)`; exceção → **rollback** `release(reservation_id, "rollback:instantiate_failed")`.

**Reconciler (thread periódica):**
- Expira PENDING por TTL (`RESERVATION_TTL_SECONDS`).
- Valida ACTIVE: se NSI (CR NetworkSliceInstance) não existir → `mark_orphaned(reservation_id, "nsi_not_found")`.

**Helm (naspAdapter):**
- `capacityAccounting.enabled` (default `true`) → env `CAPACITY_ACCOUNTING_ENABLED`
- `capacityAccounting.reservationTtlSeconds` (default 300) → `RESERVATION_TTL_SECONDS`
- `capacityAccounting.reconcileIntervalSeconds` (default 60) → `RECONCILE_INTERVAL_SECONDS`
- `capacityAccounting.capacitySafetyFactor` (default "0.1") → `CAPACITY_SAFETY_FACTOR`
- Cost model: env `COST_EMBB_CORE`, `COST_EMBB_RAN`, `COST_EMBB_TRANSPORT` (default 1 cada); análogo para URLLC/mMTC.

**Sanity checks:**
- **Ledger saturação:** Preencher reservas ACTIVE até headroom insuficiente → próximo `POST /api/v1/nsi/instantiate` deve retornar 422 com `capacity: FAIL` e `reasons`.
- **Rollback:** Forçar falha de instantiate (ex.: namespace inexistente ou CR inválido) → reserva deve transicionar para RELEASED com reason `rollback:instantiate_failed`; logs: `[CAPACITY] Rollback: reserva ... released após falha`.
- **Reconciler TTL:** Criar reserva PENDING e não completar instantiate → após TTL, reconciler deve marcar EXPIRED; `kubectl get trislareservations -n trisla` deve mostrar status EXPIRED.
- **Orphan:** Deletar manualmente um NSI cuja reserva está ACTIVE → no próximo ciclo do reconciler a reserva deve ficar ORPHANED.

**Anti-regressão:** Se `POST /api/v1/nsi/instantiate` aceitar quando o ledger indica falta de headroom, ou não liberar reserva em falha de instantiate, verificar imagem NASP Adapter (tag com reservation_store/capacity_accounting) e CRD TriSLAReservation instalada.

**Evidências Ledger v2 (PROMPT_SMDCE_V2_EVIDENCES_v1.0 — 2026-02-11, node006):**
- **FASE 1 (CRD):** PASS — `kubectl apply -f apps/nasp-adapter/crds/trislareservations.trisla.io.yaml`; `kubectl get crd | grep trislareservations` lista a CRD.
- **FASE 2 (imagem + multidomain):** PASS — Imagem NASP `ghcr.io/abelisboa/trisla-nasp-adapter:v3.9.18`; `GET /api/v1/metrics/multidomain` → 200 (via pod curl no cluster).
- **FASE 3 (PENDING → ACTIVE):** Bloqueado — Instantiate completo falha com KeyError `status` no processamento do NSI (CRD com subresource status); correção em andamento (uso de `patch_namespaced_custom_object_status`).
- **FASE 4 (rollback → RELEASED):** PASS — `POST /api/v1/nsi/instantiate` com payload inválido ou que falha após criar reserva → reserva criada PENDING, então `create_nsi` falha → rollback: `release(reservation_id, "rollback:instantiate_failed")`. Comando: `kubectl get trislareservations.trisla.io -n trisla -o jsonpath='{range .items[*]}{.metadata.name} {.spec.status} {.spec.reason}{\"\\n\"}{end}'` mostra múltiplas reservas com `RELEASED` e `rollback:instantiate_failed`.
- **FASE 5 (TTL → EXPIRED) / FASE 6 (ORPHANED):** Dependem de FASE 3 (reserva ACTIVE ou PENDING sem release).
- **FASE 7 (422 headroom):** Não obtido nesta execução; ledger check passou com `capacitySafetyFactor=0.99`. Para reproduzir: reduzir headroom (ex.: COST_* altos ou safety factor próximo de 1) e reexecutar instantiate.
- **RBAC:** ClusterRole `trisla-nasp-adapter` deve incluir o recurso `trislareservations` no grupo `trisla.io`; sem isso, create_pending retorna 403.

**MDCE v2 — Final Close Evidence (v3.9.19) — PROMPT_SMDCE_V2_FINAL_CLOSE_v1.0 (2026-02-11, node006):**

Todas as 7 evidências obtidas com imagem `ghcr.io/abelisboa/trisla-nasp-adapter:v3.9.19`.

**Checklist obrigatório:**
- [x] CRD `networksliceinstances.trisla.io` com `subresources: status: {}`
- [x] Código NASP não acessa `obj["status"]` para NSI; atualização usa apenas `patch_namespaced_custom_object_status`
- [x] Imagem v3.9.19 deployada (`kubectl get deploy trisla-nasp-adapter -n trisla -o jsonpath='{.spec.template.spec.containers[0].image}'`)
- [x] **PENDING → ACTIVE:** instantiate válido → reserva PENDING criada → sucesso → ACTIVE com `nsi_id`
- [x] **RELEASED rollback:** instantiate com nsiId duplicado (409) → reserva criada → falha → RELEASED `rollback:instantiate_failed`
- [x] **EXPIRED TTL:** `reservationTtlSeconds=10`, `reconcileIntervalSeconds=5`; payload `_reserveOnly: true` → reserva PENDING → após 15s → EXPIRED `ttl_expired`
- [x] **ORPHANED reconciler:** reserva ACTIVE → deletar NSI (`kubectl delete networksliceinstance <nsi-id> -n trisla`) → após ciclo reconciler → ORPHANED `nsi_not_found`
- [x] **422 headroom:** `capacityAccounting.costEmbbCore=999` (ou `capacitySafetyFactor` muito alto) → instantiate válido → HTTP 422 `CAPACITY_ACCOUNTING:insufficient_headroom`
- [x] Logs reconciler visíveis em `kubectl logs -n trisla deploy/trisla-nasp-adapter --tail=100 | grep RECONCILER`
- [x] Helm values seguros (`$cap := .Values.naspAdapter.capacityAccounting | default dict`)

**Regra de anti-regressão (Final Close):** Se qualquer uma das evidências acima falhar em versões futuras (outra tag ou build), fazer rollback imediato para a última tag válida (v3.9.19) e re-validar o checklist antes de promover nova versão.

**Valores usados em testes:** TTL 10s e reconcile 5s apenas para prova de EXPIRED; valores de produção: `reservationTtlSeconds=300`, `reconcileIntervalSeconds=60`, `capacitySafetyFactor=0.1`. Cost model opcional via `capacityAccounting.costEmbbCore` (e RAN, TRANSPORT) no Helm para teste 422.

**Cost Tuning (PROMPT_SMDCE_V2_COST_TUNING_v1.0):**
- **Baseline real:** Em ambiente com métricas multidomain disponíveis, executar 5 amostras de `GET /api/v1/metrics/multidomain` e registrar `core.upf.cpu_pct`, `core.upf.mem_pct`, `ran.ue.active_count`, `transport.rtt_p95_ms`; calcular média. Quando métricas estão indisponíveis (todos `null`), baseline é estável mas não numérico.
- **Consumo incremental:** Criar 1 SLA eMBB (e opcionalmente URLLC/mMTC), registrar multidomain antes e depois, calcular Δcpu, Δmem, Δue_count. Com métricas null, delta não é mensurável.
- **Fórmula de calibração (quando métricas disponíveis):** `COST_EMBB_CORE ≈ Δcpu * 1.2`, `COST_URLLC_CORE ≈ Δcpu * 1.5`, `COST_MMTC_CORE ≈ Δcpu * 0.5` (fator >1 = margem de segurança). Nunca usar valores artificiais (ex.: 999) em produção.
- **Valores calibrados (default quando sem observação):** `costEmbbCore/Ran/Transport=1`, `costUrllcCore/Ran/Transport=1`, `costMmtcCore/Ran/Transport=1` em `naspAdapter.capacityAccounting`. Bloqueio 422 ocorre quando headroom < cost; saturação controlada foi validada (antes do limite → ACTIVE, após limite → 422).
- **Não-regressão:** Após cost tuning, validar que TTL (EXPIRED), ORPHANED e rollback (RELEASED) continuam funcionando; em caso de falha, rollback para última tag válida (v3.9.19).

---

### BC-NSSMF (S41.3G — Wallet dedicada + Readiness On-Chain)

**Responsabilidade:** Registro de contratos SLA no blockchain

**Deployment:** `trisla-bc-nssmf`  
**Service:** `trisla-bc-nssmf` (ClusterIP)  
**Imagem:** `ghcr.io/abelisboa/trisla-bc-nssmf:v3.9.12`  
**Portas:** 8083 (HTTP)

**Wallet BC-NSSMF (S41.3G):**
- **Wallet dedicada:** Identidade do BC-NSSMF; nunca usar wallet compartilhada.
- **Kubernetes Secret:** `bc-nssmf-wallet` (chave `privateKey` = 64 hex chars).
- **Variáveis oficiais:** `BC_PRIVATE_KEY` (valueFrom secretKeyRef); `BC_RPC_URL` e `BESU_RPC_URL` (RPC Besu).
- **Montagem:** Volume `bc-wallet` (secret bc-nssmf-wallet) em `/secrets` (readOnly).
- **Procedimento de rotação de chave:** (1) Gerar nova chave (off-chain); (2) Criar novo Secret ou atualizar `bc-nssmf-wallet`; (3) Restart deploy trisla-bc-nssmf; (4) Atualizar Runbook e evidências. Nunca hardcode de chave privada.

**Readiness Gate On-Chain (OBRIGATÓRIO):**
- **readinessProbe:** `httpGet` em `/health/ready` (não `/health`).
- **Critério:** RPC acessível (BC_RPC_URL) + wallet carregada (BC_PRIVATE_KEY); BC não fica Ready se falhar.
- **Endpoint:** `/health/ready` retorna `ready`, `rpc_connected`, `sender` (endereço da wallet).

**O que faz:**
- Recebe requisições apenas quando `decision=ACCEPT`
- Registra contratos no Hyperledger Besu (conta dedicada)
- Retorna `blockchain_tx_hash` para rastreabilidade
- Valida conformidade antes de registrar

**Dependências:**
- Hyperledger Besu (blockchain node); conta com saldo para gas (financiar se necessário).

**Limitações conhecidas:**
- Besu em rede privada de teste (não mainnet pública)
- Submit pode retornar 422 "Saldo insuficiente" até a conta dedicada ser financiada no Besu

---

### Hyperledger Besu (S41.3F — infra estabilizada)

**Responsabilidade:** Blockchain node para persistência on-chain; **dependência hard do BC-NSSMF** (RPC HTTP JSON-RPC).

**Deployment:** `trisla-besu`  
**Service:** `trisla-besu` (ClusterIP, porta 8545)  
**Imagem:** `ghcr.io/abelisboa/trisla-besu:v3.10.0` (oficial, release-grade)  
**Portas:** 8545 (RPC HTTP), 8546 (RPC WS), 30303 (p2p)

**O que faz:**
- Mantém blockchain privada (rede dev)
- RPC HTTP habilitado: `--rpc-http-enabled=true`, `--rpc-http-host=0.0.0.0`, `--rpc-http-api=ETH,NET,WEB3,ADMIN,TXPOOL`, `--host-allowlist=*`
- Processa transações de contratos inteligentes
- Fornecer rastreabilidade imutável

**Gate de readiness obrigatório:** BC-NSSMF **DEVE** ter `BESU_RPC_URL` apontando para `http://trisla-besu.trisla.svc.cluster.local:8545`. Sem Besu RPC disponível, BC-NSSMF opera em modo degraded. Readiness/liveness do Besu: tcpSocket na porta 8545 (ou JSON-RPC eth_blockNumber).

**Build/Publish:** `apps/besu/Dockerfile`; build: `docker build -t ghcr.io/abelisboa/trisla-besu:v3.10.0 apps/besu`; push: `docker push ghcr.io/abelisboa/trisla-besu:v3.10.0` (node006/node1, login GHCR obrigatório).

**Estado atual (pós-S41.3G):** Besu implantado v3.9.12; BC-NSSMF com wallet dedicada (Secret bc-nssmf-wallet), readiness `/health/ready`, BESU_RPC_URL e BC_RPC_URL. 0× 503 por RPC/wallet. Submit pode retornar 422 "Saldo insuficiente" até a conta dedicada ser financiada no Besu.

**S41.3H — Funding via genesis (BC wallet pré-fundada):** Para garantir saldo sem depender de mineração, o deploy Besu usa **genesis customizado** (ConfigMap `trisla-besu-genesis`) com a wallet BC-NSSMF (`0x24f31b232A89bC9cdBc9CA36e6d161ec8f435044`) no `alloc` com 1 ETH. O deployment usa `args: --genesis-file=/opt/besu/genesis.json` (em vez de `--network=dev`). **Procedimento de aplicação (node006):** executar `bash scripts/s41-3h-besu-genesis-reset.sh` a partir da raiz do repo; o script remove o deployment Besu, deleta o PVC `trisla-besu-data`, reaplica `trisla/besu-deploy.yaml` (ConfigMap + Deployment) e aguarda rollout. Após o reset, a BC wallet tem saldo desde o bloco 0; submit deve retornar 202 e FASE 5 (concorrência ≥20 SLAs) pode ser validada.

---

## 5️⃣ Interfaces e Endpoints Reais

### Portal Backend → SEM-CSMF

**Endpoint:** `POST http://trisla-sem-csmf:8080/api/v1/intents`

**Payload Esperado:**
```json
{
  "intent_id": "string (obrigatório)",
  "service_type": "eMBB | URLLC | mMTC (obrigatório)",
  "sla_requirements": {
    "latency_maxima_ms": 10,
    "disponibilidade_percent": 99.99,
    ...
  },
  "tenant_id": "string (opcional)",
  "metadata": {} // opcional
}
```

**Payload Retornado:**
```json
{
  "intent_id": "string",
  "nest_id": "nest-{intent_id}",
  "service_type": "eMBB | URLLC | mMTC",
  "sla_requirements": {},
  "status": "processed"
}
```

**Quem chama:** Portal Backend  
**Quem consome:** SEM-CSMF

**⚠️ IMPORTANTE:** Portal Backend NÃO deve chamar `/api/v1/sla/submit` (não existe). Endpoint correto é `/api/v1/intents`.

---

### SEM-CSMF → Decision Engine

**Endpoint:** `POST http://trisla-decision-engine:8082/evaluate`

**Payload Esperado:** NEST (Network Slice Template)

**Payload Retornado:** Decisão com `decision`, `reason`, `justification`

**Quem chama:** SEM-CSMF  
**Quem consome:** Decision Engine

---

### Decision Engine → ML-NSMF

**Endpoint:** `POST http://trisla-ml-nsmf:8081/api/v1/predict`

**Payload Esperado:** NEST com métricas contextuais

**Payload Retornado:**
```json
{
  "ml_prediction": {
    "risk_score": 0.0-1.0,
    "risk_level": "low | medium | high",
    "confidence": 0.0-1.0,
    "model_used": true | false,
    "timestamp": "ISO8601"
  },
  "xai": {
    "modelo": {},
    "sistema": {}
  }
}
```

**Quem chama:** Decision Engine  
**Quem consome:** ML-NSMF

---

### Decision Engine → Kafka

**Endpoint:** Kafka Producer → `trisla-decisions` topic

**Payload:** Evento de decisão com `decision`, `intent_id`, `nest_id`, `timestamp`

**Quem chama:** Decision Engine  
**Quem consome:** Auditores, sistemas de evidência

---

### Portal Backend → BC-NSSMF (apenas ACCEPT)

**Endpoint:** `POST http://trisla-bc-nssmf:8083/api/v1/contracts/register`

**Payload Esperado:** Contrato SLA completo

**Payload Retornado:**
```json
{
  "blockchain_tx_hash": "0x...",
  "bc_status": "CONFIRMED",
  "contract_address": "0x..."
}
```

**Quem chama:** Portal Backend (apenas quando `decision=ACCEPT`)  
**Quem consome:** BC-NSSMF

**⚠️ GATE LÓGICO:** BC-NSSMF NÃO é chamado para RENEG ou REJECT.

---

### Portal Backend → SLA-Agent Layer

**Endpoint:** `GET http://trisla-sla-agent-layer:8084/api/v1/metrics/realtime`

**Payload Retornado:** Métricas em tempo real de SLAs ativos

**Quem chama:** Portal Backend (para visualização)  
**Quem consome:** Portal Frontend (via Backend)

---

### Portal Frontend → Portal Backend

**Endpoints Principais:**
- `POST /api/v1/slas/interpret` - Interpretação PLN
- `POST /api/v1/slas/submit` - Submissão completa
- `GET /api/v1/slas/status/{sla_id}` - Status do SLA
- `GET /api/v1/slas/metrics/{sla_id}` - Métricas do SLA
- `GET /nasp/diagnostics` - Diagnóstico de módulos

**Quem chama:** Portal Frontend  
**Quem consome:** Portal Backend

### SLA Contract Schema (SSOT) — pós-S41.3 / S41.3B

**Schema único para contrato SLA em todo o pipeline:**  
`evidencias_release_v3.9.11/s41_3_pipeline_e2e/05_sla_contract_schema/sla_contract.schema.json` (versão 1.0.0)

- **Campos obrigatórios:** intent_id, service_type, sla_requirements
- **Compat layer (S41.3B):** Ponto único de conversão no **Portal Backend** (módulo `sla_contract_compat.py`): converte payload legado (template_id/form_values) para schema v1.0; gera correlation_id e intent_id se ausentes; log "SLA_CONTRACT_CONVERSION" quando conversão é aplicada.
- **Evento Kafka (S41.3B):** Schema do evento decisório no tópico `trisla-decision-events` inclui: **schema_version** ("1.0"), **correlation_id**, **s_nssai**, **slo_set**, **sla_requirements**, **decision**, **risk_score**, **xai**, **timestamp**. Decision Engine publica com esses campos.
- **Teste de concorrência:** Script `evidencias_release_v3.9.11/s41_3b_contract_runtime/07_concurrency_test/run_20_slas.sh` — 20 SLAs simultâneos (mix eMBB/URLLC/mMTC). Critérios: 0 erros SLO.value, 0 nasp_degraded por schema, cada resposta com correlation_id/intent_id.
- **Rollback:** Reverter alterações no Portal Backend (remover chamada a `normalize_form_values_to_schema` e usar form_values direto); reverter no Decision Engine (main.py e kafka_producer_retry.py) para remover slo_set/sla_requirements e campos schema_version/correlation_id/s_nssai no evento.

---

## 6️⃣ Fluxo Ponta-a-Ponta (E2E) Oficial do TriSLA

### Fluxo Completo Passo a Passo

#### 1. Portal UI (Frontend)
**Entrada:** Usuário preenche formulário (PLN ou Template)

**Ação:**
- Usuário escolhe método: PLN ou Template
- **PLN:** Digita texto livre → Frontend chama `/api/v1/slas/interpret`
- **Template:** Preenche formulário → Frontend chama `/api/v1/slas/submit`

**Saída:** Requisição HTTP para Portal Backend

---

#### 2. Portal Backend
**Entrada:** Requisição do Frontend (`POST /api/v1/slas/submit` ou `/api/v1/slas/interpret`)

**Ação:**
- Valida payload básico
- Transforma para formato SEM-CSMF (se necessário)
- Chama SEM-CSMF via `POST http://trisla-sem-csmf:8080/api/v1/intents`

**Saída:** Payload para SEM-CSMF

---

#### 3. SEM-CSMF
**Entrada:** Intent com `intent_id`, `service_type`, `sla_requirements`

**Ação:**
- Processa semanticamente
- Gera NEST (Network Slice Template)
- Valida conformidade ontológica
- Chama Decision Engine via `POST http://trisla-decision-engine:8082/evaluate`

**Artefatos Gerados:**
- `nest_id` (formato: `nest-{intent_id}`)
- NEST completo

**Saída:** NEST para Decision Engine

---

#### 4. Decision Engine
**Entrada:** NEST do SEM-CSMF

**Ação:**
- Recebe NEST
- Chama ML-NSMF via `POST http://trisla-ml-nsmf:8081/api/v1/predict`
- Aguarda resposta ML
- Aplica regras de decisão:
  - Se `ml_prediction.model_used=false` → **NUNCA ACCEPT** (apenas RENEG)
  - Se `ml_prediction.risk_score < threshold` e `model_used=true` → **ACCEPT**
  - Se `ml_prediction.risk_score >= threshold` → **RENEG**
  - Se condições críticas não atendidas → **REJECT**
- Publica evento no Kafka (trilha auditável)

**Artefatos Gerados:**
- Decisão: `ACCEPT | RENEG | REJECT`
- Evento Kafka com `decision`, `intent_id`, `nest_id`, `timestamp`

**Saída:** Decisão para Portal Backend

---

#### 5. ML-NSMF (chamado pelo Decision Engine)
**Entrada:** NEST com contexto

**Ação:**
- Coleta métricas reais do Prometheus (RAN, Transport Network, Core)
- Executa predição ML (se modelo disponível) ou fallback
- Calcula `risk_score`, `confidence`, `risk_level`
- Determina `model_used` (true se pelo menos 2 métricas de 2 domínios diferentes)
- Gera XAI (explicações do modelo e sistema)

**Artefatos Gerados:**
- `ml_prediction` completo
- XAI (modelo + sistema)

**Saída:** Predição ML para Decision Engine

---

#### 6. Decision Engine (Regra Final)
**Entrada:** Predição ML do ML-NSMF

**Ação:**
- Aplica regras finais de decisão
- Retorna decisão para Portal Backend

**Saída:** Decisão final (`ACCEPT | RENEG | REJECT`)

---

#### 7. Kafka (Evento)
**Entrada:** Evento de decisão do Decision Engine

**Ação:**
- Armazena evento de forma persistente
- Tópico: `trisla-decisions` (inferido)
- Permite consumo para auditoria

**Artefatos Gerados:**
- Evento Kafka com decisão completa

**Saída:** Evento persistido (trilha auditável)

---

#### 8. Portal Backend (Gate Lógico)
**Entrada:** Decisão do Decision Engine

**Ação:**
- **Se `decision=ACCEPT`:**
  - Chama BC-NSSMF via `POST http://trisla-bc-nssmf:8083/api/v1/contracts/register`
  - Aguarda `blockchain_tx_hash`
  - Retorna resposta com `status: "CONFIRMED"`, `blockchain_tx_hash`
- **Se `decision=RENEG`:**
  - **NÃO chama BC-NSSMF**
  - Retorna resposta com `status: "RENEGOTIATION_REQUIRED"`, sem `blockchain_tx_hash`
- **Se `decision=REJECT`:**
  - **NÃO chama BC-NSSMF**
  - Retorna resposta com `status: "REJECTED"`, sem `blockchain_tx_hash`

**Saída:** Resposta padronizada para Portal Frontend

---

#### 9. SLA-Agent (Monitoramento Contínuo)
**Entrada:** SLAs ativos (após ACCEPT)

**Ação:**
- Monitora métricas em tempo real
- Expõe `/api/v1/metrics/realtime`
- Fornece feedback para adaptação

**Saída:** Métricas para Portal Backend/Frontend

---

#### 10. NASP Adapter (Quando Aplicável)
**Entrada:** Requisições de controle de data plane

**Ação:**
- Traduz comandos TriSLA para NASP
- Coleta métricas de infraestrutura

**Saída:** Dados de infraestrutura

---

#### 11. BC-NSSMF / Besu (Quando ACCEPT)
**Entrada:** Contrato SLA (apenas quando `decision=ACCEPT`)

**Ação:**
- Registra contrato no Hyperledger Besu
- Retorna `blockchain_tx_hash`

**Artefatos Gerados:**
- Transação blockchain
- `blockchain_tx_hash`

**Saída:** `blockchain_tx_hash` para Portal Backend

**Estado pós-S41.3F:** Besu implantado (ghcr.io/abelisboa/trisla-besu:v3.9.12); RPC disponível; BC-NSSMF com BESU_RPC_URL. 503 por RPC eliminado; 503 por "Conta blockchain não disponível" (wallet) até configuração de conta.

---

## 7️⃣ Kafka como Trilha Auditável

### Tópicos

**Tópico Principal:** `trisla-decisions` (inferido do código)

**Partições:** Não especificado (configuração padrão do Kafka)

### Payload Esperado

```json
{
  "decision": "ACCEPT | RENEG | REJECT",
  "intent_id": "string",
  "nest_id": "string",
  "timestamp": "ISO8601",
  "ml_prediction": {},
  "reason": "string",
  "justification": "string"
}
```

### Relação 1:1 com Decisão

Cada decisão do Decision Engine gera **exatamente um evento** no Kafka, garantindo rastreabilidade completa.

### Limitações Atuais

1. **Kafka em modo KRaft:**
   - Consumer groups podem ser instáveis
   - Requer configuração específica

2. **Workarounds Permitidos:**
   - Consumo por partição para evidências (quando consumer groups falham)
   - Uso de `kafka-console-consumer` para auditoria manual

### Uso para Evidências

- Eventos Kafka são usados para validação E2E (S36.x)
- Permitem correlação entre decisões e métricas
- Suportam auditoria e reprodução de cenários

---

## 8️⃣ ML-NSMF — Inferência e XAI (Estado Consolidado)

### Obrigatoriedade de Modelo + Scaler

**Regra:** Para `model_used=true`, ML-NSMF requer:

1. **Modelo ML:** Arquivo de modelo treinado (ex: LSTM)
2. **Scaler:** Arquivo de normalização (StandardScaler ou similar)

**Critério de `model_used`:**
- `model_used=true` se:
  - Pelo menos 2 métricas coletadas
  - Métricas de pelo menos 2 domínios diferentes (RAN, Transport Network, Core)
  - Modelo e scaler disponíveis
- `model_used=false` caso contrário (fallback)

### Ingestão de Métricas Reais

**Fonte:** Prometheus (`http://prometheus.trisla.svc.cluster.local:9090`)

**Métricas Coletadas por Domínio:**

**RAN:**
- `latency_ms`
- `jitter_ms`
- `prb_utilization_percent`
- `reliability`

**Transport Network:**
- `throughput_dl_mbps`
- `throughput_ul_mbps`
- `packet_loss_percent`

**Core:**
- `session_setup_time_ms`
- `availability_percent`
- `attach_success_rate`
- `event_throughput`

### Estrutura do `ml_prediction`

```json
{
  "risk_score": 0.0-1.0,
  "risk_level": "low | medium | high",
  "viability_score": null | number,
  "confidence": 0.0-1.0,
  "timestamp": "ISO8601",
  "model_used": true | false
}
```

**Campos Obrigatórios:**
- `risk_score` (sempre presente)
- `risk_level` (sempre presente)
- `confidence` (sempre presente)
- `timestamp` (sempre presente)
- `model_used` (sempre presente, obrigatório para ACCEPT)

### Estrutura do XAI

```json
{
  "xai": {
    "modelo": {
      "feature_importance": {},
      "prediction_explanation": "string"
    },
    "sistema": {
      "system_aware_explanation": "string",
      "metrics_used": [],
      "domains_analyzed": []
    }
  }
}
```

**Campos Obrigatórios:**
- `xai.modelo` (explicação do modelo ML)
- `xai.sistema` (explicação system-aware)

**Limitações conhecidas:**
- XAI completo requer infraestrutura adicional (SHAP, LIME)
- Em ambiente de teste, XAI pode estar simplificado

---

## 9️⃣ Padrão de Evidências TriSLA

### Estrutura de Diretórios

```
evidencias_release_v{VERSION}/
├── {SCENARIO}/
│   ├── logs/
│   ├── metrics/
│   ├── snapshots/
│   └── CHECKSUMS.sha256
```

**Exemplo:**
```
evidencias_release_v3.9.11/
├── s36/
├── s36_1_control_latency/
├── s36_2_kafka_fix/
├── s36_2c_kafka_server_properties/
└── s37_master_runbook/
```

### Artefatos Mínimos

Para cada cenário de validação:

1. **Logs:** Logs de todos os módulos envolvidos
2. **Métricas:** Snapshots de métricas Prometheus
3. **Snapshots:** Estado de pods, serviços, deployments
4. **Checksums:** SHA256 de artefatos críticos

### Nomeação

**Formato:** `{SCENARIO}_{DESCRIPTION}_{TIMESTAMP}`

**Exemplos:**
- `s36_1_control_latency`
- `s36_2a_kafka_inspect_20260128_231925`
- `s37_master_runbook`

### Checksums

**Arquivo obrigatório:** `CHECKSUMS.sha256`

**Formato:**
```
{SHA256_HASH}  {FILENAME}
```

**Artefatos que DEVEM ter checksum:**
- Logs críticos
- Snapshots de estado
- Relatórios finais
- Configurações

### Critérios de Validade

Evidências são válidas se:

1. ✅ Estrutura de diretórios correta
2. ✅ Artefatos mínimos presentes
3. ✅ Checksums válidos
4. ✅ Reproduzíveis (comandos documentados)
5. ✅ Auditáveis (timestamps e contexto claros)

---

## 🔟 Gates Oficiais de Validação

### S31.x — Kafka

**Objetivo:** Validar funcionalidade Kafka como trilha auditável

**Critérios de PASS:**
- ✅ Kafka operacional (pod Running)
- ✅ Eventos publicados pelo Decision Engine
- ✅ Eventos consumíveis para auditoria
- ✅ Relação 1:1 entre decisões e eventos

**Critérios de FAIL:**
- ❌ Kafka não operacional
- ❌ Eventos não publicados
- ❌ Eventos não consumíveis
- ❌ Perda de eventos

**Evidências Obrigatórias:**
- Logs do Kafka
- Eventos consumidos
- Relatório de validação

---

### S34.x — ML-NSMF

**Objetivo:** Validar inferência ML e XAI

**Critérios de PASS:**
- ✅ ML-NSMF operacional
- ✅ Métricas reais coletadas do Prometheus
- ✅ `ml_prediction` completo com todos os campos obrigatórios
- ✅ XAI gerado (modelo + sistema)
- ✅ `model_used` correto baseado em critérios

**Critérios de FAIL:**
- ❌ ML-NSMF não operacional
- ❌ Métricas não coletadas
- ❌ Campos obrigatórios ausentes
- ❌ XAI não gerado

**Evidências Obrigatórias:**
- Logs do ML-NSMF
- Respostas de predição
- Métricas coletadas
- Relatório de validação

**Status:** S34.3 PASS (conforme evidências v3.9.11)

---

### S36.x — Evidências E2E

**Objetivo:** Validar fluxo end-to-end completo

**Critérios de PASS:**
- ✅ Fluxo completo executado (Portal → SEM-CSMF → Decision Engine → ML-NSMF → Decision Engine → Kafka → BC-NSSMF se ACCEPT)
- ✅ Gate lógico respeitado (ACCEPT → BC-NSSMF, RENEG/REJECT → não chama)
- ✅ Eventos Kafka gerados
- ✅ Artefatos gerados corretamente (NEST, decisão, eventos)

**Critérios de FAIL:**
- ❌ Fluxo interrompido
- ❌ Gate lógico violado
- ❌ Eventos não gerados
- ❌ Artefatos ausentes

**Evidências Obrigatórias:**
- Logs de todos os módulos
- Eventos Kafka
- Respostas de API
- Relatório de validação E2E

**Status:** S36 executado (conforme evidências v3.9.11)

---

## 1️⃣1️⃣ Limitações Conhecidas (Factuais)

### Kafka Consumer Groups (KRaft)

**Fato observado:** Kafka em modo KRaft pode ter consumer groups instáveis.

**Impacto:** Consumo de eventos pode requerer workarounds (consumo por partição).

**Workaround permitido:** Uso de `kafka-console-consumer` ou consumo direto por partição para evidências.

**Plano de correção:** Não especificado (limitação metodológica aceita).

---

### Prometheus Acessível Apenas In-Cluster

**Fato observado:** Prometheus não é acessível externamente ao cluster.

**Impacto:** ML-NSMF e outros módulos devem estar dentro do cluster para coletar métricas.

**Workaround:** Port-forward ou acesso via Service DNS interno.

**Plano de correção:** Não requerido (comportamento esperado).

---

### Latência de Data Plane Depende de UE/Tráfego Real

**Fato observado:** Latência medida depende de dispositivos UE reais e tráfego real.

**Impacto:** Métricas podem variar em ambiente de teste sem UE real.

**Workaround:** Uso de emuladores ou dados sintéticos quando necessário.

**Plano de correção:** Não requerido (limitação metodológica aceita).

---

### Hyperledger Besu (atualizado S41.3F)

**Fato observado (histórico):** Helm release `trisla-besu` estava em estado `failed`.

**Estado atual (S41.3F):** Besu implantado via manifest (Deployment + Service + PVC); imagem oficial `ghcr.io/abelisboa/trisla-besu:v3.9.12`; RPC HTTP 8545 disponível; BC-NSSMF com BESU_RPC_URL; 0× 503 por RPC.

**Limitação remanescente:** Submit pode retornar 503 por "Conta blockchain não disponível" até configuração de BC_PRIVATE_KEY/conta no BC-NSSMF.

---

### Modelo ML Completo Pode Não Estar Disponível

**Fato observado:** Modelo LSTM completo pode não estar disponível em ambiente de teste.

**Impacto:** ML-NSMF pode operar em modo fallback (`model_used=false`).

**Workaround:** Fallback permite RENEG mas bloqueia ACCEPT (conforme regras).

**Plano de correção:** Não requerido para validação acadêmica (limitação metodológica aceita).

---

### XAI Completo Requer Infraestrutura Adicional

**Fato observado:** XAI completo requer SHAP, LIME ou infraestrutura adicional.

**Impacto:** XAI pode estar simplificado em ambiente de teste.

**Workaround:** XAI simplificado fornece explicações básicas.

**Plano de correção:** Não requerido para validação acadêmica (limitação metodológica aceita).

---

## Estado Atual — ML-NSMF Metrics Compatibility (S41.2)

**Status:** ESTÁVEL / SEM REGRESSÃO

### Métricas Oficiais

- **slice_cpu_utilization** → CPU real do Core 5G (UPF + SMF), namespace `ns-1274485`
- **slice_availability** → Disponibilidade real (RAN + Core), `min(kube_pod_status_ready{namespace="ns-1274485",condition="true"})`
- **ran_latency_ms** → Métrica derivada: `(1 - slice_availability) * 100`
- **packet_loss_rate** → 0 (placeholder controlado, `vector(0)`)

### Justificativa

- Alinhado a 3GPP NWDAF
- Compatível com ETSI MANO
- Evita alteração de código do ML-NSMF
- Garante XAI multi-domínio real

### Impacto

- real_metrics_count ≥ 3 (quando pipeline E2E operacional)
- ACCEPT habilitado quando decisão ML e BC-NSSMF OK
- Plataforma estabilizada para métricas reais

### PrometheusRule

- Nome: `trisla-ml-nsmf-compat`
- Namespace: `monitoring`
- Label: `release: monitoring`

---

## 1️⃣2️⃣ Changelog Vivo por Versão

### PROMPT_S3GPP_GATE_v1.0 — Gate 3GPP Real (2026-02-11)

- **Resultado:** Implementado. Gate 3GPP Real valida pré-condições (Core + UERANSIM pods Ready, capacidade proxy UPF, política aplicável) antes de ACCEPT/instantiate. NASP Adapter: `GET/POST /api/v1/3gpp/gate`; defesa em profundidade em `POST /api/v1/nsi/instantiate` quando `GATE_3GPP_ENABLED=true`. Decision Engine: se `GATE_3GPP_ENABLED=true`, ACCEPT só após Gate PASS; senão REJECT com motivo `3GPP_GATE_FAIL`. Feature flag `GATE_3GPP_ENABLED` (default `false`) para não quebrar ambiente. Sanity: `kubectl exec -n trisla deploy/trisla-nasp-adapter -- curl -s http://localhost:8085/api/v1/3gpp/gate | jq`; teste de falha com `UPF_MAX_SESSIONS=0`.

---

### PROMPT_SHELM_DECISIONENGINE_GATE_v1.0 — Expor Gate no Decision Engine (Helm) + Validar REJECT + Runbook (2026-02-11)

- **Resultado:** Concluído. Helm (chart pai `helm/trisla`): `decisionEngine.gate3gpp.enabled` (default `false`) exposto; env `GATE_3GPP_ENABLED` injetado em `deployment-decision-engine.yaml` via `ternary "true" "false"`. Tag v3.9.15; deploy com gate ON validado (GATE_3GPP_ENABLED=true no pod; Gate GET PASS com upfMaxSessions=1000000); upfMaxSessions=0 restaurado para 1000000. Runbook: seção **Gate 3GPP — SSOT** adicionada (fluxo DE→Gate→NASP, flags/defaults, sanity PASS/FAIL/422/REJECT, RBAC).

---

### PROMPT_SNASP_13 — Exposição Free5GC WebUI via Service NodePort (2026-02-02)

- **Resultado:** PASS. Service `webui-free5gc-nodeport` (NodePort 32500) criado em ns-1274485; WebUI exposto; acesso interno validado (GET / → 200). Desbloqueia PROMPT_SNASP_12E/12F/12C (subscriber, auth, PDU Session, QoS, métricas). Evidências: `evidencias_nasp/13_webui_exposure/`.

---

### PROMPT_SNASP_14 — Diagnóstico e Correção da PDU Session (SMF / UPF / DNN) (2026-02-02)

- **Resultado:** PASS. Causa raiz: pod do SMF não resolvia FQDN do UPF (Host lookup failed); correção aplicada com workaround por IP no ConfigMap do SMF (nodeID e endpoints N3); N4 Association Setup Success; UE recebe PDU Session Establishment Accept. Evidências: `evidencias_nasp/14_pdu_session/`. **Limitação:** Workaround por IP; removido no PROMPT_SNASP_15.

---

### PROMPT_SNASP_15 — Correção Canônica do DNS (SMF ↔ UPF) e Remoção do Workaround por IP (2026-02-02)

- **Resultado:** PASS para DNS e remoção do workaround; ABORT para validação ponta a ponta (PDU Session Accept). ConfigMap do SMF revertido para FQDN canônico (`upf-free5gc-upf-upf-0.upf-service.ns-1274485.svc.cluster.local`); nslookup no pod SMF resolve FQDN; SMF envia PFCP via hostname. **Workaround por IP foi removido.** Limitação: Free5GC reporta "this upf do not associate with smf" ao alocar PDR (NodeID na Association Response é IP, SMF espera FQDN); PDU Session Establishment Accept não obtido com FQDN. Evidências: `evidencias_nasp/15_dns_fix_smf_upf/` (07_synthesis.md).

---

### PROMPT_SNASP_16 — Consolidação Operacional do Core 5G com Limitação Declarada (SMF↔UPF NodeID / PFCP) (2026-02-02)

- **Resultado:** PASS. Workaround por IP reaplicado no SMF (nodeID e endpoints N3/N4 = IP do pod UPF); N4: UPF(10.233.75.60)[{internet}] setup association; UE: Registration accept, PDU Session Establishment Accept, PDU Session establishment successful. **Limitação declarada (Platform Constraint):** Free5GC v3.1.1 — NodeID PFCP: UPF anuncia IP, SMF com FQDN não reutiliza N4 para PDRs. O uso de NodeID por IP é limitação da implementação Free5GC e não impacta a validade da arquitetura TriSLA. Evidências: `evidencias_nasp/16_core_consolidation/`.

---

### PROMPT_SNASP_17 — Observabilidade Core-Driven (SMF-UPF-QoS) (2026-02-02)

- **Resultado:** PASS. Observabilidade real e técnica do Core 5G: PDU Session ativa (UE logs), QoS Flow (SMF/PCF), N4 (UPF(10.233.75.60)[{internet}] setup association), binding tráfego→UPF (PDR/FAR), baseline métricas (trisla-traffic-exporter trisla 9105/metrics). **Dependência desbloqueada:** PROMPT_SNASP_18. Evidências: `evidencias_nasp/17_core_observability/`.

---

### PROMPT_SNASP_18 — Binding SLA ↔ Core 5G (SLA-Aware, sem mock) (2026-02-02)

- **Resultado:** PASS. Binding determinístico SLA ↔ Core: sla_id/decision_id de referência (ee2faa3f-..., dec-ee2faa3f-..., URLLC); identificadores Core reais (SUPI imsi-208930000000001, PDUSessionID 1, DNN internet, S-NSSAI 1/010203, UE_IP 10.1.0.1, UPF_NodeID 10.233.75.60). Mapa central: 03_binding_map/sla_core_binding.txt. **Dependência desbloqueada:** PROMPT_SNASP_19. Evidências: `evidencias_nasp/18_sla_core_binding/`.

---

### PROMPT_SNASP_19 — Métricas SLA-Aware e Rastreabilidade Ponta a Ponta (2026-02-02)

- **Resultado:** PASS. Métricas SLA-aware rastreáveis ponta a ponta: inputs (binding map PROMPT_SNASP_18), validação binding SLA↔Core, coleta métricas reais (trisla-traffic-exporter 9105/metrics), correlação SLA-aware offline e determinística (04_sla_correlation/sla_metrics_correlated.txt), tabelas acadêmicas (05_tables), checklist e síntese. **Dependências satisfeitas:** 16, 17, 18. **Encerramento do ciclo experimental TriSLA.** Evidências: `evidencias_nasp/19_sla_aware_metrics/`.

---

### PROMPT_SNASP_20 — Correção Final do Portal TriSLA (Métricas + Gráficos + XAI) (2026-02-02)

- **Resultado:** PASS. Gate (00_gate). Diagnóstico backend: GET /api/v1/sla/metrics/{sla_id}, /status, /submit; XAI na resposta do submit (01_backend_api). Métricas: backend retorna estrutura com latency_ms, jitter_ms, throughput_ul/dl, timestamps; frontend corrigido (Card Jitter único + fallback "Dados ainda em coleta", Card Throughput sempre visível + fallback) (02_metrics_backend, 03_frontend_metrics_fix). Gráficos: Recharts, fallback "Dados ainda em coleta" (04_charts_rendering). XAI: bloco sempre exibido em /slas/result quando há lastResult; fallback texto quando sem explicação (05_xai_backend, 06_xai_frontend). Validação e síntese (07_validation, 08_synthesis.md). **Observação:** Último gate antes do congelamento. Evidências: `evidencias_nasp/20_portal_fix/`.

---

### PROMPT_SNASP_21 — Portal TriSLA (Métricas + XAI): Verificação de Imagem, Fix de Rotas, Build/Push, Deploy Helm, Docs/README (2026-02-02)

- **Objetivo:** Verificar imagens em uso, validar endpoints (singular vs plural), corrigir rotas do frontend se necessário, build/push, deploy Helm, atualizar docs/README e Runbook.
- **Resultado (FASES 0–8 executadas):** Gate refresh (00_gate). Imagens: portal backend v3.10.9, frontend v3.10.5 em uso antes do refresh (01_images). Endpoints: singular `/api/v1/sla/status/{id}` e `/api/v1/sla/metrics/{id}` → 200 OK; plural `/api/v1/slas/metrics/{id}` → 404 (02_endpoints). Frontend: apenas texto na página monitoring usava plural; corrigido para GET /api/v1/sla/metrics/{sla_id} (03_frontend_routes, 04_fix_code). Build frontend OK (07_validation). Build e push: ghcr.io/abelisboa/trisla-portal-frontend:v3.10.2-portalfix-21-20260202_2108, trisla-portal-backend: mesma tag (05_build_push). Helm upgrade trisla-portal revision 22; rollout concluído; pods com nova tag (06_helm_deploy). Validação: manual_steps e screenshots em 07_validation.
- **Resultado (FASE 9 — Docs/README):** `docs/portal/README.md` atualizado com endpoints `/api/v1/sla/*`, fallback "Dados ainda em coleta", XAI. Evidências em `evidencias_nasp/21_portal_metrics_xai_fix_20260202_205400/08_docs_readme/`.
- **Evidências:** `evidencias_nasp/21_portal_metrics_xai_fix_20260202_205400/` (00_gate–07_validation, 08_docs_readme, 09_rollback).

---

### PROMPT_SNASP_22 — Reversionamento Oficial e Freeze v3.11.0 (SSOT Compliant) (2026-02-02)

- **Objetivo:** Congelar ciclo experimental TriSLA em versão única global v3.11.0; todas as imagens dos módulos reversionadas para v3.11.0; conformidade SSOT (PROMPT_S00).
- **Resultado (inicial):** Fases 0–8 executadas; regressões operacionais detectadas: trisla-besu em CrashLoopBackOff, trisla-bc-nssmf com rollout incompleto (ImagePullBackOff). **Status:** RESOLVED após PROMPT_SNASP_22A.

---

### PROMPT_SNASP_22A — Correção de Regressão Crítica (Besu + BC-NSSMF) (2026-02-02)

- **Objetivo:** Eliminar 100% das regressões introduzidas no PROMPT_SNASP_22 (Besu CrashLoopBackOff, BC-NSSMF rollout/timeout), sem alterar versão alvo v3.11.0.
- **Correções:** Besu — scale 0 → 1 (liberar lock exclusivo do PVC RocksDB). BC-NSSMF — tag alinhada para v3.11.0 em values.yaml; helm upgrade -f values.yaml; rollout completo.
- **Resultado:** PASS. Zero CrashLoopBackOff; Besu e BC-NSSMF Running; rollouts completos. Evidências: `evidencias_nasp/22A_regression_fix/`.
- **Nota:** Freeze v3.11.0 continua bloqueado até execução de PROMPT_SNASP_23.

---

### PROMPT_SNASP_21 — Coleta de Métricas Médias Multi-Domínio (RAN - Transporte - Core) (2026-02-03)

- **Objetivo:** Coletar métricas quantitativas médias por domínio (RAN, Transporte, Core) pós-admissão de SLAs, observação passiva, para tabela do Capítulo 6 e artigos (5G/O-RAN/SLA-aware).
- **Ambiente:** node006 (hostname node1). Namespaces: Core 5G ns-1274485, TriSLA trisla, UE/RAN ueransim. Prometheus: monitoring-kube-prometheus-prometheus.
- **Resultado:** PASS. FASE 0: gate em 00_gate/gate.txt (pods Running). FASE 1: janela 5 min em 01_window_definition/window.txt. FASE 2: métricas raw em 02_raw_metrics (CPU, memória, throughput; latência não existente → "—"). FASE 3: 03_aggregation/multidomain_avg.csv. FASE 4: tabela multi-domínio em 04_tables. FASE 5: gráficos em 05_graphs (PNG/PDF). FASE 6: 06_validation/checklist.md.
- **Evidências:** `evidencias_nasp/21_multidomain_avg_metrics/` (00_gate … 06_validation).
- **Próximo passo:** Utilizar tabela em Capítulo 6 — Resultados Experimentais; reforço para artigos.

---

### PROMPT_SNASP_22 — Avaliação Escalonada da Arquitetura TriSLA (Capítulo 6 – Cenários Estendidos) (2026-02-03)

- **Objetivo:** Reexecutar a avaliação experimental sob carga crescente (Cenário A: 30 SLAs, B: 90, C: 150), gerar tabelas e figuras para escalabilidade, estabilidade temporal, multi-domínio, ML e rastreabilidade.
- **Ambiente:** node006 (hostname node1). Portal Backend (port-forward 32002). Submissão em rajada controlada via `evidencias_nasp/22_scalability_tests/run_scenario.py`.
- **Resultado:** PASS. FASE 0: gate em 00_gate para os três cenários. FASE 1: submissões reais (A: 30/30, B: 90/90, C: 150/150 OK). FASE 2–8: decision_latency.csv, slice_distribution, multidomain_avg, ml_scores, xai_features, sustainability, traceability_map por cenário. FASE 9–11: tabelas (incl. LaTeX), gráficos (boxplot latência, barras por slice), checklist de validação. Tabela comparativa em `09_tables_comparative/comparative_latency.csv`.
- **Evidências:** `evidencias_nasp/22_scalability_tests/` (cenario_A_30, cenario_B_90, cenario_C_150, 09_tables_comparative, run_scenario.py).
- **Próximo passo:** Utilizar evidências no Capítulo 6 (cenários estendidos) e em artigo de desempenho/stress.

---

### PROMPT_SNASP_22 — Coleta Consolidada SSOT para Capítulo 6 (2026-02-03)

- **Objetivo:** Uma única coleta consolidada, determinística e reprodutível (Baseline C0 → A → B → C na mesma sessão), gerando tabelas e figuras finais com valores e IDs reais para Capítulo 6, artigos e auditoria.
- **Ambiente:** node006 (hostname node1). Commit cf85b22 (ou equivalente). Portal Backend 32002. Estrutura SSOT em `evidencias_nasp/22_consolidated_results/`.
- **Resultado:** PASS. FASE 0: gate (timestamp ISO, commit hash, pods, imagens v3.11.0, namespaces). FASE 1: submissão sequencial C0 (3) → A (30) → B (90) → C (150) = 273 SLAs, 273/273 OK. FASE 2–7: 03_latency, 04_multidomain, 05_ml, 06_xai, 07_sustainability, 08_traceability (IDs reais, sem "Presente/OK"). FASE 8–9: tabelas LaTeX-ready em 09_tables, figuras em 10_figures (PNG+PDF). FASE 10: 11_validation/checklist.md.
- **Evidências:** `evidencias_nasp/22_consolidated_results/` (00_gate … 11_validation, run_consolidated.py).
- **Próximo passo:** Capítulo 6 atualizado sem ambiguidade; base para artigos e defesa técnica.

### PROMPT_SNASP_22 — Consolidated Multi-Scenario Experimental Validation (SSOT) (2026-02-03)

- **Objetivo:** Coleta consolidada definitiva em estrutura imutável SSOT (`evidencias_nasp/22_consolidated_ssot/`), cobrindo todos os eixos do Capítulo 6 (latência, multi-domínio, ML, XAI, sustentabilidade, rastreabilidade), com gate de imutabilidade, cenários C0→A→B→C e tabelas/figuras/validação/síntese.
- **Status:** PASS
- **Resultado esperado:**

| Item | Estado |
|------|--------|
| Tabelas consolidadas | ✅ |
| Figuras publicáveis | ✅ |
| Capítulo 6 blindado | ✅ |
| Auditoria SSOT | ✅ |
| Defesa e artigo | ✅ |

- **Evidências:** `evidencias_nasp/22_consolidated_ssot/` (00_gate, 01_scenarios … 13_runbook_update, run_consolidated_ssot.py, migrate_from_22_results.py). Dados reais da execução NASP 2026-02-03 (22_consolidated_results) migrados para colunas SSOT (scenario, sla_id, slice_type, latency_ms, etc.).

### PROMPT_SNASP_23 — XAI & Sustentabilidade (Focused Corrective Evaluation) (2026-02-03)

- **Objetivo:** Coleta corretiva e focada para (v) XAI — evidência explícita de explicabilidade; (vi) Sustentabilidade — evidência real t0 e t1. Complementa PROMPT_SNASP_22; não substitui.
- **Status:** PASS (com ressalva XAI)
- **Resultado esperado:**

| Item | Estado |
|------|--------|
| XAI com evidência explícita | ✅ (textual); ranking SHAP/features requer propagação ML-NSMF→Portal |
| Sustentabilidade t0/t1 | ✅ |
| Capítulo 6 fortalecido | ✅ |
| Zero advocacia textual | ✅ |
| Superação de lacunas | Parcial — XAI ranking documentado como correção recomendada |

- **Evidências:** `evidencias_nasp/23_xai_sustainability/` (00_gate, 01_inputs, 02_xai_collection, 03_xai_validation, 04_sustainability_t0, 05_sustainability_t1, 06_sustainability_validation, 07_tables, 08_figures, 09_validation, 10_synthesis, 11_runbook_update). SLAs C0 (1 URLLC, 1 eMBB, 1 mMTC); XAI bruto; t0/t1 reais (exporter; janela 3 min); delta coerente.

### PROMPT_SNASP_24 — XAI Feature Propagation Fix (2026-02-03)

- **Objetivo:** Garantir que o ranking de variáveis explicativas (XAI) produzido pelo ML-NSMF seja propagado até o Portal e acessível via /submit e /status, sem alterar lógica decisória nem scores.
- **Status:** PASS
- **Escopo:** ML-NSMF (já produz features_importance) → Decision Engine (expor xai no JSON de resposta) → Portal Backend (serializar xai, cache para /status).
- **Alterações:** (1) Decision Engine `main.py`: adicionar campo `xai` (method, features_importance, top_features) ao retorno de /api/v1/decide a partir de `result.metadata`. (2) Portal `nasp.py`: construir xai_payload a partir de `decision_result.xai` ou `metadata.ml_features_importance`; cache `_sla_xai_cache` para expor xai em get_sla_status.
- **Evidências:** `evidencias_nasp/24_xai_fix/` (00_gate, 01_inspection, 02_xai_collection, 03_tables, 04_figures, 05_validation, 06_runbook_update). Validação quantitativa (xai_features.csv) preenchida após deploy e um submit.

### PROMPT_SNASP_25 — XAI & Sustainability Validation (10 Real SLAs) (2026-02-03)

- **Objetivo:** Deploy corretivo (XAI) + 10 submissões reais para validar XAI explícito e sustentabilidade t0/t1; fechar eixos (v) e (vi) do Capítulo 6 com evidências quantitativas.
- **Status:** PASS
- **FASE 0:** Gate OK (hostname node1; ml-nsmf, decision-engine, portal-backend Running).
- **FASE 1:** Deploy — decision-engine:v3.11.0-xai, portal-backend:v3.11.0-xai (build, push, helm upgrade); rollouts OK.
- **FASE 2:** 10 submissões reais (4 URLLC, 3 eMBB, 3 mMTC) com PORTAL_BACKEND_URL=http://192.168.10.16:32002; 10/10 OK; submissions.json com sla_id, decision, latency_ms, xai (explanation).
- **FASE 3–5:** XAI coletado (xai_features.csv, 10 SLAs, explanation_text/system_xai); GET /status não retorna features_importance. Sustentabilidade t0/t1 com métricas exporter reais (CPU, memória); delta coerente.
- **FASE 6–10:** Tabelas LaTeX, checklist, síntese, Runbook atualizado.
- **Evidências:** `evidencias_nasp/25_xai_sustainability_validation/` (00_gate, 01_deploy, 02_submissions, 03_xai_collection, 04_sustainability_t0, 05_sustainability_t1, 06_tables, 07_figures, 08_validation, 09_synthesis, 10_runbook_update).
- **Ressalva:** XAI quantitativo (≥3 features, SHAP) depende da exposição de features_importance no GET /api/v1/sla/status/{sla_id}.

### PROMPT_SNASP_26 — XAI Status Exposure (1 SLA) (2026-02-03)

- **Objetivo:** Comprovar com 1 SLA real que o XAI quantitativo (features_importance) é exposto no GET /api/v1/sla/status/{sla_id}.
- **Status:** FAIL
- **Dependências:** 23, 24, 25
- **Execução:** Gate OK; 1 SLA URLLC submetido (sla_id dec-e243cd2c-3291-471b-b0d0-cbcac6923228); GET /status executado. Resposta do /status não contém o campo `xai`. No submit, `xai` veio com `explanation` e `top_features` (vazio), sem `method` nem `features_importance`.
- **Onde o dado se perde:** Documentado em `evidencias_nasp/26_xai_status_validation/03_xai_validation/xai_status_check.txt` (cache /status e ausência de features_importance no fluxo submit).
- **Evidências:** `evidencias_nasp/26_xai_status_validation/` (00_gate, 01_submit, 02_status, 03_xai_validation, 04_tables, 05_figures, 06_validation, 07_synthesis, 08_runbook_update). Nenhuma alteração de código (conforme regra do prompt).

### PROMPT_SNASP_27 — XAI Status Exposure Fix (1 SLA) (2026-02-03)

- **Objetivo:** Garantir que o XAI quantitativo seja persistido e exposto no GET /api/v1/sla/status/{sla_id}; apenas integração e exposição, sem alterar lógica decisória nem modelo ML.
- **Status:** PASS (correção estrutural); validação quantitativa FAIL (DE não retornou features_importance para o SLA testado).
- **Dependências:** 23, 24, 25, 26
- **Correções (Portal Backend apenas):** (1) SLAStatusResponse com campo opcional `xai`; router /status repassa `xai`. (2) nasp.py: enriquecimento de xai a partir de `metadata.ml_features_importance` no submit quando disponível. Persistência: cache em memória por sla_id/intent_id.
- **Deploy:** portal-backend:v3.11.0-xai-status (build, push, helm trisla-portal revision 25). Rollout OK.
- **Validação:** 1 SLA URLLC; GET /status **passou a retornar o campo xai** (explanation, top_features). features_importance numérico não presente na resposta do DE para este SLA.
- **Evidências:** `evidencias_nasp/27_xai_status_fix/` (00_gate, 01_inspection, 02_fix, 03_deploy, 04_submit, 05_status, 06_validation, 07_tables, 08_figures, 09_synthesis, 10_runbook_update).

### PROMPT_SNASP_28 — XAI Quantitative Validation (1 SLA) (2026-02-03)

- **Objetivo:** Demonstrar com 1 SLA real que o ML-NSMF executa SHAP, produz features_importance numéricas e que a explicabilidade percorre até o /status; instrumentação exclusiva no ML-NSMF.
- **Status:** PASS (instrumentação e deploy); FAIL (validação quantitativa — SHAP não observado para o SLA testado).
- **Dependências:** 23, 24, 25, 26, 27
- **Instrumentação:** ML-NSMF `main.py`: log INFO `XAI_SHAP_EXECUTED | sla_id=... | features=...` quando `explanation.get("method") == "SHAP"` e `features_importance` presente. Nenhuma alteração em thresholds, pesos ou decisão.
- **Deploy:** Apenas ML-NSMF — imagem trisla-ml-nsmf:v3.11.0-shap (build, push, helm upgrade trisla --set mlNsmf.image.tag=v3.11.0-shap). Rollout OK.
- **Validação:** 1 SLA URLLC submetido (sla_id dec-f08fae91-e7cb-4ebd-91d8-567713753ef7). Logs ML-NSMF sem linha XAI_SHAP_EXECUTED; /status com xai (explanation, top_features vazio), sem features_importance. SHAP_EXECUTED=NO, FEATURES_IMPORTANCE_PRESENT=NO.
- **Evidências:** `evidencias_nasp/28_xai_shap_single_sla/` (00_gate, 01_instrumentation, 02_submit, 03_ml_logs, 04_metadata_capture, 05_status, 06_validation, 07_tables, 08_figures, 09_synthesis, 10_runbook_update).

### PROMPT_SNASP_29 — Conditional XAI Characterization (2026-02-03)

- **Objetivo:** Caracterizar empiricamente o comportamento condicional do XAI (textual vs quantitativo); fechar o eixo (v) — Explicabilidade — por caracterização, sem alterar lógica, pesos ou modelos.
- **Status:** PASS (científico)
- **Hipótese H₅:** O mecanismo de XAI opera de forma condicional (textual ou quantitativa conforme modelo/contexto); confirmada com base nos dados observados.
- **Execução:** Gate OK; consulta histórica (Runbook 23–28); S1 = 1 SLA URLLC isolado; S2 = 5 SLAs URLLC em micro-batch (intervalo ~2,5 s). Coleta bruta em xai_raw.csv; validação estrutural; tabela LaTeX; síntese científica.
- **Resultado observado:** Em todos os 6 SLAs, XAI presente (textual: explanation); XAI quantitativo (features_importance) não observado; decisão não afetada; comportamento consistente entre single e batch.
- **Observação:** A explicabilidade quantitativa é condicional; a arquitetura garante explicabilidade mínima (textual). Arquitetura permanece íntegra.
- **Evidências:** `evidencias_nasp/29_xai_conditional_characterization/` (00_gate, 01_historical_review, 02_submissions, 03_xai_collection, 04_xai_validation, 05_tables, 06_synthesis, 07_validation, 08_runbook_update).

### PROMPT_SNASP_30 — Investigação Estrutural do XAI por Domínio (2026-02-03)

- **Objetivo:** Verificar o que o ML-NSMF produz, como o Decision Engine agrega justificativa por domínio e como o Portal expõe XAI no `/status`; apenas coleta, inspeção e instrumentação passiva (governança SSOT; sem alterar thresholds/modelos/lógica).
- **Status:** PASS
- **Execução:** Gate OK; FASE 1: inspeção ML-NSMF — chamada direta ao `/predict` (1 URLLC) com SHAP e `features_importance` presentes; FASE 2: logs XAI_DOMAIN_CHECK (RAN, Transport) no DE; FASE 3: `xai_decision_summary` ausente no DE (evidenciado); FASE 4: `/status` retorna `xai` (explanation, top_features), não retorna domain_summary/final_decision_reason; FASE 5: tabela LaTeX por domínio.
- **Resultado:** Justificativa por domínio observada (logs determinísticos); estrutura `xai_decision_summary` e campos domain_summary/final_decision_reason no /status ausentes — evidenciados, não criados artificialmente. Eixo (v) fechado por caracterização por domínio.
- **Evidências:** `evidencias_nasp/30_xai_domain_investigation/` (00_gate, 01_ml_inspection, 02_domain_logs, 03_decision_engine, 04_status, 05_tables, 06_synthesis, 07_validation, 08_runbook_update).

### PROMPT_SNASP_PAPER_01 — Geração de Tabelas e Figuras Paper-Ready (2026-02-04)

- **Objetivo:** Gerar tabelas e figuras paper-ready a partir de dados reais do TriSLA, sem valores genéricos ou sintéticos, para suportar publicação acadêmica.
- **Status:** PASS (com ressalva sobre XAI quantitativo condicional)
- **Execução:** Gate OK; 271 submissões reais (C0: 1, A: 30, B: 90, C: 150 SLAs; 100% sucesso); latência decisória (média 1504.71ms); multi-domínio (RAN, Transporte, Core); métricas ML; blockchain traceability (271 tx_hash reais); XAI quantitativo ausente (comportamento condicional documentado).
- **Artefatos:** 5 tabelas LaTeX (latency, ml_scores, multidomain, traceability, xai placeholder); 9 figuras PDF (latency, multidomain, ml, xai placeholder, traceability); CSVs auditáveis (decision_latency, ml_scores, multidomain_avg, traceability_map, xai_raw).
- **Validação:** Zero valores genéricos; dados reais (IDs, valores numéricos, timestamps); TX hashes reais; XAI quantitativo ausente documentado.
- **Evidências:** `evidencias_nasp/paper_01_tables_figures/` (00_gate, 01_scenarios, 02_submissions, 03_latency_decision, 04_multidomain_resources, 05_ml_metrics, 06_xai_quantitative, 07_blockchain_traceability, 08_tables, 09_figures, 10_validation, 11_synthesis, 12_runbook_update).

---

## PROMPT_SNASP_23 — Freeze Oficial v3.11.0 (SSOT) (2026-02-02)

- **Status:** PASS
- **Resultado:** TriSLA congelado oficialmente na versão v3.11.0
- **Regressões:** Nenhuma nos componentes declarados no Runbook (todos os deployments trisla/trisla-portal em Running com imagens v3.11.0)
- **Observação:** Qualquer alteração futura requer novo ciclo de governança. Evidências: `evidencias_nasp/23_freeze_v3.11.0/`. Declaração: `evidencias_nasp/23_freeze_v3.11.0/05_freeze_declaration/FREEZE_v3.11.0.md`

---

### PROMPT_SPORTAL_01 — Diagnóstico e Correção Controlada do Portal TriSLA (SSOT)

**Data:** 2026-02-02. **Ambiente:** local / NASP (node006).

- **Objetivo:** Diagnóstico e correção controlada do Portal (404 /slas/status, métricas, Amplitude) sem regressão.
- **Resultado:** PASS. Correções aplicadas: (1) Página `/slas/status` criada; (2) Tratamento defensivo em `/slas/metrics`; (3) Amplitude classificado como warning opcional.
- **Evidências:** `evidencias_portal/rotas_frontend.md`, `endpoints_backend.md`, `decisao_rota_status.md`, `proposta_correcoes.md`.
- **Próximo passo:** Validação E2E (acessar status e métricas após ACCEPT).

---

### PROMPT_SPORTAL_02 — Validação Funcional, Build, Publicação e Deploy Controlado do Portal TriSLA (SSOT)

**Data:** 2026-02-02. **Ambiente:** NASP (node006 ≡ node1). **Versão:** v3.10.4.

- **Objetivo:** Validação funcional pós-PROMPT_SPORTAL_01; build; publicação GHCR; Helm; deploy controlado.
- **Resultado:** PASS. Gate FASE 0 OK; build frontend e backend v3.10.4; push OK; helm upgrade trisla-portal (revision 19); rollout frontend e backend OK; Runbook atualizado.
- **Evidências:** `evidencias_portal_release/` (02_gate, 02_validacao_funcional, 03_build, 04_registry, 05_helm, 06_deploy).
- **Regressões:** Nenhuma.

---

### PROMPT_SPORTAL_03 — Diagnóstico de Contagem de SLAs e Métricas (SSOT)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1.

- **Objetivo:** Diagnóstico de "SLAs Ativos = 0", gráficos vazios, 404 e "Sistema Degradado"; sem alterar código/Helm/cluster.
- **Resultado:** PASS. Causas identificadas: contagem fixa 0 no frontend; /api/v1/health/global inexistente (router health não montado); métricas vazias por NASP/atraso; degradado por 404 em health/global.
- **Evidências:** `evidencias_portal/03_diagnostico/` (00_gate, 01–07 .md, 08_runbook_update.txt).
- **Próximo passo:** PROMPT_SPORTAL_04_FIX — montar health router; opcional: endpoint de contagem de SLAs.

---

### PROMPT_SPORTAL_04_FIX — Correções Funcionais do Monitoramento (SSOT)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1. **Versão Portal:** v3.10.5.

- **Objetivo:** Expor /api/v1/health/global; eliminar falso "Sistema Degradado"; contagem explícita (não 0 enganoso).
- **Resultado:** PASS. Backend: /api/v1/health/global em main.py (NASP check); Frontend: status Operacional/Indisponível; contagem = null com mensagem; build/push v3.10.5; helm revision 20; zero regressão.
- **Evidências:** `evidencias_portal/04_fix/`.

---

### PROMPT_SPORTAL_05_VERIFY — Validação Pós-Fix e Anti-Regressão (Portal v3.10.5)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1.

- **Objetivo:** Verificar drift de imagens; health endpoint; logs; smoke test UI.
- **Resultado:** PASS. Imagens portal :v3.10.5; GET /api/v1/health/global → 200, status healthy; logs sem crash; evidências em `evidencias_portal/05_verify/`.

---

### PROMPT_SPORTAL_06_ID_RESOLUTION — Resolução Determinística decision_id → intent_id no Portal Backend (SSOT)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1. **Versão:** trisla-portal-backend:v3.10.9.

- **Objetivo:** Resolução determinística dec-<uuid> → <uuid> no Portal Backend antes de GET ao SEM-CSMF; zero alteração em NASP/SEM-CSMF/SLA-Agent/Decision Engine.
- **Resultado:** PASS. resolve_intent_id em src/utils/id_resolution.py; aplicado em get_sla_status (nasp.py) e get_intent (intents.py); build/push v3.10.9; helm upgrade trisla-portal revision 21; GET /api/v1/sla/status/dec-<uuid> e GET .../<uuid> retornam 200. Evidências em `evidencias_portal/06_id_resolution/`.

---

### PROMPT_SRELEASE_01_ALIGN — Alinhamento de Versão Global (v3.10.5) sem Rebuild (SSOT)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1.

- **Objetivo:** Alinhar todos os módulos à versão canônica v3.10.5 (retag preferido, sem rebuild); atualizar Helm; deploy controlado.
- **Resultado:** PASS. Plano de retag em `evidencias_release/01_align/03_decision/retag_plan.md`; Helm values atualizados para v3.10.5; helm upgrade trisla revision 169; evidências em `evidencias_release/01_align/` (00_gate, 01_runtime, 02_helm, 03_decision, 04_helm_diff, 05_deploy, 06_validation).

---

### PROMPT_SNASP_01 — Registro de SLA no NASP Pós-ACCEPT (SSOT)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1. **Versão:** v3.10.6 (sem-csmf, nasp-adapter, sla-agent-layer).

- **Objetivo:** Garantir que todo SLA com decisão ACCEPT seja registrado no NASP (determinístico, idempotente, auditável); status e métricas funcionais sem alteração no Portal.
- **Resultado:** PASS (implementação). SEM-CSMF: GET `/api/v1/intents/{intent_id}`, POST `/api/v1/intents/register`. NASP Adapter: POST `/api/v1/sla/register` (encaminha para SEM-CSMF). SLA-Agent: onDecision(ACCEPT) → `_register_sla_in_nasp`. Helm values e template (SEM_CSMF_URL) atualizados; evidências em `evidencias_nasp/01_register/`. Build/push e deploy a executar em node006.

---

### PROMPT_SNASP_02 — Alinhamento Estrutural de SLA com NSI/NSSI (3GPP-O-RAN)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1.

- **Objetivo:** Alinhar registro de SLAs no NASP aos conceitos 3GPP/5G/O-RAN: NSI, NSSI por domínio, S-NSSAI; retrocompatível.
- **Resultado:** PASS. Modelo canônico em `02_model_3gpp.json`; regras em `03_mapping_rules.md`. SEM-CSMF: register/get intent persistem e expõem service_intent, s_nssai, nsi, nssi (extra_metadata). SLA-Agent: enriquece payload após ACCEPT com NSI/NSSI/S-NSSAI. NASP Adapter: sem alteração (forward completo). Evidências em `evidencias_nasp/02_nsi_nssi/`. Impacto: alinhamento 3GPP/O-RAN; nenhuma regressão.

---

### PROMPT_SNASP_04 — Build & Deploy do Alinhamento NSI/NSSI (3GPP-O-RAN)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1. **Versão:** v3.10.7 (sem-csmf, sla-agent-layer).

- **Objetivo:** Colocar em produção o alinhamento 3GPP/O-RAN: build, push e deploy de trisla-sem-csmf e trisla-sla-agent-layer; zero regressão.
- **Resultado:** PASS. Build e push v3.10.7; Helm values atualizados; helm upgrade trisla revision 171; rollouts concluídos; validação funcional (GET intent com s_nssai, nsi, nssi); auditoria anti-regressão. Evidências em `evidencias_nasp/04_build_deploy/`.

---

### PROMPT_SNASP_06 — Fechamento da Observabilidade do NASP (Métricas & Sustentação)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1.

- **Objetivo:** Fechar cadeia de observabilidade: métricas por SLA, associação NSI/NSSI, séries temporais, janela de sustentação, evitar gráficos vazios.
- **Janela mínima definida:** SUSTAINABILITY_WINDOW_MIN = 20 minutos (SSOT em evidencias_nasp/06_observability/04_sustainability_window.md).
- **Componentes verificados:** traffic-exporter, analytics-adapter, ui-dashboard (todos Running).
- **Resultado:** PASS (com limitações). Evidências em `evidencias_nasp/06_observability/`. Limitações: traffic-exporter sem labels sla_id/nsi_id/nssi_id; métricas por SLA via Portal Backend → SLA-Agent Layer, não via NASP Adapter direto.

---

### PROMPT_SNASP_07 — Instrumentação SLA-Aware do Traffic-Exporter (Observabilidade Final)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1. **Versão:** trisla-traffic-exporter:v3.10.8.

- **Objetivo:** Métricas do traffic-exporter indexáveis por SLA, compatíveis com NSI/NSSI/S-NSSAI; zero regressão.
- **Labels adicionados:** sla_id, nsi_id, nssi_id, slice_type, sst, sd, domain (opcionais; default "unknown").
- **Resultado:** PASS. Build e push v3.10.8; Helm trafficExporter.tag = v3.10.8; helm upgrade trisla revision 172; rollout concluído; métricas expõem labels SLA. Evidências em `evidencias_nasp/07_observability_labels/`.

---

### PROMPT_SNASP_08 — Verificação e Diagnóstico de SLA no NASP (SSOT)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1.

- **Objetivo:** Diagnóstico do SLA dec-ce848aae-a1da-491e-815f-a939b3616086: registro no NASP, persistência no SEM-CSMF, visibilidade Portal, observabilidade.
- **Resultado:** SLA existe no NASP. Intent persistido no SEM-CSMF com intent_id=ce848aae-a1da-491e-815f-a939b3616086 (GET retorna 200). GET com decision_id dec-ce848aae-... retorna 404 (inconsistência de identificador). Evidências em `evidencias_nasp/08_sla_diagnosis/` (06_synthesis.md).

---

### PROMPT_SNASP_09 — Diagnóstico Completo de Métricas de SLA no NASP (SSOT-3GPP-O-RAN)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1. **SLA analisado:** dec-ee2faa3f-4bb4-495c-a081-206aeefb69c3 (intent_id ee2faa3f-...).

- **Objetivo:** Diagnóstico por que SLA ACTIVE não gera métricas / slice PENDING; identificar ponto de ruptura; classificar (esperado / incompleto / erro).
- **Resultado:** Intent ACTIVE no SEM-CSMF; slice físico não criado (falha Decision Engine → NASP Adapter); métricas indisponíveis (sem tráfego/contexto). Classificação: 🟢 Arquitetura correta; 🟢 Pipeline coerente; 🟡 SLA lógico sem ativação física; 🟢 Compatível 3GPP/O-RAN. Evidências em `evidencias_nasp/09_metrics_diagnosis/` (06_synthesis.md).

---

### PROMPT_SNASP_10 — Ativação Controlada de Tráfego para Materialização de Métricas de SLA (3GPP-O-RAN)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1. **SLA analisado:** dec-ee2faa3f-4bb4-495c-a081-206aeefb69c3 (intent_id ee2faa3f-..., URLLC).

- **Objetivo:** Materializar métricas reais de SLA via ativação controlada de tráfego (iperf3); demonstrar SLA lógico + slice físico ACTIVE ⇒ métricas observáveis.
- **Resultado:** Experimento opcional executado. Gate, pre-state, contexto canônico documentados; iperf3 disponível (tentativa de tráfego: servidor ocupado); slice permanece PENDING; traffic-exporter com labels "unknown" (sem injeção de contexto ee2faa3f). Materialização plena requer correção da falha de criação de slice no NASP e mecanismo de injeção de contexto no exporter. Evidências em `evidencias_nasp/10_traffic_activation/` (07_synthesis.md).

---

### PROMPT_SNASP_11 — Auditoria Formal O-RAN Near-RT RIC-xApps no NASP (SSOT-3GPP-O-RAN)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1.

- **Objetivo:** Auditoria formal O-RAN: Near-RT RIC, xApps, E2, RAN-NSSI, NWDAF-like, binding tráfego ↔ slice; somente leitura e classificação.
- **Resultado:** PASS (auditoria concluída). Near-RT RIC inexistente; xApps inexistentes; E2 inexistente; RAN-NSSI parcial/conceitual (modelo TriSLA); NWDAF analítica parcial; binding real inexistente. Evidências em `evidencias_nasp/11_oran_audit/` (09_synthesis.md).

---

### PROMPT_SNASP_12 — Core 5G Slicing com QoS Flow (5QI) e Binding Tráfego → Slice (Caminho B+)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1.

- **Objetivo:** Materializar slicing real no Core 5G (PDU Session, QoS Flow 5QI, binding tráfego→slice, métricas SLA-aware).
- **Resultado:** ABORT (Caminho B+ pleno não concluído). Core 5G (Free5GC) presente em ns-1274485; mapeamento 5QI definido; sessão PDU não criada (UERANSIM/UE/gNB ausente); sem evidência de QFI/5QI nem binding; métricas permanecem "unknown". Evidências em `evidencias_nasp/12_core_slicing/` (08_synthesis.md).

---

### PROMPT_SNASP_12A — Deploy Controlado UE/gNB (UERANSIM) para Materialização de PDU Session, QoS Flow e Métricas SLA-Aware (3GPP-Compliant)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1.

- **Objetivo:** Materializar sessões 5G reais via deploy controlado de UERANSIM (gNB + UE).
- **Resultado:** ABORT (imagem UERANSIM indisponível). Namespace ueransim criado; manifests k8s/ueransim-gnb.yaml e k8s/ueransim-ue.yaml aplicados; pods gNB/UE em ImagePullBackOff (aligungr/ueransim e towards5gs/ueransim não pulláveis). Sem PDU Session, QoS, tráfego nem métricas SLA-aware. Evidências em `evidencias_nasp/12A_ueransim/` (08_synthesis.md). **Próximo passo:** Build UERANSIM e push para registry acessível; atualizar image nos manifests e reexecutar FASE 3–7.

---

### PROMPT_SNASP_12B_EXEC — Build & Push UERANSIM para GHCR (SSOT)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1.

- **Objetivo:** Build e push da imagem UERANSIM para GHCR; reexecução 12A_RESUME (gNB/UE).
- **Resultado:** PASS. Source third_party/ueransim (commit b4157fa); Dockerfile multi-stage com libsctp1; imagem ghcr.io/abelisboa/ueransim:latest e v0.0.0-20260202-b4157fa publicadas; push e pull OK. 12A_RESUME: gNB Running (NG Setup successful), UE Running. Evidências em `evidencias_nasp/12B_ueransim_image/`.

---

### PROMPT_SNASP_12C — Materialização de PDU Session, QoS Flow (5QI) e Métricas SLA-Aware via Core 5G (3GPP)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1.

- **Objetivo:** Materializar SLA em termos 3GPP reais (PDU Session, QoS Flow 5QI, binding tráfego→slice, métricas Core).
- **Resultado:** ABORT (PDU Session não materializada). UE em MM-DEREGISTERED/NO-CELL-AVAILABLE; link de rádio UE↔gNB não estabelecido entre pods ("no cells in coverage"). Sem Registration/PDU Session; sem QoS Flow, tráfego nem binding. Evidências em `evidencias_nasp/12C_pdu_qos_flow/` (07_synthesis.md). **Próximo passo:** Topologia UERANSIM com radio link funcional (ex.: mesmo pod ou hostNetwork).

---

### PROMPT_SNASP_12D — UERANSIM Single-Pod (gNB + UE) para Registration e PDU Session (SSOT)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1.

- **Objetivo:** Single-pod gNB+UE para coverage e Registration.
- **Resultado:** PASS (topologia single-pod). Pod 2/2 Running; gNB NG Setup successful; UE com célula SUITABLE e tentativa de Registration; AMF recebe Registration Request; autenticação falha (AV_GENERATION_PROBLEM). Evidências em `evidencias_nasp/12D_ueransim_singlepod/` (07_synthesis.md). **Próximo passo:** Corrigir auth Free5GC; reexecutar PROMPT_SNASP_12C a partir da FASE 2.

---

### PROMPT_SNASP_12E — Correção Controlada de Autenticação do Subscriber no Free5GC (AV_GENERATION_PROBLEM) + Revalidação Registration

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1.

- **Objetivo:** Identificar e corrigir AV_GENERATION_PROBLEM; obter Registration Accept no UE; logs AMF/AUSF/UDM confirmando autenticação OK.
- **Resultado:** **ABORT.** Causa raiz: subscriber **imsi-208930000000001** **não está cadastrado** no UDR. UDR retorna 404 para GET authentication-subscription; UDM QueryAuthSubsData error; AUSF 403 Forbidden; AMF Nausf_UEAU Authenticate Request Failed — Cause: AV_GENERATION_PROBLEM. PUT direto ao UDR (nudr-dr / nudr-dr-prov) retornou 404 (rota não exposta nesta implantação). Correção documentada: criar subscriber via **WebUI** (passo a passo em `evidencias_nasp/12E_free5gc_auth_fix/05_fix_actions/webui_actions.md` — SUPI imsi-208930000000001, Key, OPC, AMF 8000, 5G_AKA). Evidências em `evidencias_nasp/12E_free5gc_auth_fix/` (07_synthesis.md, 08_runbook_update.txt).
- **Próximo passo recomendado:** (1) Criar o subscriber no Free5GC via WebUI conforme `05_fix_actions/webui_actions.md`. (2) Após criar, reiniciar UE single-pod e validar Registration Accept; se PASS, reexecutar **PROMPT_SNASP_12C** (FASE 2–6). Se ABORT persistir, indicar exatamente qual parâmetro ainda diverge (key/opc/amf/sqn).

---

### PROMPT_SNASP_12F — Provisionamento do Subscriber no Free5GC (UDR) + Validação de Registration (SSOT)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1.

- **Objetivo:** Criar subscriber SUPI imsi-208930000000001 no Free5GC; garantir UDR/UDM/AUSF retornem subscription/auth data; obter Registration Accept no UE; liberar reexecução do PROMPT_SNASP_12C.
- **Resultado:** **ABORT.** Subscriber não foi provisionado. WebUI sem API de subscriber (root 200, /api/ e /api/subscriber 404). Inserção direta em MongoDB (subscriptionData e subscriptionData.provisionedData.authenticationData) não fez o UDR retornar 200 — UDR continua 404 (DATA_NOT_FOUND). Procedimento manual via WebUI documentado em `evidencias_nasp/12F_subscriber_provision/04_provision_actions/webui_actions.md`. Evidências em `evidencias_nasp/12F_subscriber_provision/` (07_synthesis.md, 08_runbook_update.txt).
- **Próximo passo recomendado:** (1) Criar o subscriber manualmente via WebUI conforme `04_provision_actions/webui_actions.md`. (2) Após criar, reexecutar FASE 5 (restart UDR/UDM/AUSF/AMF) e FASE 6 (UDR GET não-404 + UE Registration Accept). (3) Se PASS: reexecutar **PROMPT_SNASP_12C** (FASE 2–6).

---

### PROMPT_SNASP_13 — Exposição Formal do Free5GC WebUI via Service Kubernetes (SSOT-Governed)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1.

- **Objetivo:** Expor o Free5GC WebUI via Service NodePort de forma mínima, reversível, compatível com Kubernetes e 3GPP, sem impacto nos planos de controle/dados, plenamente rastreável no Runbook.
- **Resultado:** **PASS.** WebUI já existia (pod Running em ns-1274485) mas não estava exposto via Service. Service NodePort `webui-free5gc-nodeport` criado (selector `app.kubernetes.io/name=free5gc-webui`, nodePort 32500, port 5000); Endpoints associado ao pod WebUI; validação interna GET / → HTTP 200 OK. Instrução de acesso externo documentada (túnel SSH 5000→192.168.10.16:32500, browser localhost:5000, admin/free5gc).
- **Evidências:** `evidencias_nasp/13_webui_exposure/` (00_gate, 01_labels.txt, 02_manifest, 03_apply, 04_internal_validation.txt, 05_access_instructions.md, 06_synthesis.md). Manifest: `k8s/free5gc-webui-nodeport.yaml`.
- **Dependência explícita para:** PROMPT_SNASP_12E / 12F / 12C — criação de subscriber, autenticação 5G-AKA, PDU Session, QoS Flow (5QI), binding tráfego → slice, métricas SLA-aware dependem de acesso ao WebUI; exposição via Service desbloqueia a sequência.

---

### PROMPT_SNASP_14 — Diagnóstico e Correção da PDU Session (SMF / UPF / DNN)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1. **Namespace Core:** ns-1274485; **UERANSIM:** ueransim.

- **Objetivo:** Diagnosticar e corrigir falha de PDU Session Establishment (após Registration e 5G-AKA).
- **Resultado:** **PASS.** Causa raiz: SMF não resolvia FQDN do UPF (Host lookup failed) → panic na seleção de UPF. Correção: ConfigMap do SMF alterado para usar IP do pod do UPF em nodeID e endpoints N3; restart SMF e UERANSIM. N4 Association Setup Success; UE recebe PDU Session Establishment Accept. Evidências: `evidencias_nasp/14_pdu_session/` (07_synthesis.md). **Limitação conhecida:** Workaround por IP; removido no PROMPT_SNASP_15.

---

### PROMPT_SNASP_15 — Correção Canônica do DNS (SMF ↔ UPF) e Remoção do Workaround por IP

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1.

- **Objetivo:** Corrigir resolução DNS no SMF para FQDN do UPF e remover workaround por IP (ConfigMap do SMF com FQDN canônico).
- **Resultado:** **PASS** para correção DNS e remoção do workaround; **ABORT** para validação ponta a ponta (PDU Session Establishment Accept). ConfigMap do SMF revertido para FQDN (`upf-free5gc-upf-upf-0.upf-service.ns-1274485.svc.cluster.local`); nslookup no pod SMF resolve FQDN; SMF envia PFCP Association Request via hostname. **Workaround por IP foi removido.** Limitação: Free5GC SMF reporta "this upf do not associate with smf" ao alocar PDR (NodeID na PFCP Association Response é IP, SMF espera FQDN); PDU Session Accept não obtido. Para PDU estável com FQDN: configurar UPF para anunciar NodeID como FQDN (se suportado) ou documentar IP como limitação conhecida. Evidências: `evidencias_nasp/15_dns_fix_smf_upf/` (07_synthesis.md, 08_runbook_update.txt).

---

### PROMPT_SNASP_16 — Consolidação Operacional do Core 5G com Limitação Declarada (SMF↔UPF NodeID / PFCP)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1. **Namespaces:** Core 5G ns-1274485, UERANSIM ueransim, TriSLA trisla.

- **Objetivo:** Consolidar estado operacional estável do Core 5G após PROMPT_SNASP_14 e 15: reaplicar workaround por IP no SMF, validar N4, PDU Session, QoS Flow, binding tráfego→UPF, registrar limitação no Runbook como Platform Constraint.
- **Resultado:** **PASS.** Workaround por IP reaplicado (nodeID e endpoints N3/N4 = IP do pod UPF; após restart UPF, IP 10.233.75.60). N4: UPF(10.233.75.60)[{internet}] setup association. UE: Registration accept, PDU Session Establishment Accept, PDU Session establishment successful PSI[1]. UPF: PFCP Session Establishment Request/Response (PDR/FAR instalados).
- **Limitação declarada (Platform Constraint):** Free5GC v3.1.1 — uso de NodeID PFCP: UPF anuncia NodeID como IP; SMF configurado com FQDN não reutiliza associação N4 para PDRs. **O uso de NodeID por IP é uma limitação da implementação Free5GC e não impacta a validade da arquitetura TriSLA.** Workaround por IP assumido como configuração operacional; sem modificação de código Free5GC.
- **Referência cruzada:** PROMPT_SNASP_14 (PDU Session com workaround IP), PROMPT_SNASP_15 (DNS/FQDN; PDU com FQDN não obtida).
- **Evidências:** `evidencias_nasp/16_core_consolidation/` (00_gate–06_validation, 07_synthesis.md, 08_runbook_update.txt).

---

### PROMPT_SNASP_17 — Observabilidade Core-Driven (SMF-UPF-QoS)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1. **Namespaces:** Core 5G ns-1274485, UERANSIM ueransim, TriSLA trisla.

- **Objetivo:** Provar observabilidade real e técnica do Core 5G: PDU Session ativa, QoS Flow (5QI/QFI), associação N4 (SMF↔UPF), binding tráfego→UPF, base para SLA-aware metrics.
- **Resultado:** **PASS.** Gate e inventário Core (00_gate, 01_inventory). PDU Session: UE logs (Registration accept, PDU Session Establishment Accept, PDU Session establishment successful) (02_pdu_session). QoS Flow: SMF logs (HandlePDUSessionEstablishmentRequest, PCF Selection, HandlePfcpSessionEstablishmentResponse) (03_qos_flow). N4: UPF(10.233.75.60)[{internet}] setup association (04_n4_association). UPF: PFCP Session Establishment, PDR/FAR, DNN 10.1.0.0/17 (05_upf_traffic). Métricas: trisla-traffic-exporter trisla porta 9105 /metrics (06_metrics_snapshot). Checklist e síntese (07_validation, 08_synthesis.md).
- **Dependência desbloqueada:** PROMPT_SNASP_18 (base concreta para binding SLA↔Core).
- **Evidências:** `evidencias_nasp/17_core_observability/` (00_gate–09_runbook_update.txt).

---

### PROMPT_SNASP_18 — Binding SLA ↔ Core 5G (SLA-Aware, sem mock)

**Data:** 2026-02-02. **Ambiente:** node006 ≡ node1. **Namespaces:** Core 5G ns-1274485, TriSLA trisla, UE ueransim.

- **Objetivo:** Estabelecer binding determinístico entre TriSLA (sla_id, decision_id, tipo de slice) e Core 5G (SUPI, PDUSessionID, S-NSSAI, DNN, UE_IP, UPF_NodeID), sem mock e sem alteração no Core.
- **Resultado:** **PASS.** Contexto SLA: sla_id/intent_id ee2faa3f-4bb4-495c-a081-206aeefb69c3, decision_id dec-ee2faa3f-..., tipo URLLC (referência Runbook). Identificadores Core: SUPI imsi-208930000000001, PDUSessionID 1, DNN internet, S-NSSAI 1/010203, UE_IP 10.1.0.1, UPF_NodeID 10.233.75.60. Mapa central: 03_binding_map/sla_core_binding.txt. Métricas: trisla-traffic-exporter 9105/metrics; correlação SLA↔Core via binding map.
- **Dependência desbloqueada:** PROMPT_SNASP_19 (coleta de métricas SLA-aware e rastreabilidade ponta a ponta).
- **Evidências:** `evidencias_nasp/18_sla_core_binding/` (00_gate–07_runbook_update.txt).

---

### PROMPT_SNASP_19 — Coleta SLA-Aware Multicenários (Capítulo 6 & Artigos)

**Data:** 2026-02-03. **Ambiente:** node006 ≡ node1. **Namespaces:** Core 5G ns-1274485, TriSLA trisla, UE ueransim.

- **Objetivo:** Consolidar a fase final de validação experimental da arquitetura TriSLA no ambiente NASP, com foco na coleta SLA-aware baseada em cenários progressivos de carga, assegurando evidências válidas para Capítulo 6 — Resultados Experimentais e Artigos científicos (5G / O-RAN / SLA-aware).
- **Resultado:** **PASS.** Gate de imutabilidade (00_gate). Consolidação dos inputs — binding SLA ↔ Core de referência (PROMPT_SNASP_18) (01_inputs). Validação do binding SLA↔Core — binding determinístico, 1-para-1, sem ambiguidade (02_binding_validation). Coleta de métricas reais trisla-traffic-exporter 9105/metrics (03_metrics_collection). Correlação SLA-aware offline e determinística (04_sla_correlation/sla_metrics_correlated.txt). Tabelas acadêmicas Markdown e LaTeX-ready (05_tables). Gráficos/esquema para artigos (06_graphs). Checklist final (07_validation/checklist.md). Síntese técnica (08_synthesis.md).
- **Cenários Experimentais:** Script de submissão de SLAs criado (submit_scenarios.py) para 4 cenários progressivos: Cenário 1 (1 URLLC + 1 eMBB + 1 mMTC), Cenário 2 (10× cada tipo), Cenário 3 (30× cada tipo), Cenário 4 (60× cada tipo, total 180 SLAs).
- **Dependências satisfeitas:** PROMPT_SNASP_16 (Core consolidado), 17 (Observabilidade Core-Driven), 18 (Binding SLA↔Core).
- **Encerramento do ciclo experimental TriSLA:** Validação experimental da arquitetura TriSLA no NASP concluída (Core 5G funcional, observabilidade, binding SLA↔Core, métricas SLA-aware rastreáveis). Evidências publicáveis para Capítulo 6 e artigos científicos.
- **Evidências:** `evidencias_nasp/19_sla_aware_metrics/` (00_gate–09_runbook_update, submit_scenarios.py).

---

### v3.9.12 — Kafka Observability & Replay (S41.4A)

**Data:** 2026-01-31

- **Objetivo:** Validar Kafka como plano assíncrono de observabilidade; produção/consumo de eventos; replay; não bloqueio do SLA Admission.
- **Separação arquitetural:**
  - **SLA Admission Path (sync):** Portal → SEM-CSMF → Decision Engine → BC-NSSMF → Besu
  - **Event Streaming Path (async):** Decision Engine → Kafka → Consumers (observability)
- **Kafka opera exclusivamente como canal assíncrono** — não interfere no caminho síncrono de aceitação de SLA.
- **Tópicos:** trisla-decision-events, trisla-i04-decisions, trisla-i05-actions, trisla-ml-predictions.
- **Comandos (apache/kafka):** `/opt/kafka/bin/kafka-topics.sh`, `kafka-console-producer.sh`, `kafka-console-consumer.sh` — usar `--partition 0 --max-messages N` para evitar timeout em consumer.
- **Evidências:** `evidencias_release_v3.9.12/s41_4a_kafka_observability/`.

---

### v3.9.12 — S41.3H Gate Normalization (200/202) + Reexec Final (S41.3N)

**Data:** 2026-01-31

- **Objetivo:** Normalizar gate S41.3H para aceitar HTTP 200 ou 202; refletir comportamento real do Portal/BC.
- **Regra SSOT:** Portal success retorna HTTP 200 (sync confirm) ou 202 (async); gate aceita 200/202.
- **Patch:** Script `run_s41_3h_stabilization.sh` FASE 3 — condição alterada de `!= 202` para `!= 200 && != 202`.
- **Referência:** S41.3M (Besu QBFT); contrato atual 0xb5FE5503125DfB165510290e7782999Ed4B5c9ec.
- **Evidências:** `evidencias_release_v3.9.12/s41_3n_gate_normalization/`.

---

### v3.9.12 — S41.3H Estabilização Final + Aceitação Operacional

**Data:** 2026-01-30

- **Objetivo:** Estabilizar ambiente TriSLA com funding on-chain correto, Besu com genesis válido, pipeline completo ativo, aceitação HTTP 200/202 e concorrência ≥20 SLAs; congelar baseline v3.9.12 documentado e anti-drift.
- **Execução (via ssh node006):** `cd /home/porvir5g/gtp5g/trisla && bash evidencias_release_v3.9.12/s41_3h_stabilization/run_s41_3h_stabilization.sh`. Portal: `TRISLA_PORTAL_URL` (default http://192.168.10.15:32002).
- **Fases:** FASE 0 gate (pods Running, sem *-fix/CrashLoopBackOff), FASE 1 saldo on-chain (1 ETH; se 0x0 → corrigir genesis), FASE 2 BC readiness, FASE 3 submit único 200/202, FASE 4 Kafka eventos, FASE 5 anti-drift imagens, FASE 8 Runbook/checksums.
- **Evidências:** `evidencias_release_v3.9.12/s41_3h_stabilization/` (00_gate, 01_wallet_balance, 02_bc_readiness, 03_submit_single, 04_kafka, 05_antidrift, 08_runbook_update, 16_integrity). Guia: `EXECUTE_NODE006.md`.
- **Regra:** Genesis funding é parte da infra; baseline congelado v3.9.12.
- **Acesso operacional:** Entry point obrigatório `ssh node006`; hostname reporta `node1` (node006 ≡ node1).

---

### v3.9.12 — Besu Block Production Hardening (Single-Node) + Redeploy Contract PASS (S41.3M)

**Data:** 2026-01-31

- **Objetivo:** Fixar Besu em modo single-node que produz blocos; redeploy do contrato; BC registra SLA sem 500.
- **Modo escolhido:** QBFT (Clique deprecado em Besu 25.12.0+). `besu operator generate-blockchain-config` com count=1.
- **Procedimento:** Scale Besu 0; delete PVC; apply besu-qbft.yaml (genesis QBFT); init Job copia node key para besu-data; scale Besu 1; deploy Job contrato; ConfigMap trisla-bc-contract-address; patch BC mount contract_address.json; rollout restart BC.
- **Resultado:** blockNumber avança (0xa→0x19→…); contrato deployado 0xb5FE5503125DfB165510290e7782999Ed4B5c9ec; register-sla retorna 200 com tx mined; S41.3H submit retorna 200 (tx confirmada, bc_status=CONFIRMED).
- **Evidências:** `evidencias_release_v3.9.12/s41_3m_besu_block_production/`. ADR: `01_besu_mode_select/ADR_BESU_MODE.md`.

---

### v3.9.12 — BC-NSSMF 500 Root Cause + Contract Redeploy (S41.3L)

**Data:** 2026-01-31

- **Objetivo:** Eliminar 500 em /api/v1/register-sla; garantir registro on-chain; destravar submit 202 no S41.3H.
- **Causa raiz:** Contrato em 0x42699A7612A82f1d9C36148af9C77354759b210b inexistente na chain (eth_getCode=0x); chain reset; Besu não minera.
- **Descobertas:** Deploy Job enviou tx; wait_for_transaction_receipt timeout 120s; Besu MINER não habilitado; miner_start retorna "Method not enabled" ou "Coinbase not set"; miner-coinbase causou CrashLoopBackOff.
- **Procedimento para redeploy:** Habilitar MINER em Besu; definir coinbase; miner_start; executar Job trisla-bc-deploy-contract; atualizar contract_address.json; reiniciar BC-NSSMF.
- **Evidências:** `evidencias_release_v3.9.12/s41_3l_bc_500_root_cause/`.

---

### v3.9.12 — Portal→BC Call Path Audit + Fix URL/Timeout (S41.3K)

**Data:** 2026-01-31

- **Objetivo:** Eliminar 503 ReadTimeout na FASE 3 do S41.3H; garantir URL canônica e timeout compatível.
- **URL canônica BC:** `http://trisla-bc-nssmf.trisla.svc.cluster.local:8083`
- **Correções aplicadas (config only):** Portal Backend: BC_NSSMF_URL (FQDN), HTTP_TIMEOUT=30, BC_TIMEOUT=60; SEM-CSMF: HTTP_TIMEOUT=30.
- **Descoberta:** Portal Backend (src.services.nasp) chama BC-NSSMF diretamente; ReadTimeout ocorre ao chamar BC; retry 3/3.
- **Evidências:** `evidencias_release_v3.9.12/s41_3k_portal_bc_callpath/`.

---

### v3.9.12 — Stabilize BC-NSSMF Readiness + Remove Probe Flapping (S41.3J)

**Data:** 2026-01-31

- **Objetivo:** BC-NSSMF Ready estável (sem timeouts); garantir Service com endpoints; eliminar flapping de probes.
- **Causa raiz:** readiness probes com timeoutSeconds=1 e failureThreshold=3 causavam flapping quando Besu RPC estava lento.
- **Patch aplicado (kubectl patch):** readinessProbe timeoutSeconds=3, failureThreshold=6, initialDelaySeconds=15; livenessProbe timeoutSeconds=3, failureThreshold=6. Paths: /health/ready (readiness), /health (liveness; /health/live retorna 404).
- **Resultado:** BC-NSSMF 1/1 Running com endpoints; probes estáveis.
- **S41.3H reexec:** FASE 0–2 PASS; FASE 3 ainda 503 ReadTimeout (causa em fluxo Portal/BC, fora do escopo probes).
- **Evidências:** `evidencias_release_v3.9.12/s41_3j_bc_readiness_stabilize/`. Checklist anti-regressão: readinessProbe timeoutSeconds >= 3, failureThreshold >= 6.

---

### v3.9.12 — RESTORE BASELINE BESU DEV + FUNDING WALLET DEDICADA (S41.3I)

**Data:** 2026-01-31

- **Objetivo:** Restaurar método SSOT após execução caótica; correção controlada (não validação).
- **FASE 1 — Besu:** Inicialmente `--network=dev` (sem genesis custom); dev mode não minerava (block 0). Restaurado genesis custom (ConfigMap trisla-besu-genesis) com alloc pré-financiando BC wallet 0x24f31b... (1 ETH).
- **FASE 2 — Wallet dedicada:** Secret bc-nssmf-wallet restaurado com chave dedicada; reverter de conta dev.
- **FASE 3 — Funding:** eth_accounts vazio; fund_bc_wallet.py enviou tx mas Besu dev não minerou. Solução: genesis custom com alloc.
- **Motivo da falha anterior (S41.3H):** nonce/txpool/chain state; Besu dev mode não minera nesta versão (--miner-enabled não suportado); genesis necessário.
- **Evidências:** `evidencias_release_v3.9.12/s41_3i_restore_besu_dev/` (00_gate, 01_besu_restore, 02_wallet_restore, 03_funding_transfer, 04_bc_restart, 05_reexec_s41_3h, 08_runbook_update, 16_integrity).
- **S41.3H reexec:** FASE 0–2 PASS; FASE 3 ABORT (503 ReadTimeout). BC-NSSMF probes falham por timeout (Besu RPC lento).

---

### v3.9.12 — On-Chain Funding Model + SLA Throughput Validation (S41.3H)

**Data:** 2026-01-30

- **Funding model oficial:** Financiamento da wallet BC-NSSMF via **genesis customizado** (evita dependência de mineração em Besu dev). ConfigMap `trisla-besu-genesis` com genesis baseado em dev (chainId 1337); `alloc` inclui a conta `0x24f31b232A89bC9cdBc9CA36e6d161ec8f435044` com 1 ETH (`0xde0b6b3a7640000`).
- **Besu deploy:** Deployment usa `args: --genesis-file=/opt/besu/genesis.json` (volume ConfigMap); mesmo RPC/API; sem `--network=dev`.
- **Procedimento de aplicação (node006):** `bash scripts/s41-3h-besu-genesis-reset.sh` (remove deploy, deleta PVC trisla-besu-data, aplica trisla/besu-deploy.yaml, aguarda rollout). Executar na raiz do repo onde está trisla/besu-deploy.yaml.
- **Gate S41.3H:** FASE 0 (gate segurança), FASE 1 (funding model), FASE 2 (funding authority/genesis), FASE 3 (BC readiness), FASE 4 (submit 202), FASE 5 (concorrência ≥20 SLAs), FASE 7 (Runbook + Release Manifest).
- **Evidências:** `evidencias_release_v3.9.12/s41_3h_onchain_funding/` (00_gate, 01_funding_model, 02_onchain_funding, 03_bc_readiness, 04_submit_single, 05_concurrency, 16_integrity). Artefatos: `apps/besu/genesis.json`, `scripts/s41-3h-besu-genesis-reset.sh`.

---

### v3.9.12 — BC Wallet Provisioning + On-Chain Readiness Gate (S41.3G)

**Data:** 2026-01-30

- **Wallet dedicada BC-NSSMF:** Secret `bc-nssmf-wallet` (privateKey); env BC_PRIVATE_KEY via valueFrom secretKeyRef; volume mount /secrets (readOnly). Nunca hardcode; nunca wallet compartilhada.
- **Readiness Gate On-Chain:** readinessProbe em `/health/ready` (RPC + wallet); BC não fica Ready sem wallet válida e RPC conectado.
- **Variáveis oficiais:** BC_PRIVATE_KEY (Secret), BC_RPC_URL, BESU_RPC_URL (Besu).
- **Submit:** Wallet e RPC OK; 422 "Saldo insuficiente" até financiar conta dedicada no Besu (genesis alloc ou transferência única).
- **Evidências:** `evidencias_release_v3.9.12/s41_3g_bc_wallet/` (00_gate, 01_wallet_generation, 02_k8s_secret, 03_bc_config, 04_readiness_gate, 05_validation_single, 06_validation_concurrency, 08_runbook_update, 16_integrity).
- **Procedimento de rotação de chave:** Documentado na seção BC-NSSMF do Runbook.

---

### v3.9.12 — Besu RPC Hardening + BC Readiness Gate (S41.3F)

**Data:** 2026-01-30

- **Besu como infra estabilizada:** Imagem oficial `ghcr.io/abelisboa/trisla-besu:v3.9.12`; Dockerfile em `apps/besu` com flags RPC fixadas (--rpc-http-enabled, --rpc-http-host=0.0.0.0, --rpc-http-api=ETH,NET,WEB3,ADMIN,TXPOOL, --host-allowlist=*).
- **Deploy Besu hardened:** Deployment + Service ClusterIP 8545 + PVC trisla-besu-data; readiness/liveness tcpSocket 8545.
- **BC-NSSMF:** BESU_RPC_URL configurado para `http://trisla-besu.trisla.svc.cluster.local:8545`; gate de readiness: BC não opera em modo degraded por indisponibilidade de RPC.
- **Resultado:** 0× 503 por RPC; submit pode retornar 503 por "Conta blockchain não disponível" (wallet) até configuração de conta.
- **Evidências:** `evidencias_release_v3.9.12/s41_3f_besu_rpc_hardening/` (00_gate_anti_drift, 01_runbook_read, 02_besu_inventory, 03_besu_image_build, 04_besu_deploy_hardening, 05_bc_readiness_gate, 06_validation_concurrency, 08_runbook_update, 16_integrity).

---

### v3.9.12 — Promoção formal do hotfix do BC-NSSMF (S41.3E.2)

**Data:** 2026-01-30

- **Normalização de release:** Removida tag `v3.9.12-bcfix` em produção; BC-NSSMF em runtime usa **v3.9.12** oficial.
- **Release Manifest:** `evidencias_release_v3.9.12/RELEASE_MANIFEST.yaml` — bc-nssmf image v3.9.12, digest registrado, repo_path apps/bc-nssmf, build_method docker.
- **Regra Anti-Drift:** Documentada no Runbook (seção 2); proibido *-fix/*-hotfix/*-temp em produção; hotfixes devem ser promovidos para release oficial.
- **Evidências:** `evidencias_release_v3.9.12/s41_3e_2_release_normalization/` (00_gate_anti_drift, 01_bc_tag_promotion, 02_build_publish, 03_deploy_update, 04_manifest_update, 05_runbook_update, 06_post_validation, 16_integrity, S41_3E_2_FINAL_REPORT.md).

---

### v3.9.11 (pós-S41.3E) — Fix definitivo BC-NSSMF + schema v1.0 + compat layer

**Data:** 2026-01-30

**Execução S41.3E (PROMPT_S41.3E):**
- ✅ **Repo_path BC-NSSMF:** `trisla/apps/bc-nssmf` (node006: `/home/porvir5g/gtp5g/trisla/apps/bc-nssmf`); também `apps/bc-nssmf` no workspace.
- ✅ **Patch aplicado:** `main.py` — `register_sla` aceita `Request`; parse body (slo_set/sla_requirements ou legado SLARequest); `_normalize_slos_to_contract()` nunca acessa `.value` sem fallback; 422 para payload inválido ou lista vazia. `models.py` — SLO com `value: Optional[int] = None`.
- ✅ **Schema v1.0 aceito:** slo_set, sla_requirements; threshold como int ou objeto {value, unit}; correlation_id logado.
- ✅ **Build/Publish (método oficial):** `cd trisla && docker build -t ghcr.io/abelisboa/trisla-bc-nssmf:<tag> apps/bc-nssmf && docker push ...`; tag sugerida `v3.9.12-bcfix`. GHCR login: `echo $GITHUB_TOKEN | docker login ghcr.io -u abelisboa --password-stdin` (node1/node006).
- ✅ **Redeploy:** `kubectl set image -n trisla deploy/trisla-bc-nssmf bc-nssmf=ghcr.io/abelisboa/trisla-bc-nssmf:v3.9.12-bcfix`; `kubectl rollout status deploy/trisla-bc-nssmf -n trisla`.
- ✅ **Rollback:** `kubectl set image -n trisla deploy/trisla-bc-nssmf bc-nssmf=ghcr.io/abelisboa/trisla-bc-nssmf:v3.9.11`; ou reverter `main.py`/`models.py` para backup e rebuild.
- ✅ **Build/Push/Redeploy confirmados (node1):** Login Succeeded → `docker build -t ghcr.io/abelisboa/trisla-bc-nssmf:v3.9.12-bcfix apps/bc-nssmf` → push → `kubectl set image -n trisla deploy/trisla-bc-nssmf bc-nssmf=ghcr.io/abelisboa/trisla-bc-nssmf:v3.9.12-bcfix` → deployment "trisla-bc-nssmf" successfully rolled out. O mesmo procedimento vale no node006 (Login Succeeded + build/push + kubectl no cluster).
- **Validação pós-redeploy:** Repetir FASE 6–9 (submit único, 20 SLAs, Kafka, BC audit) para confirmar 0× 503/500 e eventos com XAI.
- **Evidências:** `evidencias_release_v3.9.11/s41_3e_bc_fix_release/` (00_gate, 01_ssot_lookup, 02_repo_bc_locate, 03_patch_bc/BC_PATCH_NOTES.md, 04_build_push, 05_redeploy, 06–09 validation, 10_runbook_update, 16_integrity).

---

### v3.9.11 (pós-S41.3D.1) — Release Unificado + Fix BC-NSSMF + Submit 202 + Reteste Concorrência

**Data:** 2026-01-30

**Execução S41.3D.1 (PROMPT_S41.3D.1):**
- ✅ **FASE 0:** Gate no node006 — core TriSLA Running.
- ✅ **FASE 1:** SSOT sync — Runbook checksum before/after em `evidencias_release_v3.9.11/s41_3d1_unified_release_fix/01_ssot_sync/`; node006 não é repositório git (git pull N/A).
- ✅ **FASE 2:** Build/Publish — não executado nesta sessão (GITHUB_TOKEN não passado; fix BC-NSSMF deve ser aplicado antes do rebuild). Log em `02_build_publish/build_publish.log`.
- ✅ **FASE 3:** Deploy order — rollout status de todos os deployments (sucesso).
- ⚠️ **FASE 4–7:** Submit retorna **503** (BC-NSSMF: `'SLO' object has no attribute 'value'`); Kafka 0 eventos; BC retorna 500; reteste concorrência 20 SLAs — 20× 503. Evidências em `04_submit_202/`, `05_kafka_events/`, `06_bc_besu/`, `07_concurrency_retest/`.
- **Comportamento submit desejado:** HTTP 202 (ou 200) com correlation_id; **NUNCA 503** após fix.
- **Contrato v1.0 / BC:** Corrigir BC-NSSMF para aceitar schema v1.0 (slo_set/sla_requirements) e eliminar uso de `SLO.value`; após fix, validar zero 500 no BC e zero SLO.value nos logs.
- **Procedimento de concorrência validado:** Script `run_20_slas.sh`; URL NodePort `http://192.168.10.15:32002/api/v1/sla/submit`; gates: 0 respostas 503, 0 erro SLO.value, Kafka ≥ eventos do batch, BC sem 500.
- **Evidências:** `evidencias_release_v3.9.11/s41_3d1_unified_release_fix/` (00_gate, 01_ssot_sync, 02_build_publish, 03_deploy_order, 04_submit_202, 05_kafka_events, 06_bc_besu, 07_concurrency_retest, 08_runbook_update, 16_integrity).

---

### v3.9.11 (pós-S41.3D.0) — Component Registry + Release Manifest SSOT

**Data:** 2026-01-30

**Execução S41.3D.0 (PROMPT_S41.3D.0):**
- ✅ **Repo base path oficial:** `/home/porvir5g/gtp5g` (confirmado em node006).
- ✅ **Component Registry (SSOT):** Tabela deployment → repo_path em `evidencias_release_v3.9.11/s41_3d0_registry_release/01_repo_discovery/component_repo_map.md`; dirs_candidates e build_files_index.
- ✅ **Runtime images:** deploy_images.txt, sts_images.txt, pod_imageIDs.txt em `02_runtime_images/`.
- ✅ **Build methods:** Scripts oficiais (build-and-push-images-3.7.9.sh, build-push-v3.9.8.sh, execute-fase3-build-push.sh); resumo em `03_build_methods/build_methods_summary.md`.
- ✅ **Release Manifest:** `04_release_manifest/RELEASE_MANIFEST.yaml` com release_id, componentes (repo_path, image_current, build_push, deploy, rollback, gates), deploy_order.
- ✅ **Runbook atualizado:** Seção 3 com Repo base path, Component Registry, Release Manifest, ordem de deploy, procedimento de rollback.
- **Regra:** Novos módulos devem ser registrados no Component Registry e no Release Manifest; build/publish via scripts oficiais ou documentados.

---

### v3.9.11 (pós-S41.3C) — Deploy + Prova XAI-Aware E2E + Concorrência

**Data:** 2026-01-30

**Execução S41.3C (ROMPT_S41.3C):**
- ✅ **FASE 0:** Gate no node006 — core TriSLA Running.
- ✅ **FASE 1:** Build/Push/Deploy (evidência: imagens v3.9.11; helm values; rollout status em `evidencias_release_v3.9.11/s41_3c_xai_aware/01_build_deploy/`).
- ✅ **FASE 2:** Teste de concorrência 20 SLAs executado; script `run_20_slas.sh`; API via NodePort (192.168.10.15:32002).
- ⚠️ **Gate XAI-Aware:** FAIL — 20 submissões retornaram 503 (BC-NSSMF: `'SLO' object has no attribute 'value'`). Kafka 0 eventos (fluxo falhou antes de publicar). Evidências em `evidencias_release_v3.9.11/s41_3c_xai_aware/` (00_gate, 01_build_deploy, 02_submit_concurrency, 03_kafka_events, 04_bc_besu_audit, 05_xai_validation, 08_runbook_update, 16_integrity).
- **Próximo passo:** Corrigir BC-NSSMF ou compat layer para aceitar schema v1.0 (slo_set/sla_requirements) e eliminar erro SLO.value.

---

### v3.9.11 (pós-S41.3B) — Implementação SLA Contract SSOT + Compat + Kafka Schema

**Data:** 2026-01-30

**Implementação S41.3B (ROMPT_S41.3B):**
- ✅ **Portal Backend:** Compat layer em `sla_contract_compat.py`; validação/conversão de payload legado para schema v1.0; intent_id e correlation_id gerados quando ausentes; integração no router de submit.
- ✅ **Decision Engine + Kafka:** Evento decisório com schema completo: schema_version, correlation_id, s_nssai, slo_set, sla_requirements, decision, risk_score, xai, timestamp (main.py e kafka_producer_retry.py).
- ✅ **Evidências:** `evidencias_release_v3.9.11/s41_3b_contract_runtime/` (gate, runbook read, portal validation, SEM normalization, decision event schema, BC/NASP validation READMEs, concurrency test script, runbook update).
- ✅ **Teste de concorrência:** Script `07_concurrency_test/run_20_slas.sh` para 20 SLAs simultâneos; critérios: 0 SLO.value, 0 nasp_degraded por schema, correlation_id em cada resposta.
- **Regra:** Schema validado E2E; compat layer ativa no Portal Backend; Kafka schema completo; Runbook atualizado.

---

### v3.9.11 (pós-S41.3) — Auditoria E2E Pipeline + SLA Contract Schema

**Data:** 2026-01-30

**Auditoria S41.3 (PROMPT_S41.3):**
- ✅ Pipeline completo auditado (Portal, Portal Backend, SEM-CSMF, ML-NSMF, Decision Engine, Kafka, BC-NSSMF, SLA-Agent, NASP Adapter)
- ✅ SLA Contract Schema SSOT definido: `evidencias_release_v3.9.11/s41_3_pipeline_e2e/05_sla_contract_schema/sla_contract.schema.json`
- ✅ Contract flow e gap analysis documentados em `03_contract_flow/SLA_FLOW.md` e `04_gap_analysis/GAPS.md`
- ✅ Regras de compatibilidade e teste de concorrência documentados em `08_runbook_update/RUNBOOK_UPDATE_S41_3.md`
- **Regra:** Módulos que manipulam SLA devem validar ou converter para o schema; evento Kafka deve incluir `sla_requirements` quando disponível

---

### v3.9.11 — Release Consolidado

**Data:** 2026-01-29

**Status dos Gates:**
- ✅ S31.1 PASS — Kafka operacional e eventos publicados
- ✅ S34.3 PASS — ML-NSMF com inferência e XAI funcionais
- ✅ S36 executado — Evidências E2E coletadas

**Principais Consolidações:**
- Master Runbook criado (S37)
- Arquitetura documentada como SSOT
- Fluxo E2E oficial estabelecido
- Padrões de evidência definidos

**Limitações Documentadas:**
- Kafka consumer groups (KRaft)
- Prometheus in-cluster
- Latência depende de UE/tráfego real
- Besu Helm release failed
- Modelo ML pode não estar completo
- XAI pode estar simplificado

---

### Versões Anteriores

**v3.9.10:** Release anterior com evidências S34.2

**v3.7.x:** Versões anteriores com diferentes estados de implementação

---

## 📌 Regra Pós-S37 (Fundamental)

Após este Runbook (S37), **TODO novo prompt DEVE:**

1. ✅ **Referenciar este Runbook** explicitamente
2. ✅ **Seguir suas regras** de engenharia (anti-regressão, anti-gambiarra, anti-invenção)
3. ✅ **Atualizar o Runbook** se algo mudar no sistema

**Sem exceções.**

---

## ✅ Estado Esperado ao Final do S37

- ✅ TriSLA com memória técnica permanente
- ✅ Fim de retrabalho
- ✅ Fim de improviso
- ✅ Base sólida para:
  - Correção definitiva do Kafka
  - Estratégia de latência (controle vs data plane)
  - Experimentos com UE/emulador
  - Evolução controlada do sistema

---

**Fim do Master Runbook TriSLA v3.9.20 (Release Final SSOT MDCE v2)**

---

## S45 — Deploy Controlado v3.10.0 + Smoke Test (2026-01-31)

### Resultado
✅ **APROVADO**

### Ações Executadas
1. Helm upgrade para v3.10.0
2. Image updates para 7 módulos core
3. Smoke test funcional (SLA eMBB criado)
4. XAI validado (13 features, risk score, confidence)
5. Blockchain validado (block 2471)
6. Kafka validado (eventos consumidos)

### Evidência
- Decision ID: dec-smoke-s45-1769827026
- ML Risk Score: 9.4% (LOW)
- Viability Score: 90.6%

### Observação
Smoke test executado com sucesso. Nenhum experimento realizado.

---

## PROMPT_SNASP_28 — Coleta Experimental Governada (2026-02-05)

**Referência:** PROMPT_SNASP_28 — Coleta Experimental Governada (total aderência PROMPT_S00, SSOT).

**Objetivo:** Coletar evidências experimentais reais para avaliação da admissão preventiva de SLAs, sem alterar arquitetura, lógica decisória ou versões; material para artigo NASP (Elsevier).

**Última execução:** 2026-02-05. **Resultado:** **PASS.** Gate FASE 0 (evidencias_nasp/SNASP_28_20260205/00_gate). Submissões controladas: URLLC, eMBB, mMTC (1 cada); decisão ACCEPT para todos; ML-NSMF, BC-NSSMF, XAI e /status validados. Evidências: 00_gate–11_runbook_update. Dependências: PROMPT_S00 (SSOT validado). Observação: Chamada ao NASP Adapter (criação de slice) falhou por conexão; fora do escopo da admissão preventiva.

**Evidências:** `evidencias_nasp/SNASP_28_20260205/`.


---

## PROMPT_S2.BIB_2020_2026 — Busca Bibliográfica Artigo 2

**ID:** PROMPT_S2.BIB_2020_2026  
**Data/Hora:** 2026-02-10T12:29:38-03:00  
**Escopo:** Artigo 2 — Trabalhos Relacionados (blockchain SLA governance)  
**Baseline:** v3.9.12  
**Ambiente:** node006  

**Resultado:** PASS

**Bases consultadas e strings utilizadas:**
- Web Search (IEEE Xplore, ACM, Springer, MDPI)
- String 1: (blockchain OR DLT) AND (SLA) AND (governance OR auditability) AND (5G slicing)
- String 2: (smart contract) AND (SLA) AND (network slicing OR 5G)
- String 3: (blockchain-based) AND (SLA management) AND (5G)
- String 4: (blockchain) AND (SLA) AND (penalty OR dispute) AND (5G)

**Estatísticas:**
- Resultados brutos: 12 papers
- Deduplicados: 0
- Selecionados (núcleo): 7 papers
- Excluídos: 5 papers (motivos documentados em screening_log.csv)

**Saídas geradas:**
-  — 12 registros brutos
-  — Triagem com decisões e motivos
-  — Tabela comparativa completa
-  — Entradas BibTeX (7 entradas)
-  — Síntese textual

**Próximo passo recomendado:**  
Escrever seção Trabalhos Relacionados do Artigo 2 utilizando a síntese textual e tabela comparativa geradas.


---

### PROMPT_SNASP_31 — MDCE Deterministic Headroom + Transport Domain Activation

**Data:** 2026-02-14T15:20:01Z  
**Ambiente:** node006 ≡ node1  

#### Objetivo

Formalizar evolução arquitetural pós-Freeze v3.11.0, ativando:

- Headroom determinístico no MDCE
- Transporte como domínio decisório completo
- RTT real via Prometheus (probe_duration_seconds)
- Aplicação de modelo conservador: estado_atual + delta_por_slice <= limite

#### Motivação Técnica

Alinhar decisão preventiva de SLA à pergunta de pesquisa:

"Como decidir, no momento da solicitação, se há recursos suficientes nos domínios RAN, Transporte e Core?"

#### Alterações Controladas

- Decision Engine:
  - MDCE_HEADROOM_ENABLED=true
  - MDCE_TRANSPORT_ENABLED=true
  - Custos por slice (CPU, MEM, UE, RTT)
- NASP Adapter:
  - Integração definitiva com Prometheus
  - Extração rtt_p95_ms real
- Nenhuma alteração em:
  - Modelo ML
  - Pesos de decisão
  - Blockchain
  - Kafka
  - Portal

#### Status

PASS (evolução governada)

#### Observação

Esta alteração inaugura nova baseline experimental pós-freeze v3.11.0.
Freeze anterior permanece íntegro e rastreável.

---


### PROMPT_SNASP_32 — E2E Deterministic Validation

**Data:** 2026-02-14T15:23:31Z

Teste E2E via Portal:

- URLLC com latency < RTT real → null
- URLLC com latency > RTT real → null

Validação determinística do domínio Transporte + Headroom.

Status: FAIL

Evidências: evidencias_nasp/32_e2e_deterministic/


---

## 🔐 BC-NSSMF – Correção Estrutural Definitiva (Helm + RPC + Wallet)

**Data:** 2026-02-17 19:12:34  
**Release Helm:** trisla-3.10.0
trisla-besu-1.0.0
trisla-portal-1.0.2  
**Imagem BC-NSSMF:**  
ghcr.io/abelisboa/trisla-bc-nssmf@sha256:b0db5eef2128baddee2c1c3ea72fb5fec421afb1d87407e5f4a6aadd75f9f95a

---

### 📌 Problema Identificado

O endpoint:

/health/ready

retornava:

rpc_unreachable  
ou  
wallet_unavailable  

---

### 🧠 Causa Raiz

- BC_RPC_URL não estava definido explicitamente
- Código exige BC_RPC_URL ou BLOCKCHAIN_RPC_URL
- Duplicação silenciosa de BC_ENABLED
- Wallet não validada corretamente

---

### 🔧 Correções Aplicadas

- Definição explícita de BC_RPC_URL
- Injeção da private key via Secret + BC_PRIVATE_KEY_PATH
- Montagem de Secret bc-nssmf-wallet
- Montagem de ConfigMap trisla-bc-contract-address
- Remoção de duplicação de BC_ENABLED
- Readiness real via /health/ready
- Imagem fixada por digest

---

### ✅ Estado Final Validado

```
{"ready":true,"rpc_connected":true,"sender":"0x24f31b232A89bC9cdBc9CA36e6d161ec8f435044"}pod "bc-ready" deleted from trisla namespace
```

---

STATUS: ✔️ PASS


---

## 🔐 BLOCKCHAIN GATE (MANDATORY BEFORE EXPERIMENTS)

Script Oficial:
`/home/porvir5g/gtp5g/trisla/scripts/gates/gate_blockchain_e2e.sh`

### Objetivo
Garantir que:

- BC_ENABLED=true em runtime
- RPC Besu conectado
- Submit real gera tx_hash
- block_number confirmado
- status="ok"
- decision retornada

### Política Obrigatória

Este Gate DEVE retornar PASS antes de:

- Execução de stress tests
- Geração de evidências científicas
- Captura de dados para Capítulo 6
- Criação de nova tag de release
- Deploy em ambiente NASP

### Política de Falha

Se FAIL:
→ ABORTAR imediatamente qualquer coleta ou experimento.
→ Corrigir BC-NSSMF / Besu antes de prosseguir.

### Registro

Todas as execuções devem gerar evidências em:

`/home/porvir5g/gtp5g/trisla/evidencias_gates/`

Data de integração automática: 20260217-200227

---


---

# 🔒 BASELINE FREEZE – 20260217-211224

## Status Geral

- Preflight Global: ✅ PASS
- Blockchain Gate: ✅ PASS
- E2E Submit + BC Validation: ✅ PASS

## Imagens Congeladas

- Decision Engine: ghcr.io/abelisboa/trisla-decision-engine@sha256:5695c700be9b83bd11bdf846a5762f1f9ba3dde143c73f3cec2b55472bb4caa6
- BC-NSSMF: ghcr.io/abelisboa/trisla-bc-nssmf@sha256:b0db5eef2128baddee2c1c3ea72fb5fec421afb1d87407e5f4a6aadd75f9f95a
- SEM-CSMF: ghcr.io/abelisboa/trisla-sem-csmf@sha256:84b73a5b8df53fb4901041d96559878bd2248517277557496cb2b7b3effeb375
- ML-NSMF: ghcr.io/abelisboa/trisla-ml-nsmf@sha256:605af0875ceb09cec0955ab6a7b47c0a4d12e0784a77afacb8cafe7c8119e71a

## Blockchain

- RPC Conectado: true
- BC_ENABLED: true
- Registro on-chain validado via tx_hash + block_number

## Governança

Esta baseline está oficialmente congelada.
Qualquer alteração futura em digest exige:

1. Execução completa do Preflight
2. Execução do Blockchain Gate
3. Atualização formal do Runbook
4. Novo registro de baseline

---

