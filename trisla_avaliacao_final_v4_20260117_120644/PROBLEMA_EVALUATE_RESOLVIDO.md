# Problema do Endpoint /evaluate - RESOLVIDO

**Data:** 2026-01-19 09:28:56

## Problema Identificado
- Endpoint /evaluate retornava 404 Not Found
- Código estava presente no arquivo local (605 linhas, endpoint na linha 455)
- Imagem Docker tinha código antigo (372 linhas, sem endpoint)

## Causa Raiz
- Docker estava usando cache durante o build
- Helm não aplicou corretamente as mudanças de imagem
- Deployment estava usando imagem do registry (ghcr.io) ao invés da imagem local

## Solução Aplicada
1. Rebuild sem cache: 
2. Patch direto do deployment para usar imagem local
3. Verificação: endpoint agora presente no código (linha 398, 545 linhas totais)

## Teste de Validação
**Endpoint:** POST /evaluate  
**Status:** ✅ HTTP 200 OK

**Resposta contém:**
- ✅ decision_id: dec-gate-final-001
- ✅ action: RENEG
- ✅ ml_risk_score: 0.5005357752797864
- ✅ ml_risk_level: medium
- ✅ reasoning: com explanation completo
- ✅ confidence: 0.85
- ✅ timestamp: 2026-01-19T12:28:40.080940+00:00

## Logs Confirmam
- ✅ SLA recebido para avaliação
- ✅ Chamada ML-NSMF realizada
- ✅ Decisão persistida
- ✅ Encaminhamento para BC-NSMF (com warning esperado)

**Status:** ✅ PROBLEMA RESOLVIDO - Endpoint funcionando corretamente
