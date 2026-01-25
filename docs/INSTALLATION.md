# TriSLA Installation Prerequisites

This document describes **what TriSLA is**, **what must exist before you deploy it**, and **how to validate your environment**. It is conceptual and infrastructural. The procedural deployment guide is in `docs/deployment/DEPLOYMENT.md`.

---

## 1. What is TriSLA (Architectural Context)

### 1.1 Definition

**TriSLA** (Triangulated Service Level Agreement Platform) is an **SLA-aware control-plane architecture based on Artificial Intelligence, Ontology, and Smart Contracts for SLA assurance in 5G and O-RAN networks**.

- **Semantic processing** (SEM-CSMF): intent normalization, ontology-based validation.
- **ML inference** (ML-NSMF): risk prediction, confidence scores, slice-type awareness.
- **Event-driven decision-making** (Decision Engine): ACCEPT / REJECT / RENEG based on semantic + ML outputs.
- **Lifecycle coordination** (SLA-Agent Layer): post-admission actions, SLO monitoring, event emission.
- **Optional governance** (BC-NSSMF): on-chain SLA registration, violation reporting, renegotiation.

### 1.2 What TriSLA Does

- **Admission control**: Evaluates SLA requests (e.g. eMBB, URLLC, mMTC) and produces deterministic decisions.
- **Semantic validation**: Ensures intents conform to a defined ontology and template structure.
- **Risk assessment**: Uses ML models to predict compliance risk and influence decisions.
- **Event emission**: Publishes decisions and lifecycle events over an **event backbone** (Kafka).
- **Platform abstraction**: Integrates with external platforms (e.g. RAN, Transport, Core) via the **NASP Adapter** for stub or real provisioning.
- **Observability**: Exposes metrics (Prometheus), optional traces (OpenTelemetry), and structured logs.

### 1.3 What TriSLA Does NOT Do

- **RAN/Transport/Core control**: TriSLA does not directly configure radios, transport, or core. It delegates to the NASP Adapter and underlying platform.
- **Data-plane forwarding**: No packet processing or user-plane functions.
- **Authentication/authorization**: No built-in IdP or RBAC for end-users; cluster-level access control applies.
- **Multi-tenant isolation**: Single logical control plane; isolation is via Kubernetes namespaces and RBAC if desired.

### 1.4 Why Kubernetes Is Used

TriSLA is deployed as **microservices on Kubernetes** because:

- **Orchestration**: Replicas, rollouts, health checks, and resource limits are managed by Kubernetes.
- **Service discovery**: Components find each other via Kubernetes DNS (`<service>.<namespace>.svc.cluster.local`).
- **Secrets and config**: Image pull secrets, environment variables, and optional ConfigMaps are handled by the platform.
- **Consistency**: The same Helm charts and container images run on any conformant cluster, enabling reproducibility.

### 1.5 Why Kafka Is Mandatory

The **event backbone** is a hard dependency for the **SLA-Agent Layer** and for **end-to-end flow validation**:

- The **Decision Engine** publishes admission outcomes (e.g. ACCEPT) to a Kafka topic consumed by the **SLA-Agent**.
- The **SLA-Agent** consumes decision events, executes lifecycle actions, and publishes agent events and action results to Kafka.
- **Observability** (e.g. Prometheus rules) assumes decision and agent events flow through Kafka for interface-level validation (I-05, I-06, I-07).

Without Kafka, the SLA-Agent cannot receive decisions, and the control-plane transaction chain is incomplete. A **minimal** deployment may omit blockchain or Portal, but **Kafka is required** for any deployment that includes the SLA-Agent.

---

## 2. Supported Deployment Profiles

### 2.1 Minimal (Core Only)

**Purpose**: Development, CI, or resource-constrained validation.

**Included**:

- SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, SLA-Agent, NASP Adapter.
- Kafka (event backbone).
- Optional: Besu + BC-NSSMF for on-chain governance.
- **Excluded**: Portal (backend/frontend), optional OTLP.

**Use when**: You need admission flow and SLA-Agent behavior without a web UI.

### 2.2 Full Control Plane

**Purpose**: Production-like or full experimental validation.

**Included**: Everything in Minimal, plus:

- Portal Backend and Portal Frontend.
- API Backend (if separate from Portal Backend in your Helm setup).
- Observability: Prometheus scraping, optional OTLP.

**Use when**: You need the full stack including user-facing Portal and observability.

