# TriSLA End-to-End Deployment Guide

This document answers: **How do I deploy TriSLA step by step, validate it, and know it is working?** It is procedural, executable, and verifiable. Prerequisites are in `docs/INSTALLATION.md`.

---

## 1. Deployment Philosophy

### 1.1 Why Order Matters

TriSLA has **hard dependencies** between components:

- **SEM-CSMF** and **ML-NSMF** feed the **Decision Engine**. The Decision Engine must not start before they are ready.
- **BC-NSSMF** depends on **Besu** (or another Ethereum-compatible node) for on-chain operations.
- **SLA-Agent** consumes decision events from **Kafka** and optionally uses **NASP Adapter** for metrics.
- **Portal** (backend/frontend) depends on SEM-CSMF, Decision Engine, and API Backend.

Deploying in the wrong order causes **CrashLoopBackOff**, **503** from downstream services, or incomplete control-plane flows. Follow the phased order below.

### 1.2 Why Event Backbone First

The **event backbone** (Kafka) is mandatory for the SLA-Agent. The Decision Engine publishes admission outcomes to Kafka; the SLA-Agent consumes them. If Kafka is not running and reachable **before** core services, the SLA-Agent cannot receive decisions and the E2E flow is broken. Deploy Kafka (or ensure it is available) **before** Phase 4 (Core TriSLA services).

### 1.3 Why Observability First

- **Prometheus** (and optional ServiceMonitors) should be in place **before** TriSLA so that metrics are scraped from first rollout.
- **OpenTelemetry Collector** (if used) should be deployed **before** enabling OTLP in TriSLA components.

This avoids gaps in metrics and traces and ensures validation queries (e.g. `trisla_*`) return data from the start.

### 1.4 Why Portal Last

The **Portal** (backend and frontend) depends on SEM-CSMF, Decision Engine, and API Backend. Deploy core services first, validate health and E2E flow, then add the Portal. Deploying Portal too early leads to **503** and **SEM-CSMF offline** errors.

---

## 2. Logical Architecture Overview

### 2.1 Deployment Layers

**Layer 1 — Backbone**

- **Kafka**: Decision events (I-05), agent events (I-06), action results (I-07). Required for SLA-Agent.
- **Optional**: Besu (blockchain) if using BC-NSSMF with on-chain governance.

**Layer 2 — Core Services**

- **SEM-CSMF**: Semantic validation, gRPC. Entry point for intents.
- **ML-NSMF**: Risk prediction, HTTP. Consumes metrics (e.g. Prometheus) and exposes inference API.
- **Decision Engine**: Admission logic, HTTP. Calls SEM-CSMF and ML-NSMF; publishes to Kafka.
- **BC-NSSMF**: Smart-contract interface, HTTP. Talks to Besu; optional if using stub.
- **SLA-Agent**: Consumes Kafka (I-05); executes lifecycle actions; publishes I-06, I-07.
- **NASP Adapter**: Platform abstraction, HTTP. Stub or real mode.

**Layer 3 — Portal**

- **Portal Backend**: REST API for SLA submission and status. Calls SEM-CSMF, Decision Engine.
- **Portal Frontend**: Web UI. Calls Portal Backend.
- **API Backend**: If separate from Portal Backend in your Helm setup, provides additional APIs.

### 2.2 Runtime Interaction

- **Intent flow**: Portal Backend → SEM-CSMF (semantic) → ML-NSMF (risk) → Decision Engine (decision) → Kafka (I-05) → SLA-Agent.
- **Lifecycle**: SLA-Agent consumes I-05, coordinates actions (optionally via NASP Adapter), publishes I-06/I-07. BC-NSSMF may record lifecycle on-chain.
- **Observability**: Prometheus scrapes `/metrics`; optional OTLP sends traces to a collector.

---

## 3. Namespaces and Release Strategy

### 3.1 Namespace Usage

- **`trisla`**: Default namespace for TriSLA workloads (SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, SLA-Agent, NASP Adapter, Portal, API Backend). Configurable via `global.namespace` in Helm values.
- **`monitoring`** (or similar): Prometheus, Grafana, Alertmanager. TriSLA does not mandate a name; ensure ServiceMonitors target the `trisla` namespace.

