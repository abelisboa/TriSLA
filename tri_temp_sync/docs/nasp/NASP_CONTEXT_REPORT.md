# Relatório de Contexto NASP — TriSLA

**Data:** <DATA_GERADA>  
**Gerado por:** scripts/discover-nasp-endpoints.sh  
**Objetivo:** Documentar o ambiente NASP sem expor informações sensíveis

---

## Visão Geral do Cluster NASP

| Campo | Valor (genérico) |
|-------|------------------|
| Número de nodes | 2 |
| Versão do Kubernetes | <K8S_VERSION> |
| CNI | Calico |
| Namespace TriSLA alvo | <TRISLA_NAMESPACE> (ex.: trisla) |

**Nota:** Este relatório é gerado automaticamente. Execute `scripts/discover-nasp-endpoints.sh` no ambiente NASP para obter valores reais.

---

## Serviços Detectados

| Componente | Namespace | Tipo de Serviço | Observação |
|------------|-----------|-----------------|------------|
| Prometheus | monitoring | ClusterIP/NodePort | Usado para métricas NASP |
| Grafana | monitoring | ClusterIP | UI de visualização de métricas |
| Kafka | <KAFKA_NS> | ClusterIP | Broker para eventos TriSLA/NASP |
| NASP Adapter | <NASP_NS> | ClusterIP | Interface entre TriSLA e NASP |
| Loki | monitoring | ClusterIP | Sistema de logs (se disponível) |
| NWDAF | <NWDAF_NS> | ClusterIP | Network Data Analytics Function (se disponível) |

**Como descobrir endpoints reais:**

1. Execute `scripts/discover-nasp-endpoints.sh` localmente no node1 do NASP (você já está dentro do node1)
2. Revise o arquivo `tmp/nasp_context_raw.txt` gerado
3. Use os FQDNs no formato: `http://<SERVICE>.<NAMESPACE>.svc.cluster.local:<PORT>`

---

## Diagnóstico de Saúde

### Problemas Encontrados

- ⚠️ Pods em CrashLoopBackOff: Verificar `tmp/nasp_context_raw.txt` para detalhes
- ⚠️ Pods em ImagePullBackOff: Verificar `tmp/nasp_context_raw.txt` para detalhes
- ⚠️ Pods não prontos: Verificar `tmp/nasp_context_raw.txt` para detalhes

**Nota:** Este relatório é um template. Execute `scripts/discover-nasp-endpoints.sh` para obter diagnóstico real.

---

## Namespaces Relevantes

| Namespace | Propósito | Observação |
|-----------|-----------|------------|
| monitoring | Stack de observabilidade | Prometheus, Grafana, Loki |
| nasp | Serviços NASP principais | NASP Adapter, controladores |
| <RAN_NS> | Serviços RAN | Controladores RAN (se aplicável) |
| <CORE_NS> | Serviços Core | UPF, AMF, SMF (se aplicável) |
| <TRANSPORT_NS> | Serviços Transport | Controladores de transporte (se aplicável) |

---

## Próximos Passos

1. **Revisar relatório raw:** `tmp/nasp_context_raw.txt`
2. **Identificar endpoints NASP:** Use FQDNs no formato Kubernetes
3. **Preencher values-nasp.yaml:** Execute `scripts/fill_values_production.sh`
4. **Validar configuração:** `helm template trisla ./helm/trisla -f ./helm/trisla/values-nasp.yaml --debug`

---

**Versão:** 1.0  
**ENGINE MASTER:** Sistema de Descoberta NASP TriSLA


