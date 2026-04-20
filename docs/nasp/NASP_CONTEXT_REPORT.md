# Relatório de Contexto NASP — TriSLA

**Data:** <DATA_GERADA>  
**Gerado por:** scripts/discover-nasp-endpoints.sh  
**Objetivo:** Documentar o environment NASP sem expor informações sensíveis

---

## Visão Geral of Cluster NASP

| Campo | Valor (genérico) |
|-------|------------------|
| Número de nodes | 2 |
| Versão of Kubernetes | <K8S_VERSION> |
| CNI | Calico |
| Namespace TriSLA alvo | <TRISLA_NAMESPACE> (ex.: trisla) |

**Nota:** Este relatório is gerado automaticamente. Execute `scripts/discover-nasp-endpoints.sh` no environment NASP for obter valores reais.

---

## Services Detectados

| Componente | Namespace | Tipo de Service | Observação |
|------------|-----------|-----------------|------------|
| Prometheus | monitoring | ClusterIP/NodePort | Usado for metrics NASP |
| Grafana | monitoring | ClusterIP | UI de visualization de metrics |
| Kafka | <KAFKA_NS> | ClusterIP | Broker for eventos TriSLA/NASP |
| NASP Adapter | <NASP_NS> | ClusterIP | Interface entre TriSLA e NASP |
| Loki | monitoring | ClusterIP | Sistema de logs (se disponível) |
| NWDAF | <NWDAF_NS> | ClusterIP | Network Data Analytics Function (se disponível) |

**Como descobrir endpoints reais:**

1. Execute `scripts/discover-nasp-endpoints.sh` localmente no node1 of NASP (você já está dentro of node1)
2. Revise o arquivo `tmp/nasp_context_raw.txt` gerado
3. Use os FQDNs no formato: `http://<SERVICE>.<NAMESPACE>.svc.cluster.local:<PORT>`

---

## Diagnóstico de Saúde

### problems Encontrados

- ⚠️ Pods in CrashLoopBackOff: Verifiesr `tmp/nasp_context_raw.txt` for detalhes
- ⚠️ Pods in ImagePullBackOff: Verifiesr `tmp/nasp_context_raw.txt` for detalhes
- ⚠️ Pods não prontos: Verifiesr `tmp/nasp_context_raw.txt` for detalhes

**Nota:** Este relatório is um template. Execute `scripts/discover-nasp-endpoints.sh` for obter diagnóstico real.

---

## Namespaces Relevantes

| Namespace | Propósito | Observação |
|-----------|-----------|------------|
| monitoring | Stack de observabilidade | Prometheus, Grafana, Loki |
| nasp | Services NASP principais | NASP Adapter, controladores |
| <RAN_NS> | Services RAN | Controladores RAN (se aplicável) |
| <CORE_NS> | Services Core | UPF, AMF, SMF (se aplicável) |
| <TRANSPORT_NS> | Services Transport | Controladores de transporte (se aplicável) |

---

## Próximos Passos

1. **Revisar relatório raw:** `tmp/nasp_context_raw.txt`
2. **Identificar endpoints NASP:** Use FQDNs no formato Kubernetes
3. **Preencher values-nasp.yaml:** Execute `scripts/fill_values_production.sh`
4. **Validate configuration:** `helm template trisla ./helm/trisla -f ./helm/trisla/values-nasp.yaml --debug`

---

**Versão:** 1.0  
**ENGINE MASTER:** Sistema de Descoberta NASP TriSLA