### 2.3 Full Governance (with Blockchain)

**Purpose**: Reproducibility of experiments that require on-chain SLA lifecycle.

**Included**: Full control plane plus:

- **Hyperledger Besu** (or compatible Ethereum-like node).
- **BC-NSSMF**: Smart contract deployment, `createSLA`, `activateSLA`, `reportViolation`, `renegotiateSLA`, `closeSLA`.

**Use when**: You need blockchain-backed governance and auditability.

### 2.4 Tradeoffs and When to Choose

| Profile           | Kafka | Besu | Portal | Use case                          |
|------------------|-------|------|--------|-----------------------------------|
| Minimal          | Yes   | No*  | No     | Dev, CI, minimal e2e              |
| Full control     | Yes   | No*  | Yes    | Full e2e, no blockchain         |
| Full governance  | Yes   | Yes  | Yes    | Experiments with on-chain lifecycle |

\*BC-NSSMF can run with a **stub** or **mock** backend if Besu is omitted; however, on-chain operations will not be performed.

---

## 3. Kubernetes Requirements

### 3.1 Supported Kubernetes Versions

- **Minimum**: Kubernetes **1.24**.
- **Tested**: 1.24–1.28 (specific patch versions may vary).
- **API compatibility**: TriSLA uses `apps/v1` Deployments, `v1` Services, and standard ConfigMap/Secret. No alpha/beta APIs are required.

### 3.2 Single-Node vs Multi-Node Clusters

- **Single-node**: All TriSLA components can run on one node. Suitable for minimal and development profiles.
- **Multi-node**: Recommended for production or stress tests. Distribute Pods across nodes for availability and load.

### 3.3 Why Version Compatibility Matters

- **CRDs**: NASP Adapter uses CustomResourceDefinitions (e.g. `NetworkSliceInstance`). Older clusters may have different CRD or RBAC behavior.
- **Metrics**: ServiceMonitors and PrometheusRules assume Prometheus Operator CRDs. Ensure your monitoring stack matches.
- **Security**: `imagePullSecrets` and Pod security context follow standard Kubernetes patterns; enforcement depends on cluster version and policies.

---

## 4. Node and Resource Requirements

### 4.1 Sizing Tables

| Profile           | CPU (cores) | Memory (GB) | Disk (GB) | Notes                          |
|------------------|-------------|-------------|-----------|--------------------------------|
| **Minimum**      | 4           | 8           | 50        | Minimal, single-node           |
| **Recommended**  | 8           | 16          | 100       | Full control plane, multi-node |
| **Review-scale** | 16+         | 32+         | 200+      | Stress, many intents, HA       |

### 4.2 Per-Component Resource Drivers

- **SEM-CSMF**: gRPC service; low CPU unless under heavy intent load.
- **ML-NSMF**: CPU-bound during inference; scales with request rate.
- **Decision Engine**: Central orchestrator; CPU and memory scale with concurrency.
- **BC-NSSMF**: Depends on Besu RPC and smart-contract calls; network and some CPU.
- **SLA-Agent**: Kafka consumer/producer; memory for consumer buffers, CPU for processing.
- **NASP Adapter**: HTTP server; low unless many CRD operations.
- **Portal / API Backend**: Typical web workload; scale with user traffic.
- **Kafka**: Memory and disk for logs; size according to retention and throughput.
- **Besu**: Disk I/O and memory; size per Ethereum node recommendations.

---

## 5. Operating System and Runtime

### 5.1 Linux Assumptions

- TriSLA container images are **Linux** images. Nodes must run a Linux kernel supported by your Kubernetes distribution.
- Architecture: **amd64** is primary; **arm64** support depends on image availability.

### 5.2 Container Runtime Expectations

- **containerd** or **CRI-O** (or Docker via CRI) are supported. Kubernetes expects a CRI-compatible runtime.
- **containerd** is preferred: it is the default in many managed Kubernetes offerings and avoids Docker-specific quirks.

### 5.3 Why containerd Is Preferred

- Standard CRI implementation; no Docker daemon dependency.
- Lower overhead and simpler configuration for cluster nodes.
- Compatible with `crictl` for debugging and image inspection.

---

## 6. Required Tooling (Client Side)

You need these tools on the machine from which you deploy and operate TriSLA.

### 6.1 kubectl

