# 🧩 Prompt — Generate_UI_and_ControlLayer.md  
**Objetivo:** Criar a camada completa de **interface, controle e observabilidade** da arquitetura TriSLA@NASP.  
**Autor:** Abel Lisboa  
**Versão:** 1.0 — Outubro/2025  

---

## 🎯 Contexto

O projeto TriSLA@NASP possui três módulos centrais:
- SEM-NSMF (ontologia e semântica)
- ML-NSMF (IA e decisão)
- BC-NSSMF (contratos inteligentes)

Cada módulo já funciona no ambiente NASP, mas falta a camada **visual de controle e monitoramento**, acessível via navegador, para:
- Solicitar e visualizar SLAs;
- Monitorar slices ativos e violações;
- Observar logs e métricas em tempo real;
- Administrar usuários e permissões.

---

## 🧭 Objetivos específicos

1. Criar **interface administrativa (front-end)** baseada em React + Tailwind.
2. Criar **back-end de controle (API Gateway)** com FastAPI (Python) ou Node.js Express.
3. Integrar front e back-end aos módulos internos SEM, ML e BC via REST/gRPC.
4. Expor dashboards de observabilidade conectados a Grafana, Jaeger e Prometheus.
5. Gerar **templates Helm** de implantação para Kubernetes no namespace `trisla-nsp`.
6. Documentar a arquitetura gerada no arquivo `docs/UI_Architecture_TriSLA.md`.

---

## ⚙️ Especificações técnicas

### 🔹 Front-end (UI)

**Stack:**
- React + Tailwind + ShadCN + Chart.js
- Estrutura de pastas:
  ```
  /src/ui/
    ├── components/
    ├── pages/
    ├── hooks/
    ├── api/
    └── public/
  ```

**Requisitos funcionais:**
- Menu lateral com seções:
  - SEM-NSMF  
  - ML-NSMF  
  - BC-NSSMF  
  - NASP Integration  
  - Monitoring
- Dashboard inicial com KPIs:
  - SLA Requests / Accepted / Violations
  - Active Slices por domínio (RAN, Core, Transport)
  - Contract Events (Blockchain)
- Painel de logs (integração Loki/Jaeger)
- Layout responsivo e leve (tema claro padrão).

---

### 🔹 Back-end (Control API)

**Stack:**  
- FastAPI (Python 3.12) ou Node.js (Express)

**Endpoints principais:**
| Endpoint | Método | Descrição |
|-----------|---------|-----------|
| `/api/sla` | GET/POST | Criação e listagem de SLAs |
| `/api/slice` | GET | Slices ativos e domínios |
| `/api/metrics` | GET | KPIs e métricas de observabilidade |
| `/api/contracts` | GET | Eventos de blockchain e compliance |
| `/api/users` | GET/POST | Gestão de usuários e permissões |

**Integrações:**
- SEM Layer → `/semantic`
- ML Layer → `/prediction`
- BC Layer → `/contract`
- Monitoring → `/grafana`, `/prometheus`, `/jaeger`

---

### 🔹 Helm Chart de implantação

Gerar pasta:
```
/helm/triSLA-dashboard/
  ├── Chart.yaml
  ├── values.yaml
  └── templates/
```

**Valores principais (`values.yaml`):**
```yaml
replicaCount: 1
image:
  repository: trisla/dashboard
  tag: latest
service:
  type: NodePort
  port: 32000
resources:
  limits:
    cpu: 500m
    memory: 512Mi
```

---

### 🔹 Observabilidade

Integrar a UI com:
- **Grafana:** métricas e painéis personalizados  
- **Prometheus:** KPIs automáticos  
- **Jaeger:** tracing de requisições  
- **Loki:** logs estruturados  

Gerar um painel inicial (`Dashboard.json`) com:
- SLA Requests
- Slice Allocation
- Contract Violations
- ML Predictions Latency

---

## 🧱 Tarefas da IA

1. Ler os arquivos das pastas `STATE/` e `PROMPTS/` para identificar interfaces e dependências existentes.
2. Gerar **estrutura completa de código front-end e back-end** dentro de `/src/ui` e `/src/backend`.
3. Criar arquivos Helm em `/helm/triSLA-dashboard/`.
4. Gerar `docs/UI_Architecture_TriSLA.md` descrevendo toda a camada visual.
5. Preparar instruções de build e deploy (Dockerfile + helm install).
6. Aguardar confirmação antes da execução de qualquer comando NASP.

---

## 🧩 Execução no Cursor

1️⃣ Abra este arquivo no Cursor.  
2️⃣ Pressione **Ctrl + I**.  
3️⃣ Escolha o modelo **GPT-5-Pro**.  
4️⃣ Diga:  
   ```
   Gerar e documentar a camada de UI e controle conforme este prompt.
   ```
5️⃣ Aguarde a geração completa do código e a criação dos diretórios.  
6️⃣ Faça commit e push no GitHub:
   ```bash
   git add .
   git commit -m "UI e Dashboard gerados automaticamente"
   git push origin main
   ```

---

## ✅ Resultado esperado

Após execução:
```
/src/ui/              → Front-end React/Tailwind
/src/backend/         → API FastAPI/Node
/helm/triSLA-dashboard/ → Chart de deploy
/docs/UI_Architecture_TriSLA.md → Documentação gerada
```

Interface acessível via:
```
http://<NASP-IP>:32000/trisla
```

---

📘 *Fim do Prompt — Generate_UI_and_ControlLayer.md*  
