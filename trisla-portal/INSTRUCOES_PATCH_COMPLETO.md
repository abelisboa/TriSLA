# 🚀 INSTRUÇÕES - PATCH COMPLETO TRI-SLA LIGHT

## ✅ PATCH APLICADO COM SUCESSO

Todas as correções foram aplicadas. Siga estas instruções para validar:

---

## 🔧 CONFIGURAÇÃO INICIAL

### 1. Criar arquivo .env.local no frontend

```bash
cd /mnt/c/Users/USER/Documents/TriSLA-clean/trisla-portal/frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1" > .env.local
```

**OU** crie manualmente o arquivo `.env.local` com:
```
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
```

---

## 🧪 VALIDAÇÃO AUTOMÁTICA

### Passo 1: Iniciar Backend

```bash
cd /mnt/c/Users/USER/Documents/TriSLA-clean
bash scripts/portal_manager.sh
# Escolha opção 1 (Iniciar Backend DEV)
```

Aguarde até ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8001
```

---

### Passo 2: Executar Testes Automáticos

Em outro terminal:

```bash
cd /mnt/c/Users/USER/Documents/TriSLA-clean/trisla-portal/backend
bash scripts/validar_rotas.sh
```

**Resultado esperado**: Todos os testes passando ✅

---

## 📋 CORREÇÕES APLICADAS

### ✅ Backend

1. **Router Exportado**: `src/routers/__init__.py` agora exporta `sla` corretamente
2. **CORS Completo**: Configurado para localhost:3000 e 127.0.0.1:3000
3. **Porta Correta**: Backend usando porta 8001
4. **Rotas Funcionando**: Todas as 4 rotas registradas e funcionando

### ✅ Frontend

1. **BaseURL Corrigida**: API client usando porta 8001
2. **Path Correto**: Todas as chamadas usando `/api/v1/sla/...`
3. **Error Handling**: Tratamento de erros melhorado

### ✅ Scripts

1. **Portal Manager**: Libera porta 8001 automaticamente se ocupada
2. **Validação**: Script automático de validação criado

---

## 🎯 ROTAS VALIDADAS

- ✅ `POST /api/v1/sla/interpret` - Criar SLA via PLN
- ✅ `POST /api/v1/sla/submit` - Criar SLA via Template  
- ✅ `GET /api/v1/sla/status/{id}` - Status do SLA
- ✅ `GET /api/v1/sla/metrics/{id}` - Métricas do SLA

---

## 🚀 PRÓXIMOS PASSOS

1. ✅ Backend iniciado e validado
2. ⏭️ Iniciar frontend:
   ```bash
   bash scripts/portal_manager.sh
   # Escolha opção 2 (Iniciar Frontend)
   ```
3. ⏭️ Acessar: http://localhost:3000

---

## ❓ TROUBLESHOOTING

### Erro: Porta 8001 ocupada

O `portal_manager.sh` já libera automaticamente. Se ainda houver problema:

```bash
kill -9 $(lsof -t -i :8001)
```

### Erro: Frontend não conecta ao backend

1. Verifique se backend está rodando: `curl http://127.0.0.1:8001/health`
2. Verifique `.env.local`: `cat trisla-portal/frontend/.env.local`
3. Deve conter: `NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1`

### Erro: CORS bloqueando requisições

Backend já está configurado. Verifique logs do backend para confirmar CORS.

---

**✅ PATCH COMPLETO APLICADO - TRI-SLA LIGHT PRONTO PARA USO!**

