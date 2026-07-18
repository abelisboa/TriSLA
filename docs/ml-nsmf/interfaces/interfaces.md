# ML-NSMF HTTP Interface

Base port: `8081`.

## Endpoints

| Method | Path | Response |
|---|---|---|
| `GET` | `/health` | Service and active model status |
| `GET` | `/metrics` | Prometheus text format |
| `POST` | `/api/v1/predict` | Prediction and explanation JSON |

## Prediction request

`POST /api/v1/predict` accepts a JSON object. The Decision Engine supplies these primary fields:

| Field | Meaning |
|---|---|
| `intent_id` | SLA intent identifier |
| `correlation_id` | Request correlation identifier |
| `slice_type` | `eMBB`, `URLLC`, or `mMTC` |
| `latency` | Maximum latency in milliseconds |
| `throughput` | Requested throughput in Mbps |
| `reliability` | Reliability ratio |
| `jitter` | Jitter in milliseconds |
| `packet_loss` | Packet-loss ratio |
| `cpu_utilization` | CPU utilization ratio |
| `memory_utilization` | Memory utilization ratio |
| `network_bandwidth_available` | Available bandwidth in Mbps |
| `active_slices_count` | Number of active slices |
| `ran_prb_utilization` | RAN PRB utilization |
| `transport_latency_ms` | Transport latency |
| `core_cpu_utilization` | Core CPU utilization ratio |
| `core_memory_utilization` | Core memory utilization |

Example:

```json
{
  "intent_id": "intent-001",
  "correlation_id": "request-001",
  "slice_type": "URLLC",
  "latency": 10,
  "throughput": 100,
  "reliability": 0.999,
  "jitter": 2,
  "packet_loss": 0.001,
  "cpu_utilization": 0.35,
  "memory_utilization": 0.40,
  "network_bandwidth_available": 1000,
  "active_slices_count": 2
}
```

## Prediction response

The response contains two objects:

- `prediction`: `risk_score`, `risk_level`, `viability_score`, `confidence`, latency, timestamp, model metadata, and timing values.
- `explanation`: explanation method, feature importance values, reasoning, and explanation timing.

Risk mapping performed by the predictor:

- `risk_score > 0.7`: `high`
- `risk_score > 0.4`: `medium`
- otherwise: `low`

The endpoint implementation is in [`main.py`](../../../apps/ml-nsmf/src/main.py).
