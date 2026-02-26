# Problema: Endpoint /api/v1/sla/submit não existe na imagem v3.8.1

## Diagnóstico

1. ✅ O código do endpoint EXISTE no repositório (trisla-portal/backend/src/routers/sla.py)
2. ✅ O router está registrado no main.py com prefixo /api/v1/sla
3. ✅ Os schemas SLASubmitRequest e SLASubmitResponse existem
4. ❌ A imagem v3.8.1 no registry NÃO contém o endpoint

## Causa Provável

A imagem foi construída antes do código ser commitado, ou o build usou cache de uma versão anterior.

## Solução

1. Fazer rebuild FORÇADO (sem cache) da imagem:
   

2. Fazer push da nova imagem:
   

3. Atualizar o deployment:
   

4. Validar o endpoint:
   
