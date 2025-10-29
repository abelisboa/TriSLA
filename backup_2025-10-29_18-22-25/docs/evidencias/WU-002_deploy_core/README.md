# 📁 Evidências — WU-002 Deploy Core Modules

**Data:** 2025-10-17  
**Responsável:** Abel José Rodrigues Lisboa  
**Ambiente:** NASP@UNISINOS

---

## 📊 Estrutura de Evidências

Este diretório contém todas as evidências do deploy dos módulos core do TriSLA no ambiente NASP.

### Arquivos Gerados Automaticamente pelo Script

| Arquivo | Descrição |
|---------|-----------|
| `deploy_log.txt` | Log completo da execução do deploy |
| `deploy_validation.json` | Resumo do deploy em formato JSON |
| `pods_list.txt` | Lista de todos os pods deployados |
| `services_list.txt` | Lista de todos os serviços criados |
| `deployments_list.txt` | Lista de todos os deployments |
| `{pod-name}_describe.txt` | Descrição detalhada de cada pod |

---

## 🎯 Módulos Deployados

| Módulo | Deployment | Service | Porta |
|--------|------------|---------|-------|
| **SEM-NSMF** | trisla-semantic-layer | trisla-semantic | 8080, 9090 |
| **ML-NSMF** | trisla-ai-layer | trisla-ai | 8080, 9090 |
| **BC-NSSMF** | trisla-blockchain-layer | trisla-blockchain | 7070, 9090 |
| **Integration** | trisla-integration-layer | trisla-integration | 8080, 9090 |
| **Monitoring** | trisla-monitoring-layer | trisla-monitoring | 8080, 9090 |

---

## ✅ Critérios de Validação

- [x] 5 deployments criados
- [x] 5 services criados
- [x] 5 pods em status Running
- [x] 0 restarts nos pods
- [x] Probes de liveness e readiness configuradas
- [x] Recursos (CPU/Memory) limitados
- [x] Namespace trisla-nsp ativo

---

## 📝 Formato do deploy_validation.json

```json
{
  "deployment_date": "2025-10-17T...",
  "namespace": "trisla-nsp",
  "modules_deployed": 5,
  "total_pods": 5,
  "running_pods": 5,
  "services": 5,
  "deployments": 5,
  "status": "SUCCESS"
}
```

---

## 🔍 Como Verificar

### Ver todos os pods
```bash
kubectl get pods -n trisla-nsp -o wide
```

### Ver serviços
```bash
kubectl get svc -n trisla-nsp
```

### Ver logs de um pod
```bash
kubectl logs -n trisla-nsp deployment/trisla-semantic-layer
```

### Testar health check
```bash
kubectl exec -n trisla-nsp deploy/trisla-semantic-layer -- curl -s http://localhost:8080/health
```

---

📅 **Criado em:** 17/10/2025  
👤 **Autor:** Abel José Rodrigues Lisboa  
🏛️ **Projeto:** TriSLA@NASP — UNISINOS




