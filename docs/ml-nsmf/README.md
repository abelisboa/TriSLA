# ML-NSMF Documentation

**Version:** 3.7.3  
**Phase:** M (ML-NSMF)  
**Status:** Stabilized  

This directory contains the complete documentation of the **ML-NSMF (Machine Learning Network Slice Management Function)** module.

---

## 📚 Available Documents

### [ML-NSMF Complete Guide](ML_NSMF_COMPLETE_GUIDE.md)

Comprehensive guide that includes:

- ✅ **Module Overview**
- ✅ **Detailed Architecture**
- ✅ **Pipeline Operation**
- ✅ **Model Training** (complete script)
- ✅ **Prediction and XAI** (SHAP/LIME)
- ✅ **Integration** with other modules
- ✅ **Interface I-03** (Kafka)
- ✅ **Observability** (metrics and traces)
- ✅ **Usage Examples** (Python code)
- ✅ **Troubleshooting** (solutions for common issues)

---

## 📁 Related Files

- **Predictor:** `apps/ml-nsmf/src/predictor.py`  
- **Training:** `apps/ml-nsmf/training/train_model.py`  
- **Model:** `apps/ml-nsmf/models/viability_model.pkl`  
- **Scaler:** `apps/ml-nsmf/models/scaler.pkl`  
- **Metadata:** `apps/ml-nsmf/models/model_metadata.json`  
- **Dataset:** `apps/ml-nsmf/data/datasets/trisla_ml_dataset.csv`  

---

## 🎯 Quick Start

1. **Read the Guide:** [`ML_NSMF_COMPLETE_GUIDE.md`](ML_NSMF_COMPLETE_GUIDE.md)  
2. **Train the Model:**  
   ```bash
   python apps/ml-nsmf/training/train_model.py

Run Predictions: See usage examples in the complete guide

🎓 Training
Run Training

cd apps/ml-nsmf
python training/train_model.py

Validate Model

python -c "from src.predictor import RiskPredictor; p = RiskPredictor(); print('Model loaded successfully!')"

Last updated: 2025-01-27
