# SEM-CSMF Usage Examples

## Health check

```bash
curl -sS http://localhost:8080/health
```

## Interpret intent text

```bash
curl -sS http://localhost:8080/api/v1/interpret \
  -H 'Content-Type: application/json' \
  -d '{
    "intent":"Create a low-latency slice for control traffic",
    "tenant_id":"tenant-001"
  }'
```

## Submit a structured intent

```bash
curl -sS http://localhost:8080/api/v1/intents \
  -H 'Content-Type: application/json' \
  -d '{
    "service_type":"eMBB",
    "intent":"Create a broadband slice",
    "tenant_id":"tenant-001",
    "sla_requirements":{
      "throughput":"500Mbps",
      "latency":"20ms",
      "reliability":0.999
    }
  }'
```

## Retrieve generated objects

```bash
curl -sS http://localhost:8080/api/v1/intents/INTENT_ID
curl -sS http://localhost:8080/api/v1/nests/NEST_ID
curl -sS http://localhost:8080/api/v1/slices
```

In Kubernetes, use `http://trisla-sem-csmf:8080` from workloads in the same namespace.
