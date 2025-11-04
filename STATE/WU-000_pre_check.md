# WU-000 — Pré-Check do Ambiente NASP
## Registro Técnico de Validação e Preparação para Implantação TriSLA@NASP

| Campo | Informação |
|--------|-------------|
| Data | 16/10/2025 |
| Responsável | Abel José Rodrigues Lisboa |
| Cluster | NASP – UNISINOS |
| Nodes | node1 (Ubuntu 24.04 LTS – v1.28.15), node2 (Ubuntu 20.04 LTS – v1.31.1) |
| Container Runtime | containerd 1.7.23 |
| Namespace oficial | trisla-nsp |
| Objetivo | Confirmar que o ambiente NASP está limpo, estável e pronto para a nova implantação TriSLA. |

---

## 🔍 Diagnóstico Executado

**Comandos principais executados:**
```bash
kubectl get nodes -o wide
kubectl get pods -A -o wide
kubectl get ns
```

**Resultados resumidos:**
- Ambos os nós **Ready** e sincronizados.  
- Todos os componentes críticos do NASP operando normalmente.  
- Novo namespace `trisla-nsp` criado e ativo.  
- Ambiente estável, sem conflitos ou resíduos de implantações anteriores.

---

## 🧱 Estado Atual do Cluster

| Item | Status |
|------|---------|
| Control Plane | node1 / node2 prontos |
| Pods essenciais (Calico, CoreDNS, Metrics) | Ativos |
| Monitoring Stack | Operacional |
| NASP Core | Estável |
| Namespace TriSLA | `trisla-nsp` (ativo e vazio) |
| Contexto Kubernetes | Configurado para `trisla-nsp` |
| Ambiente geral | **Pronto para deploy TriSLA@NASP** |

---

## 💾 Evidências

Snapshot do estado completo salvo em:
```
docs/evidencias/WU-000_pre_check/nasp_state_before_trisla.txt
```
Contendo listagens de:
- `kubectl get all -A`
- `kubectl get pv/pvc -A`
- `kubectl get secrets/cm/ingress -A`

---

## ✅ Conclusão

- Ambiente NASP verificado e **validado**.  
- Namespace `trisla-nsp` configurado corretamente.  
- Cluster apto para receber a **WU-001 — Bootstrap e Integração TriSLA**.

📅 **Data:** 16/10/2025  
👤 **Autor:** Abel José Rodrigues Lisboa  
🏛️ **Projeto:** TriSLA@NASP — UNISINOS / Mestrado em Computação Aplicada
