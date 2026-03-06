# ✅ Erro SQLAlchemy `metadata` Corrigido

## ❌ Problema

**Erro:**
```
sqlalchemy.exc.InvalidRequestError: Attribute name 'metadata' is reserved when using the Declarative API.
```

**Causa:** O atributo `metadata` é uma palavra reservada no SQLAlchemy Declarative API.

---

## ✅ Correção Aplicada

### Arquivos Corrigidos:

1. **`src/models/contract.py`** (linha 34)
   - ❌ `metadata = Column(JSON, nullable=True)`
   - ✅ `contract_metadata = Column(JSON, nullable=True)`

2. **`src/services/contracts.py`** (linha 35)
   - ❌ `ContractModel.metadata["service_type"]`
   - ✅ `ContractModel.contract_metadata["service_type"]`

3. **`src/schemas/contracts.py`** (linhas 38 e 52)
   - ❌ `metadata: Dict[str, Any]`
   - ✅ `contract_metadata: Optional[Dict[str, Any]] = None`

---

## ✅ Status

- ✅ Backend pode ser importado sem erros
- ✅ Todas as referências atualizadas
- ✅ Pronto para iniciar

---

## 🚀 Iniciar Backend

```bash
cd /mnt/c/Users/USER/Documents/TriSLA-clean/trisla-portal/backend
source venv/bin/activate
uvicorn src.main:app --reload --port 8001
```

**O backend deve iniciar sem erros!**

---

## 📝 Nota

O campo foi renomeado de `metadata` para `contract_metadata` em:
- Modelo SQLAlchemy
- Schemas Pydantic
- Serviços

Isso mantém a funcionalidade, mas evita o conflito com a palavra reservada do SQLAlchemy.
