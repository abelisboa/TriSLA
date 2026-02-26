# Status Build e Push ML-NSMF v3.9.0

## ✅ FASE 0 - Pré-check
- ✅ Branch: feature/xai-v3.9.0
- ✅ Dockerfile encontrado: apps/ml-nsmf/Dockerfile
- ✅ explain_prediction encontrado: 7 ocorrências

## ✅ FASE 1 - Build
- ✅ Build concluído com sucesso
- ✅ Imagem criada: ghcr.io/abelisboa/trisla-ml-nsmf:v3.9.0
- ✅ SHAP instalado: shap-0.49.1
- ✅ Todas as dependências instaladas

## ⏸️ FASE 2 - Login GHCR (REQUER AÇÃO MANUAL)
**Status:** Aguardando autenticação

**Instruções:**
1. Execute no terminal do node006:
   ```bash
   docker login ghcr.io -u abelisboa
   ```
2. Quando solicitado, insira seu GitHub Personal Access Token (PAT)
3. O token deve ter permissões:
   - write:packages
   - read:packages

**Alternativa (com token em variável):**
```bash
export GITHUB_TOKEN=seu_token_aqui
echo $GITHUB_TOKEN | docker login ghcr.io -u abelisboa --password-stdin
```

## ⏸️ FASE 3 - Push (APÓS LOGIN)
Após login bem-sucedido, execute:
```bash
docker push ghcr.io/abelisboa/trisla-ml-nsmf:v3.9.0
```

## ⏸️ FASE 4 - Verificação (APÓS PUSH)
Após push bem-sucedido, execute:
```bash
docker pull ghcr.io/abelisboa/trisla-ml-nsmf:v3.9.0
```

## ⏸️ FASE 5 - Atualização Helm
Após push bem-sucedido, editar:
```yaml
# helm/trisla/values-nasp.yaml
mlNsmf:
  image:
    repository: ghcr.io/abelisboa/trisla-ml-nsmf
    tag: "v3.9.0"
```

## ⏸️ FASE 6 - Deploy
Após atualizar Helm, execute:
```bash
cd ~/gtp5g/trisla
helm upgrade --install trisla helm/trisla \
  -n trisla \
  -f helm/trisla/values-nasp.yaml
```

## ⏸️ FASE 7 - Validação
```bash
kubectl -n trisla get pods | grep ml-nsmf
kubectl -n trisla logs deploy/trisla-ml-nsmf | head -n 50
```

## 📝 Próximos Passos
1. Fazer login no GHCR (FASE 2)
2. Fazer push da imagem (FASE 3)
3. Verificar pull (FASE 4)
4. Atualizar Helm (FASE 5)
5. Deploy no NASP (FASE 6)
6. Validação funcional (FASE 7)