### 3.2 Helm Release Naming

- **Release name**: Typically `trisla`. Resource names are derived from the Helm chart (e.g. `trisla-sem-csmf`, `trisla-decision-engine`).
- **Chart**: `helm/trisla` (from the repository root).

### 3.3 Why Isolation Matters

- Isolating TriSLA in a dedicated namespace simplifies RBAC, network policies, and cleanup.
- Image pull secrets and ConfigMaps are namespace-scoped; keep them in `trisla` (or the configured namespace).

### 3.4 Commands

```bash
kubectl create namespace trisla
kubectl get namespace trisla
```

**Expected**: Namespace `trisla` exists.

---

## 4. Helm Charts and Values

### 4.1 Chart Separation

- **Core**: `helm/trisla` contains Deployments, Services, ServiceMonitors, and PrometheusRules for SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, SLA-Agent, NASP Adapter, API Backend, Portal.
- **Observability**: Optional separate charts (e.g. `kube-prometheus-stack`, OTLP Collector). TriSLA chart may reference a `monitoring` namespace; deploy Prometheus first if using ServiceMonitors.

### 4.2 Values Philosophy

- **Defaults**: Chart defaults may enable only a subset of components. Override with `--set` or a values file.
- **Secrets**: Image pull secrets, Besu keys, etc. are **not** stored in values in Git. Use Kubernetes Secrets and reference them in values.

### 4.3 What MUST Be Changed vs Defaults

- **`global.imagePullSecrets`**: Set if using private images (e.g. GHCR). Example: `global.imagePullSecrets[0].name=ghcr-secret`.
- **Image tags**: Set each component’s `image.tag` to a **consistent** version (e.g. `v3.9.3`) for reproducibility.
- **Kafka**: Configure Kafka bootstrap servers (e.g. `KAFKA_BOOTSTRAP_SERVERS`) for SLA-Agent if not using a default.
- **Besu**: If using BC-NSSMF with Besu, set `besu.enabled=true` and ensure RPC URL and (if applicable) private key are provided via Secrets or values.

---

## 5. Step-by-Step Deployment Phases

### Phase 0 — Namespace and Prerequisites

**Goal**: Namespace exists; GHCR secret exists; CRDs (if using NASP Adapter) are installed.

**Commands**:

```bash
kubectl create namespace trisla
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<GITHUB_USER> \
  --docker-password=<GITHUB_PAT> \
  --docker-email=<EMAIL> \
  -n trisla
kubectl get secret ghcr-secret -n trisla
```

**CRDs** (if NASP Adapter is enabled):

```bash
kubectl apply -f apps/nasp-adapter/crds/networksliceinstances.trisla.io.yaml
kubectl apply -f apps/nasp-adapter/crds/networkslicesubnetinstances.trisla.io.yaml
kubectl get crd | grep networkslice
```

**Expected**: Namespace created; secret exists; CRDs `networksliceinstances.trisla.io` and `networkslicesubnetinstances.trisla.io` exist.

**Gate**: All commands succeed. **FAIL**: Fix namespace, secret, or CRD errors before continuing.

---

### Phase 1 — Observability

**Goal**: Prometheus (and optional OTLP Collector) are running. ServiceMonitors can later target TriSLA.

**Option A — Existing Prometheus**

```bash
kubectl get pods -n monitoring | grep prometheus
kubectl get crd servicemonitors.monitoring.coreos.com
```

**Expected**: Prometheus pods running; CRD exists. **Gate**: PASS.

**Option B — Install kube-prometheus-stack**

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=prometheus -n monitoring --timeout=300s
```

**Expected**: Prometheus is ready. **Gate**: Pods `Running`.

**OTLP Collector** (optional): Deploy per your observability setup (e.g. `helm/trisla-observability/otel-collector.yaml` or equivalent). Ensure the OTLP endpoint (e.g. `http://otel-collector.observability.svc.cluster.local:4317`) is reachable from the `trisla` namespace.

---

### Phase 2 — Kafka

**Goal**: Kafka is running and reachable from `trisla`. SLA-Agent will use it for I-05, I-06, I-07.

**Option A — Existing Kafka**

