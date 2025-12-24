# Fluxos Funcionais — Portal

**Versão:** S4.0  
**Data:** 2025-01-27  
**Origem do Conteúdo:** `trisla-portal/docs/FLUXO_XAI.md`, `trisla-portal/docs/FLUXO_PLN_NEST.md`, `trisla-portal/docs/FLUXO_BATCH_SLA.md`, `trisla-portal/docs/CICLO_VIDA_CONTRATOS.md`

---

## 📋 Sumário

1. [Fluxo XAI](#fluxo-xai)
2. [Fluxo PLN e NEST](#fluxo-pln-e-nest)
3. [Fluxo Batch SLA](#fluxo-batch-sla)
4. [Ciclo de Vida de Contratos](#ciclo-de-vida-de-contratos)

---

## Fluxo XAI

### Visão Geral

O fluxo XAI permite visualizar explicações de predições de viabilidade do ML-NSMF usando SHAP ou LIME.

### Passo a Passo

1. **Usuário solicita explicação XAI**
   - Frontend envia requisição para Backend API
   - Endpoint: `GET /api/v1/xai/{prediction_id}`

2. **Backend consulta ML-NSMF**
   - Backend API consulta ML-NSMF para obter explicação
   - ML-NSMF retorna explicação (SHAP/LIME/fallback)

3. **Backend processa explicação**
   - Agrega dados de explicação
   - Formata para visualização

4. **Frontend renderiza explicação**
   - Visualização interativa de feature importance
   - Gráficos SHAP/LIME
   - Reasoning textual

**Documentação Completa:** `trisla-portal/docs/FLUXO_XAI.md`

---

## Fluxo PLN e NEST

### Visão Geral

O fluxo PLN e NEST permite criar SLAs usando Processamento de Linguagem Natural ou Templates NEST.

### Passo a Passo

1. **Usuário cria SLA via PLN**
   - Frontend envia texto em linguagem natural
   - Endpoint: `POST /api/v1/slas/pln`

2. **Backend processa PLN**
   - Backend API envia para SEM-NSMF
   - SEM-NSMF processa com NLP
   - SEM-NSMF gera NEST

3. **Backend processa NEST**
   - Backend API recebe NEST do SEM-NSMF
   - Valida NEST
   - Envia para Decision Engine

4. **Frontend exibe resultado**
   - Exibe NEST gerado
   - Exibe status da decisão

**Documentação Completa:** `trisla-portal/docs/FLUXO_PLN_NEST.md`

---

## Fluxo Batch SLA

### Visão Geral

O fluxo Batch SLA permite criar múltiplos SLAs simultaneamente usando arquivo CSV ou JSON.

### Passo a Passo

1. **Usuário faz upload de arquivo**
   - Frontend envia arquivo CSV/JSON
   - Endpoint: `POST /api/v1/slas/batch`

2. **Backend processa arquivo**
   - Backend API valida formato
   - Processa cada SLA do arquivo
   - Envia para SEM-NSMF

3. **Backend agrega resultados**
   - Agrega resultados de cada SLA
   - Gera relatório de sucesso/falha

4. **Frontend exibe resultados**
   - Exibe relatório de batch
   - Exibe SLAs criados com sucesso
   - Exibe SLAs com erro

**Documentação Completa:** `trisla-portal/docs/FLUXO_BATCH_SLA.md`

---

## Ciclo de Vida de Contratos

### Visão Geral

O ciclo de vida de contratos descreve os estados e transições de SLAs desde a criação até a conclusão.

### Estados

1. **REQUESTED**: SLA solicitado (aguardando aprovação)
2. **APPROVED**: SLA aprovado (pronto para ativação)
3. **REJECTED**: SLA rejeitado
4. **ACTIVE**: SLA ativo (em execução)
5. **VIOLATED**: SLA violado (requisitos não atendidos)
6. **TERMINATED**: SLA terminado (finalizado)
7. **COMPLETED**: SLA completado (finalizado com sucesso)

### Transições

- **REQUESTED → APPROVED**: Decision Engine aprova SLA
- **REQUESTED → REJECTED**: Decision Engine rejeita SLA
- **APPROVED → ACTIVE**: SLA é ativado
- **ACTIVE → VIOLATED**: SLA é violado
- **ACTIVE → TERMINATED**: SLA é terminado
- **ACTIVE → COMPLETED**: SLA é completado com sucesso

**Documentação Completa:** `trisla-portal/docs/CICLO_VIDA_CONTRATOS.md`

---

## Origem do Conteúdo

Este documento foi consolidado a partir de:
- `trisla-portal/docs/FLUXO_XAI.md` — Fluxo completo de Explainable AI
- `trisla-portal/docs/FLUXO_PLN_NEST.md` — Fluxo PLN e NEST Templates
- `trisla-portal/docs/FLUXO_BATCH_SLA.md` — Fluxo de criação batch de SLAs
- `trisla-portal/docs/CICLO_VIDA_CONTRATOS.md` — Ciclo de vida completo dos contratos

**Última atualização:** 2025-01-27  
**Versão:** S4.0

