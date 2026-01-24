# TriSLA End-to-End Deployment Guide (Operational Manual)

This document is a **line-by-line operational manual** for deploying TriSLA in a generic Kubernetes environment. It enables full reproduction of the control plane and validation of correct operation. Prerequisites (tools, cluster, registry) are in `docs/INSTALLATION.md`. This guide is **procedural and validation-focused**; concepts live in `INSTALLATION.md`.

---

## 1. Purpose of This Deployment Guide

### 1.1 Why Deployment Order Matters in TriSLA

TriSLA has **strict dependency chains**:

- **SEM-CSMF** and **ML-NSMF** must be ready **before** the Decision Engine starts. The Decision Engine calls both for semantic validation and risk inference. If either is missing, the Decision Engine returns errors or 503.
- **Kafka** must be running **before** the SLA-Agent. The Decision Engine publishes admission outcomes to Kafka; the SLA-Agent consumes them. If Kafka is absent, the SLA-Agent cannot receive decisions and the end-to-end control-plane flow is broken.
- **Besu** (if used) must be ready **before** BC-NSSMF. BC-NSSMF connects to the RPC endpoint; missing Besu causes CrashLoopBackOff or connection refused.
- **Portal** (backend and frontend) depends on SEM-CSMF, Decision Engine, and API Backend. Deploying Portal before core services yields 503 and "SEM-CSMF offline" errors.

Deploying in the wrong order causes **CrashLoopBackOff**, **503** from downstream services, or **silent failures** (e.g. SLA-Agent running but never receiving events). This guide enforces a fixed order and validation gates at each step.

### 1.2 Installation Prerequisites vs Deployment Execution

- **Installation** (`docs/INSTALLATION.md`): What must exist **before** you run any deploy step — cluster access, `kubectl`, Helm, DNS, image registry, resource sizing, observability prerequisites. It is **conceptual and preflight**.
- **Deployment** (this document): **Execution** of deploy steps in sequence, plus **validation** at each phase. You run commands, inspect output, and pass **gates** before advancing. It is **operational**.

### 1.3 What "Successful Deployment" Means in TriSLA Terms

Success is **not** only "all Pods Running." It means:

1. **Pods Running and Ready**: All TriSLA Deployments have `AVAILABLE` replicas; Pods show `READY 1/1` (or `n/n`) and `STATUS Running`.
2. **Health endpoints respond**: HTTP 200 (or gRPC health OK) for SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, SLA-Agent, NASP Adapter, and (if deployed) Portal Backend.
3. **Service discovery works**: Kubernetes DNS resolves `trisla-<service>.trisla.svc.cluster.local` from within the cluster.
4. **End-to-end flow works**: Submitting an SLA (e.g. via Portal or `curl`) results in semantic validation → ML inference → decision (ACCEPT/REJECT/RENEG) → Decision Engine publishing to Kafka → SLA-Agent consuming the event and (optionally) emitting agent events. Optional: BC-NSSMF records lifecycle on-chain.
5. **Observability**: Prometheus scrapes TriSLA metrics; `trisla_*` series exist. Optionally, OTLP traces reach a collector.

This guide defines **gates** at each phase so you can assert these conditions before proceeding.

---

## 2. Deployment Topology Overview

### 2.1 Control-Plane Only, Event-Driven

TriSLA is **control-plane only**. It does not run data-plane or user-plane functions. It orchestrates **SLA admission** and **lifecycle actions** via an **event-driven** design:

- **Synchronous path**: SLA request → SEM-CSMF (semantic) → ML-NSMF (risk) → Decision Engine (decision). The Decision Engine returns the decision to the caller and **also** publishes it to Kafka.
- **Asynchronous path**: Kafka delivers decision events to the SLA-Agent. The Agent executes lifecycle actions (optionally via NASP Adapter) and publishes agent events and action results to Kafka. BC-NSSMF may consume these for on-chain registration.

### 2.2 Separation: Backbone, Core, Portal

| Layer | Components | Role |
|-------|------------|------|
| **Backbone** | Kafka (mandatory); optionally Besu | Event transport; optional blockchain |
| **Core** | SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, SLA-Agent, NASP Adapter, API Backend | Admission, lifecycle, platform abstraction |
| **Portal** | Portal Backend, Portal Frontend | Optional UI for SLA submission and status |

### 2.3 ASCII Architecture Diagram

