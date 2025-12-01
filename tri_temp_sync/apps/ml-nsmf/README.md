# ML-NSMF - Machine Learning Network Slice Management Function

Módulo de Machine Learning para previsão de performance e otimização de recursos.

## Estrutura

```
apps/ml-nsmf/
├── src/
│   ├── main.py              # Aplicação FastAPI
│   ├── model/
│   │   ├── lstm_model.py   # Modelo LSTM/GRU
│   │   └── trainer.py      # Scripts de treinamento
│   ├── predictor.py         # Previsão de risco
│   ├── xai.py              # Explicabilidade (XAI)
│   └── kafka_consumer.py    # Consumo de métricas NASP
├── models/                  # Modelos treinados
│   └── model.h5
├── data/                    # Datasets
├── tests/
├── Dockerfile
├── requirements.txt
└── README.md
```

## Pipeline

1. Receber métricas NASP
2. Normalizar dados
3. Prever risco (LSTM/GRU)
4. Explicar previsão (XAI)
5. Enviar para Decision Engine via I-03 (Kafka)

## Interface I-03

- **Protocolo**: Kafka
- **Tópico**: `trisla-ml-predictions`
- **Destino**: Decision Engine