Verify bootstrap service (e.g. `kafka.kafka.svc.cluster.local:9092`) and that `trisla` namespace can reach it (e.g. `kubectl run` + `nc` or Kafka client).

**Option B — Deploy Kafka in-cluster**

Use Bitnami Kafka chart or equivalent:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install kafka bitnami/kafka -n trisla
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=kafka -n trisla --timeout=300s
```

**Expected**: Kafka pods `Running`. **Gate**: Kafka is ready; bootstrap server known (e.g. `kafka.trisla.svc.cluster.local:9092`).

---

### Phase 3 — Optional Besu + BC-NSSMF

**Goal**: If using **full governance**, Besu is running and BC-NSSMF can connect.

**Commands**:

```bash
helm upgrade --install trisla helm/trisla -n trisla \
  --set global.imagePullSecrets[0].name=ghcr-secret \
  --set global.namespace=trisla \
  --set besu.enabled=true \
  --set sem-csmf.enabled=false \
  --set ml-nsmf.enabled=false \
  --set decision-engine.enabled=false \
  --set bc-nssmf.enabled=false \
  --set sla-agent.enabled=false \
  --set nasp-adapter.enabled=false \
  --set portal.enabled=false
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=trisla -n trisla --timeout=600s
kubectl get pods -n trisla | grep besu
```

**Expected**: Besu pod(s) `Running`. **Gate**: Besu ready. **Skip** this phase if not using blockchain.

---

### Phase 4 — Core TriSLA Services

**Goal**: SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, SLA-Agent, NASP Adapter (and optionally API Backend) are deployed and **Running**.

**Commands**:

```bash
helm upgrade --install trisla helm/trisla -n trisla \
  --set global.imagePullSecrets[0].name=ghcr-secret \
  --set global.namespace=trisla \
  --set sem-csmf.enabled=true \
  --set ml-nsmf.enabled=true \
  --set decision-engine.enabled=true \
  --set bc-nssmf.enabled=true \
  --set sla-agent.enabled=true \
  --set nasp-adapter.enabled=true \
  --set besu.enabled=true \
  --set portal.enabled=false
kubectl wait --for=condition=available deployment/trisla-sem-csmf -n trisla --timeout=300s
kubectl wait --for=condition=available deployment/trisla-ml-nsmf -n trisla --timeout=300s
kubectl wait --for=condition=available deployment/trisla-decision-engine -n trisla --timeout=300s
kubectl wait --for=condition=available deployment/trisla-bc-nssmf -n trisla --timeout=300s
kubectl wait --for=condition=available deployment/trisla-sla-agent -n trisla --timeout=300s
kubectl wait --for=condition=available deployment/trisla-nasp-adapter -n trisla --timeout=300s
kubectl get pods -n trisla
```

**Expected**: All listed deployments have `AVAILABLE` replicas; pods show `READY 1/1` and `STATUS Running`.

**Gate**: All core pods `Running` and `Ready`. **FAIL**: Check `kubectl describe pod` and `kubectl logs` for the failing deployment; see §11 (Common Failure Modes).

**Note**: Exact Helm keys (`sem-csmf`, `ml-nsmf`, etc.) must match your chart’s `values.yaml`. Adjust if your chart uses different keys (e.g. `semCsmf`).

---

### Phase 5 — Portal

**Goal**: Portal Backend and Frontend are deployed and reachable.

**Commands**:

```bash
helm upgrade trisla helm/trisla -n trisla \
  --set portal.enabled=true