```
                    +------------------+
                    |  Portal Frontend |  (optional)
                    +--------+---------+
                             | HTTP
                    +--------v---------+
                    |  Portal Backend  |  (optional)
                    +--------+---------+
                             | HTTP
    +------------+           |           +------------+
    |  SEM-CSMF  |<----------+---------->| ML-NSMF    |
    |  (gRPC)    |           |           | (HTTP)     |
    +------+-----+           |           +------+-----+
           |                 |                  |
           |                 |                  |
           v                 v                  v
    +------------------------------------------------------------------+
    |                     Decision Engine (orchestrator)                |
    |                     HTTP; calls SEM-CSMF, ML-NSMF;                |
    |                     publishes decisions to Kafka                  |
    +------------------------------------------------------------------+
           |                 |                  |
           v                 v                  v
    +------------+   +-------+-------+   +------------+
    |  BC-NSSMF  |   |     Kafka     |   | NASP       |
    |  (Besu)    |   | (event backbone)|  | Adapter    |
    +------+-----+   +-------+-------+   +------------+
           |                 |                  ^
           |                 | I-05             |
           |                 v                  |
           |          +------------+            |
           +--------->| SLA-Agent  |------------+
                      | (consumer) |
                      +------------+
                             |
                             v I-06, I-07
                      [Kafka topics]
```

- **Kafka** is at the center of the event flow. Decision Engine → **I-05** (decision events) → SLA-Agent; SLA-Agent → **I-06** (agent events), **I-07** (action results).
- **Decision Engine** orchestrates the synchronous admission path and publishes to Kafka.
- **SLA-Agent** consumes I-05, optionally talks to NASP Adapter, publishes I-06/I-07.
- **BC-NSSMF** and **Besu** are optional (governance).

---

## 3. Namespace and Release Strategy

### 3.1 Why the `trisla` Namespace Is Used

All TriSLA workloads run in a single namespace (default: **`trisla`**). This provides:

- **Isolation**: TriSLA resources are grouped; RBAC, NetworkPolicies, and cleanup apply to one namespace.
- **Service discovery**: Components use Kubernetes DNS `<service>.trisla.svc.cluster.local`. Same namespace avoids cross-namespace DNS configuration.
- **Secrets**: `imagePullSecrets` and other Secrets are namespace-scoped; a single `ghcr-secret` in `trisla` is used by all TriSLA Pods.

### 3.2 Helm Release Naming Strategy

- **Release name**: Typically **`trisla`**. Resource names are prefixed by the release (e.g. `trisla-sem-csmf`, `trisla-decision-engine`). The chart name is usually `trisla`.
- **Chart path**: `helm/trisla` (relative to repository root). Some layouts use `helm/trisla-portal` for the UI; if not present, Portal is enabled via `helm/trisla` with `portal.enabled=true`.

### 3.3 Multiple Releases Coexisting

You can run multiple TriSLA releases in different namespaces (e.g. `trisla-dev`, `trisla-staging`) by using distinct release names and namespaces. Each release must have its own Kafka bootstrap servers (or shared Kafka with distinct consumer groups) and, if used, Besu RPC endpoints. This guide assumes a **single** `trisla` release in the `trisla` namespace.

### 3.4 Commands

**Purpose**: Create the `trisla` namespace and confirm it exists.

**Command**:

```bash
kubectl create namespace trisla
kubectl get namespace trisla
```

**Expected output**:

```
NAME     STATUS   AGE
trisla   Active   0s
```

**Failure interpretation**:

- `Error from server (AlreadyExists): namespaces "trisla" already exists` → **PASS**. Namespace exists; proceed.
- `The connection to the server ... was refused` → Cluster unreachable. Fix `kubeconfig` and cluster access (see `INSTALLATION.md`).
- `Error: namespaces "trisla" is forbidden` → RBAC or policy forbids namespace creation. Use a namespace you can create or one provided by the cluster admin.

**Gate**: `kubectl get namespace trisla` shows `trisla` in `STATUS: Active`. **PASS** → continue. **FAIL** → resolve before proceeding.

---

## 4. Deployment Order Rationale (Critical Section)

The deployment order is **fixed** for the following reasons.

### 4.1 Observability First

**Why first**: Prometheus (and ServiceMonitors) must be in place **before** TriSLA so that metrics are scraped from the moment Pods start. Otherwise, you get gaps in time-series and cannot validate `trisla_*` metrics.

**What breaks if missing**: ServiceMonitors for TriSLA exist but Prometheus does not scrape them (wrong namespace, no Prometheus Operator, etc.). Result: **empty PromQL** for `trisla_*`; you cannot validate SLOs or E2E flow via metrics.

**Who depends on it**: All TriSLA components expose `/metrics`. Prometheus is the consumer; no TriSLA service *calls* Prometheus.

### 4.2 Kafka Second (Event Backbone)

**Why second**: The **SLA-Agent** consumes decision events from Kafka (topic `trisla-i05-actions`). The Decision Engine publishes there. If Kafka is not ready **before** core services, the SLA-Agent may start but never receive events; the control-plane chain is incomplete.

**What breaks if missing**: SLA-Agent runs, but no decision consumption; no I-06/I-07 traffic. E2E validation fails.

**Who depends on it**: Decision Engine (publisher); SLA-Agent (consumer).

