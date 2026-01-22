Objetivo

Executar C1.1 — eMBB com 5 SLAs simultâneos como rodada baseline válida (R1) da metodologia TriSLA, garantindo:

pré-condições estáveis

nenhuma modificação no core do TriSLA

nenhuma alteração de scripts durante a execução

coleta rastreável e auditável

resultados cientificamente defensáveis

Esta rodada substitui C1.1-R0 como referência válida.

Princípios Obrigatórios (NÃO NEGOCIÁVEIS)

❌ Nenhuma modificação em apps/, helm/, docs/

❌ Nenhuma edição de scripts durante a execução

❌ Nenhum avanço se houver CrashLoopBackOff

✅ Tudo deve ocorrer dentro de experiments/

✅ Toda evidência deve ser preservada

✅ Uma rodada = um relatório fechado

Se qualquer item falhar → ABORTAR EXECUÇÃO.

FASE 0 — Pré-condições (OBRIGATÓRIA)
0.1 — Acesso e diretório
ssh node006
cd /home/porvir5g/gtp5g/trisla/experiments
pwd


Deve retornar:

/home/porvir5g/gtp5g/trisla/experiments

0.2 — Verificação de estabilidade do cluster
kubectl -n trisla get pods


Critério de aprovação:

Todos os pods em Running ou Completed

❌ Nenhum pod em:

CrashLoopBackOff

Error

ImagePullBackOff

Pending

Se houver qualquer falha → ABORTAR.

0.3 — Verificação de serviços críticos
kubectl -n trisla get svc


Confirmar existência de:

Decision Engine

ML-NSMF

SEM-CSMF

NASP Adapter

Portal Backend

0.4 — Verificação mínima de métricas (/metrics)

Escolher 1 módulo (ex.: SEM-CSMF):

kubectl -n trisla port-forward svc/trisla-sem-csmf 19091:80 &
sleep 2
curl -s http://127.0.0.1:19091/metrics | head -n 20
kill %1


Critério:

O endpoint deve responder com texto Prometheus válido

Não é necessário haver métricas customizadas ainda

Se não responder → ABORTAR.

FASE 1 — Congelamento Experimental
1.1 — Congelar scripts e templates
ls templates/C1_eMBB_5.yaml
ls generators/submit_slas.py
ls collectors/prometheus_collector.py
ls collectors/logs_collector.py
ls analysis/compute_metrics.py


Nenhum arquivo deve ser editado após este ponto.

1.2 — Criar diretório da rodada
mkdir -p reports/C1.1_R1

FASE 2 — Execução do Cenário (C1.1)
2.1 — Submissão dos SLAs (sequencial)
python3 generators/submit_slas.py \
  --template templates/C1_eMBB_5.yaml \
  --output reports/C1.1_R1/C1.1_submissions.json


Regras:

5 SLAs

Sequencial

Intervalo ≥ 5s

Sem retries

Sem paralelismo

2.2 — Coleta de métricas Prometheus
python3 collectors/prometheus_collector.py \
  --scenario C1.1_R1 \
  --output reports/C1.1_R1/

2.3 — Coleta de logs do cluster
python3 collectors/logs_collector.py \
  --scenario C1.1_R1 \
  --output reports/C1.1_R1/

FASE 3 — Análise Offline (SEM INTERPRETAÇÃO)
python3 analysis/compute_metrics.py \
  --input reports/C1.1_R1/ \
  --output reports/C1.1_R1/analysis_C1.1_R1.json


⚠️ Proibido:

descartar outliers

ajustar dados

“corrigir” resultados

FASE 4 — Preservação de Evidência
sha256sum reports/C1.1_R1/* > reports/C1.1_R1/SHA256SUMS.txt
tar -czf reports/C1.1_R1.tgz reports/C1.1_R1
ls -lh reports/C1.1_R1.tgz

FASE 5 — Checklist de Validação

Preencher manualmente (em relatório):

 0 pods em CrashLoopBackOff

 5 SLAs submetidos

 Pipeline executou E2 end-to-end

 Decisões registradas (ACCEPT / RENEG / REJECT)

 correlation_ids preservados

 Logs coletados

 Métricas coletadas (ou justificativa técnica documentada)

 Artefatos versionados

RESULTADO ESPERADO (NEUTRO)

Este experimento NÃO TEM meta de ACCEPT.

Resultados válidos incluem:

100% RENEG

mistura ACCEPT/RENEG

até 100% REJECT

Desde que:

o pipeline funcione

os dados sejam reais

a decisão seja explicável via logs

PROIBIÇÕES ABSOLUTAS

❌ Ajustar regras do Decision Engine

❌ Alterar limiares para “forçar ACCEPT”

❌ Reexecutar silenciosamente

❌ Pular fases

❌ Avançar para C1.2 sem fechar relatório C1.1_R1

Critério de Encerramento

A execução SÓ É CONSIDERADA CONCLUÍDA se:

reports/C1.1_R1.tgz existir

SHA256 calculado

Checklist preenchido

Nenhuma modificação fora de experiments/

Somente após isso é permitido discutir:

C1.2

ajustes metodológicos

limitações reais do TriSLA
