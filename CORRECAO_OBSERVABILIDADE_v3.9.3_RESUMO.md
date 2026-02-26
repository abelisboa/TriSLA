# TriSLA v3.9.3-observability - Correção Instrumental de Observabilidade

## Data: 2026-01-21

## ✅ CORREÇÕES APLICADAS

### FASE 1 (C1): ML-NSMF Timestamp
- Arquivo: apps/ml-nsmf/src/main.py
- Alteração: Adicionado timestamp_utc na resposta do endpoint /api/v1/predict

### FASE 2 (C2): Persistência ML Metrics
- Arquivo: apps/ml-nsmf/src/predictor.py
- Alteração: Método _persist_metrics() adicionado
- Persistência: CSV e JSONL em /app/metrics/

### FASE 3 (C3): Portal Backend Timestamp
- Arquivo: trisla-portal/backend/src/services/slas.py
- Alteração: Captura t_submit no momento da submissão de SLA

### FASE 4 (C4): Decision Engine Timestamp
- Arquivo: apps/decision-engine/src/engine.py
- Alteração: Captura t_decision no momento exato da decisão

### FASE 5 (C5): Kafka Instrumental
- Arquivos: apps/decision-engine/src/kafka_producer.py e main.py
- Alteração: Novo método send_decision_event() e integração no endpoint /evaluate
- Tópico: trisla-decision-events

### FASE 6 (C6): Integração XAI Real
- Arquivo: apps/ml-nsmf/src/main.py
- Alteração: XAI acionado automaticamente após inferência ML
- Persistência: Log e CSV em /app/logs/xai/ e /app/evidence/xai/

## 📋 PRÓXIMOS PASSOS

1. Rebuild das imagens Docker (sem retreinar modelo ML)
2. Helm upgrade: helm upgrade --install trisla helm/trisla -n trisla
3. Validação: Executar 3 SLAs (URLLC / eMBB / mMTC)
4. Verificação: Confirmar latência, Kafka, ML confidence, XAI, CSVs
