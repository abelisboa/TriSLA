# Documentação do ML-NSMF

**Versão:** 3.7.3  
**Fase:** M (ML-NSMF)  
**Status:** Estabilizado

Este diretório contém a documentação completa do módulo ML-NSMF.

## 📚 Documentos Disponíveis

### [Guia Completo do ML-NSMF](ML_NSMF_COMPLETE_GUIDE.md)

Guia completo que inclui:

- ✅ **Visão Geral** do módulo
- ✅ **Arquitetura** detalhada
- ✅ **Funcionamento** do pipeline
- ✅ **Treinamento do Modelo** (script completo)
- ✅ **Predição e XAI** (SHAP/LIME)
- ✅ **Integração** com outros módulos
- ✅ **Interface I-03** (Kafka)
- ✅ **Observabilidade** (métricas e traces)
- ✅ **Exemplos de Uso** (código Python)
- ✅ **Troubleshooting** (soluções para problemas comuns)

## 📁 Arquivos Relacionados

- **Predictor:** `apps/ml_nsmf/src/predictor.py`
- **Treinamento:** `apps/ml_nsmf/training/train_model.py`
- **Modelo:** `apps/ml_nsmf/models/viability_model.pkl`
- **Scaler:** `apps/ml_nsmf/models/scaler.pkl`
- **Metadados:** `apps/ml_nsmf/models/model_metadata.json`
- **Dataset:** `apps/ml_nsmf/data/datasets/trisla_ml_dataset.csv`

## 🎯 Início Rápido

1. **Ler o Guia:** [`ML_NSMF_COMPLETE_GUIDE.md`](ML_NSMF_COMPLETE_GUIDE.md)
2. **Treinar Modelo:** `python apps/ml-nsmf/training/train_model.py`
3. **Usar Predição:** Ver exemplos no guia completo

## 🎓 Treinamento

### Executar Treinamento

```bash
cd apps/ml-nsmf
python training/train_model.py
```

### Validar Modelo

```bash
python -c "from src.predictor import RiskPredictor; p = RiskPredictor(); print('Modelo carregado!')"
```

---

**Última atualização:** 2025-01-27