### 4.3 Blockchain Third (Optional)

**Why third**: **BC-NSSMF** needs a running **Besu** (or compatible) RPC endpoint. Deploy Besu (and optionally BC-NSSMF) before the rest of core so that BC-NSSMF can connect at startup.

**What breaks if missing**: BC-NSSMF CrashLoopBackOff or "connection refused" to Besu.

**Who depends on it**: BC-NSSMF.

### 4.4 Core TriSLA Services Fourth

**Why fourth**: SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, SLA-Agent, NASP Adapter (and API Backend) form the core. They must be deployed after Kafka (and optionally Besu) and after observability.

**What breaks if missing**: N/A (this is the core deploy step).

**Who depends on it**: Portal (next).

### 4.5 Portal Last

**Why last**: Portal Backend calls SEM-CSMF and Decision Engine. If core is not ready, Portal returns 503 (e.g. "SEM-CSMF offline").

**What breaks if missing**: N/A.

**Who depends on it**: End-users (via UI).

---

## 5. Phase 0 — Pre-Deployment Validation (Hard Gate)

Re-validate prerequisites **at execution time**. Even if `INSTALLATION.md` was followed, confirm these before any deploy step.

### 5.1 Kubernetes Access

**Purpose**: Ensure the cluster is reachable and `kubectl` targets the correct context.

**Command**:

```bash
kubectl cluster-info
```

**Expected output**: URLs for `Kubernetes control plane` and `CoreDNS` (or similar). No errors.

**Failure**: `The connection to the server ... was refused` or `Unable to connect` → **FAIL**. Fix `KUBECONFIG` / `kubectl config use-context` and cluster connectivity.

**Gate**: **PASS** → cluster reachable. **FAIL** → stop; fix cluster access.

### 5.2 DNS

**Purpose**: Verify cluster DNS resolves service names.

**Command**:

```bash
kubectl run dns-check --rm -i --restart=Never --image=busybox:1.36 -n trisla -- nslookup kubernetes.default.svc.cluster.local
```

**Expected output**: Resolution of `kubernetes.default.svc.cluster.local` to an IP. `--rm` removes the Pod after the run.

**Failure**: `can't resolve` or `connection timed out` → **FAIL**. Cluster DNS is broken; fix before deploying TriSLA.

**Gate**: **PASS** → DNS works. **FAIL** → stop; fix DNS.

### 5.3 Helm

**Purpose**: Confirm Helm 3.x is available.

**Command**:

```bash
helm version --short
```

**Expected output**: `v3.x.x` (e.g. `v3.12.0`).

**Failure**: `command not found` or `v2.x.x` → **FAIL**. Install Helm 3.

**Gate**: **PASS** → Helm 3.x. **FAIL** → stop; install Helm.

### 5.4 Image Registry Access

**Purpose**: If using private images (e.g. GHCR), ensure a pull Secret exists in `trisla` and that a test Pod can pull.

**Command**:

```bash
kubectl get secret ghcr-secret -n trisla
```

**Expected output**: `ghcr-secret` listed.

**Failure**: `Error from server (NotFound)` → **FAIL** if you use private images. Create the Secret (see `INSTALLATION.md` §8.4) and retry.

**Gate**: **PASS** → Secret exists (or you use only public images). **FAIL** → create Secret or switch to public images.

---

**Phase 0 GATE**: All four checks **PASS**. Proceed to Phase 1. If any **FAIL**, resolve before continuing.

---

## 6. Phase 1 — Observability Stack Deployment

### 6.1 Why Observability First

Metrics must be collected from the first moment TriSLA Pods run. Deploying Prometheus (and ServiceMonitors) **before** TriSLA avoids gaps and allows immediate validation of `trisla_*` series.

### 6.2 Minimum Viable Observability

- **Prometheus**: Scrapes `/metrics` from TriSLA services.
- **ServiceMonitors**: Prometheus Operator CRDs that tell Prometheus which Services to scrape and in which namespace. The TriSLA Helm chart can create ServiceMonitors for SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, SLA-Agent, NASP Adapter, API Backend.
- **Optional**: Grafana, Alertmanager, OTLP Collector. Not required for minimum validation.

### 6.3 Deploy Prometheus (Generic)

**Option A — Use existing Prometheus**

If Prometheus already runs in your cluster (e.g. in `monitoring`):

**Command**:

```bash
kubectl get pods -n monitoring -l app.kubernetes.io/name=prometheus
kubectl get crd servicemonitors.monitoring.coreos.com
```

**Expected**: Prometheus Pods `Running`; CRD `servicemonitors.monitoring.coreos.com` exists.

**Option B — Install kube-prometheus-stack**