kubectl wait --for=condition=available deployment/trisla-portal-backend -n trisla --timeout=300s
kubectl wait --for=condition=available deployment/trisla-portal-frontend -n trisla --timeout=300s
kubectl get pods -n trisla | grep portal
```

**Expected**: Portal backend and frontend pods `Running`. **Gate**: Both deployments `AVAILABLE`.

---

## 6. Service and Pod Validation Gates

### 6.1 What “Running” Actually Means

- **Status**: `Running` — container has started and not exited.
- **Ready**: `1/1` (or `n/n`) — readiness probe is passing. Traffic is sent only to ready pods.

A pod can be `Running` but not `Ready` (e.g. failing readiness checks). For validation, **both** must hold.

### 6.2 Replica Expectations

- **Default**: One replica per deployment unless overridden. For HA, increase replicas and ensure Kafka consumer group and Besu topology support it.
- **Check**:
  ```bash
  kubectl get deployments -n trisla
  ```
  **Expected**: `DESIRED` = `CURRENT` = `UP-TO-DATE` = `AVAILABLE` for each TriSLA deployment.

### 6.3 Endpoint Readiness

```bash
kubectl get endpoints -n trisla
```

**Expected**: Each service has at least one endpoint (subset addresses). Empty subsets indicate no ready pods for that service.

### 6.4 kubectl Commands and Interpretation

| Command | Interpretation |
|--------|-----------------|
| `kubectl get pods -n trisla` | All TriSLA pods should be `Running` and `READY 1/1`. |
| `kubectl get deployment -n trisla` | All `AVAILABLE` ≥ 1. |
| `kubectl get endpoints -n trisla` | Non-empty subsets for each TriSLA service. |
| `kubectl rollout status deployment/<name> -n trisla` | Rollout completes without timeout. |

---

## 7. Health Checks

### 7.1 Why Health Endpoints Matter

- **Liveness**: Kubernetes restarts the container if the liveness probe fails.
- **Readiness**: Kubernetes removes the pod from Service endpoints if the readiness probe fails. This avoids sending traffic to broken instances.

TriSLA components expose **HTTP** `/health` (or gRPC health) for probes. Correct port configuration is critical; mismatches cause **CrashLoopBackOff** or **503**.

### 7.2 How to Port-Forward

Example — Decision Engine:

```bash
kubectl port-forward -n trisla svc/trisla-decision-engine 8082:8082
curl -s http://localhost:8082/health
```

**Expected**: HTTP 200 and a healthy payload (e.g. `{"status":"ok"}`). **Fail**: Connection refused or 5xx — check Service port, targetPort, and container port in Helm values.

### 7.3 What HTTP 200 Means in TriSLA Context

- **Decision Engine**: `/health` returns 200 when the process is up and can serve requests. It does **not** guarantee SEM-CSMF or ML-NSMF are reachable; that is validated via E2E flow.
- **SEM-CSMF**: gRPC health check; equivalent to “process ready.”
- **BC-NSSMF**: HTTP `/health` — process ready; optional check against Besu RPC.

---

## 8. Portal Exposure and Access

### 8.1 NodePort

- Set `portal.service.type=NodePort` (or equivalent) in values. Kubernetes allocates a port on each node.
- **Access**: `http://<node-ip>:<nodeport>`. Ensure firewall rules allow traffic.

### 8.2 Ingress

- Use an Ingress resource and controller. Point host/path to the Portal Frontend or Backend service.
- **TLS**: Terminate at Ingress; use cert-manager or manual certs.

### 8.3 Common Misconfigurations

- **Wrong service**: Frontend must target Backend URL (e.g. env var), not Backend’s cluster-internal name only if users are outside the cluster.
- **CORS**: Backend must allow the Frontend origin. 403/ CORS errors indicate backend CORS config.
- **503 SEM-CSMF offline**: Backend calls SEM-CSMF; if SEM-CSMF is down or wrong URL, 503 results. Verify SEM-CSMF is running and Backend config points to `trisla-sem-csmf.trisla.svc.cluster.local` (or configured namespace).

---

## 9. End-to-End Functional Validation

### 9.1 Full Control-Plane Transaction

A minimal E2E flow:

1. **SLA submission**: Client sends an SLA request (e.g. via Portal Backend `/api/v1/sla/submit` or equivalent).
2. **Semantic processing**: SEM-CSMF validates intent and ontology.
3. **ML inference**: ML-NSMF returns risk/confidence.
4. **Decision generation**: Decision Engine produces ACCEPT/REJECT/RENEG and publishes to Kafka (I-05).
5. **Event emission**: SLA-Agent consumes I-05, executes actions, publishes I-06/I-07.
6. **Optional blockchain registration**: BC-NSSMF records lifecycle on-chain (if Besu enabled).

### 9.2 curl Example

**Submit SLA** (adjust URL if your API differs):

