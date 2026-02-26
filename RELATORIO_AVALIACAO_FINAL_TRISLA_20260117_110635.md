# Relatório de Avaliação Final TriSLA
**Data:** sáb 17 jan 2026 11:06:10 -03
**Ambiente:** NASP (node006)
**Namespace:** trisla

## FASE 0 - Baseline

### Pods Essenciais
kafka-c948b8d64-jgmz5                     1/1     Running            0                3d13h   10.233.75.59     node2   <none>           <none>
trisla-bc-nssmf-7b5c6fd7b7-zc4zl          1/1     Running            0                21d     10.233.102.138   node1   <none>           <none>
trisla-bc-nssmf-7d99b476b7-r75jl          0/1     ImagePullBackOff   0                3d15h   10.233.102.155   node1   <none>           <none>
trisla-besu-6448cb6bc6-mxb84              1/1     Running            0                24d     10.233.75.56     node2   <none>           <none>
trisla-decision-engine-7984f6f486-jgn96   1/1     Running            0                3d      10.233.102.145   node1   <none>           <none>
trisla-ml-nsmf-648666b86-7ghmv            1/1     Running            0                3d4h    10.233.102.149   node1   <none>           <none>
trisla-portal-backend-69568dbdb7-5z8k9    1/1     Running            0                3d10h   10.233.75.39     node2   <none>           <none>
trisla-portal-frontend-6dd98dc868-2nx7k   1/1     Running            0                25d     10.233.102.141   node1   <none>           <none>
trisla-sem-csmf-685985d44-6v9hk           1/1     Running            0                3d10h   10.233.102.161   node1   <none>           <none>

### Versões
kafka-c948b8d64-jgmz5	apache/kafka:latest
trisla-bc-nssmf-7b5c6fd7b7-zc4zl	ghcr.io/abelisboa/trisla-bc-nssmf:v3.7.21
trisla-bc-nssmf-7d99b476b7-r75jl	ghcr.io/abelisboa/trisla-bc-nssmf:v3.7.18
trisla-besu-6448cb6bc6-mxb84	ghcr.io/abelisboa/trisla-besu:v3.7.29
trisla-decision-engine-7984f6f486-jgn96	localhost/trisla-decision-engine:xai-evaluate-final-v2
trisla-ml-nsmf-648666b86-7ghmv	ghcr.io/abelisboa/trisla-ml-nsmf:v3.7.36-ml-numpy2
trisla-portal-backend-69568dbdb7-5z8k9	ghcr.io/abelisboa/trisla-portal-backend:v3.7.35
trisla-portal-frontend-6dd98dc868-2nx7k	ghcr.io/abelisboa/trisla-portal-frontend:v3.7.21
trisla-sem-csmf-685985d44-6v9hk	ghcr.io/abelisboa/trisla-sem-csmf:v3.7.34

### Serviços
kafka                            ClusterIP   10.233.43.214   <none>        9092/TCP                      3d13h
trisla-bc-nssmf                  ClusterIP   10.233.39.215   <none>        8083/TCP                      28d
trisla-bc-nssmf-metrics          ClusterIP   10.233.30.108   <none>        8083/TCP                      27d
trisla-besu                      ClusterIP   10.233.11.101   <none>        8545/TCP,8546/TCP,30303/TCP   24d
trisla-decision-engine           ClusterIP   10.233.26.201   <none>        8082/TCP                      28d
trisla-decision-engine-metrics   ClusterIP   10.233.32.162   <none>        8082/TCP                      27d
trisla-ml-nsmf                   ClusterIP   10.233.28.209   <none>        8081/TCP                      28d
trisla-portal-backend            NodePort    10.233.46.159   <none>        8001:32002/TCP                27d
trisla-portal-frontend           NodePort    10.233.19.22    <none>        80:32001/TCP                  27d
trisla-sem-csmf                  ClusterIP   10.233.13.160   <none>        8080/TCP                      28d

## FASE 1 - SEM-CSMF e Semântica

Resposta SEM-CSMF:
{
  "intent_id": "f6a56d0b-e56b-4b85-b1c1-1f58bf918738",
  "status": "accepted",
  "nest_id": "nest-f6a56d0b-e56b-4b85-b1c1-1f58bf918738",
  "message": "Intent processed and NEST generated. Decision Engine: Erro HTTP ao comunicar com Decision Engine: 500 Server Error: Internal Server Error for url: http://trisla-decision-engine.trisla.svc.cluster.local:8082/evaluate"
}
---
Resposta SEM-CSMF:
{
  "intent_id": "14e9596c-7132-4715-87ce-6a584facdef7",
  "status": "accepted",
  "nest_id": "nest-14e9596c-7132-4715-87ce-6a584facdef7",
  "message": "Intent processed and NEST generated. Decision Engine: Erro HTTP ao comunicar com Decision Engine: 500 Server Error: Internal Server Error for url: http://trisla-decision-engine.trisla.svc.cluster.local:8082/evaluate"
}
---
Resposta SEM-CSMF:
{
  "intent_id": "51776808-74ed-46bc-bda0-fdfd1fa88eac",
  "status": "accepted",
  "nest_id": "nest-51776808-74ed-46bc-bda0-fdfd1fa88eac",
  "message": "Intent processed and NEST generated. Decision Engine: Erro HTTP ao comunicar com Decision Engine: 500 Server Error: Internal Server Error for url: http://trisla-decision-engine.trisla.svc.cluster.local:8082/evaluate"
}
---

