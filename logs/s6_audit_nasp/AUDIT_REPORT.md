# AUDITORIA TÉCNICA NASP — Relatório

**Data:** 2025-12-21  
**Objetivo:** Descobrir como o NASP realmente cria (ou simula) um slice/SLA

## FASE A1 — Serviços Ativos do NASP

NAME                             TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                       AGE
trisla-bc-nssmf                  ClusterIP   10.233.39.215   <none>        8083/TCP                      2d1h
trisla-bc-nssmf-metrics          ClusterIP   10.233.30.108   <none>        8083/TCP                      27h
trisla-besu                      ClusterIP   10.233.37.164   <none>        8545/TCP,8546/TCP,30303/TCP   5h23m
trisla-decision-engine           ClusterIP   10.233.26.201   <none>        8082/TCP                      2d1h
trisla-decision-engine-metrics   ClusterIP   10.233.32.162   <none>        8082/TCP                      27h
trisla-ml-nsmf                   ClusterIP   10.233.28.209   <none>        8081/TCP                      2d1h
trisla-nasp-adapter              ClusterIP   10.233.6.35     <none>        8085/TCP                      2d1h
trisla-portal-backend            NodePort    10.233.46.159   <none>        8001:32002/TCP                26h
trisla-portal-frontend           NodePort    10.233.19.22    <none>        80:32001/TCP                  26h
trisla-sem-csmf                  ClusterIP   10.233.13.160   <none>        8080/TCP                      2d1h
trisla-sla-agent-layer           ClusterIP   10.233.4.83     <none>        8084/TCP                      2d1h
trisla-sla-agent-metrics         ClusterIP   10.233.25.234   <none>        8084/TCP                      27h
trisla-ui-dashboard              ClusterIP   10.233.4.125    <none>        80/TCP                        2d1h

NAME                                      READY   STATUS             RESTARTS         AGE
test-curl2                                0/1     Completed          0                27h
test-metrics-ml                           0/1     Completed          0                9h
trisla-bc-nssmf-84995f7445-t2jd2          1/1     Running            0                2d
trisla-besu-6db76bff8c-gjhnw              1/1     Running            8 (5h10m ago)    5h19m
trisla-besu-76776f744c-454rr              0/1     CrashLoopBackOff   11 (5m42s ago)   35m
trisla-decision-engine-6656d4965f-7pq47   1/1     Running            0                73m
trisla-ml-nsmf-866d669bcb-8qbbl           1/1     Running            0                3h21m
trisla-nasp-adapter-74cd854849-4tmwv      1/1     Running            0                2d1h
trisla-portal-backend-565fcc7f45-kqd8b    1/1     Running            0                21h
trisla-portal-frontend-6dd98dc868-7vfqf   1/1     Running            0                21h
trisla-sem-csmf-848588fdd6-nqnp2          1/1     Running            0                3h19m
trisla-sla-agent-layer-bb7f5558c-zlf7r    1/1     Running            0                44m
trisla-ui-dashboard-dfb9ff9cc-jk4xb       1/1     Running            0                2d1h

## FASE A2 — APIs do NASP Adapter

HOSTNAME=trisla-nasp-adapter-74cd854849-4tmwv
OTLP_ENDPOINT=http://trisla-otel-collector:4317
TRISLA_NASP_ADAPTER_PORT_8085_TCP_ADDR=10.233.6.35
TRISLA_NASP_ADAPTER_PORT_8085_TCP_PORT=8085
TRISLA_NASP_ADAPTER_PORT_8085_TCP_PROTO=tcp
TRISLA_NASP_ADAPTER_PORT_8085_TCP=tcp://10.233.6.35:8085
TRISLA_NASP_ADAPTER_PORT=tcp://10.233.6.35:8085
TRISLA_NASP_ADAPTER_SERVICE_HOST=10.233.6.35
TRISLA_NASP_ADAPTER_SERVICE_PORT=8085
TRISLA_NASP_ADAPTER_SERVICE_PORT_HTTP=8085

## FASE A4 — Recursos do Cluster

NAME                  DATA   AGE
kube-root-ca.crt      1      2d1h
trisla-besu-genesis   1      5h23m
trisla-config         7      2d1h

networksliceinstances.trisla.io                       2025-12-12T21:16:01Z
networkslicesubnetinstances.trisla.io                 2025-12-12T21:16:02Z
