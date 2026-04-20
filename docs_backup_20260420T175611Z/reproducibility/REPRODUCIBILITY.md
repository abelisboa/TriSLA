# TriSLA Reproducibility (SSOT)

This document defines how to validate and reproduce a deployed TriSLA environment.

---

## 1. Scope

This guide assumes:

- TriSLA is already deployed using:
  -> `../INSTALLATION_FINAL.md`

It focuses on:

- validation
- verification
- reproducibility

---

## 2. Environment Requirements

### Kubernetes
- Version: 1.26+
- kubectl aligned with cluster

### Helm
- Version: 3.12+

### Runtime
- containerd or Docker

---

## 3. Baseline Verification

### Cluster access

```bash
kubectl cluster-info
kubectl get nodes
```

### Namespace

```bash
kubectl get ns trisla
```

---

## 4. Core Services Validation

```bash
kubectl get pods -n trisla
```

Expected:

- all services Running
- 1/1 READY

---

## 5. Service Endpoints

```bash
kubectl get svc -n trisla
```

---

## 6. Pipeline Validation

Test full flow:

```bash
curl -X POST http://<portal-backend>/api/v1/sla/submit
```

Expected:

- intent_id
- decision
- response payload

---

## 7. Observability Validation

### Prometheus

```bash
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
```

Query:

```promql
rate(trisla_decision_engine_requests_total[5m])
```

### Kafka

```bash
kubectl get pods -n kafka
```

---

## 8. Expected Behavior

System must provide:

- SLA submission flow
- decision response
- correlation IDs
- metrics availability

---

## 9. Known Non-Deterministic Factors

- latency
- CPU usage
- network conditions
- blockchain timing

---

## 10. Troubleshooting

Pods not running:

- check resources, image pull, config

Kafka issues:

- check topics and connectivity

No metrics:

- check Prometheus scrape config

---

## 11. Validation Checklist

- [ ] cluster accessible
- [ ] pods running
- [ ] services reachable
- [ ] pipeline functional
- [ ] metrics available

---

## 12. Installation Reference

-> `../INSTALLATION_FINAL.md`