## FASE 2 - ML + Decision Engine + XAI

Resposta Decision Engine:
{
  "detail": [
    {
      "type": "missing",
      "loc": [
        "body",
        "intent"
      ],
      "msg": "Field required",
      "input": {
        "intent_id": "eval-1768658766-14328",
        "service_type": "URLLC",
        "slice_type": "URLLC"
      },
      "url": "https://errors.pydantic.dev/2.5/v/missing"
    }
  ]
}
---
Resposta Decision Engine:
{
  "detail": [
    {
      "type": "missing",
      "loc": [
        "body",
        "intent"
      ],
      "msg": "Field required",
      "input": {
        "intent_id": "eval-1768658768-13666",
        "service_type": "eMBB",
        "slice_type": "eMBB"
      },
      "url": "https://errors.pydantic.dev/2.5/v/missing"
    }
  ]
}
---
Resposta Decision Engine:
{
  "detail": [
    {
      "type": "missing",
      "loc": [
        "body",
        "intent"
      ],
      "msg": "Field required",
      "input": {
        "intent_id": "eval-1768658769-2030",
        "service_type": "mMTC",
        "slice_type": "mMTC"
      },
      "url": "https://errors.pydantic.dev/2.5/v/missing"
    }
  ]
}
---

## FASE 3 - XAI

    features = self._extract_features(decision_input)
    features = self._extract_features(decision_input)
    decision_result = await decision_service.process_decision_from_input(decision_input)
  File "/app/src/service.py", line 70, in process_decision_from_input
    ml_prediction = await self.engine.ml_client.predict_viability(decision_input)
    decision_result = await decision_service.process_decision_from_input(decision_input)
  File "/app/src/service.py", line 70, in process_decision_from_input
    ml_prediction = await self.engine.ml_client.predict_viability(decision_input)
    features = self._extract_features(decision_input)
    features = self._extract_features(decision_input)
    decision_result = await decision_service.process_decision_from_input(decision_input)
  File "/app/src/service.py", line 70, in process_decision_from_input
    ml_prediction = await self.engine.ml_client.predict_viability(decision_input)
    decision_result = await decision_service.process_decision_from_input(decision_input)
  File "/app/src/service.py", line 70, in process_decision_from_input
    ml_prediction = await self.engine.ml_client.predict_viability(decision_input)
    features = self._extract_features(decision_input)
    decision_result = await decision_service.process_decision_from_input(decision_input)
  File "/app/src/service.py", line 70, in process_decision_from_input
    ml_prediction = await self.engine.ml_client.predict_viability(decision_input)
    features = self._extract_features(decision_input)
    decision_result = await decision_service.process_decision_from_input(decision_input)
  File "/app/src/service.py", line 70, in process_decision_from_input
    ml_prediction = await self.engine.ml_client.predict_viability(decision_input)
    features = self._extract_features(decision_input)
    features = self._extract_features(decision_input)
    decision_result = await decision_service.process_decision_from_input(decision_input)
  File "/app/src/service.py", line 70, in process_decision_from_input
    ml_prediction = await self.engine.ml_client.predict_viability(decision_input)
    decision_result = await decision_service.process_decision_from_input(decision_input)
  File "/app/src/service.py", line 70, in process_decision_from_input
    ml_prediction = await self.engine.ml_client.predict_viability(decision_input)
    features = self._extract_features(decision_input)
    features = self._extract_features(decision_input)
    decision_result = await decision_service.process_decision_from_input(decision_input)
  File "/app/src/service.py", line 70, in process_decision_from_input
    ml_prediction = await self.engine.ml_client.predict_viability(decision_input)
    decision_result = await decision_service.process_decision_from_input(decision_input)
  File "/app/src/service.py", line 70, in process_decision_from_input
    ml_prediction = await self.engine.ml_client.predict_viability(decision_input)

## FASE 4 - Blockchain

Nenhum log blockchain encontrado

## FASE 5 - Logs Completos

