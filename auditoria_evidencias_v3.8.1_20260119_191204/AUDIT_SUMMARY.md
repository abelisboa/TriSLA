=== AUDITORIA EVIDENCIAS v3.8.1 ===
Timestamp: 20260119_191204
Namespace: trisla
Evidências: /home/porvir5g/gtp5g/trisla/evidencias_resultados_v3.8.1

## FASE 0 — Pré-check
- Arquivos encontrados: 19
⚠️ ALERTA: Existem arquivos vazios (evidência parcial).
Veja: VAZIOS.txt

## FASE 1 — Varredura de erros (linha-a-linha)
- ⚠️ ALERTA: padrões de erro encontrados (não reprova sozinho; precisa contexto).
  Arquivo: ERROS_ENCONTRADOS.txt (contém linha e arquivo)
  Total de ocorrências: 69

## FASE 2 — Validação de formato (JSON/CSV)
- JSON encontrados: 4
- ✅ Todos os JSON são válidos
- CSV encontrados: 0
- ✅ CSVs aparentam conter dados

## FASE 3 — Auditoria de SLAs (Portal) — 01_slas/
- Arquivos SLA: 5
- IDs extraídos (únicos): 0
❌ FAIL: Nenhum SLA/decision_id extraído das respostas do Portal.
   Correção necessária: alinhar endpoint e payload do Portal (template_id/form_values) e repetir coleta.
- ⚠️ Há indícios de falhas em respostas do Portal (ver SLA_FALHAS.txt)

## FASE 4 — Auditoria Decision Engine — 04_decisions/
