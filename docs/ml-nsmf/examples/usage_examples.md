# ML-NSMF Usage Examples and Operations

## 1. Training Execution

```bash
cd apps/ml-nsmf
python training/train_model.py
```

## 2. Predictor Load Check

```bash
python -c "from src.predictor import RiskPredictor; p = RiskPredictor(); print('Model loaded successfully!')"
```

## 3. Conceptual Prediction Example

```python
from src.predictor import RiskPredictor

predictor = RiskPredictor()

features = {
    "latency": 12.0,
    "throughput": 120.0,
    "reliability": 0.999,
    "jitter": 2.1,
    "cpu_utilization": 0.78,
    "memory_utilization": 0.71,
    "network_bandwidth_available": 220.0,
    "active_slices_count": 18
}

result = predictor.predict(features)
print(result)
```

## 4. Troubleshooting Patterns

- **Model artifact missing**: verify model/scaler files and metadata path
- **Kafka unavailable**: verify broker endpoint and topic availability
- **Unexpected score drift**: verify feature normalization and model version alignment
- **XAI unavailable**: fallback method should be enabled and logged

## 5. Reproducibility Checklist

- Pin model/scaler versions in experiment records
- Persist feature schema used during inference
- Log prediction ID, model metadata, and elapsed inference time
- Correlate I-02 and I-03 message identifiers