```bash
curl -X POST http://<portal-backend-url>/api/v1/sla/submit \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "template:eMBB",
    "form_values": { "latency_ms": 10, "throughput_mbps": 100 }
  }'
```

**Expected**: HTTP 200 or 202; JSON body with `intent_id` or `decision_id`.

### 9.3 Expected JSON Patterns

- **Success**: `{"intent_id":"...", "decision":"ACCEPT", ...}` or similar.
- **Reject**: `{"decision":"REJECT", ...}`.
- **Error**: 4xx/5xx with error message.

### 9.4 What Proves Success

- **HTTP 200/202** from submit endpoint.
- **Logs**: Decision Engine and SLA-Agent logs show the same `intent_id` / `decision_id`.
- **Kafka**: Messages on `trisla-i05-actions`, then `trisla-i06-agent-events` or `trisla-i07-agent-actions`.
- **Metrics**: `trisla_intents_processed_total` or similar counters increase (see §10).
- **Blockchain** (if used): BC-NSSMF logs show `tx_hash` or equivalent.

---

## 10. Observability Validation

### 10.1 What Must Be Observable

- **Metrics**: Counters (intents, decisions, errors), histograms (latency), gauges (queue size). Exposed at `/metrics` per component.
- **Logs**: Structured logs with `intent_id`, `decision_id`, correlation IDs.
- **Traces** (optional): OTLP spans across SEM-CSMF → ML-NSMF → Decision Engine → Kafka → SLA-Agent.

### 10.2 Typical PromQL Pitfalls

- **No data**: ServiceMonitors not created or Prometheus not scraping `trisla` namespace. Check `kubectl get servicemonitor -n trisla` and Prometheus config.
- **Job label mismatch**: PrometheusRules use `job=~"trisla-.*"`. Ensure ServiceMonitor `jobLabel` or scrape config matches.
- **Wrong namespace**: Prometheus must scrape `trisla` (or `global.namespace`). Verify `namespaceSelector` in ServiceMonitors.

### 10.3 Low-Frequency Experiment Considerations

- **Rate()**: For low traffic, `rate(...[5m])` can be zero or very small. Use `increase(...[1h])` or longer windows for validation.
- **Absence of data**: `up{job="trisla-decision-engine"} == 0` indicates scrape failure or pod down, not necessarily “no intents.”

---

## 11. Common Failure Modes

### 11.1 Image Pull (ImagePullBackOff)

**Symptom**: Pods stuck in `ImagePullBackOff` or `ErrImagePull`.

**Root cause**: Missing or invalid `imagePullSecret`; wrong image name/tag; registry auth failure.

**Fix**:

```bash
kubectl get secret ghcr-secret -n trisla
kubectl create secret docker-registry ghcr-secret ... -n trisla   # if missing
helm upgrade trisla helm/trisla -n trisla --set global.imagePullSecrets[0].name=ghcr-secret
kubectl delete pods -n trisla --all
```

**Gate**: Pods transition to `Running`.

---

### 11.2 Kafka Readiness

**Symptom**: SLA-Agent CrashLoopBackOff; logs show “connection refused” or “broker unreachable.”

**Root cause**: Kafka not running, wrong bootstrap servers, or network isolation.

**Fix**:

- Verify Kafka pods `Running` and bootstrap service (e.g. `kafka.trisla.svc.cluster.local:9092`) reachable from `trisla`.
- Set `KAFKA_BOOTSTRAP_SERVERS` (or equivalent) in SLA-Agent env to match Kafka deployment.
- Restart SLA-Agent after Kafka is ready.

**Gate**: SLA-Agent logs show successful Kafka consumer/producer startup.

---

### 11.3 Portal / Backend Mismatch

**Symptom**: Portal Frontend returns 502/503; Backend logs “SEM-CSMF offline” or connection errors.

**Root cause**: Backend cannot reach SEM-CSMF or Decision Engine; wrong URLs or SEM-CSMF not deployed.

**Fix**:

