# Reproducibility Guide

This document describes how to reproduce a baseline TriSLA deployment and validate the end-to-end pipeline behavior.

## Clean Clone Procedure

```bash
# Clone the repository
git clone https://github.com/abelisboa/TriSLA.git
cd TriSLA

# Checkout the version tag (if applicable)
git checkout v3.9.3

# Verify repository state
git status
```

## Required OS / Docker / Kubernetes Versions

### Operating System
- **Linux**: Ubuntu 20.04+ or equivalent
- **Container Runtime**: containerd 1.6+ or Docker 20.10+

### Kubernetes
- **Kubernetes**: 1.26+ (tested with 1.26, 1.27, 1.28)
- **kubectl**: 1.26+ (must match cluster version)

### Helm
- **Helm**: 3.12+ (required for chart features)

### Additional Tools
- **Docker**: 20.10+ (for local builds, if needed)
- **Python**: 3.10+ (for local development, if needed)
- **Node.js**: 18+ (for Portal Frontend builds, if needed)

## Deterministic Build Order

### 1. Prerequisites Setup

```bash
# Verify Kubernetes cluster access
kubectl cluster-info
kubectl get nodes

# Verify Helm is installed
helm version

# Create namespace
kubectl create namespace trisla
```

### 2. Observability Stack (if not pre-installed)

```bash
# Install Prometheus (example, adjust to your environment)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace

# Verify Prometheus is accessible
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
# Access: http://localhost:9090
```

### 3. Kafka (Event Backbone)

```bash
# Install Kafka (example, adjust to your environment)
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install kafka bitnami/kafka -n kafka --create-namespace

# Verify Kafka is running
kubectl get pods -n kafka
```

### 4. Besu (if Blockchain Governance Enabled)

```bash
# Follow Besu deployment guide
# See: docs/deployment/BESU_DEPLOY_GUIDE.md
```

### 5. Core TriSLA Services

```bash
# Install TriSLA core
helm upgrade --install trisla ./helm/trisla -n trisla -f ./helm/trisla/values.yaml

# Verify all pods are running
kubectl get pods -n trisla

# Check service endpoints
kubectl get svc -n trisla
```

### 6. Portal (if separated)

```bash
# Install Portal (if using separate chart)
helm upgrade --install trisla-portal ./helm/trisla-portal -n trisla -f ./helm/trisla-portal/values.yaml
```

## Expected Outputs

### Service Health

All pods should be in  state:
```bash
kubectl get pods -n trisla
```

Expected output:
```
NAME                                    READY   STATUS    RESTARTS   AGE
trisla-sem-csmf-xxx                     1/1     Running   0          5m
trisla-ml-nsmf-xxx                      1/1     Running   0          5m
trisla-decision-engine-xxx               1/1     Running   0          5m
trisla-sla-agent-xxx                    1/1     Running   0          5m
trisla-nasp-adapter-xxx                 1/1     Running   0          5m
trisla-bc-nssmf-xxx                     1/1     Running   0          5m
trisla-portal-backend-xxx               1/1     Running   0          5m
trisla-portal-frontend-xxx              1/1     Running   0          5m
```

### Health Endpoints

All services should respond to health checks:
```bash
# Decision Engine
curl http://<decision-engine-service>/health

# Portal Backend
curl http://<portal-backend-service>/health
```

### Kafka Topic Readiness

Decision events topic should exist:
```bash
# List Kafka topics (adjust based on your Kafka setup)
kubectl exec -n kafka <kafka-pod> -- kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Prometheus Queries

Prometheus should be able to query expected signals:
```promql
# Example: Decision Engine requests
rate(trisla_decision_engine_requests_total[5m])

# Example: Infrastructure metrics
rate(container_cpu_usage_seconds_total[5m])
```

## What You Can Reproduce Publicly

- Service health and readiness (all core modules)
- Portal submission flow and decision response
- Correlation IDs (intent_id / decision_id) across modules
- Observability availability (metrics + traces, if enabled)
- End-to-end decision pipeline (SEM → ML → Decision → SLA-Agent)
- On-chain registration (if Besu is enabled)

## What Is Intentionally Excluded

The following cannot be reproduced publicly due to infrastructure or data constraints:

- **Private lab evidence packs**: Internal experimental data and results
- **Internal audit logs**: Operational logs and debugging traces from private deployments
- **Institution-specific NASP credentials**: Authentication tokens and infrastructure details
- **Private network configurations**: Internal IP addresses, VPN configurations, firewall rules
- **Performance benchmarks on private infrastructure**: Results from institution-specific hardware

## Recommended Validation Checklist

1. **Submit a SLA request via Portal Backend**
   - Verify request is accepted
   - Verify intent_id is generated
   - Verify request reaches Decision Engine

2. **Validate Decision Engine response**
   - Verify decision outcome (ACCEPT/REJECT/RENEG)
   - Verify decision_id is generated
   - Verify justification fields are present

3. **Validate ML-NSMF inference output fields**
   - Verify risk_score is present
   - Verify confidence level is present
   - Verify XAI metadata is available (if enabled)

4. **Validate SEM-CSMF semantic processing logs**
   - Verify NEST generation
   - Verify slice type identification

5. **Validate Kafka decision event emission**
   - Verify decision event is published to topic
   - Verify event contains correlation IDs

6. **Validate BC-NSSMF event (if Besu is enabled)**
   - Verify on-chain registration
   - Verify transaction hash is generated

## Known Non-Reproducible Elements

### Infrastructure-Dependent
- Exact Prometheus metric values (depend on cluster state)
- Network latency measurements (depend on infrastructure)
- Resource utilization (depends on cluster load)

### Time-Dependent
- Transaction confirmation times (depend on blockchain network)
- ML model inference times (depend on hardware)
- End-to-end latency (depends on system load)

### Configuration-Dependent
- Decision thresholds (configurable in Helm values)
- Kafka topic names (configurable)
- Service endpoints (depend on deployment configuration)

## Troubleshooting Reproduction Issues

### Issue: Services do not start
**Check**: Verify image pull secrets, resource limits, and service account permissions

### Issue: Prometheus queries return empty
**Check**: Verify scrape configuration, service discovery, and metric endpoint accessibility

### Issue: Kafka events not consumed
**Check**: Verify topic creation, consumer group configuration, and network policies

### Issue: Portal cannot reach backend
**Check**: Verify service endpoints, DNS resolution, and CORS configuration
