# WU-003 — Integração TriSLA ↔ NASP Core
## Ativação de Interfaces O1, A1, E2 e Sincronização com SMO/NWDAF

---

| Campo | Informação |
|--------|-------------|
| Data | 16/10/2025 |
| Responsável | Abel José Rodrigues Lisboa |
| Cluster | NASP – UNISINOS |
| Namespace | trisla-nsp |
| Objetivo | Integrar os módulos centrais da TriSLA (SEM‑NSMF, ML‑NSMF, BC‑NSSMF) ao NASP Core, habilitando comunicação com as interfaces O1, A1, E2 e os serviços SMO, RIC e NWDAF. |

---

## 🧩 1️⃣ Contexto

Após o deploy local dos módulos TriSLA (WU‑002), esta unidade de trabalho estabelece a **integração operacional com o NASP Core**.  
O objetivo é permitir que a TriSLA troque informações com os controladores e serviços de rede (O‑RAN/NASP) através das interfaces padronizadas:  

- **O1:** comunicação com elementos da RAN via SMO (gerência e telemetria).  
- **A1:** troca de políticas e feedback entre Non‑RT RIC e Near‑RT RIC.  
- **E2:** controle e coleta de métricas em tempo quase real na RAN.  
- **NWDAF:** obtenção de dados analíticos e eventos.  

---

## ⚙️ 2️⃣ Pré‑Requisitos

| Item | Status |
|------|---------|
| WU‑002 — Deploy Core Modules | ✅ Concluído |
| Módulos SEM‑NSMF / ML‑NSMF / BC‑NSSMF ativos | ✅ Validado |
| NASP Core e SMO operacionais | ✅ Confirmados |
| Acesso às interfaces O1/A1/E2 | ✅ Disponíveis |
| Contexto Kubernetes setado para `trisla-nsp` | ✅ |

---

## 🧱 3️⃣ Configuração de Interfaces e Endpoints

### 🔹 O1 — SMO / Element Management
```bash
kubectl exec -n trisla-nsp deploy/sem-nsmf -- curl -X POST http://smo.nasp-core:8080/api/v1/register
```

**Esperado:** resposta `200 OK` com ID de registro TriSLA no SMO.

### 🔹 A1 — Non‑RT RIC ↔ ML‑NSMF
```bash
kubectl exec -n trisla-nsp deploy/ml-nsmf -- curl http://nonrtric.a1-interface:8085/policy
```

**Esperado:** status `Active` e retorno de políticas disponíveis.

### 🔹 E2 — Near‑RT RIC ↔ BC‑NSSMF
```bash
kubectl exec -n trisla-nsp deploy/bc-nssmf -- curl http://nearrtric.e2-interface:8086/handshake
```

**Esperado:** retorno `E2 Link Established`.

### 🔹 NWDAF — Coleta de Dados Analíticos
```bash
kubectl exec -n trisla-nsp deploy/ml-nsmf -- curl http://nwdaf-core:8081/api/v1/subscribe
```

**Esperado:** `Subscription Confirmed` e token de sessão analítica.

---

## 🔗 4️⃣ Sincronização TriSLA ↔ NASP

### 🔹 Validar registro TriSLA no SMO
```bash
kubectl exec -n trisla-nsp deploy/sem-nsmf -- curl http://smo.nasp-core:8080/api/v1/status
```

### 🔹 Confirmar descoberta de endpoints RIC
```bash
kubectl exec -n trisla-nsp deploy/ml-nsmf -- curl http://nonrtric.discovery:8080/health
```

### 🔹 Verificar blockchain listener (BC‑NSSMF)
```bash
kubectl exec -n trisla-nsp deploy/bc-nssmf -- curl http://bc-nssmf:7070/status
```

---

## 📊 5️⃣ Estrutura de Evidências

Os resultados e logs devem ser registrados em:

```
docs/evidencias/WU-003_integration_core/
 ├── o1_registration.log
 ├── a1_policy_exchange.log
 ├── e2_handshake.log
 ├── nwdaf_subscription.log
 ├── smo_status.json
 └── integration_summary.txt
```

---

## ✅ 6️⃣ Critérios de Aceitação

| Critério | Status Esperado |
|-----------|------------------|
| Registro TriSLA confirmado no SMO | ✅ |
| Handshake A1 e E2 bem-sucedidos | ✅ |
| Subscription NWDAF ativa | ✅ |
| Comunicação bidirecional entre módulos TriSLA e NASP Core | ✅ |
| Evidências armazenadas e validadas | ✅ |

---

## 🧾 7️⃣ Conclusão

A execução da WU‑003 estabelece a **integração funcional entre a TriSLA e o NASP Core**, confirmando a operação das interfaces O1, A1, E2 e NWDAF.  
Os módulos SEM‑NSMF, ML‑NSMF e BC‑NSSMF estão agora sincronizados com o SMO e os controladores O‑RAN do NASP.  
O ambiente está pronto para a **WU‑004 — Testes Detalhados, KPIs e Observabilidade Multi‑Domínio.**

📅 **Data:** 16/10/2025  
👤 **Autor:** Abel José Rodrigues Lisboa  
🏛️ **Projeto:** TriSLA@NASP — UNISINOS / Mestrado em Computação Aplicada