- Confirm SEM-CSMF and Decision Engine are `Running` and `Ready`.
- Check Backend env (e.g. `SEM_CSMF_URL`, `DECISION_ENGINE_URL`) point to `trisla-sem-csmf.trisla.svc.cluster.local` and `trisla-decision-engine.trisla.svc.cluster.local` (or your namespace).
- Ensure Backend and TriSLA core are in the same namespace or that DNS/networking allows cross-namespace access.

**Gate**: Backend `/health` returns 200; submit flow returns 200/202.

---

### 11.4 Empty Prometheus Queries

**Symptom**: PromQL `trisla_*` returns no series.

**Root cause**: ServiceMonitors not applied; Prometheus not scraping `trisla`; wrong job labels.

**Fix**:

- `kubectl get servicemonitor -n trisla`
- Confirm Prometheus Operator CRD exists and Prometheus instance selects these ServiceMonitors.
- Check Prometheus targets for `trisla` namespace and fix `namespaceSelector` or scrape config.

**Gate**: `up{job=~"trisla-.*"}` shows targets `1` for deployed components.

---

### 11.5 Port Mismatch (e.g. ML-NSMF)

**Symptom**: Pod CrashLoopBackOff; logs “connection refused” on health check port.

**Root cause**: Image listens on a different port than Helm `service.targetPort` (e.g. ML-NSMF 8082 vs chart 8081).

**Fix**:

- Inspect container port: `kubectl logs -n trisla deploy/trisla-ml-nsmf | grep -i listen`
- Update Helm values to match (e.g. `ml-nsmf.service.port` and `ml-nsmf.service.targetPort`).
- `helm upgrade trisla helm/trisla -n trisla --set ml-nsmf.service.targetPort=8082` (example).

**Gate**: Pod becomes `Ready`; `/health` returns 200 on the configured port.

---

### 11.6 CRD Not Found (NASP Adapter)

**Symptom**: NASP Adapter fails with “CustomResourceDefinition ... not found.”

**Root cause**: CRDs not installed before NASP Adapter deployment.

**Fix**:

```bash
kubectl apply -f apps/nasp-adapter/crds/networksliceinstances.trisla.io.yaml
kubectl apply -f apps/nasp-adapter/crds/networkslicesubnetinstances.trisla.io.yaml
kubectl rollout restart deployment/trisla-nasp-adapter -n trisla
```

**Gate**: NASP Adapter pod `Running`; no CRD errors in logs.

---

## 12. Reproducibility Criteria

### 12.1 What Makes a Deployment Reproducible

- **Same Git tag / chart version**: Use a specific TriSLA release (e.g. `v3.9.3`).
- **Same image tags**: All components use the **same** version tag (e.g. `v3.9.3`).
- **Documented values**: Record `--set` flags or values files used (excluding secrets).
- **Fixed Kafka/Besu topology**: Same bootstrap servers, same Besu RPC and genesis (if applicable).
- **Observability**: Same Prometheus/OTLP setup so that metrics and traces can be compared.

### 12.2 What Invalidates Experimental Results

- **Mixed image versions**: Different components on different tags break API and event schemas.
- **Changing Kafka retention or topology** mid-experiment: Alters order or presence of events.
- **Besu reset or different genesis**: On-chain state diverges; BC-NSSMF results not comparable.
- **Resource contention**: Different CPU/memory or node count changes latency and throughput; document baseline.

---

## 13. Public Scope Disclaimer

### 13.1 No Lab Leakage

This guide and the TriSLA project do **not** reference:

- Private clusters, internal hostnames, or evidence folders.
- Proprietary platform details or vendor-specific NASP configurations.

### 13.2 No Private Artifacts

- **Secrets**: Tokens, keys, and credentials are **not** in Git. Use Kubernetes Secrets and document *where* they are used.
- **Datasets**: Training or proprietary datasets are out of scope; only public, documented inputs are assumed.

### 13.3 Still Scientifically Valid

- **Deployment**: TriSLA can be deployed on any conformant Kubernetes cluster using `helm/trisla` and the same images.
- **Validation**: Metrics, health checks, and E2E flows are defined in terms of standard interfaces. Reproducibility is achieved by following this guide and `docs/INSTALLATION.md` with consistent versions and topology.

---

**End of Deployment Guide.** For prerequisites and preflight checks, see `docs/INSTALLATION.md`.
