# Helm Chart to Image Mapping

## Helm Releases

Based on audit, the following Helm releases are deployed:

- **trisla**: Chart version 3.7.10, App version 3.7.10 (deployed)
- **trisla-portal**: Chart version 1.0.2, App version 1.0.0 (deployed)
- **trisla-besu**: Chart version 1.0.0, App version 23.10.1 (failed)

## Image to Helm Chart Mapping

| Component | Image | Helm Chart | Values Key | Service Port | Health Check |
|-----------|-------|------------|------------|--------------|--------------|
| SEM-CSMF | ghcr.io/abelisboa/trisla-sem-csmf:v3.9.4 | trisla | sem-csmf.image | 8080 | TBD |
| ML-NSMF | ghcr.io/abelisboa/trisla-ml-nsmf:v3.9.4 | trisla | ml-nsmf.image | 8081 | TBD |
| Decision Engine | ghcr.io/abelisboa/trisla-decision-engine:v3.9.5-fix | trisla | decision-engine.image | 8082 | TBD |
| BC-NSSMF | ghcr.io/abelisboa/trisla-bc-nssmf:v3.9.4 | trisla | bc-nssmf.image | 8083 | TBD |
| SLA-Agent | ghcr.io/abelisboa/trisla-sla-agent-layer:v3.9.4 | trisla | sla-agent.image | 8084 | TBD |
| NASP Adapter | ghcr.io/abelisboa/trisla-nasp-adapter:v3.9.4 | trisla | nasp-adapter.image | 8085 | TBD |
| Portal Backend | ghcr.io/abelisboa/trisla-portal-backend:v3.8.1 | trisla-portal | backend.image | 8001 | TBD |
| Portal Frontend | ghcr.io/abelisboa/trisla-portal-frontend:v3.8.1 | trisla-portal | frontend.image | 80 | TBD |
| UI Dashboard | ghcr.io/abelisboa/trisla-ui-dashboard:v3.9.4 | trisla | ui-dashboard.image | 80 | TBD |
| Traffic Exporter | ghcr.io/abelisboa/trisla-traffic-exporter:v3 | trisla | traffic-exporter.image | 9105 | TBD |
| Kafka | apache/kafka:latest | trisla | kafka.image | 9092 | TBD |

## Notes

- Exact values.yaml keys need to be verified by inspecting helm/trisla/values.yaml
- Health check endpoints should be documented from deployment manifests
- trisla-besu release is in failed state (Hyperledger Besu not active)
- Port numbers extracted from running deployments
