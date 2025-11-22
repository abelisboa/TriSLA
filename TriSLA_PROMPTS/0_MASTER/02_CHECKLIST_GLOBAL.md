# 02 – CHECKLIST GLOBAL

Checklist completo para validação de todas as fases.
# CHECKLIST GERAL DE QUALIDADE — PROJETO TRI-SLA

## 1. Infraestrutura
- [ ] Cluster NASP funcional (2 control-plane + ≥1 worker)
- [ ] Calico OK
- [ ] Storage Class configurado
- [ ] Load balancer acessível
- [ ] DNS interno funcional

## 2. Imagens
- [ ] Todas imagens existem no GHCR
- [ ] Tags versionadas corretamente
- [ ] Nenhuma imagem latest em produção

## 3. Módulos TriSLA
- [ ] SEM-CSMF valida intents e gera NEST corretamente
- [ ] ML-NSMF treinado e validado
- [ ] Decision Engine com regras e thresholds definidos
- [ ] BC-NSSMF executando SCs e recebendo métricas
- [ ] SLA-Agent Layer funcionando nos 3 domínios
- [ ] Todas interfaces I-01...I-07 testadas

## 4. Observabilidade
- [ ] OTLP collector operacional
- [ ] Prometheus scrape OK
- [ ] Traces no Grafana
- [ ] Métricas específicas TriSLA funcionando

## 5. Testes
- [ ] Unit OK
- [ ] Integration OK
- [ ] E2E OK
- [ ] Testes de contrato OK

## 6. Deploy
- [ ] Helm validado
- [ ] Dry-run OK
- [ ] Deploy NASP OK
- [ ] Dashboards importados
- [ ] Rollback funcional