**Command**:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=prometheus -n monitoring --timeout=300s
```

**Expected**: Prometheus Pods in `monitoring` become `Ready`.

**Failure**: Timeout or `ImagePullBackOff` → Fix Helm repo, images, or namespace; retry.

### 6.4 ServiceMonitors Relevance

After TriSLA is deployed (Phase 4), ServiceMonitors in `trisla` namespace select TriSLA Services. Prometheus must scrape the `trisla` namespace (via `namespaceSelector` or global config). Otherwise, **no `trisla_*` metrics**.

### 6.5 Validation

**Command**:

```bash
kubectl get servicemonitors -n trisla
kubectl get pods -n monitoring
```

**Expected**: After Phase 4, ServiceMonitors for `trisla-*` exist. Prometheus Pods in `monitoring` are `Running`.

**PASS**: Prometheus runs; ServiceMonitors (or equivalent) will target TriSLA once deployed. **FAIL**: No Prometheus or no ServiceMonitor CRD → fix before Phase 4.

**Phase 1 GATE**: Prometheus is running; ServiceMonitor CRD exists. **PASS** → Phase 2.

---

## 7. Phase 2 — Kafka Deployment (Event Backbone)

### 7.1 Why Kafka Is Mandatory

The Decision Engine publishes **decision events** (e.g. ACCEPT/REJECT) to Kafka. The **SLA-Agent** consumes them to drive lifecycle actions. Without Kafka, the Agent never receives decisions; E2E flow is broken.

### 7.2 Topics Used by TriSLA

| Topic | Producer | Consumer | Purpose |
|-------|----------|----------|---------|
| **trisla-i05-actions** | Decision Engine | SLA-Agent | Decision events (ACCEPT/REJECT/RENEG) |
| **trisla-i06-agent-events** | SLA-Agent | (downstream) | Agent events (e.g. violations, risk) |
| **trisla-i07-agent-actions** | SLA-Agent | (downstream) | Action results |

Topics may be created automatically by brokers or by a bootstrap job; ensure they exist or are auto-created.

### 7.3 Deploy Kafka (Generic)

Example using Bitnami Kafka (adjust namespace if needed):

**Command**:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm upgrade --install kafka bitnami/kafka -n trisla
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kafka -n trisla --timeout=300s
```

**Expected**: Kafka Pod(s) `Running` and `Ready`. Service `kafka` (or similar) in `trisla`.

**Failure**: Timeout, `ImagePullBackOff`, or PVC issues → Check images, storage class, and resource limits; fix and retry.

### 7.4 Validate Broker Readiness, DNS, Port

**Broker readiness**:

```bash
kubectl get pods -n trisla -l app.kubernetes.io/name=kafka
```

**Expected**: Pod(s) `1/1 Running`.

**Service DNS**:

```bash
kubectl run kafka-dns --rm -i --restart=Never --image=busybox:1.36 -n trisla -- nslookup kafka.trisla.svc.cluster.local
```

**Expected**: Resolution to ClusterIP(s).

**Port reachability** (e.g. 9092):

```bash
kubectl run kafka-nc --rm -i --restart=Never --image=busybox:1.36 -n trisla -- sh -c "nc -zv kafka.trisla.svc.cluster.local 9092"
```

**Expected**: `open` or `succeeded`. Adjust host/port if your Kafka chart uses different names.

### 7.5 How SLA-Agent Depends on Kafka

The SLA-Agent runs a **Kafka consumer** for `trisla-i05-actions`. It expects:

- **KAFKA_BOOTSTRAP_SERVERS**: e.g. `kafka.trisla.svc.cluster.local:9092`.
- **KAFKA_ENABLED**: `true` (or equivalent). If disabled, the Agent skips consumption; no E2E validation.

At startup, the Agent connects to Kafka and joins a consumer group (e.g. `sla-agents-i05-consumer`). If Kafka is down or unreachable, the Agent logs connection errors and may exit or retry indefinitely.

**Phase 2 GATE**: Kafka Pod(s) `Ready`; DNS resolves; port 9092 reachable. **PASS** → Phase 3.

---

## 8. Phase 3 — Optional Blockchain Governance

### 8.1 When Besu + BC-NSSMF Are Required

Use them when you need **on-chain** SLA lifecycle: `createSLA`, `activateSLA`, `reportViolation`, `renegotiateSLA`, `closeSLA`. For **minimal** or **stub-only** deployments, you can omit Phase 3 and disable BC-NSSMF.

### 8.2 What Happens If Omitted

BC-NSSMF is disabled (`bc-nssmf.enabled=false`). No blockchain calls; no smart-contract deployment. The rest of TriSLA (SEM-CSMF, ML-NSMF, Decision Engine, Kafka, SLA-Agent) still works. E2E validation **without** blockchain is possible.

### 8.3 Deploy Besu (Single Node)

**Command** (example; Besu may be part of `helm/trisla` or a separate chart):