- **Why**: Create namespaces, apply manifests, inspect Pods/Services, run `kubectl exec` for health checks.
- **Minimum version**: 1.24 (match cluster version).
- **Check**:
  ```bash
  kubectl version --client --short
  ```
  **Expected**: `Client Version: v1.24.x` or newer.

### 6.2 Helm

- **Why**: Install and upgrade the TriSLA Helm chart; manage values and releases.
- **Minimum version**: Helm 3.x.
- **Check**:
  ```bash
  helm version --short
  ```
  **Expected**: `v3.x.x` (e.g. `v3.12.0`).

### 6.3 curl

- **Why**: Call health and metrics endpoints (e.g. via `kubectl exec` or port-forward); trigger API flows.
- **Check**:
  ```bash
  curl --version
  ```
  **Expected**: Any recent curl; HTTP/1.1 support.

### 6.4 jq

- **Why**: Parse JSON output from APIs and `kubectl` for scripting and validation.
- **Check**:
  ```bash
  jq --version
  ```
  **Expected**: `jq-1.6` or similar.

### 6.5 yq (Optional)

- **Why**: Edit or validate YAML (e.g. values files, manifests). Not required for basic install.
- **Check**:
  ```bash
  yq --version
  ```
  **Expected**: `yq (https://github.com/mikefarah/yq/) version v4.x` or compatible.

---

## 7. Networking and Service Discovery

### 7.1 DNS Dependency

TriSLA relies on **Kubernetes DNS** for service discovery. Each service is reachable as:

```
<service-name>.<namespace>.svc.cluster.local
```

Example: `trisla-decision-engine.trisla.svc.cluster.local`.

### 7.2 Cluster-Internal Communication

- SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, SLA-Agent, NASP Adapter, and Portal components communicate over **cluster-internal** HTTP or gRPC.
- Kafka is typically deployed in-cluster; bootstrap servers use Kubernetes DNS (e.g. `kafka.trisla.svc.cluster.local:9092`).

### 7.3 Portal Exposure Strategies

- **NodePort**: Allocate a fixed port on each node for the Portal frontend (or backend). Simple, no Ingress controller.
- **Ingress**: Use an Ingress controller (e.g. NGINX, Traefik) for host-based or path-based routing. Requires TLS termination and DNS configuration.

### 7.4 DNS Validation Command

Run from a Pod in the cluster (e.g. `trisla` namespace):

```bash
kubectl run -it --rm dns-check --image=busybox:1.36 --restart=Never -n trisla -- \
  nslookup trisla-decision-engine.trisla.svc.cluster.local
```

**Expected**: Resolution of the service name to cluster-internal IP(s). A failure indicates DNS or service configuration issues.

---

## 8. Container Images and Registry

### 8.1 ghcr.io Usage

TriSLA images are published to **GitHub Container Registry** (`ghcr.io`). Typical pattern:

```
ghcr.io/<org>/trisla-<component>:<tag>
```

Example: `ghcr.io/abelisboa/trisla-decision-engine:v3.9.3`.

### 8.2 Tag Consistency Strategy

- **Image tags** (e.g. `v3.9.3`) MUST match across components for a given release to avoid API or schema mismatches.
- **Helm values**: Set each component’s `image.tag` to the same version when installing or upgrading.

### 8.3 Why Tag Mismatch Breaks Reproducibility

- Different component versions may use different request/response schemas or Kafka event formats.
- Mixed versions lead to obscure failures (e.g. parsing errors, missing fields) and non-reproducible experiments.

### 8.4 imagePullSecret Creation

**When needed**: GHCR images are **private** by default. You must create a Kubernetes `imagePullSecret` in the target namespace and reference it in the Helm chart (e.g. `global.imagePullSecrets`).

**Create secret**:

```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=<GITHUB_USER> \
  --docker-password=<GITHUB_PAT_OR_TOKEN> \
  --docker-email=<EMAIL> \
  -n trisla
```

Use a **GitHub Personal Access Token** with `read:packages` scope. **When not needed**: If you use only public images or an internal registry with no auth, you can omit the secret.

---

## 9. Observability Prerequisites

### 9.1 Why Observability Is Architectural

TriSLA treats **observability** as part of the architecture:

- **Metrics**: Admission rates, latency, errors, SLO compliance. Required for validation and alerting.
- **Traces**: Optional but recommended for debugging cross-component flows.
- **Logs**: Structured logs with correlation IDs (e.g. `intent_id`, `decision_id`).

