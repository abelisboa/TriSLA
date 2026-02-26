# Instruções de Execução - PROMPT_S31.4

## ✅ Status Atual
- FASE 0: ✅ Concluída (Snapshot criado)
- FASE 1: ✅ Concluída (Código verificado)
- FASE 2: ✅ Concluída (Versões atualizadas para 3.9.8)
- FASE 4: ✅ Concluída (Helm atualizado)
- FASE 5: ✅ Concluída (Helm upgrade executado)

## 📋 Próximos Passos

### PASSO 1: Executar FASE 3 (Build + Push)
**No terminal interativo do node006:**

```bash
ssh node006
cd /home/porvir5g/gtp5g/trisla
./scripts/execute-fase3-build-push.sh
```

**OU execute manualmente:**
```bash
export TAG=v3.9.8
echo "$GITHUB_TOKEN" | docker login ghcr.io -u abelisboa --password-stdin
# Depois execute os builds conforme o script
```

⏱️ **Tempo estimado:** 30-60 minutos (dependendo da velocidade de build/push)

### PASSO 2: Executar Fases Restantes
**Após o build/push concluir:**

```bash
cd /home/porvir5g/gtp5g/trisla
./scripts/execute-s31-4-completo.sh
```

Este script executa automaticamente:
- FASE 5: Verificação de rollout
- FASE 6: Verificação de imagens em runtime
- FASE 7: Smoke test Kafka
- FASE 8: Coleta de evidências finais

### PASSO 3: Executar Fases Individuais (Opcional)
Se preferir executar fase por fase:

```bash
# FASE 5 - Rollout
./scripts/execute-fase5-rollout.sh

# FASE 7 - Smoke Test
./scripts/execute-fase7-smoke-test.sh
```

## 📁 Arquivos Criados

- `scripts/execute-fase3-build-push.sh` - Build e push de todas as imagens
- `scripts/execute-fase5-rollout.sh` - Verificação de rollout
- `scripts/execute-fase7-smoke-test.sh` - Smoke test Kafka
- `scripts/execute-s31-4-completo.sh` - Script master (executa tudo)

## 📊 Evidências

Todas as evidências serão salvas em:
`/home/porvir5g/gtp5g/trisla/evidencias_release_v3.9.8/s31/`

## ⚠️ Notas Importantes

1. **GITHUB_TOKEN**: Deve estar disponível no ambiente onde você executa o build
2. **Tempo de Build**: Os builds podem levar bastante tempo, especialmente com `--no-cache`
3. **Smoke Test**: Requer que você submeta SLAs via portal-backend durante o teste
4. **Rollout**: Pode levar alguns minutos para os pods iniciarem após o push

## 🔍 Verificações Pós-Execução

Após concluir todas as fases, verifique:

1. ✅ Todos os pods decision-engine rodando com v3.9.8
2. ✅ Nenhum pod com versões antigas (v3.9.6, v3.9.7, etc.)
3. ✅ Eventos sendo publicados no Kafka (trisla-decision-events)
4. ✅ Logs do decision-engine sem erros críticos

