# ML-NSMF Usage Examples

## Health check

```bash
curl -sS http://localhost:8081/health
```

## Prometheus metrics

```bash
curl -sS http://localhost:8081/metrics
```

## Request a prediction

```bash
curl -sS http://localhost:8081/api/v1/predict \
  -H 'Content-Type: application/json' \
  -d '{
    "intent_id":"intent-001",
    "correlation_id":"request-001",
    "slice_type":"eMBB",
    "latency":20,
    "throughput":500,
    "reliability":0.999,
    "jitter":3,
    "packet_loss":0.001,
    "cpu_utilization":0.3,
    "memory_utilization":0.4,
    "network_bandwidth_available":1000,
    "active_slices_count":2
  }'
```

Read `prediction.risk_score`, `prediction.risk_level`, `prediction.viability_score`, and `prediction.confidence` from the response. Explanation details are returned under `explanation`.

In Kubernetes, use the service address `http://trisla-ml-nsmf:8081` from workloads in the same namespace.