```bash
# If Besu is in helm/trisla:
helm upgrade --install trisla helm/trisla -n trisla \
  --set global.namespace=trisla \
  --set besu.enabled=true \
  --set sem-csmf.enabled=false \
  --set ml-nsmf.enabled=false \
  --set decision-engine.enabled=false \
  --set bc-nssmf.enabled=false \
  --set sla-agent.enabled=false \
  --set nasp-adapter.enabled=false \
  --set portal.enabled=false
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=besu -n trisla --timeout=600s
```

**Expected**: Besu Pod(s) `Running`. RPC typically on port 8545.

**Failure**: CrashLoopBackOff (e.g. genesis, disk, memory) → Check logs, PVC, and resource requests; fix and retry.

### 8.4 Deploy BC-NSSMF

BC-NSSMF is usually deployed with the rest of core in Phase 4. Enable it only if Besu is ready. Set `bc-nssmf.enabled=true` and ensure `BC_BESU_RPC_URL` (or equivalent) points to `trisla-besu.trisla.svc.cluster.local:8545`.

### 8.5 Validate RPC, BC-NSSMF Health, Smart Contract Readiness

**RPC**:

```bash
kubectl port-forward -n trisla svc/trisla-besu 8545:8545 &
curl -s -X POST http://localhost:8545 -H "Content-Type: application/json" --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
kill %1 2>/dev/null
```

**Expected**: JSON with `result` (block number in hex).

**BC-NSSMF health** (after Phase 4):

```bash
kubectl exec -n trisla deploy/trisla-bc-nssmf -- curl -s http://localhost:8083/health
```

**Expected**: HTTP 200.

**Smart contract readiness**: Conceptually, BC-NSSMF deploys or attaches to a contract. Logs should show successful deployment or binding. No explicit command here; rely on BC-NSSMF logs and health.

**Phase 3 GATE**: If using blockchain, Besu is `Ready` and RPC responds. **PASS** → Phase 4. **SKIP** if not using blockchain.

---

## 9. Phase 4 — Core TriSLA Services Deployment

### 9.1 Deploy via Helm

**Purpose**: Install all core TriSLA components (SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, SLA-Agent, NASP Adapter, API Backend) via the `helm/trisla` chart.

**Command** (from repository root; adjust paths if your layout differs):

```bash
helm upgrade --install trisla ./helm/trisla -n trisla \
  --set global.namespace=trisla \
  --set global.imagePullSecrets[0].name=ghcr-secret \
  --set sem-csmf.enabled=true \
  --set ml-nsmf.enabled=true \
  --set "decision-engine.enabled=true" \
  --set bc-nssmf.enabled=true \
  --set sla-agent.enabled=true \
  --set nasp-adapter.enabled=true \
  --set portal.enabled=false
```

If your chart uses different keys (e.g. `semCsmf`), adjust. If you have `values-nasp.yaml` or a custom values file:

```bash
helm upgrade --install trisla ./helm/trisla -n trisla -f ./helm/trisla/values-nasp.yaml
```

**Expected**: `Release "trisla" has been upgraded. Happy Helming!` (or `installed`). No template errors.

**Failure**: `Error: ...` (e.g. unknown key, missing value) → Fix `--set` keys or values file; ensure chart path is correct.

### 9.2 What the Chart Installs

The `helm/trisla` chart typically deploys:

- Deployments: `trisla-sem-csmf`, `trisla-ml-nsmf`, `trisla-decision-engine`, `trisla-bc-nssmf`, `trisla-sla-agent`, `trisla-nasp-adapter`, `trisla-api-backend` (if present).
- Services: One per Deployment, same names.
- ServiceMonitors: For Prometheus scraping (if enabled).
- PrometheusRules: Optional alerting rules.

### 9.3 How Services Discover Each Other

Components use **Kubernetes DNS**: `trisla-<service>.trisla.svc.cluster.local`. The Decision Engine, for example, is configured with URLs for SEM-CSMF, ML-NSMF, and Kafka. All run in `trisla`; no cross-namespace discovery needed.

### 9.4 Why All Images Must Share the Same Tag

TriSLA APIs and Kafka event schemas are **versioned**. Mixing image tags (e.g. SEM-CSMF `v3.9.3`, ML-NSMF `v3.8.0`) can cause request/response or event format mismatches. **Pin every component to the same tag** (e.g. `v3.9.3`) for reproducibility.

### 9.5 Validation

**Command**:

```bash
kubectl get pods -n trisla
kubectl get svc -n trisla
```

**Expected**:

- Pods: `trisla-sem-csmf-*`, `trisla-ml-nsmf-*`, `trisla-decision-engine-*`, `trisla-bc-nssmf-*`, `trisla-sla-agent-*`, `trisla-nasp-adapter-*` (and optionally `trisla-api-backend-*`) in `Running` / `1/1`.
- Services: Matching `ClusterIP` (or `NodePort`) entries.

