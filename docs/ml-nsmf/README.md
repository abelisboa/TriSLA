# ML-NSMF Documentation

**Version:** 3.7.3  
**Phase:** M (ML-NSMF)  
**Status:** Stabilized

This directory contains a documentação completa of módulo ML-NSMF.

## 📚 Available Documents

### [ML-NSMF Complete Guide](ML_NSMF_COMPLETE_GUIDE.md)

Complete guide that includes:

- ✅ **Overview** of módulo
- ✅ **Architecture** detalhada
- ✅ **Functioning** of pipeline
- ✅ **Model Training** (script completo)
- ✅ **Prediction and XAI** (SHAP/LIME)
- ✅ **Integration** com outros módulos
- ✅ **Interface I-03** (Kafka)
- ✅ **Observability** (métricas e traces)
- ✅ **Usage Examples** (código Python)
- ✅ **Troubleshooting** (soluções for problemas comuns)

## 📁 Related Files

- **Predictor:** `apps/ml_nsmf/src/predictor.py`
- **Treinamento:** `apps/ml_nsmf/training/train_model.py`
- **Modelo:** `apps/ml_nsmf/models/viability_model.pkl`
- **Scaler:** `apps/ml_nsmf/models/scaler.pkl`
- **Metadados:** `apps/ml_nsmf/models/model_metadata.json`
- **Dataset:** `apps/ml_nsmf/data/datasets/trisla_ml_dataset.csv`

## 🎯 Quick Start

1. **Read the Guide:** [`ML_NSMF_COMPLETE_GUIDE.md`](ML_NSMF_COMPLETE_GUIDE.md)
2. **Train Model:** `python apps/ml-nsmf/training/train_model.py`
3. **Use Prediction:** Ver exemplos no guia completo

## 🎓 Training

### Run Training

```bash
cd apps/ml-nsmf
python training/train_model.py
```

### Validate Model

```bash
python -c "from src.predictor import RiskPredictor; p = RiskPredictor(); print('Modelo carregado!')"
```

---

**Última atualização:** 2025-01-27