### Decision Engine
  File "/app/src/ml_client.py", line 43, in predict_viability
    features = self._extract_features(decision_input)
  File "/app/src/ml_client.py", line 145, in _extract_features
    features["reliability"] = float(sla_reqs.get("reliability", 0.99))
TypeError: float() argument must be a string or a real number, not 'NoneType'
    features["reliability"] = float(sla_reqs.get("reliability", 0.99))
TypeError: float() argument must be a string or a real number, not 'NoneType'
2026-01-17 14:06:01,857 - src.main - ERROR - ❌ Erro ao avaliar SLA: 1 validation error for MLPrediction
timestamp
  Field required [type=missing, input_value={'risk_score': 0.5, 'risk...number, not 'NoneType'"}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.5/v/missing
Traceback (most recent call last):
  File "/app/src/main.py", line 530, in evaluate_sla
    decision_result = await decision_service.process_decision_from_input(decision_input)
  File "/app/src/service.py", line 70, in process_decision_from_input
    ml_prediction = await self.engine.ml_client.predict_viability(decision_input)
  File "/app/src/ml_client.py", line 110, in predict_viability
2026-01-17 14:06:01,857 - src.main - ERROR - ❌ Erro ao avaliar SLA: 1 validation error for MLPrediction
timestamp
  Field required [type=missing, input_value={'risk_score': 0.5, 'risk...number, not 'NoneType'"}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.5/v/missing
Traceback (most recent call last):
    return MLPrediction(
  File "/usr/local/lib/python3.10/site-packages/pydantic/main.py", line 164, in __init__
  File "/app/src/main.py", line 530, in evaluate_sla
    decision_result = await decision_service.process_decision_from_input(decision_input)
  File "/app/src/service.py", line 70, in process_decision_from_input
    ml_prediction = await self.engine.ml_client.predict_viability(decision_input)
  File "/app/src/ml_client.py", line 110, in predict_viability
    return MLPrediction(
  File "/usr/local/lib/python3.10/site-packages/pydantic/main.py", line 164, in __init__
    __pydantic_self__.__pydantic_validator__.validate_python(data, self_instance=__pydantic_self__)
pydantic_core._pydantic_core.ValidationError: 1 validation error for MLPrediction
timestamp
  Field required [type=missing, input_value={'risk_score': 0.5, 'risk...number, not 'NoneType'"}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.5/v/missing
    __pydantic_self__.__pydantic_validator__.validate_python(data, self_instance=__pydantic_self__)
pydantic_core._pydantic_core.ValidationError: 1 validation error for MLPrediction
timestamp
  Field required [type=missing, input_value={'risk_score': 0.5, 'risk...number, not 'NoneType'"}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.5/v/missing
INFO:     10.233.102.161:40026 - "POST /evaluate HTTP/1.1" 500 Internal Server Error
2026-01-17 14:06:02,920 - src.main - INFO - 📥 SLA recebido para avaliação: intent_id=51776808-74ed-46bc-bda0-fdfd1fa88eac, nest_id=nest-51776808-74ed-46bc-bda0-fdfd1fa88eac
2026-01-17 14:06:02,920 - src.main - INFO - 📥 SLA recebido para avaliação: intent_id=51776808-74ed-46bc-bda0-fdfd1fa88eac, nest_id=nest-51776808-74ed-46bc-bda0-fdfd1fa88eac
2026-01-17 14:06:02,920 - src.main - INFO - 🔍 Chamando ML-NSMF para intent_id=51776808-74ed-46bc-bda0-fdfd1fa88eac
2026-01-17 14:06:02,920 - src.main - INFO - 🔍 Chamando ML-NSMF para intent_id=51776808-74ed-46bc-bda0-fdfd1fa88eac
2026-01-17 14:06:02,920 - ml_client - ERROR - ❌ Erro inesperado ao chamar ML-NSMF: float() argument must be a string or a real number, not 'NoneType'
Traceback (most recent call last):
  File "/app/src/ml_client.py", line 43, in predict_viability
    features = self._extract_features(decision_input)

### ML-NSMF
INFO:     192.168.10.16:53290 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:53302 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:44168 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:44172 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:44174 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:60592 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:60600 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:60614 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:50060 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:50062 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:50064 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:36100 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:36112 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:36122 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:36180 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:36182 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:36184 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:54976 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:54992 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:55004 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:44492 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:44494 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:44504 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:54608 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:54616 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:54624 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:55422 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:55424 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:55426 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:42404 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:42420 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:42424 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:52636 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:52640 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:52642 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:55622 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:55636 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:55638 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:41268 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:41270 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:41286 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:48008 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:48014 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:48024 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:40782 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:40790 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:40802 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:36004 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:36016 - "GET /health HTTP/1.1" 200 OK
INFO:     192.168.10.16:36030 - "GET /health HTTP/1.1" 200 OK