**Expected pod count**: At least 6 (SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, SLA-Agent, NASP Adapter). Plus API Backend, Besu, Kafka if deployed via same chart or separately.

**Stateful vs stateless**: Besu and Kafka are **stateful** (PVCs). TriSLA core components are **stateless**; no PVCs.

**Failure**: Any Pod in `ImagePullBackOff`, `CrashLoopBackOff`, or `Pending` → See §14 (Common Failure Modes); fix and retry.

**Phase 4 GATE**: All core Pods `Running` and `Ready`; Services exist. **PASS** → Phase 5.

---

## 10. Phase 5 — SLA-Agent Operational Validation

### 10.1 Why SLA-Agent Is Proof of End-to-End Flow

The SLA-Agent **consumes** decision events from Kafka. If it receives and processes them, the chain **Portal/API → SEM-CSMF → ML-NSMF → Decision Engine → Kafka → SLA-Agent** is working. Validating the Agent therefore validates E2E.

### 10.2 What It Consumes and Emits

- **Consumes**: `trisla-i05-actions` (decision events).
- **Emits**: `trisla-i06-agent-events`, `trisla-i07-agent-actions`.

### 10.3 Validate Kafka Consumer Group and Logs

**Consumer group** (if your Kafka exposes consumer groups):

```bash
# Example for Kafka; adjust for your setup
kubectl exec -n trisla deploy/kafka -- kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list | grep sla
```

**Expected**: A group such as `sla-agents-i05-consumer`.

**Logs**:

```bash
kubectl logs -n trisla deploy/trisla-sla-agent -f --tail=100
```

**Expected**: Log lines indicating successful Kafka consumer creation and (after E2E traffic) **decision consumption** (e.g. "Consumed decision", "Processing intent", or similar). No repeated "connection refused" or "broker unreachable".

### 10.4 What Absence of Logs Means

- **No consumer logs at all**: Agent may not be starting (check CrashLoopBackOff, env vars, Kafka bootstrap servers).
- **Consumer created but no "Consumed" logs**: No traffic on `trisla-i05-actions`. Decision Engine may not be publishing (check Decision Engine logs and E2E submission). Or Kafka topic missing / wrong topic name.
- **Connection errors**: Kafka unreachable; fix bootstrap servers, DNS, or network.

**Phase 5 GATE**: SLA-Agent Pod `Running`; logs show consumer init and (after E2E test) decision consumption. **PASS** → Phase 6. **FAIL** → debug Kafka and Decision Engine (§14).

---

## 11. Phase 6 — Portal Deployment (Optional UI)

### 11.1 Two Options

- **Option A**: Separate chart `helm/trisla-portal`. Deploy with:

  ```bash
  helm upgrade --install trisla-portal ./helm/trisla-portal -n trisla -f ./helm/trisla-portal/values.yaml
  ```

- **Option B**: Portal bundled in `helm/trisla`. Enable with:

  ```bash
  helm upgrade trisla ./helm/trisla -n trisla --set portal.enabled=true
  ```

Use whichever matches your repository layout.

### 11.2 Backend vs Frontend Separation

- **Portal Backend**: REST API for SLA submit, status, etc. Calls SEM-CSMF and Decision Engine. Exposed as a Service (e.g. `trisla-portal-backend` or `trisla-portal`).
- **Portal Frontend**: Static assets + API proxy. Sends requests to Backend. Exposed via NodePort or Ingress.

### 11.3 API Routing and Base URL Pitfalls

- Frontend must know the **Backend base URL** (env or build-time). If wrong, browser requests fail (404, CORS, or connection refused).
- Backend must allow Frontend origin (CORS). Misconfiguration → CORS errors in browser.

### 11.4 Validation

```bash
kubectl get pods -n trisla | grep portal
kubectl get svc -n trisla | grep portal
```

**Expected**: Portal Backend and Frontend Pods `Running`; Services exist. Access Frontend via NodePort or Ingress; submit a test SLA and confirm 200/202.

**Phase 6 GATE**: Portal Pods `Running`; UI loads; submission reaches Backend. **PASS** → Phase 7. **SKIP** if not deploying Portal.

---

## 12. Phase 7 — End-to-End Functional Validation (CRITICAL)

This phase is the **scientific proof** of deployment correctness.

### 12.1 Full SLA Transaction

1. **SLA submission**: Client sends SLA request (e.g. template, form values).
2. **Semantic validation**: SEM-CSMF validates intent and ontology.
3. **ML inference**: ML-NSMF returns risk/confidence.
4. **Decision emission**: Decision Engine produces ACCEPT/REJECT/RENEG and **publishes to Kafka**.
5. **SLA-Agent reaction**: Agent consumes event, runs lifecycle logic, optionally publishes I-06/I-07.
6. **Optional blockchain**: BC-NSSMF records lifecycle on-chain.

### 12.2 curl Example