### 9.2 Minimum Viable Observability

- **Prometheus**: Scrape TriSLA ServiceMonitors. Required for metrics-based validation and PrometheusRules (alerts).
- **ServiceMonitors**: TriSLA Helm chart can deploy ServiceMonitors for SEM-CSMF, ML-NSMF, Decision Engine, BC-NSSMF, SLA-Agent, NASP Adapter, API Backend. Prometheus Operator must be installed.

### 9.3 Prometheus Role

- Scrapes `/metrics` endpoints of TriSLA components.
- Stores time-series for queries and dashboards.
- Evaluates PrometheusRules (e.g. module down, high latency, E2E interface errors).

### 9.4 Optional OTEL

- **OpenTelemetry Collector**: Receives OTLP traces from TriSLA components (if configured). Useful for distributed tracing.
- Not required for minimal or basic full deployments; add when you need trace-level debugging.

---

## 10. External Platform Assumptions (NASP Adapter)

### 10.1 Abstract Platform Integration

The **NASP Adapter** abstracts integration with an external platform (RAN, Transport, Core). It:

- Translates TriSLA lifecycle actions into platform-specific operations.
- Fetches metrics from the platform for SLO evaluation in the SLA-Agent.

### 10.2 Stub vs Real Platform

- **Stub mode**: NASP Adapter simulates platform responses. No external platform is required. Suitable for development and CI.
- **Real mode**: NASP Adapter talks to a real platform API. You must provide endpoints, credentials, and ensure network connectivity.

This documentation does **not** prescribe a specific platform, topology, or internal paths. The Adapter’s role is generic; configuration is environment-specific.

---

## 11. Preflight Checklist (Hard Gate)

Run these checks **before** deploying TriSLA. Each must **PASS**.

### 11.1 Cluster Access

```bash
kubectl cluster-info
```

**Expected**: Kubernetes control plane is reachable. **FAIL**: Cannot connect; fix `kubeconfig` and cluster connectivity.

### 11.2 Namespace Exists

```bash
kubectl get namespace trisla
```

**Expected**: `trisla` namespace exists. **FAIL**: Create it with `kubectl create namespace trisla`.

### 11.3 kubectl and Helm Versions

```bash
kubectl version --client --short
helm version --short
```

**Expected**: kubectl 1.24+, Helm 3.x. **FAIL**: Upgrade client tools.

### 11.4 GHCR Secret (If Using Private Images)

```bash
kubectl get secret ghcr-secret -n trisla
```

**Expected**: Secret exists. **FAIL**: Create `ghcr-secret` as in §8.4.

### 11.5 DNS Resolution

```bash
kubectl run -it --rm preflight-dns --image=busybox:1.36 --restart=Never -n trisla -- \
  nslookup kubernetes.default.svc.cluster.local
```

**Expected**: Resolution succeeds. **FAIL**: Cluster DNS is broken; fix before proceeding.

### 11.6 Kafka Reachable (If Deploying SLA-Agent)

If Kafka is deployed in-cluster, ensure it is running and that the intended bootstrap service (e.g. `kafka.trisla.svc.cluster.local:9092`) is reachable from the `trisla` namespace. Use `kubectl get svc` and optional `kubectl run` + `nc` or Kafka client tools to verify.

**PASS**: All preflight checks succeed. **FAIL**: Resolve failures before deployment.

---

## 12. Public Scope Disclaimer

### 12.1 What Is Intentionally Excluded

- **Internal lab or platform specifics**: No references to private clusters, internal hostnames, or evidence folders.
- **Proprietary integrations**: NASP Adapter configuration for specific vendors or deployments is not part of this document.
- **Experimental datasets**: Training data or proprietary datasets are out of scope.

### 12.2 Why This Does Not Break Scientific Reproducibility

- **Deployment**: TriSLA can be deployed on any conformant Kubernetes cluster using the same Helm charts and images.
- **Configuration**: Required inputs (Kafka bootstrap servers, image tags, optional Besu RPC) are described in this document and in `docs/deployment/DEPLOYMENT.md`.
- **Validation**: Metrics, health checks, and E2E flows are defined in terms of standard Prometheus and HTTP/gRPC interfaces. Reproducibility is achieved by following the installation and deployment guides and using the same versions and topology.

---

**Next step**: Proceed to `docs/deployment/DEPLOYMENT.md` for step-by-step deployment, validation gates, and failure resolutions.
