# Instruções FASE 5 - Build Local e Deploy no NASP v3.7.31

## ✅ Status Atual

- ✅ FASE 3.1: Versionamento completo (v3.7.31)
- ✅ FASE 3.2: Validação de estrutura completada
- ✅ FASE 4: Commit e tag criados
  - Commit: `7ea6daa`
  - Tag: `v3.7.31`
  - ⚠️ **PUSH PENDENTE** - Execute manualmente:
    ```bash
    git push origin v3.7.31
    git push origin main
    ```

## 🏗️ FASE 5.1 - Build Local (OBRIGATÓRIO)

### Pré-requisitos:
```bash
cd trisla-portal/frontend
npm install  # Se ainda não executado
```

### Executar Build:
```bash
cd trisla-portal/frontend
npm run build
```

### Validações:
- ✅ Build completa sem erros
- ✅ Arquivos gerados em `.next/`
- ✅ Nenhum warning crítico
- ✅ Versão 3.7.31 presente no build

### Verificação:
```bash
# Verificar se o build foi gerado
ls -la .next/

# Verificar versão no código compilado (opcional)
grep -r "3.7.31" .next/ | head -5
```

## 🐳 FASE 5.2 - Build da Imagem Docker (TAG VERSIONADA)

### ⚠️ REGRA INVIOLÁVEL:
- ❌ **NUNCA usar `latest`**
- ✅ **SEMPRE usar tag versionada: `v3.7.31`**

### Build da Imagem:
```bash
cd trisla-portal/frontend

# Build com tag versionada
docker build -t ghcr.io/abelisboa/trisla-portal:v3.7.31 .

# Verificar imagem criada
docker images | grep trisla-portal
```

### Validações:
- ✅ Imagem criada com sucesso
- ✅ Tag correta: `ghcr.io/abelisboa/trisla-portal:v3.7.31`
- ✅ Tamanho da imagem razoável
- ✅ Nenhum erro durante o build

## 📤 FASE 5.3 - Push da Imagem Docker

### Login no GHCR (se necessário):
```bash
# Opção 1: Via token
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Opção 2: Interativo
docker login ghcr.io
```

### Push da Imagem:
```bash
docker push ghcr.io/abelisboa/trisla-portal:v3.7.31
```

### Validações:
- ✅ Push bem-sucedido
- ✅ Imagem disponível no GHCR
- ✅ Tag v3.7.31 visível no repositório

### Verificação no GHCR:
- Acessar: https://github.com/abelisboa?tab=packages
- Verificar: `trisla-portal` com tag `v3.7.31`

## 🚀 FASE 5.4 - Deploy no NASP

### SSH no node006:
```bash
ssh node006
```

### Navegar para Diretório:
```bash
cd /home/porvir5g/gtp5g/trisla
```

### Verificar Helm Chart:
```bash
# Verificar se Chart.yaml tem versão 3.7.31
cat helm/trisla-portal/Chart.yaml | grep version

# Verificar se values.yaml tem tag v3.7.31
cat helm/trisla-portal/values.yaml | grep tag
```

### Atualizar Helm (se necessário):
```bash
# Editar values.yaml se tag não estiver correta
nano helm/trisla-portal/values.yaml

# Confirmar:
# frontend:
#   image:
#     tag: v3.7.31
```

### Deploy via Helm:
```bash
helm upgrade trisla-portal ./helm/trisla-portal \
  --namespace trisla \
  --set frontend.image.tag=v3.7.31 \
  --reuse-values
```

### Validações Pós-Deploy:
```bash
# Verificar pods
kubectl get pods -n trisla | grep trisla-portal

# Verificar se pods estão Running
kubectl get pods -n trisla -l app=trisla-portal

# Verificar logs (se necessário)
kubectl logs -n trisla -l app=trisla-portal --tail=50

# Verificar NodePort
kubectl get svc -n trisla | grep trisla-portal
```

### Verificar Portal Acessível:
- Frontend: `http://192.168.10.16:32001`
- Backend: `http://192.168.10.16:32002`

### Validações Finais:
- ✅ Portal carrega corretamente
- ✅ Versão v3.7.31 exibida no portal
- ✅ Criação de SLA via PLN funciona
- ✅ Criação de SLA via Template funciona
- ✅ Página de resultado funciona
- ✅ Monitoramento acessível
- ✅ Área Admin mostra versão correta

## 📋 Checklist Completo FASE 5

### Build Local:
- [ ] `npm run build` executado com sucesso
- [ ] Nenhum erro de build
- [ ] Arquivos gerados em `.next/`

### Docker:
- [ ] Imagem buildada: `ghcr.io/abelisboa/trisla-portal:v3.7.31`
- [ ] Imagem pushada para GHCR
- [ ] Tag v3.7.31 visível no GHCR

### Deploy:
- [ ] SSH no node006 realizado
- [ ] Helm Chart atualizado (se necessário)
- [ ] Helm upgrade executado
- [ ] Pods em estado Running
- [ ] Portal acessível via NodePort
- [ ] Versão v3.7.31 exibida no portal
- [ ] Funcionalidades testadas e funcionando

## ⚠️ Observações Importantes

1. **Versionamento**: Sempre usar tag versionada, nunca `latest`
2. **Build Local**: Sempre fazer build local antes do deploy
3. **Validação**: Sempre validar após deploy
4. **Rollback**: Se necessário, usar:
   ```bash
   helm rollback trisla-portal -n trisla
   ```

## 🎯 Próximo Passo

Após deploy bem-sucedido, prosseguir para **FASE 6 - Validação Final**.