**Purpose**: Submit an SLA via Portal Backend (or API Backend) and inspect response.

**Command** (adjust URL if you use NodePort/Ingress):

```bash
kubectl port-forward -n trisla svc/trisla-portal-backend 8080:8080 &
curl -s -X POST http://localhost:8080/api/v1/sla/submit \
  -H "Content-Type: application/json" \
  -d '{"template_id":"template:eMBB","form_values":{"latency_ms":10,"throughput_mbps":100}}'
kill %1 2>/dev/null
```

If your API uses a different path or body, adjust. Replace `trisla-portal-backend` with the actual Service name if different.

**Expected**: HTTP 200 or 202; JSON with `intent_id`, `decision`, or similar.

### 12.3 Expected JSON Patterns

- **ACCEPT**: `{"decision":"ACCEPT", "intent_id":"...", ...}` or equivalent.
- **REJECT**: `{"decision":"REJECT", ...}`.
- **Error**: 4xx/5xx with `{"error":"...","message":"..."}` or similar.

### 12.4 What ACCEPT / REJECT Proves

- **ACCEPT**: Full path (SEM-CSMF → ML-NSMF → Decision Engine) executed; decision published to Kafka; SLA-Agent can consume it. Control-plane flow is **correct**.
- **REJECT**: Same path executed; policy or ML produced REJECT. Also valid.
- **5xx or no response**: Failure upstream (SEM-CSMF, ML-NSMF, Decision Engine, or API routing). Check logs and §14.

**Phase 7 GATE**: `curl` returns 200/202 and JSON with `decision`; SLA-Agent logs show consumption. **PASS** → deployment validated. **FAIL** → debug E2E path (§14).

---

## 13. Observability Validation

### 13.1 Metrics That MUST Exist

After TriSLA and ServiceMonitors are in place, Prometheus should scrape:

- **Up**: `up{job=~"trisla-.*"} == 1` for each TriSLA Service.
- **Counters**: e.g. `trisla_intents_processed_total`, `trisla_decision_intents_total`, `http_requests_total{job=~"trisla-.*"}`.
- **Histograms**: e.g. `http_request_duration_seconds_bucket{job=~"trisla-.*"}`.

Exact names depend on instrumentation; use `{job=~"trisla-.*"}` or similar.

### 13.2 Why Empty PromQL Queries Are Common

- **Wrong job label**: Prometheus uses `job` from scrape config. ServiceMonitors set it via `jobLabel` or defaults. If you query `job="trisla-decision-engine"` but the actual label differs, you get no data.
- **Namespace**: Prometheus must scrape `trisla`. If `namespaceSelector` excludes it, no series.
- **No traffic**: `rate(...[5m])` is 0 if there have been no requests. Use `increase(...[1h])` or longer windows for low-traffic checks.

### 13.3 Choosing Query Windows

- **Availability**: `up{job=~"trisla-.*"}` — instant.
- **Throughput**: `rate(http_requests_total{job=~"trisla-.*"}[5m])` — 5m window.
- **Low traffic**: `increase(trisla_intents_processed_total[1h])` — 1h window.

### 13.4 Example PromQL Queries

```promql
# TriSLA targets up
up{job=~"trisla-.*"}

# Request rate (5m)
rate(http_requests_total{job=~"trisla-.*"}[5m])

# Intent processing increase (1h)
increase(trisla_intents_processed_total[1h])
```

Run in Prometheus UI or via `curl` to the Prometheus API. **PASS**: Series returned. **FAIL**: Fix ServiceMonitors and scrape config (§14).

---

## 14. Common Failure Modes (Deep)

### 14.1 ImagePullBackOff

**Symptom**: Pods stuck in `ImagePullBackOff` or `ErrImagePull`.

**Root cause**: Missing or invalid `imagePullSecret`; wrong image name/tag; registry auth failure.

**Fix**:

1. `kubectl get secret ghcr-secret -n trisla`. If missing, create it (see `INSTALLATION.md` §8.4).
2. `kubectl describe pod <trisla-pod> -n trisla` → check `Events` for pull error.
3. Ensure `global.imagePullSecrets[0].name=ghcr-secret` in Helm values and that Pod spec uses `imagePullSecrets`.
4. `kubectl delete pods -n trisla --all` to force repull after fixing Secret.

**Gate**: Pods transition to `Running`.

### 14.2 Kafka Ready But No Events

**Symptom**: Kafka Pods `Running`; SLA-Agent `Running`; no "Consumed" logs; no I-06/I-07 traffic.

**Root cause**: (a) Decision Engine not publishing to Kafka (wrong bootstrap servers, topic, or disabled producer); (b) SLA-Agent `KAFKA_BOOTSTRAP_SERVERS` or topic wrong; (c) no E2E traffic yet (no SLA submissions).

**Fix**:

1. Confirm E2E traffic: submit SLA via Portal/curl (§12).
2. Check Decision Engine logs for "published" or "Kafka" errors.
3. Verify SLA-Agent `KAFKA_BOOTSTRAP_SERVERS` and `KAFKA_ENABLED=true`; topic `trisla-i05-actions` exists or is auto-created.
4. Verify same Kafka bootstrap servers in Decision Engine and SLA-Agent.

**Gate**: SLA-Agent logs show consumption after E2E submit.

### 14.3 Portal Frontend Cannot Reach Backend

**Symptom**: UI loads but API calls fail (404, CORS, connection refused).

**Root cause**: (a) Frontend base URL points to wrong Backend host/port; (b) Backend Service not exposed or wrong port; (c) CORS disallows Frontend origin.

**Fix**:

1. Check Frontend env/build-time config for API base URL; must match Backend Service (or NodePort/Ingress).
2. `kubectl get svc -n trisla` → confirm Backend Service and port.
3. Test Backend from within cluster: `kubectl run curl --rm -i --restart=Never --image=curlimages/curl -n trisla -- curl -s http://trisla-portal-backend.trisla.svc.cluster.local:8080/health`.
4. Adjust CORS on Backend to allow Frontend origin.

**Gate**: Browser can call Backend; 200/202 on submit.

### 14.4 Prometheus Shows No Data

**Symptom**: `trisla_*` or `up{job=~"trisla-.*"}` return no series.

**Root cause**: (a) ServiceMonitors not created or not selected by Prometheus; (b) Prometheus does not scrape `trisla` namespace; (c) wrong `job` labels in queries.

**Fix**:

1. `kubectl get servicemonitors -n trisla` → ServiceMonitors exist.
2. Check Prometheus scrape config / `namespaceSelector` for `trisla`.
3. Prometheus UI → Status → Targets → verify `trisla` targets and `job` labels.
4. Query `up` without job filter, then narrow to `trisla` jobs.

**Gate**: `up{job=~"trisla-.*"}` returns series.

### 14.5 Decision Engine Running But No ACCEPTs

**Symptom**: Decision Engine Pod `Running`; health OK; SLA submissions return 200, but `decision` is always REJECT or never ACCEPT.

**Root cause**: (a) Policy or ML configured to reject (e.g. risk threshold); (b) SEM-CSMF or ML-NSMF returning errors or strict outcomes; (c) Test payload not matching expected template (e.g. template_id, form_values).

**Fix**:

1. Check Decision Engine logs for SEM-CSMF/ML-NSMF responses and decision rationale.
2. Check SEM-CSMF and ML-NSMF logs for validation/inference errors.
3. Use a known-good payload (e.g. from reproducibility docs or tests); ensure `template_id` and `form_values` match schema.
4. Adjust ML or policy config if you intend to get ACCEPTs for the test payload.

**Gate**: At least one ACCEPT for a controlled test payload, or explicit understanding of REJECT reason.

---

## 15. Reproducibility Guarantees

### 15.1 Parameters That Affect Reproducibility

- **Image tags**: All TriSLA components **same** tag (e.g. `v3.9.3`).
- **Helm chart version**: Use a specific chart version or Git tag.
- **Values**: Record `--set` and values files (excluding secrets); same Kafka bootstrap, same Besu RPC if used.
- **Kubernetes version**: Document cluster version (e.g. 1.26).
- **Order**: Deploy in the order given (Observability → Kafka → Optional Blockchain → Core → Portal).

### 15.2 Why Version Pinning Matters

Mixing versions causes API/event schema drift and non-reproducible behavior. Pin **everything** (images, chart, Kafka, Besu) when reporting experiments.

### 15.3 How to Cite This Deployment in a Paper

- **Artifact**: TriSLA deployment following `docs/deployment/DEPLOYMENT.md` and `docs/INSTALLATION.md`.
- **Version**: Git tag (e.g. `v3.9.3`) and chart/image tags.
- **Scope**: Control-plane only; generic Kubernetes; no proprietary platform details.

---

## 16. Public Scope Disclaimer

### 16.1 What Is Intentionally Excluded

- **Internal clusters, hostnames, or paths**: No references to private labs, specific nodes, or evidence folders.
- **Proprietary platforms**: NASP Adapter configuration for specific vendors or deployments is environment-specific; not part of this guide.
- **Secrets and credentials**: Never stored in Git; use Kubernetes Secrets and document usage only.

### 16.2 Why Exclusion Does Not Invalidate Experiments

- **Deployment**: TriSLA can be reproduced on any conformant Kubernetes cluster using this guide and the same artifact versions.
- **Validation**: Success criteria (Pods Ready, health, E2E flow, metrics) are defined in terms of standard interfaces. Reproducibility holds as long as the same steps and versions are used.

---

**End of Deployment Guide.** For prerequisites and tooling, see `docs/INSTALLATION.md`.
